"""add status to external connections table

Revision ID: d44b0832307c
Revises: 89da5bf99c88
Create Date: 2026-02-12 15:03:53.269982

"""
from alembic import op
import sqlalchemy as sa

from appointment.database.models import ExternalConnectionStatus


# revision identifiers, used by Alembic.
revision = 'd44b0832307c'
down_revision = '89da5bf99c88'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the enum type in PostgreSQL before using it in a column
    sa.Enum(ExternalConnectionStatus).create(op.get_bind(), checkfirst=True)
    op.add_column(
        'external_connections',
        sa.Column('status', sa.Enum(ExternalConnectionStatus), server_default='ok', nullable=False),
    )
    op.add_column(
        'external_connections',
        sa.Column('status_checked_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_column('external_connections', 'status_checked_at')
    op.drop_column('external_connections', 'status')
    sa.Enum(ExternalConnectionStatus).drop(op.get_bind(), checkfirst=True)
