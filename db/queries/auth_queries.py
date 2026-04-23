SELECT_USER_BY_ID = """
SELECT id, full_name, email, password_hash, role, created_at, updated_at
FROM users
WHERE id = $1
"""

SELECT_USER_BY_EMAIL = """
SELECT id, full_name, email, password_hash, role, created_at, updated_at
FROM users
WHERE email = $1
"""

INSERT_USER = """
INSERT INTO users (id, full_name, email, password_hash, role, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
RETURNING id, full_name, email, password_hash, role, created_at, updated_at
"""
