"""add general availability tables

Revision ID: f9660871710e
Revises: da069f44bca7
Create Date: 2023-06-27 11:08:39.853063

"""
import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy import DateTime, false
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from database.models import AppointmentType


def secret():
    return os.getenv("DB_SECRET")


# revision identifiers, used by Alembic.
revision = "f9660871710e"
down_revision = "da069f44bca7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("appointment_id", sa.Integer),
        sa.Column(
            "name",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255),
            index=False,
        ),
        sa.Column("time_created", DateTime()),
        sa.Column("time_updated", DateTime()),
    )
    op.create_table(
        "availabilities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("schedule_id", sa.Integer),
        sa.Column(
            "day_of_week",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255),
            index=False,
        ),
        sa.Column(
            "start_time",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255),
        ),
        sa.Column(
            "end_time",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255),
            index=False,
        ),
        sa.Column(
            "min_time_before_meeting",
            StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255),
            index=False,
        ),
        sa.Column("slot_duration", sa.Integer),
        sa.Column("time_created", DateTime()),
        sa.Column("time_updated", DateTime()),
    )
    op.add_column(
        "appointments",
        sa.Column(
            "appointment_type",
            sa.Enum(AppointmentType),
            default=AppointmentType.schedule,
        ),
    )


def downgrade() -> None:
    op.drop_table("schedules")
    op.drop_table("availabilities")
    op.drop_column("appointments", "appointment_type")
