"""Add config fields to subscribers table

Revision ID: 4a15d01919b8
Revises: 0c99f6a02f3b
Create Date: 2025-01-15 13:40:12.022117

"""
import os
from alembic import op
import sqlalchemy as sa
from appointment.database.models import ColourScheme, TimeMode


def secret():
    return os.getenv('DB_SECRET')


# revision identifiers, used by Alembic.
revision = '4a15d01919b8'
down_revision = '0c99f6a02f3b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'subscribers',
        sa.Column('colour_scheme', sa.Enum(ColourScheme), default=ColourScheme.system, nullable=False, index=True)
    )
    op.add_column(
        'subscribers',
        sa.Column('time_mode', sa.Enum(TimeMode), default=TimeMode.h24, nullable=False, index=True)
    )


def downgrade() -> None:
    op.drop_column('subscribers', 'colour_scheme')
    op.drop_column('subscribers', 'time_mode')
