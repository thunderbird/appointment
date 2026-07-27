"""DEMO ONLY - deliberately non-additive. Do not merge.

Exists to prove the `migration-additivity` CI job actually goes red.
See thunderbird/appointment#1770.

Revision ID: deadbeef0001
Revises: d4e5f6a7b8c9
Create Date: 2026-07-27 12:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = 'deadbeef0001'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def _tidy_up():
    """Hidden in a helper on purpose: proves the scan follows call graphs."""
    op.drop_column('subscribers', 'ftue_level')


def upgrade() -> None:
    # 1. destructive call reached only via a helper
    _tidy_up()
    # 2. NOT NULL with no server_default -> old replicas' INSERTs start failing
    op.add_column('subscribers', sa.Column('demo_flag', sa.Boolean(), nullable=False))
    # 3. raw DDL through a non-`op` receiver
    op.get_bind().execute(sa.text('ALTER TABLE subscribers DROP COLUMN avatar_url'))


def downgrade() -> None:
    # Destructive, but never executed by a deploy -> must NOT be flagged.
    op.drop_column('subscribers', 'demo_flag')
