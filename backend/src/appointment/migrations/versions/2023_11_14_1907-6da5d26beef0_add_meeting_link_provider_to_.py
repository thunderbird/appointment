"""add meeting_link_provider to schedules table

Revision ID: 6da5d26beef0
Revises: d0c36eef5da9
Create Date: 2023-11-14 19:07:56.496112

"""

import os
from alembic import op
import sqlalchemy as sa


from sqlalchemy_utils import StringEncryptedType, ChoiceType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from database.models import MeetingLinkProviderType


def secret():
    return os.getenv("DB_SECRET")


# revision identifiers, used by Alembic.
revision = "6da5d26beef0"
down_revision = "d0c36eef5da9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "schedules",
        sa.Column(
            "meeting_link_provider",
            StringEncryptedType(ChoiceType(MeetingLinkProviderType), secret, AesEngine, "pkcs5", length=255),
            index=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("schedules", "meeting_link_provider")
