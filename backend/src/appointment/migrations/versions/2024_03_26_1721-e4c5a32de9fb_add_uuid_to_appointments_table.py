"""add uuid to appointments table

Revision ID: e4c5a32de9fb
Revises: bbdfad87a7fb
Create Date: 2024-03-26 17:21:55.528828

"""

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import UUIDType

# revision identifiers, used by Alembic.
revision = 'e4c5a32de9fb'
down_revision = 'bbdfad87a7fb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('appointments', sa.Column('uuid', UUIDType(native=False), default=uuid.uuid4(), index=True))


def downgrade() -> None:
    op.drop_column('appointments', 'uuid')
