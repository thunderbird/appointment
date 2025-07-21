"""update booking status enum values

Revision ID: b2f516cb40cc
Revises: fb27de54e731
Create Date: 2025-07-17 19:24:54.607556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2f516cb40cc'
down_revision = 'fb27de54e731'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('slots', 'booking_status',
               existing_type=sa.Enum('none', 'requested', 'booked'),
               type_=sa.Enum('none', 'requested', 'booked', 'declined', 'cancelled'),
               existing_nullable=True)


def downgrade() -> None:
     op.alter_column('slots', 'booking_status',
               existing_type=sa.Enum('none', 'requested', 'booked', 'declined', 'cancelled'),
               type_=sa.Enum('none', 'requested', 'booked'),
               existing_nullable=True)
