"""[data migration] fix encrypted fields

Revision ID: 47b5a1508312
Revises: c5b9fc31b555
Create Date: 2024-04-04 22:27:26.387234

"""
import os
from functools import cache

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from appointment.database import models

# revision identifiers, used by Alembic.
revision = '47b5a1508312'
down_revision = 'c5b9fc31b555'
branch_labels = None
depends_on = None


def secret():
    return os.getenv("DB_SECRET")


@cache
def setup_encryption_engine():
    engine = AesEngine()
    # Yes we need to use protected methods to set this up.
    # We could replace it with our own encryption,
    # but I wanted it to be similar to the db.
    engine._update_key(secret())
    engine._set_padding_mechanism("pkcs5")
    return engine


def upgrade() -> None:
    session = Session(op.get_bind())

    encryption = setup_encryption_engine()

    model_and_fields = {
        models.Subscriber: ['id', 'username', 'password', 'email', 'name', 'timezone', 'avatar_url', 'short_link_hash', 'minimum_valid_iat_time'],
        models.Calendar: ['id', 'title', 'color', 'url', 'user', 'password'],
        models.Appointment: ['id', 'title', 'location_name', 'location_url', 'location_phone', 'details', 'slug', 'meeting_link_provider'],
        models.Attendee: ['id', 'email', 'name'],
        models.Slot: ['id', 'meeting_link_id', 'meeting_link_url', 'booking_tkn'],
        models.Schedule: ['id', 'name', 'location_url', 'details', 'start_date', 'end_date', 'start_time', 'end_time', 'meeting_link_provider'],
        models.Availability: ['id', 'day_of_week', 'start_time', 'end_time', 'min_time_before_meeting'],
        models.ExternalConnections: ['id', 'name', 'type_id', 'token']
    }

    for model, fields in model_and_fields.items():
        db_select = session.execute(f"SELECT {', '.join(fields)} FROM {model.__tablename__}")

        for select in db_select.all():
            primary_id = select[0]
            update_fields = fields[1:]

            # Exclude id
            new_fields = [ encryption.decrypt(field) if field is not None else field for field in select[1:] ]

            key_values = dict(zip(update_fields, new_fields))

            query_params = []
            for key, value in key_values.items():
                query_params.append(f"{key} = :{key}")

            key_values['id'] = primary_id

            session.execute(f"UPDATE {model.__tablename__} SET {', '.join( query_params )} WHERE id = :id",
                            key_values)



def downgrade() -> None:
    pass
