from __future__ import annotations

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.enums import PaymentStatus


class ConfirmPaymentRequest(BaseModel):
    transaction_id: str = Field(min_length=1, max_length=255)


class ConfirmPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ride_id: UUID
    user_id: UUID
    amount: float
    status: PaymentStatus
    payment_method: str
    transaction_id: str
    created_at: datetime
    updated_at: datetime
