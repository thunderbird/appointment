"""add slug to schedules

Revision ID: f1e20604d6e8
Revises: d5de8f10ab87
Create Date: 2024-06-04 16:13:50.182484

"""
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv("DB_SECRET")

# revision identifiers, used by Alembic.
revision = 'f1e20604d6e8'
down_revision = 'd5de8f10ab87'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('schedules', sa.Column('slug', StringEncryptedType(sa.DateTime, secret, AesEngine, "pkcs5", length=255),  unique=True, index=True))


def downgrade() -> None:
    op.drop_column('schedules', 'slug')
