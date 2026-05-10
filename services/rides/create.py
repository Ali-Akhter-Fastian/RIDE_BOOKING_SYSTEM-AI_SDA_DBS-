from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from core.enums import RideStatus
from exception.ride_exceptions import RiderHasActiveRide
from models.ride import Ride
from schemas.rides.create import CreateRideRequest

from .base import RideServiceBase


class RideCreationService(RideServiceBase):

    async def create_ride(self, payload: CreateRideRequest, rider_id: UUID) -> Ride:
        active = await self.repository.get_active_ride_by_rider(rider_id)
        if active is not None:
            raise RiderHasActiveRide(
                "You already have an active ride. Complete or cancel it before requesting a new one."
            )

        now = datetime.now(timezone.utc)
        ride = Ride(
            id=uuid4(),
            rider_id=rider_id,
            driver_id=None,
            status=RideStatus.requested,
            origin=payload.origin,
            destination=payload.destination,
            fare=None,
            rating=None,
            created_at=now,
            updated_at=now,
            pickup_latitude=Decimal(str(payload.pickup_latitude)),
            pickup_longitude=Decimal(str(payload.pickup_longitude)),
        )
        return await self.repository.create(ride)
