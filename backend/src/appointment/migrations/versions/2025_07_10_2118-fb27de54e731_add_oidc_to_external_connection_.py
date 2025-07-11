"""add oidc to external connection type

Revision ID: fb27de54e731
Revises: 8a1aa9d3524d
Create Date: 2025-07-10 21:18:04.933145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb27de54e731'
down_revision = '8a1aa9d3524d'
branch_labels = None
depends_on = None


old_external_connections = ','.join(['"zoom"', '"google"', '"fxa"', '"caldav"', '"accounts"'])
new_external_connections = ','.join(['"zoom"', '"google"', '"fxa"', '"caldav"', '"accounts"', '"oidc"'])


def upgrade() -> None:
    op.execute(
        f'ALTER TABLE `external_connections` MODIFY COLUMN `type` enum({new_external_connections}) NOT NULL AFTER `name`;'  # noqa: E501
    )


def downgrade() -> None:
    op.execute(
        f'ALTER TABLE `external_connections` MODIFY COLUMN `type` enum({old_external_connections}) NOT NULL AFTER `name`;'  # noqa: E501
    )
