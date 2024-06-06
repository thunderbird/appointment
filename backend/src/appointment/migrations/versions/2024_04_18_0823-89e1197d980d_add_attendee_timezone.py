"""add attendee timezone

Revision ID: 89e1197d980d
Revises: fadd0d1ef438
Create Date: 2024-04-18 08:23:55.660065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "89e1197d980d"
down_revision = "fadd0d1ef438"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("attendees", sa.Column("timezone", sa.String(255), index=True))


def downgrade() -> None:
    op.drop_column("attendees", "timezone")
