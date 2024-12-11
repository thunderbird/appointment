"""update external connection type enum

Revision ID: a3fc3cc13f56
Revises: d791a3f0e478
Create Date: 2024-12-03 16:26:56.843324
Updated Date: 2025-03-20
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = 'a3fc3cc13f56'
down_revision = '537672c3933d'
branch_labels = None
depends_on = None


old_external_connections = ','.join(['"zoom"', '"google"', '"fxa"', '"caldav"'])
new_external_connections = ','.join(['"zoom"', '"google"', '"fxa"', '"caldav"', '"accounts"'])


def upgrade() -> None:
    op.execute(
        f'ALTER TABLE `external_connections` MODIFY COLUMN `type` enum({new_external_connections}) NOT NULL AFTER `name`;'  # noqa: E501
    )


def downgrade() -> None:
    op.execute(
        f'ALTER TABLE `external_connections` MODIFY COLUMN `type` enum({old_external_connections}) NOT NULL AFTER `name`;'  # noqa: E501
    )
