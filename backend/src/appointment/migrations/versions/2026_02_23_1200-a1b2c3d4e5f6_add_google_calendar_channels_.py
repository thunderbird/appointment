"""add google_calendar_channels table

Revision ID: a1b2c3d4e5f6
Revises: 17792ef315c1
Create Date: 2026-02-23 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '17792ef315c1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'google_calendar_channels',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('calendar_id', sa.Integer, sa.ForeignKey('calendars.id'), unique=True),
        sa.Column('channel_id', sa.String, index=True),
        sa.Column('resource_id', sa.String),
        sa.Column('expiration', sa.DateTime),
        sa.Column('sync_token', sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('google_calendar_channels')
