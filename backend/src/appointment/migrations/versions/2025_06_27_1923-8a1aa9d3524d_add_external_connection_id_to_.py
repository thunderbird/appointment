"""add external_connection_id to calendars

Revision ID: 8a1aa9d3524d
Revises: 88dbe32dc40d
Create Date: 2025-06-27 19:23:58.668420

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a1aa9d3524d'
down_revision = '88dbe32dc40d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the external_connection_id column
    op.add_column('calendars', sa.Column('external_connection_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_calendars_external_connection_id', 'calendars', 'external_connections', ['external_connection_id'], ['id']
    )

    # Data migration: Update existing Google calendars with their external connection IDs
    connection = op.get_bind()

    # Get all Google calendars and their owners
    google_calendars = connection.execute(sa.text("""
        SELECT c.id, c.owner_id 
        FROM calendars c 
        WHERE c.provider = 2  -- CalendarProvider.google = 2
    """)).fetchall()

    for calendar_id, owner_id in google_calendars:
        # Get external connections for this owner
        external_connections = connection.execute(sa.text("""
            SELECT id FROM external_connections 
            WHERE owner_id = :owner_id AND type = 2  -- ExternalConnectionType.google = 2
        """), {'owner_id': owner_id}).fetchall()

        if len(external_connections) == 0:
            raise Exception(f"Calendar {calendar_id} (owner_id: {owner_id}) has no Google external connection")

        if len(external_connections) > 1:
            raise Exception(
                f"Calendar {calendar_id} (owner_id: {owner_id}) has {len(external_connections)} Google external connections, expected exactly 1"  # noqa: E501
            )

        # Update the calendar with the external connection ID
        external_connection_id = external_connections[0][0]
        connection.execute(sa.text("""
            UPDATE calendars 
            SET external_connection_id = :external_connection_id 
            WHERE id = :calendar_id
        """), {
            'external_connection_id': external_connection_id,
            'calendar_id': calendar_id
        })


def downgrade() -> None:
    op.drop_constraint('fk_calendars_external_connection_id', 'calendars', type_='foreignkey')
    op.drop_column('calendars', 'external_connection_id')
