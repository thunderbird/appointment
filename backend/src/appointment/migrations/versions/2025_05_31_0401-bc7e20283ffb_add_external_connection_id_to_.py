"""add external_connection_id to calendars

Revision ID: bc7e20283ffb
Revises: ceecffbb5eb5
Create Date: 2025-05-31 04:01:38.267046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc7e20283ffb'
down_revision = 'ceecffbb5eb5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('calendars', sa.Column('external_connection_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_calendars_external_connection_id', 'calendars', 'external_connections', ['external_connection_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('fk_calendars_external_connection_id', 'calendars', type_='foreignkey')
    op.drop_column('calendars', 'external_connection_id')

# HERE: I need a function that will:
# - get all existing Calendar rows with provider == 'google'
# - get the owner_id
# - get the ExternalConnections for this owner_id
# - set the Calendar.external_connection_id to external_connection.id
# throw an error if there is len(external_connection) != 1
# this means that there was no external connection or somehow, multiple snuck into the database.