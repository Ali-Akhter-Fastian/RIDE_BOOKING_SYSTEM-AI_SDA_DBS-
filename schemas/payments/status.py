from __future__ import annotations

from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from core.enums import PaymentStatus


class PaymentStatusResponse(BaseModel):
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
