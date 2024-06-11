"""add time_created and time_updated to tables

Revision ID: 502c76bc79e0
Revises: 0dc429ca07f5
Create Date: 2024-01-10 22:59:02.194281

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision = '502c76bc79e0'
down_revision = '0dc429ca07f5'
branch_labels = None
depends_on = None

affected_tables = ['attendees', 'calendars', 'slots', 'subscribers']
index_tables = [
    'appointments',
    'availabilities',
    'external_connections',
    'schedules',
    'slots',
]


def upgrade() -> None:
    for table in affected_tables:
        op.add_column(table, sa.Column('time_created', sa.DateTime, server_default=func.now(), index=True))
        # Slots already has this column...
        if table != 'slots':
            op.add_column(table, sa.Column('time_updated', sa.DateTime, server_default=func.now(), index=True))

    # Fix some existing time_* columns
    for table in index_tables:
        op.create_index('ix_time_created', table, ['time_created'])
        op.create_index('ix_time_updated', table, ['time_updated'])


def downgrade() -> None:
    for table in affected_tables:
        op.drop_column(table, 'time_created')
        if table != 'slots':
            op.drop_column(table, 'time_updated')

    for table in index_tables:
        op.drop_index('ix_time_created', table)
        op.drop_index('ix_time_updated', table)
