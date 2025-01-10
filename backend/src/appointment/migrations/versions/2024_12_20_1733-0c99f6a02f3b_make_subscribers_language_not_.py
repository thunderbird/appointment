"""make subscribers.language not nullable

Revision ID: 0c99f6a02f3b
Revises: b398005a40e7
Create Date: 2024-12-20 17:33:19.666412

"""

from alembic import op
import sqlalchemy as sa
from appointment.database import models

# revision identifiers, used by Alembic.
revision = '0c99f6a02f3b'
down_revision = 'b398005a40e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('subscribers', 'language', type_=models.encrypted_type(sa.String), nullable=False)


def downgrade() -> None:
    op.alter_column('subscribers', 'language', type_=models.encrypted_type(sa.String), nullable=True)
