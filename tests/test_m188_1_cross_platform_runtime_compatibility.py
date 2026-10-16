from __future__ import annotations

import os
from pathlib import Path

from core.platform_runtime_compatibility import (
    apply_private_file_permissions,
    private_file_is_protected,
    process_exists,
)


def test_private_file_policy_accepts_written_file(tmp_path: Path):
    path = tmp_path / "private.json"
    path.write_text("{}", encoding="utf-8")
    apply_private_file_permissions(path)
    assert private_file_is_protected(path)


def test_private_file_policy_rejects_missing_file(tmp_path: Path):
    assert not private_file_is_protected(tmp_path / "missing.json")


def test_current_process_is_detected():
    assert process_exists(os.getpid())


def test_non_positive_process_ids_do_not_exist():
    assert not process_exists(0)
    assert not process_exists(-1)


def test_private_file_has_exact_posix_mode_when_supported(tmp_path: Path):
    path = tmp_path / "private.txt"
    path.write_text("private", encoding="utf-8")
    apply_private_file_permissions(path)
    if os.name != "nt":
        assert path.stat().st_mode & 0o777 == 0o600
