"""add language to attendee

Revision ID: 4f6693fcc9d7
Revises: 89da5bf99c88
Create Date: 2026-02-17 15:34:09.224587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f6693fcc9d7'
down_revision = '89da5bf99c88'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('attendees', sa.Column('language', sa.String, nullable=True))


def downgrade() -> None:
    op.drop_column('attendees', 'language')
