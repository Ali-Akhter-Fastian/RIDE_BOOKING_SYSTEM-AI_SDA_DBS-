from __future__ import annotations

RETURNING_FIELDS = """
    id, rider_id, driver_id, status, origin, destination, fare, rating, created_at, updated_at
"""

INSERT_RIDE = f"""
INSERT INTO rides (id, rider_id, status, origin, destination, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
RETURNING {RETURNING_FIELDS}
"""

SELECT_RIDE_BY_ID = f"""
SELECT {RETURNING_FIELDS}
FROM rides
WHERE id = $1
"""

SELECT_RIDES_BY_RIDER = f"""
SELECT {RETURNING_FIELDS}
FROM rides
WHERE rider_id = $1
ORDER BY created_at DESC
"""

SELECT_RIDES_BY_DRIVER = f"""
SELECT {RETURNING_FIELDS}
FROM rides
WHERE driver_id = $1
ORDER BY created_at DESC
"""

# For pagination: count total rows before slicing
COUNT_RIDES_BY_RIDER = """
SELECT COUNT(*) FROM rides WHERE rider_id = $1
"""

COUNT_RIDES_BY_DRIVER = """
SELECT COUNT(*) FROM rides WHERE driver_id = $1
"""

# Paginated history queries
SELECT_RIDES_BY_RIDER_PAGINATED = f"""
SELECT {RETURNING_FIELDS}
FROM rides
WHERE rider_id = $1
ORDER BY created_at DESC
LIMIT $2 OFFSET $3
"""

SELECT_RIDES_BY_DRIVER_PAGINATED = f"""
SELECT {RETURNING_FIELDS}
FROM rides
WHERE driver_id = $1
ORDER BY created_at DESC
LIMIT $2 OFFSET $3
"""

SELECT_ACTIVE_RIDE_BY_RIDER = f"""
SELECT {RETURNING_FIELDS}
FROM rides
WHERE rider_id = $1
  AND status IN ('requested', 'accepted', 'in_progress')
LIMIT 1
"""

# State-guarded status transitions — prevents skipping states at the DB level
START_RIDE = f"""
UPDATE rides
SET status = 'in_progress', updated_at = NOW()
WHERE id = $1
  AND status = 'accepted'
RETURNING {RETURNING_FIELDS}
"""

COMPLETE_RIDE = f"""
UPDATE rides
SET status = 'completed', updated_at = NOW()
WHERE id = $1
  AND status = 'in_progress'
RETURNING {RETURNING_FIELDS}
"""

ASSIGN_DRIVER = f"""
UPDATE rides
SET driver_id = $2, status = 'accepted', updated_at = NOW()
WHERE id = $1
  AND status = 'requested'
RETURNING {RETURNING_FIELDS}
"""

CANCEL_RIDE = f"""
UPDATE rides
SET status = 'cancelled', updated_at = NOW()
WHERE id = $1
  AND status IN ('requested', 'accepted')
RETURNING {RETURNING_FIELDS}
"""

UPDATE_DRIVER_RATING = f"""
UPDATE rides
SET rating = $2, updated_at = NOW()
WHERE id = $1
  AND rider_id = $3
  AND status = 'completed'
  AND rating IS NULL
RETURNING {RETURNING_FIELDS}
"""
