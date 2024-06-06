"""update subscribers table to remove google token references

Revision ID: f92bae6c27da
Revises: ea551afc14fc
Create Date: 2024-03-13 16:21:54.415458

"""

import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy import DateTime
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

# revision identifiers, used by Alembic.
revision = "f92bae6c27da"
down_revision = "ea551afc14fc"
branch_labels = None
depends_on = None


def secret():
    return os.getenv("DB_SECRET")


def upgrade() -> None:
    op.drop_column("subscribers", "google_tkn")
    op.drop_column("subscribers", "google_state")
    op.drop_column("subscribers", "google_state_expires_at")


def downgrade() -> None:
    op.add_column(
        "subscribers",
        sa.Column(
            "google_tkn",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=2048),
            index=False,
        ),
    )
    op.add_column(
        "subscribers",
        sa.Column(
            "google_state",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=2048),
            index=False,
        ),
    )
    op.add_column("subscribers", sa.Column("google_state_expires_at", DateTime()))
