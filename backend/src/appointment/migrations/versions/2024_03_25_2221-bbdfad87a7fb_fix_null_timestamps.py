"""[data migration] fix null timestamps

Revision ID: bbdfad87a7fb
Revises: f92bae6c27da
Create Date: 2024-03-25 22:21:21.464528

"""

from alembic import op
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = "bbdfad87a7fb"
down_revision = "f92bae6c27da"
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())
    tables = [
        "appointments",
        "attendees",
        "availabilities",
        "calendars",
        "external_connections",
        "schedules",
        "slots",
        "subscribers",
    ]

    for table in tables:
        session.execute(f"UPDATE {table} SET time_created = NOW() WHERE time_created is NULL")
        session.execute(f"UPDATE {table} SET time_updated = NOW() WHERE time_updated is NULL")


def downgrade() -> None:
    pass
