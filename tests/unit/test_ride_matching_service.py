from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from app.config import Settings
from core.enums import RideStatus
from exception.ride_exceptions import (
    InvalidRideTransition,
    RideNotFound,
    RideOwnershipError,
)
from models.ride import Ride
from services.rides.matching import RideMatchingService


def _ride(
    status: RideStatus = RideStatus.requested,
    rider_id: UUID | None = None,
    driver_id: UUID | None = None,
) -> Ride:
    now = datetime.now(timezone.utc)
    return Ride(
        id=uuid4(),
        rider_id=rider_id or uuid4(),
        driver_id=driver_id,
        status=status,
        origin="Downtown",
        destination="Airport",
        fare=None,
        rating=None,
        created_at=now,
        updated_at=now,
    )


@dataclass
class FakeRideRepository:
    rides: dict[UUID, Ride] = field(default_factory=dict)
    replacement_driver_id: UUID | None = None

    async def get_by_id(self, ride_id: UUID) -> Ride | None:
        return self.rides.get(ride_id)

    async def reject_driver_and_find_new_driver(
        self, ride_id: UUID, driver_id: UUID
    ) -> Ride:
        ride = self.rides.get(ride_id)
        if ride is None or ride.status != RideStatus.accepted:
            raise RideNotFound(f"Ride {ride_id} not found")
        if ride.driver_id != driver_id:
            raise RideOwnershipError("You are not the assigned driver for this ride")

        if self.replacement_driver_id is None:
            updated = Ride(
                id=ride.id,
                rider_id=ride.rider_id,
                driver_id=None,
                status=RideStatus.requested,
                origin=ride.origin,
                destination=ride.destination,
                fare=ride.fare,
                rating=ride.rating,
                created_at=ride.created_at,
                updated_at=datetime.now(timezone.utc),
            )
        else:
            updated = Ride(
                id=ride.id,
                rider_id=ride.rider_id,
                driver_id=self.replacement_driver_id,
                status=RideStatus.accepted,
                origin=ride.origin,
                destination=ride.destination,
                fare=ride.fare,
                rating=ride.rating,
                created_at=ride.created_at,
                updated_at=datetime.now(timezone.utc),
            )
        self.rides[ride_id] = updated
        return updated


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        database_url="postgresql://localhost/test",
        jwt_secret="test-secret",
        jwt_algorithm="HS256",
        access_token_expire_minutes=60,
        refresh_token_expire_minutes=10080,
    )


@pytest.fixture()
def repo() -> FakeRideRepository:
    return FakeRideRepository()


@pytest.mark.asyncio()
async def test_driver_reject_matched_ride_triggers_rematch_when_available(
    repo: FakeRideRepository, settings: Settings
) -> None:
    driver_id = uuid4()
    new_driver_id = uuid4()
    ride = _ride(RideStatus.accepted, driver_id=driver_id)
    repo.rides[ride.id] = ride
    repo.replacement_driver_id = new_driver_id

    result = await RideMatchingService(repo, settings).driver_reject_matched_ride(
        ride.id, driver_id
    )

    assert result.status == RideStatus.accepted
    assert result.driver_id == new_driver_id


@pytest.mark.asyncio()
async def test_driver_reject_matched_ride_returns_requested_when_no_driver_available(
    repo: FakeRideRepository, settings: Settings
) -> None:
    driver_id = uuid4()
    ride = _ride(RideStatus.accepted, driver_id=driver_id)
    repo.rides[ride.id] = ride
    repo.replacement_driver_id = None

    result = await RideMatchingService(repo, settings).driver_reject_matched_ride(
        ride.id, driver_id
    )

    assert result.status == RideStatus.requested
    assert result.driver_id is None


@pytest.mark.asyncio()
async def test_driver_reject_matched_ride_rejects_wrong_driver(
    repo: FakeRideRepository, settings: Settings
) -> None:
    ride = _ride(RideStatus.accepted, driver_id=uuid4())
    repo.rides[ride.id] = ride

    with pytest.raises(RideOwnershipError):
        await RideMatchingService(repo, settings).driver_reject_matched_ride(
            ride.id, uuid4()
        )


@pytest.mark.asyncio()
async def test_driver_reject_matched_ride_rejects_wrong_status(
    repo: FakeRideRepository, settings: Settings
) -> None:
    driver_id = uuid4()
    ride = _ride(RideStatus.requested, driver_id=driver_id)
    repo.rides[ride.id] = ride

    with pytest.raises(InvalidRideTransition):
        await RideMatchingService(repo, settings).driver_reject_matched_ride(
            ride.id, driver_id
        )
