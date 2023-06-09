"""add calendar connected

Revision ID: da069f44bca7
Revises: 81ace90a911b
Create Date: 2023-06-08 22:01:31.788967

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import DateTime, false

# revision identifiers, used by Alembic.
revision = "da069f44bca7"
down_revision = "81ace90a911b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "calendars",
        sa.Column(
            "connected",
            sa.Boolean,
            index=True,
            server_default=false(),
        ),
    )
    op.add_column("calendars", sa.Column("connected_at", DateTime()))


def downgrade() -> None:
    op.drop_column("calendars", "connected")
    op.drop_column("calendars", "connected_at")
