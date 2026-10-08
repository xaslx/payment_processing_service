import enum
import uuid
from decimal import Decimal

from sqlalchemy import JSON, Enum, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Currency(enum.Enum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency_enum", create_type=True),
        default=Currency.RUB,
        nullable=False,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(
            PaymentStatus,
            name="paymentstatus",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        server_default=PaymentStatus.PENDING.value,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(String(255))
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    meta_data: Mapped[dict | None] = mapped_column(JSON)
    webhook_url: Mapped[str | None] = mapped_column(String(512))
