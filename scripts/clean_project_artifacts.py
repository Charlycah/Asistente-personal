"""Remove transient Python artifacts from the ROBY project tree."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

TRANSIENT_DIRECTORIES = {"__pycache__", ".pytest_cache"}
TRANSIENT_SUFFIXES = {".pyc", ".pyo"}


def clean_project(root: Path) -> tuple[int, int]:
    """Remove transient directories and compiled Python files below *root*."""
    removed_directories = 0
    removed_files = 0

    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_dir() and path.name in TRANSIENT_DIRECTORIES:
            shutil.rmtree(path)
            removed_directories += 1
        elif path.is_file() and path.suffix in TRANSIENT_SUFFIXES:
            path.unlink()
            removed_files += 1

    return removed_directories, removed_files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove Python cache and bytecode artifacts from ROBY."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    removed_directories, removed_files = clean_project(args.root.resolve())
    print(
        "ROBY project cleanup complete: "
        f"{removed_directories} directories and {removed_files} files removed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
