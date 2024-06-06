"""create invites table

Revision ID: fadd0d1ef438
Revises: c5b9fc31b555
Create Date: 2024-04-16 12:41:53.550102

"""

import os

from alembic import op
import sqlalchemy as sa
from database.models import InviteStatus
from sqlalchemy import func, ForeignKey
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

# revision identifiers, used by Alembic.
revision = "fadd0d1ef438"
down_revision = "c5b9fc31b555"
branch_labels = None
depends_on = None


def secret():
    return os.getenv("DB_SECRET")


def upgrade() -> None:
    op.create_table(
        "invites",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("subscriber_id", sa.Integer, ForeignKey("subscribers.id")),
        sa.Column("code", StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255), index=False),
        sa.Column("status", sa.Enum(InviteStatus), index=True),
        sa.Column("time_created", sa.DateTime, server_default=func.now()),
        sa.Column("time_updated", sa.DateTime, server_default=func.now()),
    )


def downgrade() -> None:
    op.drop_table("invites")
