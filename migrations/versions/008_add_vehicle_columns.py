"""add_vehicle_columns

Revision ID: 008_add_vehicle_columns
Revises: 007_merge_006_heads
Create Date: 2026-05-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "008_add_vehicle_columns"
down_revision: Union[str, Sequence[str], None] = "007_merge_006_heads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Compatibility migration for environments that used this revision ID.
    # Keep it idempotent so it is safe across partially-migrated databases.
    op.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS vehicle_number VARCHAR(50);")
    op.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS vehicle_type VARCHAR(50);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_drivers_vehicle_number ON drivers (vehicle_number);")


def downgrade() -> None:
    # Do not drop columns on downgrade; this revision is a compatibility bridge.
    pass
