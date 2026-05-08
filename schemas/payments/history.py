from __future__ import annotations

from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from core.enums import PaymentStatus


class PaymentHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ride_id: UUID
    amount: Decimal
    status: PaymentStatus
    payment_method: str
    created_at: datetime
    updated_at: datetime


class PaymentHistoryResponse(BaseModel):
    payments: list[PaymentHistoryItem]
    total: int
    limit: int
    offset: int
