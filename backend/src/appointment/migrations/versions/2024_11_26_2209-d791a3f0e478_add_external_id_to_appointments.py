"""add external_id to appointments

Revision ID: d791a3f0e478
Revises: 71cf5d3ee14b
Create Date: 2024-11-26 22:09:48.062308

"""
from alembic import op
import sqlalchemy as sa

from appointment.database.models import encrypted_type

# revision identifiers, used by Alembic.
revision = 'd791a3f0e478'
down_revision = 'e1519cfdc484'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('appointments', sa.Column('external_id', encrypted_type(sa.String), nullable=True, index=True))


def downgrade() -> None:
    op.drop_column('appointments', 'external_id')
