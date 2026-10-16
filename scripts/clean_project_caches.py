"""Safely remove project-local Python/test caches without touching virtualenvs."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

CACHE_DIRECTORIES = {"__pycache__", ".pytest_cache", ".ruff_cache"}
BYTECODE_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "venv_old",
    "env",
    ".tox",
    ".nox",
}


@dataclass(frozen=True)
class CleanupResult:
    removed_directories: int
    removed_files: int
    failures: tuple[str, ...]
    residual_bytecode: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not self.failures and not self.residual_bytecode


def _is_excluded(path: Path, root: Path) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        return True
    return bool(EXCLUDED_DIRECTORIES.intersection(relative_parts))


def clean_project_caches(root: Path) -> CleanupResult:
    """Remove caches under *root*, excluding virtualenvs and tooling environments."""
    root = root.resolve()
    removed_directories = 0
    removed_files = 0
    failures: list[str] = []

    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        directories[:] = [
            name
            for name in directories
            if name not in EXCLUDED_DIRECTORIES
            and not (current_path / name).is_symlink()
        ]

        for name in list(directories):
            if name not in CACHE_DIRECTORIES:
                continue
            target = current_path / name
            try:
                shutil.rmtree(target)
                removed_directories += 1
                directories.remove(name)
            except OSError as exc:
                failures.append(f"{target}: {exc}")

        if _is_excluded(current_path, root):
            continue
        for name in files:
            target = current_path / name
            if target.suffix not in BYTECODE_SUFFIXES or target.is_symlink():
                continue
            try:
                target.unlink()
                removed_files += 1
            except OSError as exc:
                failures.append(f"{target}: {exc}")

    residual_bytecode = tuple(
        str(path)
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in BYTECODE_SUFFIXES
        and not path.is_symlink()
        and not _is_excluded(path, root)
    )
    return CleanupResult(
        removed_directories=removed_directories,
        removed_files=removed_files,
        failures=tuple(failures),
        residual_bytecode=residual_bytecode,
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = clean_project_caches(root)
    print(
        "ROBY cache cleanup: "
        f"{result.removed_directories} cache directories removed, "
        f"{result.removed_files} bytecode files removed."
    )
    if result.failures:
        print("Cleanup failures:")
        for failure in result.failures:
            print(f"- {failure}")
    if result.residual_bytecode:
        print("Residual project bytecode:")
        for path in result.residual_bytecode:
            print(f"- {path}")
    if result.clean:
        print("ROBY project caches clean; virtual environments were not touched.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
