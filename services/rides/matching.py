from __future__ import annotations

from uuid import UUID

from core.enums import RideStatus
from exception.ride_exceptions import (
    DriverNotAvailable,
    InvalidRideTransition,
    RideNotFound,
    RideOwnershipError,
)
from models.ride import Ride

from .base import RideServiceBase


class RideMatchingService(RideServiceBase):

    async def find_driver_for_ride(self, ride_id: UUID, rider_id: UUID) -> Ride:
        ride = await self.repository.get_by_id(ride_id)
        if ride is None:
            raise RideNotFound(f"Ride {ride_id} not found")
        if ride.rider_id != rider_id:
            raise RideOwnershipError("You are not the owner of this ride request")
        if ride.status != RideStatus.requested:
            raise InvalidRideTransition(
                "Driver search can only be started for rides in requested status"
            )

        driver_id = await self.repository.find_available_driver()
        if driver_id is None:
            raise DriverNotAvailable("No available drivers at the moment")

        return await self.repository.assign_driver(ride_id, driver_id)

    async def driver_accept_matched_ride(self, ride_id: UUID, driver_id: UUID) -> Ride:
        """Driver confirms acceptance of a matched ride offer."""
        ride = await self.repository.get_by_id(ride_id)
        if ride is None:
            raise RideNotFound(f"Ride {ride_id} not found")
        if ride.driver_id != driver_id:
            raise RideOwnershipError(
                "You are not the assigned driver for this ride"
            )
        if ride.status != RideStatus.accepted:
            raise InvalidRideTransition(
                f"Can only accept rides in 'accepted' status, current status is '{ride.status}'"
            )
        return ride

    async def driver_reject_matched_ride(self, ride_id: UUID, driver_id: UUID) -> Ride:
        """Driver rejects a matched ride and triggers a rematch with a new available driver."""
        ride = await self.repository.get_by_id(ride_id)
        if ride is None:
            raise RideNotFound(f"Ride {ride_id} not found")
        if ride.driver_id != driver_id:
            raise RideOwnershipError(
                "You are not the assigned driver for this ride"
            )
        if ride.status != RideStatus.accepted:
            raise InvalidRideTransition(
                f"Can only reject rides in 'accepted' status, current status is '{ride.status}'"
            )

        return await self.repository.reject_driver_and_find_new_driver(
            ride_id, driver_id
        )

    async def get_matching_status(self, ride_id: UUID, rider_id: UUID) -> Ride:
        """Get current status of driver matching for a ride (polling endpoint)."""
        ride = await self.repository.get_by_id(ride_id)
        if ride is None:
            raise RideNotFound(f"Ride {ride_id} not found")
        if ride.rider_id != rider_id:
            raise RideOwnershipError("You are not the owner of this ride request")
        return ride
