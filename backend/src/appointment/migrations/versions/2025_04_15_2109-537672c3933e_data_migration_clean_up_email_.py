"""data migration clean up email case

Revision ID: 537672c3933e
Revises: 330fdd8cd0f8
Create Date: 2025-03-07 21:09:16.541016

"""

from alembic import op
from sqlalchemy.orm import Session

from appointment.database import models

# revision identifiers, used by Alembic.
revision = '537672c3933e'
down_revision = 'a3fc3cc13f56'
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())
    subscribers: list[models.Subscriber] = session.query(models.Subscriber).all()
    for subscriber in subscribers:
        # Lowercase the emails
        subscriber.email = subscriber.email.lower()
        if subscriber.secondary_email:
            subscriber.secondary_email = subscriber.secondary_email.lower()

        # Add the subscriber to the database session and commit (update) it
        session.add(subscriber)
        session.commit()

    waiting_list: list[models.WaitingList] = session.query(models.WaitingList).all()
    for waiting_list_individual in waiting_list:
        # Lowercase the emails
        waiting_list_individual.email = waiting_list_individual.email.lower()

        # Add the waiting list individual to the database session and commit (update) it
        session.add(waiting_list_individual)
        session.commit()


def downgrade() -> None:
    pass
