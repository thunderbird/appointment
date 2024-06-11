"""create external_connections table

Revision ID: 9a96baa7ecd5
Revises: 3789c9fd57c5
Create Date: 2023-11-02 21:21:24.792951

"""

import os

from alembic import op
import sqlalchemy as sa
from database.models import ExternalConnectionType
from sqlalchemy import func, ForeignKey
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv('DB_SECRET')


# revision identifiers, used by Alembic.
revision = '9a96baa7ecd5'
down_revision = '3789c9fd57c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'external_connections',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('owner_id', sa.Integer, ForeignKey('subscribers.id')),
        sa.Column('name', StringEncryptedType(sa.String, secret, AesEngine, 'pkcs5', length=255), index=False),
        sa.Column('type', sa.Enum(ExternalConnectionType), index=True),
        sa.Column('type_id', StringEncryptedType(sa.String, secret, AesEngine, 'pkcs5', length=255), index=True),
        sa.Column('token', StringEncryptedType(sa.String, secret, AesEngine, 'pkcs5', length=2048), index=False),
        sa.Column('time_created', sa.DateTime, server_default=func.now()),
        sa.Column('time_updated', sa.DateTime, server_default=func.now()),
    )


def downgrade() -> None:
    op.drop_table('external_connections')
