"""add password to subscriber table

Revision ID: c4a5f0df612c
Revises: 14c33a37c43c
Create Date: 2023-12-04 18:07:44.775739

"""
import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv("DB_SECRET")


# revision identifiers, used by Alembic.
revision = 'c4a5f0df612c'
down_revision = '14c33a37c43c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('subscribers', sa.Column('password', StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255), index=False))


def downgrade() -> None:
    op.drop_column('subscribers', 'password')

