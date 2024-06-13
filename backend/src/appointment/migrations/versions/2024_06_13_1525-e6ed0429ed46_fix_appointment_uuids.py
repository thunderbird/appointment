"""fix appointment uuids

Revision ID: e6ed0429ed46
Revises: 12c7e1b34dd6
Create Date: 2024-06-13 15:25:07.086174

"""
import uuid

from alembic import op
from sqlalchemy.orm import Session

from appointment.database import models, repo


# revision identifiers, used by Alembic.
revision = 'e6ed0429ed46'
down_revision = '12c7e1b34dd6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())
    appointments: list[models.Appointment] = session.query(models.Appointment).all()
    for appointment in appointments:
        appointment.uuid = uuid.uuid4()
        session.add(appointment)
        session.commit()


def downgrade() -> None:
    pass
