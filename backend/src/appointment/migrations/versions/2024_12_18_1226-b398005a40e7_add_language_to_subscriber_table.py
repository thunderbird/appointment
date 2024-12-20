"""Add language to subscriber table

Revision ID: b398005a40e7
Revises: d791a3f0e478
Create Date: 2024-12-18 12:26:56.211080

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

from appointment.database import models
from appointment.defines import FALLBACK_LOCALE

# revision identifiers, used by Alembic.
revision = 'b398005a40e7'
down_revision = 'd791a3f0e478'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add language column to subscribers table
    op.add_column('subscribers', sa.Column('language', models.encrypted_type(sa.String), nullable=False, default=FALLBACK_LOCALE, index=True))


def downgrade() -> None:
    op.drop_column('subscribers', 'language')
