"""fix column types

Revision ID: 1d8af482e853
Revises: 47b5a1508312
Create Date: 2024-04-05 16:55:49.891877

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = '1d8af482e853'
down_revision = '47b5a1508312'
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())

    session.execute("ALTER TABLE schedules MODIFY start_date DATE;")
    session.execute("ALTER TABLE schedules MODIFY end_date DATE;")
    session.execute("ALTER TABLE schedules MODIFY start_time TIME;")
    session.execute("ALTER TABLE schedules MODIFY end_time TIME;")


def downgrade() -> None:
    pass
