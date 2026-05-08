"""create_rider_table

Revision ID: 3d374016640c
Revises: b8a2442bbfdb
Create Date: 2026-05-08 21:21:00.547048

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d374016640c'
down_revision: Union[str, Sequence[str], None] = 'b8a2442bbfdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE riders (
            phone_number VARCHAR(20),
            emergency_contact_name VARCHAR(120),
            emergency_contact_phone VARCHAR(20),
            payment_method VARCHAR(50) DEFAULT 'credit_card',
            wallet_balance DECIMAL(10,2) DEFAULT 0.00,
            is_verified BOOLEAN DEFAULT false,
            total_rides INTEGER DEFAULT 0,
            average_rating DECIMAL(3,2) DEFAULT 0.00,
            PRIMARY KEY (id)
        ) INHERITS (users);
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_riders_phone_number ON riders (phone_number);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_riders_is_verified ON riders (is_verified);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_riders_payment_method ON riders (payment_method);")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS riders;")
