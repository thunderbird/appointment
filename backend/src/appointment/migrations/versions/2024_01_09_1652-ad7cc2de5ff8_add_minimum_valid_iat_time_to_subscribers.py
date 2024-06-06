"""add minimum_valid_iat_time to subscribers

Revision ID: ad7cc2de5ff8
Revises: 0dc429ca07f5
Create Date: 2024-01-09 16:52:20.941572

"""

import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv("DB_SECRET")


# revision identifiers, used by Alembic.
revision = "ad7cc2de5ff8"
down_revision = "0dc429ca07f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subscribers",
        sa.Column("minimum_valid_iat_time", StringEncryptedType(sa.DateTime, secret, AesEngine, "pkcs5", length=255)),
    )


def downgrade() -> None:
    op.drop_column("subscribers", "minimum_valid_iat_time")
