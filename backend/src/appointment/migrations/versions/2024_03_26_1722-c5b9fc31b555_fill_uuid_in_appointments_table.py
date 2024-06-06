"""[data migration] fill uuid in appointments table

Revision ID: c5b9fc31b555
Revises: e4c5a32de9fb
Create Date: 2024-03-26 17:22:03.157695

"""

import uuid

from alembic import op
from sqlalchemy.orm import Session

from appointment.database import models

# revision identifiers, used by Alembic.
revision = "c5b9fc31b555"
down_revision = "e4c5a32de9fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())
    appointments: list[models.Appointment] = (
        session.query(models.Appointment).where(models.Appointment.uuid.is_(None)).all()
    )
    for appointment in appointments:
        appointment.uuid = uuid.uuid4()
        session.add(appointment)
        session.commit()


def downgrade() -> None:
    pass
