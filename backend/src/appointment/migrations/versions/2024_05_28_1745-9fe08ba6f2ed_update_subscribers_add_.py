"""update subscribers add preferred_email

Revision ID: 9fe08ba6f2ed
Revises: 89e1197d980d
Create Date: 2024-05-28 17:45:48.192560

"""

import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def secret():
    return os.getenv("DB_SECRET")


# revision identifiers, used by Alembic.
revision = "9fe08ba6f2ed"
down_revision = "89e1197d980d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subscribers",
        sa.Column(
            "secondary_email",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255),
            nullable=True,
            index=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("subscribers", "secondary_email")
