"""update appointments make uuid unique

Revision ID: f732d6e597fe
Revises: e6ed0429ed46
Create Date: 2024-06-13 15:25:22.440864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f732d6e597fe'
down_revision = 'e6ed0429ed46'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index('ix_appointments_uuid', 'appointments')
    op.create_index('ix_appointments_uuid', 'appointments', ['uuid'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_appointments_uuid', 'appointments')
    op.create_index('ix_appointments_uuid', 'appointments', ['uuid'], unique=False)
