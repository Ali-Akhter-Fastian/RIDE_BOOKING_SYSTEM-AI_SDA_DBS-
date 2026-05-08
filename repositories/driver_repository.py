from __future__ import annotations
from uuid import UUID
import asyncpg

from db.queries.auth_queries import SELECT_USER_BY_ID
from db.queries.driver_queries import (
    INSERT_DRIVER,
    SELECT_DRIVER_BY_EMAIL,
    SELECT_DRIVER_BY_ID,
    SELECT_AVAILABLE_DRIVERS,
    UPDATE_DRIVER_AVAILABILITY,
    UPDATE_DRIVER_RATING,
)
from exception.driver_exceptions import DriverDatabaseSchemaError, DriverRepositoryError
from models.driver import Driver


class DriverRepository:
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def get_by_id(self, driver_id: UUID) -> Driver | None:
        try:
            record = await self.connection.fetchrow(SELECT_DRIVER_BY_ID, driver_id)
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Drivers table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to read driver from database") from exc
        if record is None:
            return None
        return Driver.from_record(record)

    async def get_by_email(self, email: str) -> Driver | None:
        try:
            record = await self.connection.fetchrow(SELECT_DRIVER_BY_EMAIL, email.lower())
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Drivers table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to read driver from database") from exc
        if record is None:
            return None
        return Driver.from_record(record)

    async def create(self, driver: Driver) -> Driver:
        try:
            record = await self.connection.fetchrow(
                INSERT_DRIVER,
                driver.id,
                driver.full_name,
                driver.email,
                driver.password_hash,
                driver.role.value,
                driver.license_number,
                driver.vehicle_number,
                driver.vehicle_type,
                float(driver.rating),
                driver.total_rides,
                driver.is_available,
            )
        except asyncpg.UniqueViolationError as exc:
            raise DriverRepositoryError("Email already exists") from exc
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Drivers table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to create driver in database") from exc
        if record is None:
            raise DriverRepositoryError("Failed to create driver - no record returned")
        return Driver.from_record(record)

    async def get_available_drivers(self) -> list[Driver]:
        try:
            records = await self.connection.fetch(SELECT_AVAILABLE_DRIVERS)
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Drivers table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to read available drivers from database") from exc
        return [Driver.from_record(record) for record in records]

    async def update_availability(self, driver_id: UUID, is_available: bool) -> Driver | None:
        try:
            record = await self.connection.fetchrow(UPDATE_DRIVER_AVAILABILITY, driver_id, is_available)
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Drivers table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to update driver availability") from exc
        if record is None:
            return None
        return Driver.from_record(record)

    async def update_rating(self, driver_id: UUID, new_rating: float) -> Driver | None:
        try:
            record = await self.connection.fetchrow(UPDATE_DRIVER_RATING, driver_id, new_rating)
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Drivers table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to update driver rating") from exc
        if record is None:
            return None
        return Driver.from_record(record)
