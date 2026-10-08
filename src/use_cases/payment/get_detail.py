from dataclasses import dataclass
from uuid import UUID

from src.db.uow import IUnitOfWork
from src.exceptions.payment import PaymentNotFoundError
from src.models.payment import Payment
from src.schemas.payment import PaymentDetailResponse


@dataclass
class GetPaymentUseCase:
    uow: IUnitOfWork

    async def execute(self, payment_id: UUID) -> PaymentDetailResponse:
        async with self.uow:
            payment: Payment | None = await self.uow.payments.get_by_id(
                payment_id=payment_id
            )

            if not payment:
                raise PaymentNotFoundError(payment_id=payment_id)

            return PaymentDetailResponse.model_validate(payment)
