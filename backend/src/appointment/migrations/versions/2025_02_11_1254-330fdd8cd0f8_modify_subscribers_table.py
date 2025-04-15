"""modify subscribers table

Revision ID: 330fdd8cd0f8
Revises: 16c0299eff23
Create Date: 2025-02-11 12:54:51.256163

"""
from alembic import op
import sqlalchemy as sa
from appointment.database.models import TimeMode


# revision identifiers, used by Alembic.
revision = '330fdd8cd0f8'
down_revision = '16c0299eff23'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('subscribers', 'time_mode', default=TimeMode.h12)


def downgrade() -> None:
    op.alter_column('subscribers', 'time_mode', default=TimeMode.h24)
