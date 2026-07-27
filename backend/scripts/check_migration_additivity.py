#!/usr/bin/env python3
"""Fail CI when a new Alembic migration is not additive (expand/contract safe).

WHY
---
Appointment is deployed with a blue-green rollout: for a window during every
deploy, the OLD and NEW replicas run against the SAME database. A migration that
removes or narrows something the old replicas still use breaks them the moment it
lands -- and a schema change cannot be rolled back by aborting the deploy. So a
migration must only ever ADD things ("expand"); removals ("contract") ship in a
LATER release, once no running replica references them.

This check runs in CI on the migrations a PR ADDS, so the author finds out while
it is still cheap to fix, and before the migration can ever execute anywhere.

WHAT IS FLAGGED (in `upgrade()` only -- `downgrade()` is never run by the deploy)
---------------------------------------------------------------------------
  * op.drop_column / drop_table / drop_constraint / drop_index
  * op.rename_table, and op.alter_column(new_column_name=...)   (renames)
  * op.alter_column(nullable=False)                             (narrowing)
  * op.add_column(... nullable=False) with NO server_default    (old replicas'
    INSERTs omit the column, so they start failing)
  * op.create_index(unique=True) / op.create_unique_constraint  (fails outright
    if existing rows collide, leaving a half-applied release)
  * op.batch_alter_table(...)                                   (recreates the
    table; never additive under blue-green)
  * op.execute("...") containing destructive SQL

WHAT IS NOT FLAGGED (deliberately -- these are additive)
--------------------------------------------------------
  * anything inside `downgrade()`
  * `nullable=False` on a column of a brand-new `op.create_table(...)` -- old
    replicas do not know the table exists
  * `existing_nullable=False` -- a descriptor of current state, not a change
  * `op.add_column(... nullable=False, server_default=...)` -- the default
    backfills for old replicas

ESCAPE HATCH
------------
A genuinely-needed contract migration ships by declaring it in the migration
itself, so the reviewer of the schema change sees the justification in the diff:

    # additivity-exempt: https://github.com/thunderbird/appointment/issues/1234
    #   invites table removal; no replica has referenced it since v1.9.

The marker must carry a URL. Prefer splitting into expand/contract over exempting.

USAGE
-----
    check_migration_additivity.py <file.py> [<file.py> ...]
    check_migration_additivity.py --all      # scan every migration (audit)

Exit 0 = additive (or exempt), 1 = non-additive found, 2 = usage/parse error.
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

VERSIONS_DIR = pathlib.Path(__file__).resolve().parents[1] / 'src/appointment/migrations/versions'

# op.<name>(...) calls that remove or rename something an old replica may use.
DESTRUCTIVE_OPS = {
    'drop_column': 'drops a column the old replicas may still SELECT',
    'drop_table': 'drops a table the old replicas may still query',
    'drop_constraint': 'drops a constraint the old replicas rely on',
    'drop_index': 'drops an index; old replicas lose the query plan mid-rollout',
    'rename_table': 'renames a table; old replicas still use the old name',
}

# Raw SQL that is destructive regardless of how it is spelled.
DESTRUCTIVE_SQL = re.compile(
    r'\b(?:'
    r'DROP\s+(?:COLUMN|TABLE|CONSTRAINT|INDEX)'
    r'|ALTER\s+TABLE\b[\s\S]*?\b(?:DROP|MODIFY|CHANGE)\b'
    r'|RENAME\s+(?:TO|COLUMN)'
    r'|TRUNCATE\b'
    r'|DELETE\s+FROM\b'
    r'|NOT\s+NULL'
    r')',
    re.IGNORECASE,
)

EXEMPT_RE = re.compile(r'#\s*additivity-exempt:\s*(\S+)(.*)', re.IGNORECASE)


class Finding:
    def __init__(self, line: int, rule: str, detail: str, fix: str):
        self.line, self.rule, self.detail, self.fix = line, rule, detail, fix


def _kwarg(call: ast.Call, name: str) -> ast.expr | None:
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _is_true(node: ast.expr | None) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def _is_false(node: ast.expr | None) -> bool:
    return isinstance(node, ast.Constant) and node.value is False


def _op_name(call: ast.Call) -> str | None:
    """Return the method name for `op.<name>(...)` / `batch_op.<name>(...)`."""
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _receiver(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id
    return None


def _columns_in(call: ast.Call) -> list[ast.Call]:
    """sa.Column(...) calls appearing anywhere inside this call's arguments."""
    out = []
    for node in ast.walk(call):
        if isinstance(node, ast.Call) and _op_name(node) == 'Column':
            out.append(node)
    return out


def check_upgrade(tree: ast.Module) -> list[Finding]:
    upgrade = next(
        (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith('upgrade')),
        None,
    )
    if upgrade is None:
        return []

    findings: list[Finding] = []

    # NOTE: `op.create_table(...)` is never inspected below -- a brand-new table's
    # NOT NULL columns are additive (no running replica knows the table exists), so
    # create_table is exempt by construction rather than by an explicit filter.
    for node in ast.walk(upgrade):
        if not isinstance(node, ast.Call):
            continue
        name = _op_name(node)
        if name is None:
            continue

        if name in DESTRUCTIVE_OPS:
            findings.append(
                Finding(node.lineno, f'op.{name}', DESTRUCTIVE_OPS[name],
                        'Remove it here; ship the removal in a LATER release (contract phase).')
            )
            continue

        if name == 'batch_alter_table':
            findings.append(
                Finding(node.lineno, 'op.batch_alter_table',
                        'batch mode recreates the table, which is never additive',
                        'Use direct op.* calls for the additive parts.')
            )
            continue

        if name == 'alter_column':
            if _kwarg(node, 'new_column_name') is not None:
                findings.append(
                    Finding(node.lineno, 'op.alter_column(new_column_name=...)',
                            'renames a column; old replicas still SELECT the old name',
                            'Add the new column, dual-write, backfill, drop the old one in a later release.')
                )
            if _is_false(_kwarg(node, 'nullable')):
                findings.append(
                    Finding(node.lineno, 'op.alter_column(nullable=False)',
                            "narrows a column; old replicas' NULL-omitting INSERTs start failing",
                            'Backfill first, then enforce NOT NULL in a later release.')
                )
            continue

        if name == 'add_column':
            for col in _columns_in(node):
                if _is_false(_kwarg(col, 'nullable')) and _kwarg(col, 'server_default') is None:
                    findings.append(
                        Finding(col.lineno, 'op.add_column(nullable=False) without server_default',
                                "old replicas' INSERTs omit the column, so they fail",
                                "Add server_default=... (note: SQLAlchemy's default= is client-side "
                                'and emits no DDL default, so it does not help here).')
                    )
            continue

        if name == 'create_index' and _is_true(_kwarg(node, 'unique')):
            findings.append(
                Finding(node.lineno, 'op.create_index(unique=True)',
                        'fails outright if existing rows collide, leaving a half-applied release',
                        'De-duplicate in a prior release, then add the unique index.')
            )
            continue

        if name == 'create_unique_constraint':
            findings.append(
                Finding(node.lineno, 'op.create_unique_constraint',
                        'fails outright if existing rows collide',
                        'De-duplicate in a prior release, then add the constraint.')
            )
            continue

        if name == 'execute' and _receiver(node) == 'op':
            for arg in ast.walk(node):
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    m = DESTRUCTIVE_SQL.search(arg.value)
                    if m:
                        findings.append(
                            Finding(node.lineno, 'op.execute(<destructive SQL>)',
                                    f'raw SQL contains {m.group(0).strip()!r}',
                                    'Express the additive part in SQL; defer the destructive part a release.')
                        )
                        break

    return findings


def check_file(path: pathlib.Path) -> tuple[list[Finding], str | None]:
    """Return (findings, exemption_reason)."""
    src = path.read_text(encoding='utf-8')
    m = EXEMPT_RE.search(src)
    if m:
        url, rest = m.group(1), m.group(2).strip()
        if not url.startswith(('http://', 'https://')):
            return (
                [Finding(0, 'additivity-exempt without a URL',
                         f'marker points at {url!r}',
                         'Use: # additivity-exempt: <issue-url> <reason>')],
                None,
            )
        return [], f'{url} {rest}'.strip()

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as exc:  # pragma: no cover
        return [Finding(exc.lineno or 0, 'syntax error', str(exc), 'Fix the migration file.')], None
    return check_upgrade(tree), None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='*', help='migration files to check')
    ap.add_argument('--all', action='store_true', help='check every migration (audit mode)')
    args = ap.parse_args()

    if args.all:
        paths = sorted(VERSIONS_DIR.glob('*.py'))
    else:
        paths = [pathlib.Path(f) for f in args.files]
        paths = [p for p in paths if p.suffix == '.py' and p.name != '__init__.py' and p.exists()]

    if not paths:
        print('migration-additivity: no migration files to check.')
        return 0

    failed = False
    for path in paths:
        findings, exempt = check_file(path)
        if exempt:
            print(f'\N{WARNING SIGN}  {path.name}: EXEMPT -- {exempt}')
            continue
        if not findings:
            print(f'\N{CHECK MARK}  {path.name}: additive')
            continue
        failed = True
        print(f'\N{CROSS MARK}  {path.name}: NOT additive')
        for f in findings:
            print(f'      line {f.line}: {f.rule}')
            print(f'        why: {f.detail}')
            print(f'        fix: {f.fix}')

    if failed:
        print(
            '\nA blue-green deploy runs the OLD and NEW replicas against the same database,\n'
            'and a schema change cannot be undone by aborting the deploy. Split the change:\n'
            '  release N   : add the new thing (and backfill / dual-write)\n'
            '  release N+1 : remove the old thing, once nothing references it\n\n'
            'If the removal is genuinely safe now, declare it in the migration:\n'
            '  # additivity-exempt: <issue-url> <why it is safe>\n'
        )
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
