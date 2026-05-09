from __future__ import annotations

# Driver table queries - drivers now reference users via user_id
INSERT_DRIVER = """
INSERT INTO drivers (
	id,
	user_id,
	full_name,
	email,
	password_hash,
	role,
	created_at,
	updated_at,
	license_number,
	vehicle_number,
	vehicle_type,
	rating,
	total_rides,
	is_available
)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
RETURNING id
"""

# Return a joined driver+user view
SELECT_DRIVER_BY_ID = """
SELECT
	users.id,
	users.full_name,
	users.email,
	users.password_hash,
	users.role,
	users.created_at,
	users.updated_at,
	drivers.license_number,
	drivers.vehicle_number,
	drivers.vehicle_type,
	drivers.rating,
	drivers.total_rides,
	drivers.is_available
FROM drivers
JOIN users ON users.id = drivers.user_id
WHERE drivers.id = $1
"""

SELECT_DRIVER_BY_EMAIL = """
SELECT
	users.id,
	users.full_name,
	users.email,
	users.password_hash,
	users.role,
	users.created_at,
	users.updated_at,
	drivers.license_number,
	drivers.vehicle_number,
	drivers.vehicle_type,
	drivers.rating,
	drivers.total_rides,
	drivers.is_available
FROM drivers
JOIN users ON users.id = drivers.user_id
WHERE users.email = $1
"""

SELECT_AVAILABLE_DRIVERS = """
SELECT
	users.id,
	users.full_name,
	users.email,
	users.password_hash,
	users.role,
	users.created_at,
	users.updated_at,
	drivers.license_number,
	drivers.vehicle_number,
	drivers.vehicle_type,
	drivers.rating,
	drivers.total_rides,
	drivers.is_available
FROM drivers
JOIN users ON users.id = drivers.user_id
WHERE drivers.is_available = true
ORDER BY drivers.rating DESC, drivers.total_rides DESC
"""

UPDATE_DRIVER_AVAILABILITY = """
UPDATE drivers
SET is_available = $2, updated_at = NOW()
WHERE id = $1
RETURNING id
"""

UPDATE_DRIVER_RATING = """
UPDATE drivers
SET rating = $2, total_rides = total_rides + 1, updated_at = NOW()
WHERE id = $1
RETURNING id
"""

# Vehicles
INSERT_VEHICLE = """
INSERT INTO vehicles (vehicle_id, plate_no, driver_id, make_model, color, vehicle_type, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
RETURNING vehicle_id
"""
