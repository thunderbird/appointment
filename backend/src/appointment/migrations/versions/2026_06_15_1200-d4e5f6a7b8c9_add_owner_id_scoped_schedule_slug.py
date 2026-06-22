"""add owner_id and scoped schedule slug uniqueness

Revision ID: d4e5f6a7b8c9
Revises: c7a1b2d3e4f5
Create Date: 2026-06-15 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from appointment.database import models

# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c7a1b2d3e4f5'
branch_labels = None
depends_on = None


def _column_exists(connection, table, column) -> bool:
    insp = inspect(connection)
    cols = [c['name'] for c in insp.get_columns(table)]
    return column in cols


def _constraint_exists(connection, name) -> bool:
    insp = inspect(connection)
    return name in {c['name'] for c in insp.get_unique_constraints('schedules')}


def _drop_global_slug_unique(connection) -> None:
    insp = inspect(connection)
    for idx in insp.get_indexes('schedules'):
        if idx.get('unique') and idx.get('column_names') == ['slug']:
            op.drop_index(idx['name'], table_name='schedules')

    for constraint in insp.get_unique_constraints('schedules'):
        if constraint.get('column_names') == ['slug']:
            op.drop_constraint(constraint['name'], 'schedules', type_='unique')


def upgrade() -> None:
    connection = op.get_bind()

    if not _column_exists(connection, 'schedules', 'owner_id'):
        op.add_column('schedules', sa.Column('owner_id', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_schedules_owner_id'), 'schedules', ['owner_id'], unique=False)
        op.create_foreign_key(
            'fk_schedules_owner_id_subscribers',
            'schedules',
            'subscribers',
            ['owner_id'],
            ['id'],
        )

    session = Session(connection)
    schedules = session.query(models.Schedule).where(models.Schedule.owner_id.is_(None)).all()
    for schedule in schedules:
        schedule.owner_id = schedule.calendar.owner_id
        session.add(schedule)
    session.commit()

    op.alter_column('schedules', 'owner_id', existing_type=sa.Integer(), nullable=False)

    _drop_global_slug_unique(connection)

    if not _constraint_exists(connection, 'uq_schedules_owner_slug'):
        op.create_unique_constraint('uq_schedules_owner_slug', 'schedules', ['owner_id', 'slug'])


def downgrade() -> None:
    connection = op.get_bind()

    if _constraint_exists(connection, 'uq_schedules_owner_slug'):
        op.drop_constraint('uq_schedules_owner_slug', 'schedules', type_='unique')

    insp = inspect(connection)
    slug_unique_exists = any(
        idx.get('unique') and idx.get('column_names') == ['slug'] for idx in insp.get_indexes('schedules')
    )
    if not slug_unique_exists:
        op.create_index(op.f('ix_schedules_slug'), 'schedules', ['slug'], unique=True)

    if _column_exists(connection, 'schedules', 'owner_id'):
        op.drop_constraint('fk_schedules_owner_id_subscribers', 'schedules', type_='foreignkey')
        op.drop_index(op.f('ix_schedules_owner_id'), table_name='schedules')
        op.drop_column('schedules', 'owner_id')
