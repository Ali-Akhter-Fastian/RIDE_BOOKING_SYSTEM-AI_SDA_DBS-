from __future__ import annotations

from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.enums import PaymentStatus


class CreatePaymentRequest(BaseModel):
    ride_id: UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    payment_method: str = Field(min_length=1, max_length=50)


class CreatePaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ride_id: UUID
    user_id: UUID
    amount: Decimal
    status: PaymentStatus
    payment_method: str
    transaction_id: str | None
    created_at: datetime
    updated_at: datetime
