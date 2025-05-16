"""add start of week user setting

Revision ID: 666158eab217
Revises: a3fc3cc13f56
Create Date: 2025-04-04 15:36:08.853611

"""
from alembic import op
import sqlalchemy as sa
from appointment.database.models import IsoWeekday

# revision identifiers, used by Alembic.
revision = '666158eab217'
down_revision = 'a3fc3cc13f56'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('subscribers', sa.Column('start_of_week', sa.Enum(IsoWeekday), default=IsoWeekday.sunday, nullable=False, index=True))


def downgrade() -> None:
    op.drop_column('subscribers', 'start_of_week')
