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
from exception.driver_exceptions import DriverDatabaseSchemaError, DriverRepositoryError, DriverExists
from models.driver import Driver
import uuid
from db.queries.driver_queries import INSERT_VEHICLE


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
            # Insert driver-specific fields and link to the user via user_id
            record = await self.connection.fetchrow(
                INSERT_DRIVER,
                driver.id,
                driver.id,  # user_id should match the user id (legacy behavior)
                driver.full_name,
                driver.email,
                driver.password_hash,
                driver.role.value,
                driver.created_at,
                driver.updated_at,
                driver.license_number,
                driver.vehicle_number,
                driver.vehicle_type,
                float(driver.rating),
                driver.total_rides,
                driver.is_available,
            )
        except asyncpg.UniqueViolationError as exc:
            # Unique violation likely means a driver/user with this identity already exists
            raise DriverExists("Driver with this id or unique field already exists") from exc
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Drivers table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to create driver in database") from exc
        if record is None:
            raise DriverRepositoryError("Failed to create driver - no id returned")

        # Fetch the full joined driver+user record
        created_id = record["id"]
        try:
            joined = await self.connection.fetchrow(SELECT_DRIVER_BY_ID, created_id)
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to read created driver from database") from exc
        if joined is None:
            raise DriverRepositoryError("Failed to fetch created driver")
        return Driver.from_record(joined)

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
            record = await self.connection.fetchrow(UPDATE_DRIVER_AVAILABILITY, str(driver_id), is_available)
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Drivers table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to update driver availability") from exc
        if record is None:
            return None
        # fetch full joined record
        joined = await self.connection.fetchrow(SELECT_DRIVER_BY_ID, record["id"])
        if joined is None:
            return None
        return Driver.from_record(joined)

    async def update_rating(self, driver_id: UUID, new_rating: float) -> Driver | None:
        try:
            record = await self.connection.fetchrow(UPDATE_DRIVER_RATING, driver_id, new_rating)
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Drivers table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to update driver rating") from exc
        if record is None:
            return None
        joined = await self.connection.fetchrow(SELECT_DRIVER_BY_ID, driver_id)
        if joined is None:
            return None
        return Driver.from_record(joined)

    async def create_vehicle(self, driver_id: UUID, plate_no: str, make_model: str, color: str | None, vehicle_type: str) -> uuid.UUID:
        try:
            vehicle_id = uuid.uuid4()
            record = await self.connection.fetchrow(
                INSERT_VEHICLE,
                vehicle_id,
                plate_no,
                driver_id,
                make_model,
                color,
                vehicle_type,
            )
        except asyncpg.UniqueViolationError as exc:
            raise DriverExists("Vehicle with this plate number already exists") from exc
        except asyncpg.UndefinedTableError as exc:
            raise DriverDatabaseSchemaError("Vehicles table is missing. Run DB migrations first.") from exc
        except asyncpg.PostgresError as exc:
            raise DriverRepositoryError("Failed to create vehicle in database") from exc
        if record is None:
            raise DriverRepositoryError("Failed to create vehicle - no id returned")
        return record["vehicle_id"]
