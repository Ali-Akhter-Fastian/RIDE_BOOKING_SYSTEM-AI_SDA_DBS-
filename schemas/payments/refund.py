from __future__ import annotations

from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from core.enums import PaymentStatus


class RefundPaymentRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class PartialRefundRequest(BaseModel):
    refund_amount: Decimal = Field(gt=0, decimal_places=2)
    reason: str = Field(min_length=1, max_length=500)


class RefundResponse(BaseModel):
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
