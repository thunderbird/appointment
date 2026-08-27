"""remove time_mode from subscribers table

Revision ID: e0edc48b1a2d
Revises: d4e5f6a7b8c9
Create Date: 2026-08-18 21:02:33.879876

"""
import enum
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0edc48b1a2d'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


class TimeMode(enum.Enum):
    h12 = 12
    h24 = 24


def upgrade() -> None:
    op.drop_column('subscribers', 'time_mode')


def downgrade() -> None:
    op.add_column(
        'subscribers',
        sa.Column('time_mode', sa.Enum(TimeMode), default=TimeMode.h12, nullable=False, index=True)
    )
