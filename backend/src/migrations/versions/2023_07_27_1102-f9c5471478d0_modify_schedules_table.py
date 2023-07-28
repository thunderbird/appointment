"""modify_schedules_table

Revision ID: f9c5471478d0
Revises: f9660871710e
Create Date: 2023-07-27 11:02:39.900134

"""
import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy import DateTime
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from database.models import LocationType


def secret():
    return os.getenv("DB_SECRET")


# revision identifiers, used by Alembic.
revision = "f9c5471478d0"
down_revision = "f9660871710e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("appointments", "appointment_type")
    op.drop_constraint("schedules_ibfk_1", "schedules", type_="foreignkey")
    op.drop_column("schedules", "appointment_id")
    op.add_column("schedules", sa.Column("calendar_id", sa.Integer, sa.ForeignKey("calendars.id")))
    op.add_column("schedules", sa.Column("location_type", sa.Enum(LocationType), default=LocationType.online))
    op.add_column(
        "schedules", sa.Column("location_url", StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=2048))
    )
    op.add_column(
        "schedules", sa.Column("details", StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255))
    )
    op.add_column(
        "schedules",
        sa.Column("start_date", StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255), index=True),
    )
    op.add_column(
        "schedules",
        sa.Column("end_date", StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255), index=True),
    )
    op.add_column(
        "schedules",
        sa.Column("start_time", StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255), index=True),
    )
    op.add_column(
        "schedules",
        sa.Column("end_time", StringEncryptedType(sa.String, secret, AesEngine, "pkcs5", length=255), index=True),
    )
    op.add_column("schedules", sa.Column("earliest_booking", sa.Integer, default=1440))
    op.add_column("schedules", sa.Column("farthest_booking", sa.Integer, default=20160))
    op.add_column("schedules", sa.Column("weekdays", sa.JSON))
    op.add_column("schedules", sa.Column("slot_duration", sa.Integer, default=30))


def downgrade() -> None:
    pass
