"""add minimum_valid_iat_time to subscribers

Revision ID: ad7cc2de5ff8
Revises: 0dc429ca07f5
Create Date: 2024-01-09 16:52:20.941572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad7cc2de5ff8'
down_revision = '0dc429ca07f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('subscribers', sa.Column('minimum_valid_iat_time', sa.DateTime, index=True))


def downgrade() -> None:
    op.drop_column('subscribers', 'minimum_valid_iat_time')
