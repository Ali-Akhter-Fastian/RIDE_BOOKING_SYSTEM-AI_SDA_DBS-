from __future__ import annotations

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentMethodRequest(BaseModel):
    method_type: str = Field(min_length=1, max_length=50)
    is_default: bool = False


class PaymentMethodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    method_type: str
    is_default: bool
    created_at: datetime
    updated_at: datetime
