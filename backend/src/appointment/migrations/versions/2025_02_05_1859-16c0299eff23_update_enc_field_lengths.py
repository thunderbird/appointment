"""update enc field lengths

Revision ID: 16c0299eff23
Revises: 645fd31f827d
Create Date: 2025-02-05 18:59:31.214328

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa
from sqlalchemy import String
from sqlalchemy.dialects import mysql

from appointment.database.models import calculate_encrypted_length

# revision identifiers, used by Alembic.
revision = '16c0299eff23'
down_revision = '645fd31f827d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('appointments', 'title',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('appointments', 'location_name',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('appointments', 'location_url',
               existing_type=mysql.VARCHAR(length=2048),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               existing_nullable=True)
    op.alter_column('appointments', 'location_phone',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('appointments', 'details',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('appointments', 'slug',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('appointments', 'external_id',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('appointments', 'meeting_link_provider',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('attendees', 'email',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('attendees', 'name',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('availabilities', 'day_of_week',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('availabilities', 'start_time',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('availabilities', 'end_time',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('availabilities', 'min_time_before_meeting',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('calendars', 'title',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('calendars', 'color',
               existing_type=mysql.VARCHAR(length=32),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(32)),
               existing_nullable=True)
    op.alter_column('calendars', 'url',
               existing_type=mysql.VARCHAR(length=2048),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               existing_nullable=True)
    op.alter_column('calendars', 'user',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('calendars', 'password',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('external_connections', 'name',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('external_connections', 'type',
               existing_type=mysql.ENUM('zoom', 'google', 'fxa', 'caldav'),
               nullable=True)
    op.alter_column('external_connections', 'type_id',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('external_connections', 'token',
               existing_type=mysql.VARCHAR(length=2048),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               existing_nullable=True)
    op.alter_column('invites', 'code',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('schedules', 'name',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('schedules', 'slug',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('schedules', 'location_url',
               existing_type=mysql.VARCHAR(length=2048),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               existing_nullable=True)
    op.alter_column('schedules', 'details',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('schedules', 'start_date',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('schedules', 'end_date',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('schedules', 'start_time',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('schedules', 'end_time',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('schedules', 'timezone',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('schedules', 'meeting_link_provider',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('slots', 'meeting_link_id',
               existing_type=mysql.VARCHAR(length=1024),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(1024)),
               existing_nullable=True)
    op.alter_column('slots', 'meeting_link_url',
               existing_type=mysql.VARCHAR(length=2048),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               existing_nullable=True)
    op.alter_column('slots', 'booking_tkn',
               existing_type=mysql.VARCHAR(length=512),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(512)),
               existing_nullable=True)
    op.alter_column('subscribers', 'username',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('subscribers', 'password',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('subscribers', 'email',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('subscribers', 'secondary_email',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('subscribers', 'name',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('subscribers', 'avatar_url',
               existing_type=mysql.VARCHAR(length=2048),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               existing_nullable=True)
    op.alter_column('subscribers', 'short_link_hash',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('subscribers', 'language',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=False)
    op.alter_column('subscribers', 'timezone',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('subscribers', 'minimum_valid_iat_time',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=True)
    op.alter_column('waiting_list', 'email',
               existing_type=mysql.VARCHAR(length=255),
               type_=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('waiting_list', 'email',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=False)
    op.alter_column('subscribers', 'minimum_valid_iat_time',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('subscribers', 'timezone',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('subscribers', 'language',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=False)
    op.alter_column('subscribers', 'short_link_hash',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('subscribers', 'avatar_url',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               type_=mysql.VARCHAR(length=2048),
               existing_nullable=True)
    op.alter_column('subscribers', 'name',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('subscribers', 'secondary_email',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('subscribers', 'email',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('subscribers', 'password',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('subscribers', 'username',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('slots', 'booking_tkn',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(512)),
               type_=mysql.VARCHAR(length=512),
               existing_nullable=True)
    op.alter_column('slots', 'meeting_link_url',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               type_=mysql.VARCHAR(length=2048),
               existing_nullable=True)
    op.alter_column('slots', 'meeting_link_id',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(1024)),
               type_=mysql.VARCHAR(length=1024),
               existing_nullable=True)
    op.alter_column('schedules', 'meeting_link_provider',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('schedules', 'timezone',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('schedules', 'end_time',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('schedules', 'start_time',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('schedules', 'end_date',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('schedules', 'start_date',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('schedules', 'details',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('schedules', 'location_url',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               type_=mysql.VARCHAR(length=2048),
               existing_nullable=True)
    op.alter_column('schedules', 'slug',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('schedules', 'name',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('invites', 'code',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('external_connections', 'token',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               type_=mysql.VARCHAR(length=2048),
               existing_nullable=True)
    op.alter_column('external_connections', 'type_id',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('external_connections', 'type',
               existing_type=mysql.ENUM('zoom', 'google', 'fxa', 'caldav'),
               nullable=False)
    op.alter_column('external_connections', 'name',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('calendars', 'password',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('calendars', 'user',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('calendars', 'url',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               type_=mysql.VARCHAR(length=2048),
               existing_nullable=True)
    op.alter_column('calendars', 'color',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(32)),
               type_=mysql.VARCHAR(length=32),
               existing_nullable=True)
    op.alter_column('calendars', 'title',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('availabilities', 'min_time_before_meeting',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('availabilities', 'end_time',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('availabilities', 'start_time',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('availabilities', 'day_of_week',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('attendees', 'name',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('attendees', 'email',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('appointments', 'meeting_link_provider',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('appointments', 'external_id',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('appointments', 'slug',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('appointments', 'details',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('appointments', 'location_phone',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('appointments', 'location_url',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(2048)),
               type_=mysql.VARCHAR(length=2048),
               existing_nullable=True)
    op.alter_column('appointments', 'location_name',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('appointments', 'title',
               existing_type=mysql.VARCHAR(length=calculate_encrypted_length(255)),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    # ### end Alembic commands ###
