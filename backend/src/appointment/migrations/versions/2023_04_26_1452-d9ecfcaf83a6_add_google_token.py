"""add google token

Revision ID: d9ecfcaf83a6
Revises: 5aec90d60d85
Create Date: 2023-04-26 14:52:25.425491

"""
import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv("DB_SECRET")


# revision identifiers, used by Alembic.
revision = "d9ecfcaf83a6"
down_revision = "5aec90d60d85"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subscribers",
        sa.Column(
            "google_tkn",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=2048),
            index=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("subscribers", "google_tkn")
