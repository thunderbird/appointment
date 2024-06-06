"""add subscriber soft delete

Revision ID: d5de8f10ab87
Revises: 9fe08ba6f2ed
Create Date: 2024-05-31 14:54:23.772015

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d5de8f10ab87"
down_revision = "9fe08ba6f2ed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("subscribers", sa.Column("time_deleted", sa.DateTime, nullable=True))


def downgrade() -> None:
    op.drop_column("subscribers", "time_deleted")
