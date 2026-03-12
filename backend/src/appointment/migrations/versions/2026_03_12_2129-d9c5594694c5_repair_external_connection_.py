"""repair external connection status

Revision ID: d9c5594694c5
Revises: 17792ef315c1
Create Date: 2026-03-12 21:29:55.016221

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

from appointment.database.models import ExternalConnectionStatus

# revision identifiers, used by Alembic.
revision = 'd9c5594694c5'
down_revision = '17792ef315c1'
branch_labels = None
depends_on = None


def _status_column_missing(connection) -> bool:
    insp = inspect(connection)
    cols = [c["name"] for c in insp.get_columns("external_connections")]
    return "status" not in cols


def upgrade() -> None:
    connection = op.get_bind()

    # Note: This is a repair migration since d44b0832307c was introduced before the HEAD.
    #       and ended up not being ran on staging, breaking the connection status column.
    #
    # See: https://github.com/thunderbird/appointment/pull/1509#discussion_r2894699341
    if not _status_column_missing(connection):
        return

    sa.Enum(ExternalConnectionStatus).create(connection, checkfirst=True)
    op.add_column(
        "external_connections",
        sa.Column(
            "status",
            sa.Enum(ExternalConnectionStatus),
            server_default="ok",
            nullable=False,
        ),
    )
    op.add_column(
        "external_connections",
        sa.Column("status_checked_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    # No-op: repair migration; leave schema as-is on downgrade.
    pass
