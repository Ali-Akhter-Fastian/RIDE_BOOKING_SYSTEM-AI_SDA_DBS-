from __future__ import annotations

# ================================================================ #
# Create                                                           #
# ================================================================ #

INSERT_PAYMENT = """
    INSERT INTO payments (id, ride_id, user_id, amount, status, payment_method, transaction_id, created_at, updated_at)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    RETURNING *;
"""

# ================================================================ #
# Read                                                              #
# ================================================================ #

SELECT_PAYMENT_BY_ID = """
    SELECT * FROM payments WHERE id = $1;
"""

SELECT_PAYMENT_BY_RIDE_ID = """
    SELECT * FROM payments WHERE ride_id = $1;
"""

SELECT_PAYMENTS_BY_USER_ID = """
    SELECT * FROM payments WHERE user_id = $1;
"""

SELECT_PAYMENT_BY_TRANSACTION_ID = """
    SELECT * FROM payments WHERE transaction_id = $1;
"""

SELECT_PAYMENTS_BY_USER_PAGINATED = """
    SELECT * FROM payments 
    WHERE user_id = $1
    ORDER BY created_at DESC
    LIMIT $2 OFFSET $3;
"""

COUNT_PAYMENTS_BY_USER = """
    SELECT COUNT(*) FROM payments WHERE user_id = $1;
"""

# ================================================================ #
# Update                                                            #
# ================================================================ #

UPDATE_PAYMENT_STATUS = """
    UPDATE payments 
    SET status = $1, updated_at = $2 
    WHERE id = $3
    RETURNING *;
"""

UPDATE_PAYMENT_TRANSACTION_ID = """
    UPDATE payments 
    SET transaction_id = $1, updated_at = $2 
    WHERE id = $3
    RETURNING *;
"""

# ================================================================ #
# Delete                                                            #
# ================================================================ #

DELETE_PAYMENT_BY_ID = """
    DELETE FROM payments WHERE id = $1;
"""

ARCHIVE_PAYMENT = """
    UPDATE payments 
    SET deleted_at = $1
    WHERE id = $2;
"""
