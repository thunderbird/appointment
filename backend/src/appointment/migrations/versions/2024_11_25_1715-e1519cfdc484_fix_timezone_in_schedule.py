"""fix timezone in schedule

Revision ID: e1519cfdc484
Revises: 71cf5d3ee14b
Create Date: 2024-11-25 17:15:13.027568

"""

from alembic import op
from sqlalchemy.orm import Session

from appointment.database import models

# revision identifiers, used by Alembic.
revision = 'e1519cfdc484'
down_revision = '71cf5d3ee14b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())
    schedules: list[models.Schedule] = session.query(models.Schedule).where(models.Schedule.timezone.is_(None)).all()
    for schedule in schedules:
        if schedule.owner.timezone:
            schedule.timezone = schedule.owner.timezone
        else:
            # Handle any cases where user timezone may be null
            owner = schedule.owner
            owner.timezone = 'UTC'
            session.add(owner)
            schedule.timezone = owner.timezone

        # Add the schedule to the database session and commit (update) it
        session.add(schedule)
        session.commit()


def downgrade() -> None:
    pass
