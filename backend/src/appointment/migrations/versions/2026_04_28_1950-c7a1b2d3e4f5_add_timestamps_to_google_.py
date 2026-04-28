"""add timestamps to google_calendar_channels

Revision ID: c7a1b2d3e4f5
Revises: 04f5df8311e9
Create Date: 2026-04-28 19:50:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func, inspect


# revision identifiers, used by Alembic.
revision = 'c7a1b2d3e4f5'
down_revision = '04f5df8311e9'
branch_labels = None
depends_on = None


def _column_exists(connection, table, column) -> bool:
    insp = inspect(connection)
    cols = [c['name'] for c in insp.get_columns(table)]
    return column in cols


def upgrade() -> None:
    conn = op.get_bind()
    if not _column_exists(conn, 'google_calendar_channels', 'time_created'):
        op.add_column(
            'google_calendar_channels',
            sa.Column('time_created', sa.DateTime, server_default=func.now(), index=True),
        )
    if not _column_exists(conn, 'google_calendar_channels', 'time_updated'):
        op.add_column(
            'google_calendar_channels',
            sa.Column('time_updated', sa.DateTime, server_default=func.now(), index=True),
        )


def downgrade() -> None:
    op.drop_column('google_calendar_channels', 'time_updated')
    op.drop_column('google_calendar_channels', 'time_created')
