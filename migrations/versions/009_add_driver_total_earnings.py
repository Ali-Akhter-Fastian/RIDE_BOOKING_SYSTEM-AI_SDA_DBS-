"""add driver total earnings

Revision ID: 009_add_driver_total_earnings
Revises: c3f2a9b8d4e1
Create Date: 2026-05-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "009_add_driver_total_earnings"
down_revision: Union[str, Sequence[str], None] = "c3f2a9b8d4e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS total_earnings NUMERIC(12, 2);")
    op.execute("UPDATE drivers SET total_earnings = 0.00 WHERE total_earnings IS NULL;")
    op.execute("ALTER TABLE drivers ALTER COLUMN total_earnings SET DEFAULT 0.00;")
    op.execute("ALTER TABLE drivers ALTER COLUMN total_earnings SET NOT NULL;")


def downgrade() -> None:
    op.execute("ALTER TABLE drivers DROP COLUMN IF EXISTS total_earnings;")
