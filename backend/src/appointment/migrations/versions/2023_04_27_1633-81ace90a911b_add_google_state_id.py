"""add google state id

Revision ID: 81ace90a911b
Revises: d9ecfcaf83a6
Create Date: 2023-04-27 16:33:15.095853

"""
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy import DateTime
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv("DB_SECRET")


# revision identifiers, used by Alembic.
revision = "81ace90a911b"
down_revision = "d9ecfcaf83a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subscribers",
        sa.Column(
            "google_state",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=2048),
            index=False,
        ),
    )
    op.add_column("subscribers", sa.Column("google_state_expires_at", DateTime()))


def downgrade() -> None:
    op.drop_column("subscribers", "google_state")
    op.drop_column("subscribers", "google_state_expires_at")
