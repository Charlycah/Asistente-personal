"""R-CAP17-O3-S10 RED: governed explicit relative-path lookup, no full scan.

Contract proposal only. This module intentionally fails against O2 GREEN until
its canonical implementation is authorized. No production changes in S10.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)


def _owner(root: Path, *, limit: int = 1) -> GovernedLocalLibraryCatalogueV1:
    return GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=root, max_catalogue_entries=limit)
    )


def _fixture(root: Path) -> str:
    filename = "Robots e Imperio - Isaac Asimov.epub"
    nested = root / "Robots e Imperio (15050)"
    nested.mkdir()
    (root / filename).write_bytes(b"diagnostic-root")
    (nested / filename).write_bytes(b"diagnostic-nested")
    return f"{nested.name}/{filename}"


def test_o3_explicit_path_outside_truncated_catalogue(tmp_path: Path) -> None:
    relative = _fixture(tmp_path)
    owner = _owner(tmp_path)
    assert owner.catalogue().truncated is True
    assert owner.search(relative, max_results=10).matches == ()

    entry = owner.lookup_explicit_relative_path(relative)

    assert entry.relative_path == relative
    assert entry.entry_id and entry.source_reference and entry.fingerprint
    assert owner.validate_selected_entry(
        entry_id=entry.entry_id,
        source_reference=entry.source_reference,
    ) == entry


def test_o3_explicit_path_does_not_scan_catalogue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relative = _fixture(tmp_path)
    owner = _owner(tmp_path)

    def forbidden_scan():
        raise AssertionError("explicit lookup must not enumerate catalogue")

    monkeypatch.setattr(owner, "_scan_entries", forbidden_scan)
    assert owner.lookup_explicit_relative_path(relative).relative_path == relative


@pytest.mark.parametrize(
    "invalid",
    ["../outside.epub", "", "Robots e Imperio - Isaac Asimov.epub"],
)
def test_o3_explicit_path_rejects_non_nested_or_invalid(
    tmp_path: Path, invalid: str
) -> None:
    _fixture(tmp_path)
    owner = _owner(tmp_path)
    with pytest.raises((ValueError, PermissionError, FileNotFoundError)):
        owner.lookup_explicit_relative_path(invalid)


def test_o3_explicit_path_rejects_disallowed_suffix(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "private.exe").write_bytes(b"not a book")
    with pytest.raises((ValueError, PermissionError, FileNotFoundError)):
        _owner(tmp_path).lookup_explicit_relative_path("folder/private.exe")


def test_o3_explicit_path_rejects_intermediate_symlink(tmp_path: Path) -> None:
    actual = tmp_path / "actual"
    actual.mkdir()
    (actual / "book.epub").write_bytes(b"test")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(actual, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    with pytest.raises((ValueError, PermissionError, FileNotFoundError)):
        _owner(tmp_path).lookup_explicit_relative_path("alias/book.epub")


def test_o3_explicit_path_rejects_stale_identity(tmp_path: Path) -> None:
    relative = _fixture(tmp_path)
    owner = _owner(tmp_path)
    entry = owner.lookup_explicit_relative_path(relative)
    (tmp_path / relative).write_bytes(b"changed-content")
    with pytest.raises(ValueError):
        owner.validate_selected_entry(
            entry_id=entry.entry_id,
            source_reference=entry.source_reference,
        )
