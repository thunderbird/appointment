"""add avatar_url to subscribers table

Revision ID: 0dc429ca07f5
Revises: 7f8b4f463f1d
Create Date: 2023-12-05 17:34:38.294266

"""
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv("DB_SECRET")


# revision identifiers, used by Alembic.
revision = '0dc429ca07f5'
down_revision = '7f8b4f463f1d'
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.add_column('subscribers', sa.Column('avatar_url', StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=2048), index=False))


def downgrade() -> None:
    op.drop_column('subscribers', 'avatar_url')
