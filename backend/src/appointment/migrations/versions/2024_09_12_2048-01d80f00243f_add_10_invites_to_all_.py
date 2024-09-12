"""add 10 invites to all subscribers

Revision ID: 01d80f00243f
Revises: 5edcde3f14c6
Create Date: 2024-09-12 20:48:33.473091

"""
from typing import Type

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Session

from appointment.database import models, repo

# revision identifiers, used by Alembic.
revision = '01d80f00243f'
down_revision = '5edcde3f14c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())

    # This was a single sqlalchemy statement, but their orm is not the best
    # and we don't have that many subscribers.
    subs: list[models.Subscriber] = session.query(models.Subscriber).all()
    subs = list(filter(lambda s: len(s.owned_invites) == 0, subs))

    count = 0
    for subscriber in subs:
        invites = repo.invite.generate_codes(session, 10, subscriber.id)
        count += len(invites)

    print(f"Generated {count} invites!")


def downgrade() -> None:
    pass
