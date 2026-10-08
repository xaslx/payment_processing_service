from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.models.payment import Currency, PaymentStatus


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    currency: Currency
    description: str | None = Field(None, max_length=255)
    meta_data: dict[str, Any] = Field(default_factory=dict)
    webhook_url: HttpUrl


class PaymentCreatedResponse(BaseModel):
    payment_id: UUID = Field(validation_alias="id")
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentDetailResponse(BaseModel):
    payment_id: UUID = Field(validation_alias="id")
    amount: Decimal
    currency: Currency
    status: PaymentStatus
    description: str | None = None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="meta_data")
    webhook_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
