"""Tests for scripts/check_migration_additivity.py (the CI expand/contract gate).

A gate is only useful if it is well calibrated in BOTH directions: a false
positive on an ordinary additive migration teaches people to ignore it, and a
false negative defeats the point. These tests pin both, and are deliberately
written so that a checker which silently stops working fails the suite rather
than passing vacuously.
"""

import ast
import importlib.util
import pathlib
import sys
from urllib.parse import urlparse

import pytest

_SCRIPT = pathlib.Path(__file__).resolve().parents[2] / 'scripts/check_migration_additivity.py'
assert _SCRIPT.is_file(), f'checker script not found at {_SCRIPT}'
_spec = importlib.util.spec_from_file_location('check_migration_additivity', _SCRIPT)
checker = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = checker
_spec.loader.exec_module(checker)


def rules(source: str) -> list[str]:
    return [f.rule for f in checker.check_upgrade(ast.parse(source)) if f.blocking]


def notes(source: str) -> list[str]:
    return [f.rule for f in checker.check_upgrade(ast.parse(source)) if not f.blocking]


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
    assert rules(wrap("op.create_table('t', sa.Column('c', sa.String, nullable=False))")) == []


def test_unique_index_on_a_table_created_here_is_additive():
    src = wrap("op.create_table('t', sa.Column('c', sa.String))\n    op.create_index('i', 't', ['c'], unique=True)")
    assert rules(src) == []


def test_existing_nullable_is_not_a_change():
    """`existing_nullable=` describes current state; it is not a narrowing."""
    assert rules(wrap("op.alter_column('t', 'c', type_=sa.String(64), existing_nullable=False)")) == []


def test_widening_a_type_is_additive():
    src = wrap("op.alter_column('t', 'c', type_=sa.String(255), existing_type=sa.String(64))")
    assert rules(src) == []


def test_destructive_ddl_in_downgrade_is_ignored():
    """Alembic autogenerates a mirror-image downgrade(); the deploy never runs it.

    The single most important false-positive guard: without it, every ordinary
    add_column migration would be flagged.
    """
    src = wrap("op.add_column('t', sa.Column('c', sa.String, nullable=True))", "op.drop_column('t', 'c')")
    assert rules(src) == []


def test_helper_called_only_from_downgrade_is_ignored():
    src = (
        'def _cleanup():\n    op.drop_table("t")\n\n\n'
        'def upgrade():\n    op.add_column("t", sa.Column("c", sa.String))\n\n\n'
        'def downgrade():\n    _cleanup()\n'
    )
    assert rules(src) == []


def test_index_swap_is_not_flagged():
    """drop_index + create_index on the same table is one logical operation."""
    src = wrap("op.drop_index('i', 't')\n    op.create_index('i', 't', ['c'])")
    assert 'op.drop_index' not in rules(src)


def test_non_destructive_execute_is_additive():
    assert rules(wrap('op.execute("UPDATE t SET c = \'x\' WHERE c IS NULL")')) == []


def test_add_column_raw_sql_is_additive():
    """The expand-phase statement the gate itself recommends must not be flagged."""
    assert rules(wrap("op.execute('ALTER TABLE t ADD COLUMN c INT NOT NULL DEFAULT 0')")) == []


# --- non-additive: must be flagged -------------------------------------------------


@pytest.mark.parametrize(
    'body,expected',
    [
        ("op.drop_column('t', 'c')", 'op.drop_column'),
        ("op.drop_table('t')", 'op.drop_table'),
        ("op.drop_constraint('c', 't')", 'op.drop_constraint'),
        ("op.drop_index('i', 't')", 'op.drop_index'),
        ("op.rename_table('a', 'b')", 'op.rename_table'),
        ("op.create_unique_constraint('u', 't', ['c'])", 'op.create_unique_constraint (unique)'),
    ],
)
def test_destructive_ops_are_flagged(body, expected):
    assert expected in rules(wrap(body))


def test_narrowing_to_not_null_is_flagged():
    assert 'op.alter_column(nullable=False)' in rules(wrap("op.alter_column('t', 'c', nullable=False)"))


def test_narrowing_a_type_is_flagged():
    src = wrap("op.alter_column('t', 'c', type_=sa.String(50), existing_type=sa.String(255))")
    assert 'op.alter_column(<narrowing type>)' in rules(src)


def test_removing_a_server_default_is_flagged():
    src = wrap("op.alter_column('t', 'c', server_default=None, existing_server_default='0')")
    assert 'op.alter_column(server_default=None)' in rules(src)


def test_column_rename_is_flagged():
    src = wrap("op.alter_column('t', 'old', new_column_name='new')")
    assert 'op.alter_column(new_column_name=...)' in rules(src)


def test_add_not_null_without_server_default_is_flagged():
    """`default=` is SQLAlchemy client-side only and emits no DDL default."""
    src = wrap("op.add_column('t', sa.Column('c', sa.Integer, default=0, nullable=False))")
    assert any('add_column' in r for r in rules(src))


def test_explicit_server_default_none_does_not_satisfy_the_rule():
    src = wrap("op.add_column('t', sa.Column('c', sa.Integer, nullable=False, server_default=None))")
    assert any('add_column' in r for r in rules(src))


def test_unique_index_on_existing_table_is_flagged():
    assert 'op.create_index (unique)' in rules(wrap("op.create_index('i', 't', ['c'], unique=True)"))


def test_destructive_batch_alter_is_flagged():
    src = 'def upgrade():\n    with op.batch_alter_table("t") as b:\n        b.drop_column("c")\n'
    assert 'op.batch_alter_table(<destructive>)' in rules(src)


def test_additive_batch_alter_is_not_flagged():
    src = 'def upgrade():\n    with op.batch_alter_table("t") as b:\n        b.add_column(sa.Column("c", sa.String))\n'
    assert rules(src) == []


@pytest.mark.parametrize(
    'sql',
    [
        'ALTER TABLE `t` DROP COLUMN `c`',
        'DROP TABLE t',
        'TRUNCATE TABLE t',
        'ALTER TABLE t RENAME COLUMN a TO b',
    ],
)
def test_destructive_raw_sql_is_flagged(sql):
    """Raw SQL is the obvious way to sidestep an op.*-only ruleset."""
    assert any('execute' in r for r in rules(wrap(f'op.execute("{sql}")')))


@pytest.mark.parametrize(
    'stmt',
    [
        'op.get_bind().execute(sa.text("DROP TABLE t"))',
        'session.execute(sa.text("DROP TABLE t"))',
        'connection.execute("DROP TABLE t")',
    ],
)
def test_raw_sql_on_any_receiver_is_flagged(stmt):
    """op.get_bind()/Session is the most-used raw-SQL path in this repo."""
    assert any('execute' in r for r in rules(wrap(stmt)))


def test_destructive_op_in_a_helper_is_flagged():
    """Factoring a drop into a helper is house style here; it must not hide it."""
    src = (
        'def _cleanup(conn):\n    op.drop_index("i", "t")\n\n\n'
        'def upgrade():\n    _cleanup(op.get_bind())\n\n\ndef downgrade():\n    pass\n'
    )
    assert 'op.drop_index' in rules(src)


def test_missing_upgrade_is_flagged_not_ignored():
    """A file the checker cannot understand must never be a silent pass."""
    assert 'no upgrade() found' in rules('def upgade():\n    op.drop_table("t")\n')


# --- non-blocking notes ------------------------------------------------------------


def test_enum_change_is_a_note_not_a_block():
    """Appending an enum value is additive; removing one is not, and the member
    list is usually interpolated, so it cannot be decided statically."""
    src = wrap("op.execute(f'ALTER TABLE `t` MODIFY COLUMN `c` enum({vals}) NOT NULL')")
    assert rules(src) == []
    assert 'execute(<enum change>)' in notes(src)


def test_dynamic_sql_is_a_note_not_a_block():
    src = wrap('op.execute(some_statement)')
    assert rules(src) == []


# --- exemption ---------------------------------------------------------------------


def test_exemption_with_valid_url_and_reason_waives(tmp_path):
    p = tmp_path / 'm.py'
    p.write_text(
        '# additivity-exempt: https://github.com/thunderbird/appointment/issues/1 unused since v1.9\n'
        + wrap("op.drop_table('t')")
    )
    findings, waiver = checker.check_file(p)
    assert waiver is not None
    parsed = urlparse(waiver.split()[0])
    assert parsed.scheme == 'https' and parsed.netloc == 'github.com'
    # The waiver must still report what it is waiving, so it stays auditable.
    assert any('drop_table' in f.rule for f in findings)


@pytest.mark.parametrize(
    'marker',
    [
        '# additivity-exempt: trust-me a good reason here',  # not a URL
        '# additivity-exempt: https:// a good reason here',  # bare scheme
        '# additivity-exempt: https://evil.example/1 a good reason',  # wrong host
        '# additivity-exempt: https://github.com/thunderbird/appointment/issues/1',  # no reason
    ],
)
def test_invalid_exemptions_are_rejected(tmp_path, marker):
    p = tmp_path / 'm.py'
    p.write_text(marker + '\n' + wrap("op.drop_table('t')"))
    findings, waiver = checker.check_file(p)
    assert waiver is None
    assert any('invalid additivity-exempt' in f.rule for f in findings)


def test_exemption_inside_a_docstring_does_not_count(tmp_path):
    """The marker must be a real comment, not text in a string."""
    p = tmp_path / 'm.py'
    p.write_text(
        '"""docs\n# additivity-exempt: https://github.com/thunderbird/appointment/issues/1 reason here\n"""\n'
        + wrap("op.drop_table('t')")
    )
    findings, waiver = checker.check_file(p)
    assert waiver is None
    assert any('drop_table' in f.rule for f in findings)


# --- calibration against the real corpus -------------------------------------------
#
# Migrations that predate this gate and are non-additive in upgrade(). New
# migrations must be additive or carry an exemption. Both directions are asserted
# so that a checker which stops flagging anything FAILS rather than passing.

GRANDFATHERED = frozenset(
    {
        '2023_07_27_1102-f9c5471478d0_modify_schedules_table.py',
        '2024_03_13_1621-f92bae6c27da_update_subscribers_table_to_.py',
        '2024_06_13_1525-f732d6e597fe_update_appointments_make_uuid_.py',
        '2024_06_25_2133-156b3b0d77b9_add_ftue_level_to_subscribers.py',
        '2024_12_20_1733-0c99f6a02f3b_make_subscribers_language_not_.py',
        '2025_01_15_1340-4a15d01919b8_add_config_fields_to_subscribers_table.py',
        '2025_04_04_1536-666158eab217_add_start_of_week_user_setting.py',
        '2025_05_13_0837-ceecffbb5eb5_update_availabilities_table.py',
        '2025_06_26_1629-88dbe32dc40d_switch_appointment_uuid_type.py',
        '2026_02_19_0842-17792ef315c1_remove_invites_and_waiting_list_.py',
        '2026_06_15_1200-d4e5f6a7b8c9_add_owner_id_scoped_schedule_slug.py',
    }
)


def _blocking_flagged() -> set[str]:
    return {
        p.name
        for p in checker.VERSIONS_DIR.glob('*.py')
        if p.name != '__init__.py' and any(f.blocking for f in checker.check_file(p)[0])
    }


def test_corpus_is_non_empty():
    """Guards against VERSIONS_DIR resolving somewhere wrong, which would make
    every calibration assertion below pass over zero files."""
    found = [p for p in checker.VERSIONS_DIR.glob('*.py') if p.name != '__init__.py']
    assert len(found) >= 60, f'only {len(found)} migrations found; VERSIONS_DIR may be wrong'


def test_no_new_non_additive_migrations():
    """New migrations must be additive, or carry an exemption."""
    unexpected = _blocking_flagged() - GRANDFATHERED
    assert unexpected == set(), f'non-additive migration(s) added without an exemption: {sorted(unexpected)}'


def test_grandfathered_migrations_are_still_detected():
    """Non-vacuous regression guard: if a ruleset change stops catching the known
    offenders, this fails -- unlike a subset assertion, which passes on an empty set."""
    missed = {n for n in GRANDFATHERED if (checker.VERSIONS_DIR / n).is_file()} - _blocking_flagged()
    assert missed == set(), f'ruleset regression -- no longer flagged: {sorted(missed)}'
