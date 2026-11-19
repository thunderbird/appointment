#!/usr/bin/env python3
"""Fail CI when a new Alembic migration is not additive (expand/contract safe).

WHY
---
For a window during every deploy, the OLD and NEW replicas run against the SAME
database. A migration that removes or narrows something the old replicas still
use breaks them the moment it lands -- and a schema change cannot be rolled back
by aborting the deploy. So a migration must only ever ADD things ("expand");
removals ("contract") ship in a LATER release, once no running replica
references them.

That window already exists in the current ECS Fargate rolling deploy (AWS
default min 100% / max 200%), where it is short and incidental. This check is
groundwork for the Argo Rollouts BLUE-GREEN deploy on the new EKS tb-dev /
tb-prod clusters (thunderbird/platform-infrastructure#781), which holds both
versions up on purpose -- for the length of prePromotionAnalysis plus
scaleDownDelaySeconds -- and offers an abort path that looks like a rollback but
cannot undo DDL.

This runs in CI on the migrations a PR adds or edits, so the author finds out
while it is still cheap to fix, and before the migration can execute anywhere.

SCOPE OF THE SCAN
-----------------
Every top-level `upgrade` / `upgrade_<engine>` function, PLUS every module-level
helper transitively called from them -- factoring a drop into a helper is the
house style here, and must not hide it. `downgrade()` and anything reachable only
from it is ignored: the deploy never runs it, and Alembic autogenerates a
destructive downgrade for every additive upgrade.

WHAT IS FLAGGED
---------------
  * op.drop_column / drop_table / drop_constraint / rename_table
  * op.drop_index                       (unless the same table is re-indexed here)
  * op.alter_column(new_column_name=)   (rename)
  * op.alter_column(nullable=False)     (narrowing)
  * op.alter_column(type_=) that shrinks a length
  * op.alter_column(server_default=None) over an existing default
  * op.add_column(nullable=False) with no server_default
  * unique constraints/indexes on a PRE-EXISTING table (they abort on duplicates)
  * op.batch_alter_table(...) whose body is destructive (batch recreates the table)
  * .execute() -- on ANY receiver -- carrying destructive SQL

NOT FLAGGED (these are additive)
--------------------------------
  * anything reachable only from `downgrade()`
  * NOT NULL / unique on a table created in the same migration
  * `existing_nullable=` / `existing_server_default=` (they describe current state)
  * op.add_column(nullable=False, server_default=...)

ESCAPE HATCH
------------
A genuinely-safe contract migration declares itself, in a real comment, so the
justification sits in the diff the schema reviewer reads:

    # additivity-exempt: https://github.com/thunderbird/appointment/issues/1234
    #   invites table; nothing has referenced it since v1.9

The URL must be a Thunderbird issue/PR and a reason is required. Exempt files are
still scanned, and everything waived is printed, so the waiver is auditable.

USAGE
-----
    check_migration_additivity.py <file.py> [<file.py> ...]
    check_migration_additivity.py --all      # audit every migration

Exit 0 = additive (or waived), 1 = non-additive found, 2 = tool/usage error.
"""

from __future__ import annotations

import argparse
import ast
import io
import os
import pathlib
import re
import sys
import tokenize

VERSIONS_DIR = pathlib.Path(__file__).resolve().parents[1] / 'src/appointment/migrations/versions'

UPGRADE_RE = re.compile(r'^upgrade(_\w+)?$')

# Removals/renames: an old replica still referencing the thing breaks immediately.
DESTRUCTIVE_OPS = {
    'drop_column': 'drops a column the old replicas may still SELECT',
    'drop_table': 'drops a table the old replicas may still query',
    'drop_constraint': 'drops a constraint the old replicas rely on',
    'rename_table': 'renames a table; old replicas still use the old name',
}

# Destructive SQL. Anchored to DDL verbs so a bare "NOT NULL" in a CREATE TABLE,
# or the word DELETE inside a string value, does not trip it.
DESTRUCTIVE_SQL = re.compile(
    r'\b(?:'
    r'DROP\s+(?:COLUMN|TABLE|CONSTRAINT|INDEX)'
    r'|ALTER\s+TABLE\b[\s\S]{0,200}?\b(?:DROP|MODIFY|CHANGE)\b'
    r'|RENAME\s+(?:TO|COLUMN)'
    r'|TRUNCATE\s+TABLE'
    r')',
    re.IGNORECASE,
)

# Only a real Thunderbird issue/PR justifies a waiver.
EXEMPT_URL_RE = re.compile(r'^https://github\.com/thunderbird/[\w.-]+/(?:issues|pull)/\d+/?$')
EXEMPT_MARKER_RE = re.compile(r'#\s*additivity-exempt:\s*(\S+)\s*(.*)', re.IGNORECASE)


class ToolError(Exception):
    """Something prevented the check from running; never a silent pass."""


class Finding:
    def __init__(self, line: int, rule: str, detail: str, fix: str, blocking: bool = True):
        self.line, self.rule, self.detail, self.fix, self.blocking = line, rule, detail, fix, blocking


# --- small AST helpers -------------------------------------------------------------


def _attr_name(call: ast.Call) -> str | None:
    """`x.foo(...)` -> 'foo'."""
    return call.func.attr if isinstance(call.func, ast.Attribute) else None


def _receiver(call: ast.Call) -> str | None:
    """`op.foo(...)` -> 'op'. Returns None for chained calls like op.get_bind().foo()."""
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id
    return None


def _kwarg(call: ast.Call, name: str) -> ast.expr | None:
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _has_kwarg(call: ast.Call, name: str) -> bool:
    return any(kw.arg == name for kw in call.keywords)


def _is(node: ast.expr | None, value) -> bool:
    return isinstance(node, ast.Constant) and node.value is value


def _str_arg(call: ast.Call, index: int) -> str | None:
    if len(call.args) > index and isinstance(call.args[index], ast.Constant):
        v = call.args[index].value
        return v if isinstance(v, str) else None
    return None


def _sa_columns(call: ast.Call) -> list[ast.Call]:
    return [n for n in ast.walk(call) if isinstance(n, ast.Call) and _attr_name(n) == 'Column']


def _type_length(node: ast.expr | None) -> tuple[str, int] | None:
    """`sa.String(50)` -> ('String', 50). Only literal lengths are comparable."""
    if not isinstance(node, ast.Call):
        return None
    name = _attr_name(node) or (node.func.id if isinstance(node.func, ast.Name) else None)
    if not name or not node.args:
        return None
    first = node.args[0]
    length = _kwarg(node, 'length')
    for candidate in (first, length):
        if isinstance(candidate, ast.Constant) and isinstance(candidate.value, int):
            return name, candidate.value
    return None


def _literal_sql(call: ast.Call) -> tuple[str, bool]:
    """Best-effort SQL text inside a call. Returns (text, fully_static)."""
    parts: list[str] = []
    static = True
    for node in ast.walk(call):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            parts.append(node.value)
        elif isinstance(node, ast.JoinedStr):
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    parts.append(v.value)
                else:
                    static = False
                    parts.append(' ? ')
        elif isinstance(node, ast.Name):
            static = False
    return ' '.join(parts), static


# --- scan scope: upgrade() plus the helpers it calls --------------------------------


def _scanned_functions(tree: ast.Module) -> tuple[list[ast.AST], list[str]]:
    """Return (functions to scan, names of upgrade entrypoints found)."""
    funcs: dict[str, ast.AST] = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    entry = [name for name in funcs if UPGRADE_RE.match(name)]
    if not entry:
        return [], []

    # Transitively pull in module-level helpers called from the upgrade path, so a
    # destructive op factored into a helper cannot hide. `downgrade` and anything
    # only it calls are never added.
    selected: dict[str, ast.AST] = {name: funcs[name] for name in entry}
    queue = list(entry)
    while queue:
        node = funcs[queue.pop()]
        for call in ast.walk(node):
            if not isinstance(call, ast.Call):
                continue
            callee = call.func.id if isinstance(call.func, ast.Name) else None
            if callee and callee in funcs and callee not in selected and not callee.startswith('downgrade'):
                selected[callee] = funcs[callee]
                queue.append(callee)
    return list(selected.values()), entry


# --- the rules ---------------------------------------------------------------------


def check_upgrade(tree: ast.Module) -> list[Finding]:
    scoped, entry = _scanned_functions(tree)
    if not entry:
        return [
            Finding(
                0,
                'no upgrade() found',
                'the file defines no top-level upgrade()/upgrade_<engine>()',
                'A migration must define upgrade(); the check cannot verify this file.',
            )
        ]

    calls = [n for f in scoped for n in ast.walk(f) if isinstance(n, ast.Call)]

    # Tables created here are additive wholesale: no running replica knows them.
    new_tables = {t for c in calls if _attr_name(c) == 'create_table' and (t := _str_arg(c, 0))}
    # A drop_index paired with a create_index on the same table is an index swap.
    reindexed = {t for c in calls if _attr_name(c) == 'create_index' and (t := _str_arg(c, 1))}
    # `with op.batch_alter_table(...) as batch_op:` binds an alias we must trust.
    batch_aliases = {
        item.optional_vars.id
        for f in scoped
        for n in ast.walk(f)
        if isinstance(n, ast.With)
        for item in n.items
        if isinstance(item.context_expr, ast.Call)
        and _attr_name(item.context_expr) == 'batch_alter_table'
        and isinstance(item.optional_vars, ast.Name)
    }
    ddl_receivers = {'op'} | batch_aliases

    findings: list[Finding] = []
    for node in calls:
        name = _attr_name(node)
        if name is None:
            continue
        recv = _receiver(node)

        # `.execute()` is checked on ANY receiver: op.execute, session.execute,
        # connection.execute and op.get_bind().execute are all used in this repo.
        if name == 'execute':
            sql, static = _literal_sql(node)
            hit = DESTRUCTIVE_SQL.search(sql)
            if hit and re.search(r'\benum\s*\(', sql, re.IGNORECASE):
                # An enum MODIFY is ambiguous: appending a value is additive, removing
                # one is not, and the member list is usually interpolated so it cannot
                # be compared statically. Surface it; do not block on it.
                findings.append(
                    Finding(
                        node.lineno,
                        'execute(<enum change>)',
                        'alters an enum; additive only if values are ADDED, never removed',
                        'Reviewer must confirm no enum value was removed.',
                        blocking=False,
                    )
                )
            elif hit:
                findings.append(
                    Finding(
                        node.lineno,
                        'execute(<destructive SQL>)',
                        f'raw SQL contains {hit.group(0).strip()!r}',
                        'Defer the destructive statement to a later release.',
                    )
                )
            elif not static and sql.strip():
                findings.append(
                    Finding(
                        node.lineno,
                        'execute(<dynamic SQL>)',
                        'SQL is built at runtime, so it cannot be verified statically',
                        'Reviewer must confirm this is additive.',
                        blocking=False,
                    )
                )
            continue

        # Everything below is a DDL op and must actually be on op/batch_op.
        if recv not in ddl_receivers and name not in ('add_column',):
            continue

        if name in DESTRUCTIVE_OPS:
            findings.append(
                Finding(
                    node.lineno,
                    f'op.{name}',
                    DESTRUCTIVE_OPS[name],
                    'Ship the removal in a LATER release (contract phase).',
                )
            )
            continue

        if name == 'drop_index':
            table = _str_arg(node, 1) or (
                k.value if isinstance(k := _kwarg(node, 'table_name'), ast.Constant) else None
            )
            if table in reindexed:
                continue  # index swap: dropped and recreated in the same migration
            findings.append(
                Finding(
                    node.lineno,
                    'op.drop_index',
                    'removes an index the old replicas depend on for query plans',
                    'Recreate it here, or drop it in a later release.',
                )
            )
            continue

        if name == 'batch_alter_table':
            table = _str_arg(node, 0)
            parent = next(
                (
                    w
                    for f in scoped
                    for w in ast.walk(f)
                    if isinstance(w, ast.With) and any(i.context_expr is node for i in w.items)
                ),
                None,
            )
            destructive = parent is not None and any(
                _attr_name(c) in (DESTRUCTIVE_OPS | {'drop_index': ''})
                for c in ast.walk(parent)
                if isinstance(c, ast.Call)
            )
            if destructive and table not in new_tables:
                findings.append(
                    Finding(
                        node.lineno,
                        'op.batch_alter_table(<destructive>)',
                        'batch mode recreates the table, and the body removes something',
                        'Defer the removal to a later release.',
                    )
                )
            continue

        if name == 'alter_column':
            table = _str_arg(node, 0)
            if _kwarg(node, 'new_column_name') is not None:
                findings.append(
                    Finding(
                        node.lineno,
                        'op.alter_column(new_column_name=...)',
                        'renames a column; old replicas still SELECT the old name',
                        'Add the new column, dual-write, backfill, drop the old one later.',
                    )
                )
            if _is(_kwarg(node, 'nullable'), False) and table not in new_tables:
                findings.append(
                    Finding(
                        node.lineno,
                        'op.alter_column(nullable=False)',
                        "narrows a column; old replicas' NULL-omitting INSERTs start failing",
                        'Backfill first, then enforce NOT NULL in a later release.',
                    )
                )
            if (
                _has_kwarg(node, 'server_default')
                and _is(_kwarg(node, 'server_default'), None)
                and _has_kwarg(node, 'existing_server_default')
            ):
                findings.append(
                    Finding(
                        node.lineno,
                        'op.alter_column(server_default=None)',
                        "removes a default the old replicas' INSERTs rely on",
                        'Remove the default in a later release.',
                    )
                )
            new_t, old_t = _type_length(_kwarg(node, 'type_')), _type_length(_kwarg(node, 'existing_type'))
            if new_t and old_t and new_t[0] == old_t[0] and new_t[1] < old_t[1]:
                findings.append(
                    Finding(
                        node.lineno,
                        'op.alter_column(<narrowing type>)',
                        f'{old_t[0]}({old_t[1]}) -> {new_t[0]}({new_t[1]}) truncates existing data',
                        'Widen instead, or narrow in a later release after backfilling.',
                    )
                )
            continue

        if name == 'add_column':
            if recv not in ddl_receivers:
                continue
            table = _str_arg(node, 0)
            if table in new_tables:
                continue
            for col in _sa_columns(node):
                default = _kwarg(col, 'server_default')
                if _is(_kwarg(col, 'nullable'), False) and (default is None or _is(default, None)):
                    findings.append(
                        Finding(
                            col.lineno,
                            'op.add_column(nullable=False) without server_default',
                            "old replicas' INSERTs omit the column, so they fail",
                            "Add server_default=... (SQLAlchemy's default= is client-side and emits no DDL default).",
                        )
                    )
            continue

        if (name == 'create_index' and _is(_kwarg(node, 'unique'), True)) or name == 'create_unique_constraint':
            table = _str_arg(node, 1)
            if table in new_tables:
                continue
            findings.append(
                Finding(
                    node.lineno,
                    f'op.{name} (unique)',
                    'aborts the migration if existing rows collide',
                    'De-duplicate in a prior release, then add the constraint.',
                )
            )

    return findings


# --- exemptions (real comments only) -----------------------------------------------


def _exemptions(src: str) -> list[tuple[int, str, str]]:
    """Markers found in genuine COMMENT tokens -- not docstrings or SQL strings."""
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT and (m := EXEMPT_MARKER_RE.search(tok.string)):
                out.append((tok.start[0], m.group(1), m.group(2).strip()))
    except (tokenize.TokenError, IndentationError):
        pass
    return out


def check_file(path: pathlib.Path) -> tuple[list[Finding], str | None]:
    """Return (findings, waiver). A waiver never skips the scan."""
    try:
        src = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        raise ToolError(f'{path}: cannot read ({exc})') from exc

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as exc:
        raise ToolError(f'{path}: syntax error at line {exc.lineno} ({exc.msg})') from exc

    findings = check_upgrade(tree)

    markers = _exemptions(src)
    if not markers:
        return findings, None

    bad = [(ln, url) for ln, url, reason in markers if not EXEMPT_URL_RE.match(url) or len(reason) < 10]
    if bad:
        ln, url = bad[0]
        return findings + [
            Finding(
                ln,
                'invalid additivity-exempt marker',
                f'{url!r} is not a Thunderbird issue/PR URL followed by a reason',
                'Use: # additivity-exempt: https://github.com/thunderbird/<repo>/issues/<n> <why it is safe>',
            )
        ], None

    return findings, '; '.join(f'{url} {reason}' for _, url, reason in markers)


# --- output ------------------------------------------------------------------------


def _annotate(path: pathlib.Path, f: Finding) -> None:
    if os.environ.get('GITHUB_ACTIONS') and f.line:
        print(f'::error file={path},line={f.line},title=Non-additive migration::{f.rule} -- {f.detail}')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='*', help='migration files to check')
    ap.add_argument('--all', action='store_true', help='audit every migration')
    args = ap.parse_args()

    if args.all:
        if not VERSIONS_DIR.is_dir():
            print(f'error: migrations directory not found: {VERSIONS_DIR}', file=sys.stderr)
            return 2
        paths = [p for p in sorted(VERSIONS_DIR.glob('*.py')) if p.name != '__init__.py']
    else:
        paths = []
        for f in args.files:
            p = pathlib.Path(f)
            # A path we were asked to check but cannot must never be a silent pass.
            if not p.is_file() or p.suffix != '.py':
                print(f'error: not a migration file: {f}', file=sys.stderr)
                return 2
            if p.name != '__init__.py':
                paths.append(p)

    if not paths:
        print('migration-additivity: no migration files to check.')
        return 0

    failed = False
    for path in paths:
        try:
            findings, waiver = check_file(path)
        except ToolError as exc:
            print(f'ERROR  {exc}', file=sys.stderr)
            return 2

        blocking = [f for f in findings if f.blocking]
        if waiver:
            print(f'WAIVED {path.name}: {waiver}')
            for f in findings:
                print(f'         line {f.line}: {f.rule} -- {f.detail}')
            continue
        if not blocking:
            print(f'PASS   {path.name}: additive')
            for f in findings:
                print(f'         note line {f.line}: {f.rule} -- {f.detail}')
            continue

        failed = True
        print(f'FAIL   {path.name}: not additive')
        for f in findings:
            print(f'         line {f.line}: {f.rule}')
            print(f'           why: {f.detail}')
            print(f'           fix: {f.fix}')
            if f.blocking:
                _annotate(path, f)

    if failed:
        print(
            '\nA deploy runs the OLD and NEW replicas against the same database (briefly on\n'
            'ECS rolling; deliberately, for longer, on the EKS blue-green rollout), and a\n'
            'schema change cannot be undone by aborting the deploy. Split the change:\n'
            '  release N   : add the new thing, and dual-write/backfill it in the app\n'
            '  release N+1 : remove the old thing, once no running replica references it\n'
            '\nA rename is add -> dual-write -> backfill -> drop, i.e. more than two releases.\n'
            '\nIf the removal is genuinely safe now, declare it in the migration:\n'
            '  # additivity-exempt: https://github.com/thunderbird/<repo>/issues/<n> <why it is safe>\n'
        )
    return 1 if failed else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except ToolError as exc:  # pragma: no cover
        print(f'ERROR  {exc}', file=sys.stderr)
        sys.exit(2)
