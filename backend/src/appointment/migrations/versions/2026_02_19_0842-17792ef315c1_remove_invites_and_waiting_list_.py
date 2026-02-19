"""remove invites and waiting_list tables

Revision ID: 17792ef315c1
Revises: 4f6693fcc9d7
Create Date: 2026-02-19 08:42:50.122412

"""
import os
import enum

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func, ForeignKey
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from appointment.database.models import encrypted_type


# revision identifiers, used by Alembic.
revision = '17792ef315c1'
down_revision = '4f6693fcc9d7'
branch_labels = None
depends_on = None


class InviteStatus(enum.Enum):
    active = 1  # The code is still valid. It may be already used or is still to be used
    revoked = 2  # The code is no longer valid and cannot be used for sign up anymore

def secret():
    return os.getenv('DB_SECRET')


def upgrade() -> None:
    op.drop_table('waiting_list')
    op.drop_table('invites')



def downgrade() -> None:
    op.create_table(
        'invites',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('subscriber_id', sa.Integer, ForeignKey('subscribers.id')),
        sa.Column('code', StringEncryptedType(sa.String, secret, AesEngine, 'pkcs5', length=255), index=False),
        sa.Column('status', sa.Enum(InviteStatus), index=True),
        sa.Column('time_created', sa.DateTime, server_default=func.now()),
        sa.Column('time_updated', sa.DateTime, server_default=func.now()),
    )
    op.create_table(
        'waiting_list',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('email', encrypted_type(sa.String), unique=True, index=True, nullable=False),
        sa.Column('email_verified', sa.Boolean, nullable=False, index=True, default=False),
        sa.Column('invite_id', sa.Integer, ForeignKey('invites.id'), nullable=True, index=True),
        sa.Column('time_created', sa.DateTime, server_default=func.now()),
        sa.Column('time_updated', sa.DateTime, server_default=func.now()),
    )
