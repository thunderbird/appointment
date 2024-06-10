"""update external connections type enum

Revision ID: 7f8b4f463f1d
Revises: c4a5f0df612c
Create Date: 2023-12-05 00:27:08.011155

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '7f8b4f463f1d'
down_revision = 'c4a5f0df612c'
branch_labels = None
depends_on = None

old_external_connections = ','.join(['"zoom"', '"google"'])
new_external_connections = ','.join(['"zoom"', '"google"', '"fxa"'])


def upgrade() -> None:
    op.execute(
        f'ALTER TABLE `external_connections` MODIFY COLUMN `type` enum({new_external_connections}) NOT NULL AFTER `name`;'  # noqa: E501
    )


def downgrade() -> None:
    op.execute(
        f'ALTER TABLE `external_connections` MODIFY COLUMN `type` enum({old_external_connections}) NOT NULL AFTER `name`;'  # noqa: E501
    )
