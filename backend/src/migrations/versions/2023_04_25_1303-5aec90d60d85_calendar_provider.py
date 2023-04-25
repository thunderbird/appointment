"""calendar provider

Revision ID: 5aec90d60d85
Revises: 9614c3875c5e
Create Date: 2023-04-25 13:03:01.556282

"""
from alembic import op
import sqlalchemy as sa
from database.models import CalendarProvider


# revision identifiers, used by Alembic.
revision = '5aec90d60d85'
down_revision = '9614c3875c5e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('calendars', sa.Column('provider', sa.Enum(CalendarProvider), default=CalendarProvider.caldav))


def downgrade() -> None:
    op.drop_column('calendars', 'provider')
