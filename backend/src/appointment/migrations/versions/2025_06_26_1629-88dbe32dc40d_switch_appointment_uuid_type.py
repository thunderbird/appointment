"""switch appointment uuid type

Revision ID: 88dbe32dc40d
Revises: 2b40448be2f5
Create Date: 2025-06-26 16:29:19.679356

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '88dbe32dc40d'
down_revision = '2b40448be2f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a temporary uuid_str as CHAR(32), convert BINARY(16) to CHAR(32) and rename it to uuid
    op.add_column('appointments', sa.Column('uuid_str', sa.CHAR(32), nullable=True))
    op.execute('UPDATE appointments SET uuid_str = LOWER(HEX(uuid))')
    op.alter_column('appointments', 'uuid_str', existing_type=sa.CHAR(32), nullable=False)
    op.drop_column('appointments', 'uuid')
    op.alter_column('appointments', 'uuid_str', new_column_name='uuid', existing_type=sa.CHAR(32))


def downgrade() -> None:
    # Create a temporary uuid_str as MySQL's BINARY(16), convert CHAR(32) to BINARY(16) and rename it to uuid
    op.alter_column('appointments', 'uuid', new_column_name='uuid_str', existing_type=sa.CHAR(32))
    op.add_column('appointments', sa.Column('uuid', mysql.BINARY(16), nullable=True))
    op.execute('UPDATE appointments SET uuid = UNHEX(uuid_str)')
    op.alter_column('appointments', 'uuid', existing_type=mysql.BINARY(16), nullable=False)
    op.drop_column('appointments', 'uuid_str')
