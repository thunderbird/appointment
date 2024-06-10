"""change subscriber table

Revision ID: eb50007f7a21
Revises:
Create Date: 2023-04-05 17:03:56.183728

"""

import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv('DB_SECRET')


# revision identifiers, used by Alembic.
revision = '9614c3875c5e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'subscribers',
        'timezone',
        type_=StringEncryptedType(sa.String, secret, AesEngine, 'pkcs5', length=255),
        index=True,
    )


def downgrade() -> None:
    op.alter_column('subscribers', 'timezone', type_=sa.Integer, index=True)
