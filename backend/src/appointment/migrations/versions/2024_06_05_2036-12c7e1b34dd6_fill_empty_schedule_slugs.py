"""fill empty schedule slugs

Revision ID: 12c7e1b34dd6
Revises: f1e20604d6e8
Create Date: 2024-06-05 20:36:20.503151

"""
from alembic import op
from sqlalchemy.orm import Session

from appointment.database import models, repo

# revision identifiers, used by Alembic.
revision = '12c7e1b34dd6'
down_revision = 'f1e20604d6e8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())
    schedules: list[models.Schedule] = session.query(models.Schedule).where(models.Schedule.slug.is_(None)).all()
    for schedule in schedules:
        repo.schedule.generate_slug(session, schedule.id)


def downgrade() -> None:
    pass
