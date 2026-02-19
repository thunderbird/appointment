"""update availabilities table

Revision ID: ceecffbb5eb5
Revises: 666158eab217
Create Date: 2025-05-13 08:37:05.161807

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import false
from sqlalchemy.dialects import mysql
from appointment.database.models import IsoWeekday
from appointment.database.models import calculate_encrypted_length


# revision identifiers, used by Alembic.
revision = 'ceecffbb5eb5'
down_revision = '666158eab217'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'schedules',
        sa.Column('use_custom_availabilities', sa.Boolean, nullable=False, server_default=false(), index=True)
    )
    op.alter_column('availabilities', 'day_of_week', existing_type=mysql.ENUM(*list(IsoWeekday.__members__.keys())),
                    nullable=False)


def downgrade() -> None:
    op.drop_column('schedules', 'use_custom_availabilities')
    op.alter_column('availabilities', 'day_of_week', existing_type=mysql.VARCHAR(length=255),
                    type_=mysql.VARCHAR(length=calculate_encrypted_length(255)), existing_nullable=True)
