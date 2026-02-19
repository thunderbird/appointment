"""update external connections type enum with caldav

Revision ID: 71cf5d3ee14b
Revises: 01d80f00243f
Create Date: 2024-10-09 20:06:47.631534

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '71cf5d3ee14b'
down_revision = '502d0217a555'
branch_labels = None
depends_on = None


old_external_connections = ','.join(['"zoom"', '"google"', '"fxa"'])
new_external_connections = ','.join(['"zoom"', '"google"', '"fxa"', '"caldav"'])


def upgrade() -> None:
    op.execute(
        f'ALTER TABLE `external_connections` MODIFY COLUMN `type` enum({new_external_connections}) NOT NULL AFTER `name`;'  # noqa: E501
    )


def downgrade() -> None:
    op.execute(
        f'ALTER TABLE `external_connections` MODIFY COLUMN `type` enum({old_external_connections}) NOT NULL AFTER `name`;'  # noqa: E501
    )
