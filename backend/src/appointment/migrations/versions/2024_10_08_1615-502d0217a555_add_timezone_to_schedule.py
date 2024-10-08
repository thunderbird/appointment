"""add timezone to schedule

Revision ID: 502d0217a555
Revises: 01d80f00243f
Create Date: 2024-10-08 16:15:22.157158

"""
from alembic import op
import sqlalchemy as sa

from appointment.database.models import encrypted_type

# revision identifiers, used by Alembic.
revision = '502d0217a555'
down_revision = '01d80f00243f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('schedules', sa.Column('timezone', encrypted_type(sa.String), nullable=True, index=True))


def downgrade() -> None:
    op.drop_column('schedules', 'timezone')
