"""add meeting_link_provider to appointment table

Revision ID: d0c36eef5da9
Revises: 9a96baa7ecd5
Create Date: 2023-11-13 22:25:05.485397

"""

import os

from alembic import op
import sqlalchemy as sa

from sqlalchemy_utils import StringEncryptedType, ChoiceType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from database.models import MeetingLinkProviderType


def secret():
    return os.getenv('DB_SECRET')


# revision identifiers, used by Alembic.
revision = 'd0c36eef5da9'
down_revision = '9a96baa7ecd5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'appointments',
        sa.Column(
            'meeting_link_provider',
            StringEncryptedType(ChoiceType(MeetingLinkProviderType), secret, AesEngine, 'pkcs5', length=255),
            index=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('appointments', 'meeting_link_provider')
