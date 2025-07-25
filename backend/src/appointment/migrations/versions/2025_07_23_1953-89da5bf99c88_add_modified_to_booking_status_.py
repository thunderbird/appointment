"""add modified to booking status enum

Revision ID: 89da5bf99c88
Revises: b2f516cb40cc
Create Date: 2025-07-23 19:53:56.050724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89da5bf99c88'
down_revision = 'b2f516cb40cc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('slots', 'booking_status',
               existing_type=sa.Enum('none', 'requested', 'booked', 'declined', 'cancelled'),
               type_=sa.Enum('none', 'requested', 'booked', 'declined', 'cancelled', 'modified'),
               existing_nullable=True)


def downgrade() -> None:
     op.alter_column('slots', 'booking_status',
               existing_type=sa.Enum('none', 'requested', 'booked', 'declined', 'cancelled', 'modified'),
               type_=sa.Enum('none', 'requested', 'booked', 'declined', 'cancelled'),
               existing_nullable=True)
