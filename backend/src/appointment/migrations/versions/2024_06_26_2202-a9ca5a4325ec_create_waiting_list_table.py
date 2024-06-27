"""create waiting list table

Revision ID: a9ca5a4325ec
Revises: f732d6e597fe
Create Date: 2024-06-26 22:02:19.851617

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey, func

from appointment.database.models import encrypted_type

# revision identifiers, used by Alembic.
revision = 'a9ca5a4325ec'
down_revision = 'f732d6e597fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'waiting_list',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('email', encrypted_type(sa.String), unique=True, index=True, nullable=False),
        sa.Column('email_verified', sa.Boolean, nullable=False, index=True, default=False),
        sa.Column('invite_id', sa.Integer, ForeignKey('invites.id'), nullable=True, index=True),
        sa.Column('time_created', sa.DateTime, server_default=func.now()),
        sa.Column('time_updated', sa.DateTime, server_default=func.now()),
    )


def downgrade() -> None:
    op.drop_table('waiting_list')
