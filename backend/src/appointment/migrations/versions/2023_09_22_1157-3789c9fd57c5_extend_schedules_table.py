"""extend schedules table

Revision ID: 3789c9fd57c5
Revises: f9c5471478d0
Create Date: 2023-09-22 11:57:49.222824

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3789c9fd57c5'
down_revision = 'f9c5471478d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('schedules', sa.Column('active', sa.Boolean, index=True, default=True))


def downgrade() -> None:
    op.drop_column('schedules', 'active')
