"""add state to google_calendar_channels

Revision ID: b3c4d5e6f7a8
Revises: d9c5594694c5
Create Date: 2026-04-01 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

from appointment.database.models import encrypted_type

# revision identifiers, used by Alembic.
revision = 'b3c4d5e6f7a8'
down_revision = 'd9c5594694c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'google_calendar_channels',
        sa.Column('state', encrypted_type(sa.String, length=36), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('google_calendar_channels', 'state')
