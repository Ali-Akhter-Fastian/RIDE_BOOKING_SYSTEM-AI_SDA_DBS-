from __future__ import annotations

from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.enums import RideStatus, RideType


class CreateRideRequest(BaseModel):
    origin: str = Field(min_length=3, max_length=255)
    destination: str = Field(min_length=3, max_length=255)
    ride_type: RideType = Field(default=RideType.ridex)
    pickup_latitude: float = Field(ge=-90, le=90)
    pickup_longitude: float = Field(ge=-180, le=180)


class CreateRideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rider_id: UUID
    driver_id: UUID | None
    status: RideStatus
    origin: str
    destination: str
    ride_type: RideType
    fare: Decimal | None
    pickup_latitude: float | None
    pickup_longitude: float | None
    created_at: datetime
    updated_at: datetime
