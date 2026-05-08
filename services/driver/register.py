from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from core.enums import UserRole
from core.security import hash_password
from exception.driver_exceptions import DriverExists
from models.driver import Driver
from repositories.driver_repository import DriverRepository
from schemas.driver.register import DriverRegisterRequest

from .base import DriverServiceBase


class RegisterDriverService(DriverServiceBase):
    async def register_driver(self, payload: DriverRegisterRequest) -> Driver:
        existing_driver = await self.repository.get_by_email(payload.email)
        if existing_driver is not None:
            raise DriverExists("Driver with this email already exists")

        now = datetime.now(timezone.utc)
        driver = Driver(
            id=uuid4(),
            full_name=payload.full_name,
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            role=UserRole.driver,
            created_at=now,
            updated_at=now,
            license_number=payload.license_number,
            vehicle_number=payload.vehicle_number,
            vehicle_type=payload.vehicle_type,
            rating=Decimal('0.00'),
            total_rides=0,
            is_available=True,
        )
        return await self.repository.create(driver)
