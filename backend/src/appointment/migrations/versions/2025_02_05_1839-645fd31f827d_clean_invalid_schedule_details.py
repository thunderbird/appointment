"""clean invalid schedule details

Revision ID: 645fd31f827d
Revises: 4a15d01919b8
Create Date: 2025-02-05 18:39:12.277713

"""
import binascii

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
import base64

# revision identifiers, used by Alembic.
revision = '645fd31f827d'
down_revision = '4a15d01919b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())
    bad_fields_found = 0
    rows = session.execute(sa.text('SELECT id, details FROM schedules WHERE details is not null;')).all()
    for row in rows:
        id, details = row
        try:
            base64.b64decode(details)
        except binascii.Error:
            bad_fields_found += 1
            statement = sa.text('UPDATE schedules SET details = NULL WHERE id = :id')
            statement = statement.bindparams(id=id)
            op.execute(statement)

    print(f'Nulled {bad_fields_found} schedules.details fields.')


def downgrade() -> None:
    pass
