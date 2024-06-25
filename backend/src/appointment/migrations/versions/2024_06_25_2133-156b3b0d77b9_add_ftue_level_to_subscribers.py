"""add ftue_level to subscribers

Revision ID: 156b3b0d77b9
Revises: 12c7e1b34dd6
Create Date: 2024-06-25 21:33:27.094632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '156b3b0d77b9'
down_revision = '12c7e1b34dd6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('subscribers', sa.Column('ftue_level', sa.Integer, default=0, nullable=False, index=True))


def downgrade() -> None:
    op.drop_column('subscribers', 'ftue_level')
