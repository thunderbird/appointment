"""Tests for scripts/check_migration_additivity.py (the CI expand/contract gate).

The gate is only useful if it is well calibrated: a false positive on an ordinary
additive migration teaches people to ignore it, and a false negative defeats the
point. These tests pin both directions.
"""

import ast
import importlib.util
import pathlib

import pytest

_SCRIPT = pathlib.Path(__file__).resolve().parents[2] / 'scripts/check_migration_additivity.py'
_spec = importlib.util.spec_from_file_location('check_migration_additivity', _SCRIPT)
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


def rules(source: str) -> list[str]:
    return [f.rule for f in checker.check_upgrade(ast.parse(source))]


def wrap(upgrade_body: str, downgrade_body: str = 'pass') -> str:
    return f'def upgrade():\n    {upgrade_body}\n\n\ndef downgrade():\n    {downgrade_body}\n'


# --- additive: must NOT be flagged -------------------------------------------------

def test_add_nullable_column_is_additive():
    assert rules(wrap("op.add_column('t', sa.Column('c', sa.String, nullable=True))")) == []


def test_add_not_null_column_with_server_default_is_additive():
    src = wrap("op.add_column('t', sa.Column('c', sa.Boolean, nullable=False, server_default=false()))")
    assert rules(src) == []


def test_create_table_with_not_null_columns_is_additive():
    """A brand-new table cannot break replicas that do not know it exists."""
    src = wrap("op.create_table('t', sa.Column('c', sa.String, nullable=False))")
    assert rules(src) == []


def test_existing_nullable_is_not_a_change():
    """`existing_nullable=` describes current state; it is not a narrowing."""
    src = wrap("op.alter_column('t', 'c', type_=sa.String(64), existing_nullable=False)")
    assert rules(src) == []


def test_destructive_ddl_in_downgrade_is_ignored():
    """Alembic autogenerates a mirror-image downgrade(); the deploy never runs it.

    This is the single most important false-positive guard: without it, every
    ordinary add_column migration would be flagged.
    """
    src = wrap("op.add_column('t', sa.Column('c', sa.String, nullable=True))", "op.drop_column('t', 'c')")
    assert rules(src) == []


def test_non_destructive_execute_is_additive():
    assert rules(wrap("op.execute(\"UPDATE t SET c = 'x' WHERE c IS NULL\")")) == []


# --- non-additive: must be flagged -------------------------------------------------

@pytest.mark.parametrize(
    'body,expected',
    [
        ("op.drop_column('t', 'c')", 'op.drop_column'),
        ("op.drop_table('t')", 'op.drop_table'),
        ("op.drop_constraint('c', 't')", 'op.drop_constraint'),
        ("op.drop_index('i', 't')", 'op.drop_index'),
        ("op.rename_table('a', 'b')", 'op.rename_table'),
        ("op.create_unique_constraint('u', 't', ['c'])", 'op.create_unique_constraint'),
    ],
)
def test_destructive_ops_are_flagged(body, expected):
    assert expected in rules(wrap(body))


def test_narrowing_to_not_null_is_flagged():
    assert 'op.alter_column(nullable=False)' in rules(wrap("op.alter_column('t', 'c', nullable=False)"))


def test_column_rename_is_flagged():
    src = wrap("op.alter_column('t', 'old', new_column_name='new')")
    assert 'op.alter_column(new_column_name=...)' in rules(src)


def test_add_not_null_without_server_default_is_flagged():
    """`default=` is SQLAlchemy client-side only and emits no DDL default."""
    src = wrap("op.add_column('t', sa.Column('c', sa.Integer, default=0, nullable=False))")
    assert any('add_column' in r for r in rules(src))


def test_unique_index_is_flagged():
    src = wrap("op.create_index('i', 't', ['c'], unique=True)")
    assert 'op.create_index(unique=True)' in rules(src)


def test_batch_alter_table_is_flagged():
    """batch mode recreates the table, and also hides op.* calls from the scan."""
    src = 'def upgrade():\n    with op.batch_alter_table("t") as b:\n        b.drop_column("c")\n'
    assert 'op.batch_alter_table' in rules(src)


@pytest.mark.parametrize(
    'sql',
    [
        'ALTER TABLE `t` DROP COLUMN `c`',
        'ALTER TABLE `t` MODIFY COLUMN `c` int NOT NULL',
        'DROP TABLE t',
        'TRUNCATE t',
    ],
)
def test_destructive_raw_sql_is_flagged(sql):
    """Raw SQL is the obvious way to sidestep an op.*-only ruleset."""
    assert any('execute' in r for r in rules(wrap(f'op.execute("{sql}")')))


# --- exemption ---------------------------------------------------------------------

def test_exemption_with_url_passes(tmp_path):
    p = tmp_path / 'm.py'
    p.write_text(
        '# additivity-exempt: https://example.com/issues/1 unused since v1.9\n'
        + wrap("op.drop_table('t')")
    )
    findings, exempt = checker.check_file(p)
    assert findings == [] and exempt and 'example.com' in exempt


def test_exemption_without_url_is_rejected(tmp_path):
    p = tmp_path / 'm.py'
    p.write_text('# additivity-exempt: trust-me\n' + wrap("op.drop_table('t')"))
    findings, exempt = checker.check_file(p)
    assert exempt is None
    assert findings and 'URL' in findings[0].rule


# --- calibration against the real corpus -------------------------------------------

def test_existing_migrations_are_stable():
    """The committed migrations must not change verdict unexpectedly.

    Guards the calibration: if a future ruleset change starts flagging the
    historical additive migrations, this fails loudly instead of in someone's PR.
    """
    flagged = sorted(
        p.name for p in checker.VERSIONS_DIR.glob('*.py')
        if p.name != '__init__.py' and checker.check_file(p)[0]
    )
    # Historical migrations that are genuinely non-additive in upgrade(). They
    # predate this gate; new migrations must be additive or carry an exemption.
    assert all(
        any(tok in name for tok in (
            'f9c5471478d0', 'f92bae6c27da', '88dbe32dc40d', '17792ef315c1',  # drop_*
            'f732d6e597fe',                                                   # drop_index + unique
            '7f8b4f463f1d', '71cf5d3ee14b', 'a3fc3cc13f56', 'fb27de54e731',   # raw DDL
            '156b3b0d77b9', '4a15d01919b8', '666158eab217',                   # NOT NULL, no default
            '0c99f6a02f3b', 'ceecffbb5eb5', 'd4e5f6a7b8c9',                   # narrowing / unique
        ))
        for name in flagged
    ), f'unexpected migration flagged: {flagged}'
