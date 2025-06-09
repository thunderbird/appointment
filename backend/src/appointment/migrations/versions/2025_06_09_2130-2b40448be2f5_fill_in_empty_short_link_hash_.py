"""fill in empty short_link_hash entries

Revision ID: 2b40448be2f5
Revises: ceecffbb5eb5
Create Date: 2025-06-09 21:30:49.323301

"""

import secrets

from alembic import op
from sqlalchemy.orm import Session

from appointment.database import models

# revision identifiers, used by Alembic.
revision = '2b40448be2f5'
down_revision = 'ceecffbb5eb5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())

    amount = 0

    subscribers = session.query(models.Subscriber).where(models.Subscriber.short_link_hash.is_(None)).all()
    for subscriber in subscribers:
        subscriber.short_link_hash = secrets.token_hex(32)
        session.add(subscriber)
        session.commit()
        amount += 1

    if amount > 0:
        print(f'[Migration=2b40448be2f5] Filled {amount} short_link_hash fields.')


def downgrade() -> None:
    pass
