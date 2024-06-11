"""add short_link_hash to subscribers table

Revision ID: 845089644770
Revises: da069f44bca7
Create Date: 2023-06-20 22:16:54.576754

"""

import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv('DB_SECRET')


# revision identifiers, used by Alembic.
revision = '845089644770'
down_revision = 'da069f44bca7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'subscribers',
        sa.Column(
            'short_link_hash',
            StringEncryptedType(sa.String, secret, AesEngine, 'pkcs5', length=2048),
            index=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('subscribers', 'short_link_hash')
