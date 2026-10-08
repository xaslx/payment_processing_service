from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from src.db.uow import IUnitOfWork
from src.exceptions.payment import (
    PaymentAlreadyExistsError,
    PaymentIdempotencyConflictError,
)
from src.models.outbox import OutboxEvent
from src.models.payment import Payment
from src.schemas.payment import PaymentCreate, PaymentCreatedResponse


def _same_payload(existing: Payment, schema: PaymentCreate) -> bool:
    existing_amount = Decimal(existing.amount).quantize(Decimal("0.01"))
    request_amount = Decimal(schema.amount).quantize(Decimal("0.01"))
    existing_meta = existing.meta_data or {}
    request_meta = schema.meta_data or {}
    existing_webhook = existing.webhook_url or ""
    request_webhook = str(schema.webhook_url) if schema.webhook_url else ""

    return (
        existing_amount == request_amount
        and existing.currency == schema.currency
        and (existing.description or None) == (schema.description or None)
        and existing_meta == request_meta
        and existing_webhook == request_webhook
    )


@dataclass
class CreatePaymentUseCase:
    uow: IUnitOfWork

    async def execute(
        self, schema: PaymentCreate, idempotency_key: str
    ) -> PaymentCreatedResponse:
        async with self.uow:
            existing: Payment | None = await self.uow.payments.get_by_idempotency_key(
                idempotency_key
            )
            if existing:
                if not _same_payload(existing, schema):
                    raise PaymentIdempotencyConflictError(idempotency_key)
                return PaymentCreatedResponse.model_validate(existing)

            payment = Payment(
                amount=schema.amount,
                currency=schema.currency,
                description=schema.description,
                meta_data=schema.meta_data,
                webhook_url=str(schema.webhook_url) if schema.webhook_url else None,
                idempotency_key=idempotency_key,
            )
            try:
                await self.uow.payments.add(payment)
                await self.uow.flush()

                event = OutboxEvent(
                    event_type="payment.new",
                    payload={"payment_id": str(payment.id)},
                    processed=False,
                )
                await self.uow.outbox.add(event)
                await self.uow.commit()
                return PaymentCreatedResponse.model_validate(payment)
            except IntegrityError as exc:
                await self.uow.rollback()
                raise PaymentAlreadyExistsError(idempotency_key) from exc
