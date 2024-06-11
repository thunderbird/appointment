"""extend slots table for availability bookings

Revision ID: 2b1d96fb4058
Revises: 3789c9fd57c5
Create Date: 2023-10-19 15:35:17.671137

"""

import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy import DateTime
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from database.models import BookingStatus


def secret():
    return os.getenv('DB_SECRET')


# revision identifiers, used by Alembic.
revision = '2b1d96fb4058'
down_revision = '3789c9fd57c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('slots', sa.Column('schedule_id', sa.Integer, sa.ForeignKey('schedules.id')))
    op.add_column(
        'slots',
        sa.Column('booking_tkn', StringEncryptedType(sa.String, secret, AesEngine, 'pkcs5', length=512), index=False),
    )
    op.add_column('slots', sa.Column('booking_expires_at', DateTime()))
    op.add_column('slots', sa.Column('booking_status', sa.Enum(BookingStatus), default=BookingStatus.none))


def downgrade() -> None:
    op.drop_constraint('slots_ibfk_4', 'slots', type_='foreignkey')
    op.drop_column('slots', 'schedule_id')
    op.drop_column('slots', 'booking_tkn')
    op.drop_column('slots', 'booking_expires_at')
    op.drop_column('slots', 'booking_status')
