"""schedule booking confirmation

Revision ID: fb1feb76c467
Revises: 0c22678e25db
Create Date: 2024-07-04 15:01:47.090876

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import true

# revision identifiers, used by Alembic.
revision = 'fb1feb76c467'
down_revision = '0c22678e25db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('schedules', sa.Column('booking_confirmation', sa.Boolean, nullable=False, server_default=true(), index=True))


def downgrade() -> None:
    op.drop_column('schedules', 'booking_confirmation')
