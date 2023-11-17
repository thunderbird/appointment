"""add meeting_link_id to slots table

Revision ID: 14c33a37c43c
Revises: 7e426358642e
Create Date: 2023-11-15 20:52:50.545477

"""
import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv("DB_SECRET")

# revision identifiers, used by Alembic.
revision = '14c33a37c43c'
down_revision = '7e426358642e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('slots', sa.Column('meeting_link_id', StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=1024), index=False))
    # A location_url override for generated meeting link urls
    op.add_column('slots', sa.Column('meeting_link_url', StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=2048), index=False))


def downgrade() -> None:
    op.drop_column('slots', 'meeting_link_id')
    op.drop_column('slots', 'meeting_link_url')
