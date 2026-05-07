from __future__ import annotations

from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.enums import RideStatus


class CreateRideRequest(BaseModel):
    origin: str = Field(min_length=3, max_length=255)
    destination: str = Field(min_length=3, max_length=255)


class CreateRideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rider_id: UUID
    driver_id: UUID | None
    status: RideStatus
    origin: str
    destination: str
    fare: Decimal | None
    created_at: datetime
    updated_at: datetime
