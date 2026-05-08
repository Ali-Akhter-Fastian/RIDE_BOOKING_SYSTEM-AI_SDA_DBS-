from __future__ import annotations

# Driver table queries
INSERT_DRIVER = """
INSERT INTO drivers (id, full_name, email, password_hash, role, created_at, updated_at, license_number, vehicle_number, vehicle_type, rating, total_rides, is_available)
VALUES ($1, $2, $3, $4, $5, NOW(), NOW(), $6, $7, $8, $9, $10, $11)
RETURNING id, full_name, email, password_hash, role, created_at, updated_at, license_number, vehicle_number, vehicle_type, rating, total_rides, is_available
"""

SELECT_DRIVER_BY_ID = """
SELECT id, full_name, email, password_hash, role, created_at, updated_at, license_number, vehicle_number, vehicle_type, rating, total_rides, is_available
FROM drivers
WHERE id = $1
"""

SELECT_DRIVER_BY_EMAIL = """
SELECT id, full_name, email, password_hash, role, created_at, updated_at, license_number, vehicle_number, vehicle_type, rating, total_rides, is_available
FROM drivers
WHERE email = $1
"""

SELECT_AVAILABLE_DRIVERS = """
SELECT id, full_name, email, password_hash, role, created_at, updated_at, license_number, vehicle_number, vehicle_type, rating, total_rides, is_available
FROM drivers
WHERE is_available = true
ORDER BY rating DESC, total_rides DESC
"""

UPDATE_DRIVER_AVAILABILITY = """
UPDATE drivers
SET is_available = $2, updated_at = NOW()
WHERE id = $1
RETURNING id, full_name, email, password_hash, role, created_at, updated_at, license_number, vehicle_number, vehicle_type, rating, total_rides, is_available
"""

UPDATE_DRIVER_RATING = """
UPDATE drivers
SET rating = $2, total_rides = total_rides + 1, updated_at = NOW()
WHERE id = $1
RETURNING id, full_name, email, password_hash, role, created_at, updated_at, license_number, vehicle_number, vehicle_type, rating, total_rides, is_available
"""
