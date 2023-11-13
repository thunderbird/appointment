"""add meeting_link_provider to schedules table

Revision ID: 6da5d26beef0
Revises: d0c36eef5da9
Create Date: 2023-11-14 19:07:56.496112

"""
from alembic import op
import sqlalchemy as sa

from database.models import MeetingLinkProviderType

# revision identifiers, used by Alembic.
revision = '6da5d26beef0'
down_revision = 'd0c36eef5da9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('schedules', sa.Column("meeting_link_provider", sa.Enum(MeetingLinkProviderType, index=True, default=MeetingLinkProviderType.none)))


def downgrade() -> None:
    op.drop_column('schedules', 'meeting_link_provider')
