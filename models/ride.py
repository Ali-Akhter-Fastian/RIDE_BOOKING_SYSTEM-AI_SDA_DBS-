from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from core.enums import RideStatus


@dataclass(slots=True)
class Ride:
    id: UUID
    rider_id: UUID
    driver_id: UUID | None
    status: RideStatus
    origin: str
    destination: str
    fare: Decimal | None
    rating: int | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: object) -> "Ride":
        return cls(
            id=record["id"],
            rider_id=record["rider_id"],
            driver_id=record["driver_id"],
            status=RideStatus(record["status"]),
            origin=record["origin"],
            destination=record["destination"],
            fare=record["fare"],
            rating=record["rating"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )
