"""add owner_id to invites table

Revision ID: 5edcde3f14c6
Revises: fb1feb76c467
Create Date: 2024-09-12 20:47:54.910571

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey

# revision identifiers, used by Alembic.
revision = '5edcde3f14c6'
down_revision = 'fb1feb76c467'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('invites', sa.Column('owner_id', sa.Integer, ForeignKey('subscribers.id'), nullable=True, index=True))


def downgrade() -> None:
    op.drop_column('invites', 'owner_id')
