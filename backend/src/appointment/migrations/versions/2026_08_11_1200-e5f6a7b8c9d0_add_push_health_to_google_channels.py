"""add push-health columns to google_calendar_channels

Adds the bookkeeping the push-driven cache invalidation relies on to decide
whether a channel can be trusted in place of polling:

  last_synced_at       - watermark of the last successful incremental sync
  last_notification_at - when a push notification was last received

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-11 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None

TABLE = 'google_calendar_channels'
COLUMNS = (
    ('last_synced_at', sa.DateTime()),
    ('last_notification_at', sa.DateTime()),
)


def _column_exists(connection, table, column) -> bool:
    insp = inspect(connection)
    return column in [c['name'] for c in insp.get_columns(table)]


def upgrade() -> None:
    connection = op.get_bind()
    for name, type_ in COLUMNS:
        if not _column_exists(connection, TABLE, name):
            op.add_column(TABLE, sa.Column(name, type_, nullable=True))


def downgrade() -> None:
    connection = op.get_bind()
    for name, _ in reversed(COLUMNS):
        if _column_exists(connection, TABLE, name):
            op.drop_column(TABLE, name)
