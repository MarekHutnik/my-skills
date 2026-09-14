"""List Python modules, classes, functions and methods that have no docstring.

Finding them is mechanical; deciding which ones deserve a docstring is not. This prints the
candidates so that judgment is where the attention goes.

Usage:
    python find_missing_docstrings.py PATH [PATH ...] [--all] [--changed] [--base REF]

    --all       include private symbols (leading underscore) and dunder methods
    --changed   only files changed against the base ref
    --base REF  what --changed compares against (default: origin/HEAD, then main, then master)
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

# Overriding one of these without a docstring is normal: the base class documents the contract.
EXEMPT_METHODS = frozenset(
    {
        '__init__',
        '__post_init__',
        '__repr__',
        '__str__',
        '__eq__',
        '__hash__',
        '__enter__',
        '__exit__',
    }
)

SKIP_DIRS = frozenset({'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.mypy_cache', '.ruff_cache'})


def is_private(name: str) -> bool:
    """Whether a symbol is private by convention.

    Args:
        name (str): The symbol's name.

    Returns:
        bool: True for a single leading underscore, which excludes dunders.
    """
    return name.startswith('_') and not name.startswith('__')


def python_files(paths: list[Path]) -> list[Path]:
    """Every .py file under the given paths, skipping vendored and cache directories.

    Args:
        paths (list[Path]): Files or directories to walk.

    Returns:
        list[Path]: Sorted, de-duplicated file paths.
    """
    found: set[Path] = set()
    for path in paths:
        if path.is_file() and path.suffix == '.py':
            found.add(path)
            continue
        for candidate in path.rglob('*.py'):
            if not SKIP_DIRS.intersection(candidate.parts):
                found.add(candidate)
    return sorted(found)


def changed_files(base: str | None) -> list[Path]:
    """Python files this branch changed, for scoping a pass to one review.

    Args:
        base (str | None): Ref to diff against, or None to try the usual defaults.

    Returns:
        list[Path]: Existing .py files that differ from the base ref.

    Raises:
        SystemExit: When no base ref can be resolved, since silently scanning everything
            would misrepresent the scope.
    """
    candidates = [base] if base else ['origin/HEAD', 'main', 'master']
    for ref in candidates:
        try:
            out = subprocess.run(
                ['git', 'diff', '--name-only', f'{ref}...HEAD'],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        files = [Path(line) for line in out.splitlines() if line.endswith('.py')]
        return [f for f in files if f.is_file()]
    raise SystemExit(f'Could not resolve a base ref (tried {", ".join(str(c) for c in candidates)}). Pass --base.')


def missing_in(path: Path, include_private: bool) -> list[tuple[int, str, str]]:
    """Symbols in one file that have no docstring.

    Args:
        path (Path): The file to parse.
        include_private (bool): Whether to report private symbols and dunder methods.

    Returns:
        list[tuple[int, str, str]]: (line, kind, qualified name), in line order. A file that
            cannot be parsed reports itself as a syntax error rather than being skipped
            silently.
    """
    source = path.read_text(encoding='utf-8', errors='replace')
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [(exc.lineno or 0, 'syntax error', str(exc.msg))]

    found: list[tuple[int, str, str]] = []
    if ast.get_docstring(tree) is None:
        found.append((1, 'module', path.name))

    def walk(node: ast.AST, prefix: str) -> None:
        """Append every undocumented definition under `node` to `found`, depth first."""
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            name = child.name
            qualified = f'{prefix}.{name}' if prefix else name
            is_method = bool(prefix)
            skip = (not include_private) and (is_private(name) or (is_method and name in EXEMPT_METHODS))
            if not skip and ast.get_docstring(child) is None:
                kind = 'class' if isinstance(child, ast.ClassDef) else ('method' if is_method else 'function')
                found.append((child.lineno, kind, qualified))
            walk(child, qualified)

    walk(tree, '')
    return sorted(found)


def main() -> int:
    """Print every symbol missing a docstring, grouped by file.

    Returns:
        int: 1 when anything is missing, so the script can gate a pipeline; 0 otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('paths', nargs='*', type=Path, default=[Path('.')])
    parser.add_argument('--all', action='store_true', help='include private symbols and dunder methods')
    parser.add_argument('--changed', action='store_true', help='only files changed against the base ref')
    parser.add_argument('--base', default=None, help='base ref for --changed')
    args = parser.parse_args()

    files = changed_files(args.base) if args.changed else python_files(args.paths or [Path('.')])
    if not files:
        print('No Python files to check.')
        return 0

    total = 0
    unparsed = 0
    for path in files:
        rows = missing_in(path, include_private=args.all)
        if not rows:
            continue
        print(f'{path}')
        for line, kind, name in rows:
            print(f'  {line:>5}  {kind:<12} {name}')
        total += sum(1 for _, kind, _ in rows if kind != 'syntax error')
        unparsed += sum(1 for _, kind, _ in rows if kind == 'syntax error')

    scope = 'symbols' if args.all else 'public symbols'
    print(f'{chr(10)}{total} {scope} without a docstring, across {len(files)} file(s).')
    if unparsed:
        print(f'{unparsed} file(s) could not be parsed and were not checked.')
    if total:
        print('Add one where a caller could get it wrong; leave it where the name already says it.')
    return 1 if (total or unparsed) else 0


if __name__ == '__main__':
    sys.exit(main())
