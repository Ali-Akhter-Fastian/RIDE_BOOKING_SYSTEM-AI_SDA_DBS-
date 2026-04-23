from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "af1000c2d7aa"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID generation for default primary keys.
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # Create the users table if it does not exist.
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            full_name VARCHAR(120) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'rider' CHECK (role IN ('rider', 'driver')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)

    # Index creation is idempotent across retries.
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS users;")