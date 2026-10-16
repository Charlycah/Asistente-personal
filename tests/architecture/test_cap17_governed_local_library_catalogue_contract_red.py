from __future__ import annotations

import importlib
from pathlib import Path

import pytest

MODULE = "core.governed_local_library"


def _library_api():
    module = importlib.import_module(MODULE)
    return (
        module.GovernedLocalLibraryConfig,
        module.GovernedLocalLibraryCatalogueV1,
    )


def _owner(tmp_path: Path, **overrides):
    config_type, owner_type = _library_api()
    values = {
        "root": tmp_path,
        "max_catalogue_entries": 100,
        "allowed_suffixes": (".txt", ".pdf", ".docx"),
        "follow_symlinks": False,
    }
    values.update(overrides)
    return owner_type(config_type(**values))


def test_cap17_catalogues_only_the_authorized_root(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "inside.txt").write_text("inside", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")

    catalogue = _owner(root).catalogue()

    assert [entry.relative_path for entry in catalogue.entries] == ["inside.txt"]
    assert all(
        str(outside) not in entry.source_reference
        for entry in catalogue.entries
    )


def test_cap17_catalogue_is_read_only(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    book = root / "book.txt"
    book.write_text("original", encoding="utf-8")
    before = book.read_bytes()

    _owner(root).catalogue()

    assert book.read_bytes() == before
    assert sorted(path.name for path in root.iterdir()) == ["book.txt"]


def test_cap17_rejects_root_escape(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    owner = _owner(root)

    with pytest.raises((ValueError, PermissionError)):
        owner.resolve_entry(Path("..") / "outside.txt")


def test_cap17_does_not_follow_external_symlink(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret", encoding="utf-8")
    link = root / "external"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is unavailable on this platform.")

    catalogue = _owner(root).catalogue()

    assert all("secret.txt" not in entry.relative_path for entry in catalogue.entries)


def test_cap17_produces_deterministic_entry_identity(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "book.txt").write_text("book", encoding="utf-8")
    owner = _owner(root)

    first = owner.catalogue()
    second = owner.catalogue()

    assert first.entries[0].entry_id == second.entries[0].entry_id
    assert first.catalogue_fingerprint == second.catalogue_fingerprint


def test_cap17_preserves_relative_path_and_provenance(tmp_path: Path) -> None:
    root = tmp_path / "library"
    nested = root / "Astronomia"
    nested.mkdir(parents=True)
    (nested / "estrellas.pdf").write_bytes(b"not-read-by-catalogue")

    entry = _owner(root).catalogue().entries[0]

    assert entry.relative_path == "Astronomia/estrellas.pdf"
    assert entry.source_reference
    assert entry.entry_id


def test_cap17_catalogue_is_bounded_and_reports_truncation(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    for index in range(5):
        (root / f"book-{index}.txt").write_text("x", encoding="utf-8")

    catalogue = _owner(root, max_catalogue_entries=2).catalogue()

    assert len(catalogue.entries) == 2
    assert catalogue.truncated is True
    assert catalogue.scanned_entry_count >= 2


def test_cap17_search_is_deterministic_and_bounded(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    for name in ("astronomia-a.txt", "astronomia-b.txt", "astronomia-c.txt"):
        (root / name).write_text(name, encoding="utf-8")
    owner = _owner(root)

    first = owner.search("astronomia", max_results=2)
    second = owner.search("astronomia", max_results=2)

    assert len(first.matches) == 2
    assert first.matches == second.matches
    assert first.bounded is True


def test_cap17_catalogue_does_not_read_document_contents(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "book.txt").write_text("content", encoding="utf-8")

    def forbidden_read(*args, **kwargs):
        raise AssertionError("CAP-17 catalogue must not read book contents.")

    monkeypatch.setattr(Path, "read_text", forbidden_read)
    monkeypatch.setattr(Path, "read_bytes", forbidden_read)

    catalogue = _owner(root).catalogue()

    assert len(catalogue.entries) == 1


def test_cap17_has_no_memory_or_learning_side_effects(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "book.txt").write_text("content", encoding="utf-8")
    owner = _owner(root)

    catalogue = owner.catalogue()
    result = owner.search("book", max_results=1)

    assert catalogue.entries
    assert result.matches
    assert not hasattr(owner, "learn")
    assert not hasattr(owner, "remember")
    assert not hasattr(owner, "admit_knowledge")


def test_cap17_keeps_existing_document_reader_as_content_owner(
    tmp_path: Path,
) -> None:
    from app.document_reading import DocumentReadingService

    root = tmp_path / "library"
    root.mkdir()
    book = root / "book.txt"
    book.write_text("grounded content", encoding="utf-8")

    entry = _owner(root).catalogue().entries[0]

    assert not hasattr(entry, "content")
    assert DocumentReadingService().read_text(book) == "grounded content"


def test_cap17_does_not_hardcode_or_modify_roby_config(tmp_path: Path) -> None:
    config_path = Path(".roby/config.json")
    before = config_path.read_bytes() if config_path.exists() else None
    root = tmp_path / "library"
    root.mkdir()

    owner = _owner(root)
    owner.catalogue()

    after = config_path.read_bytes() if config_path.exists() else None
    assert after == before
    owner_root = Path(owner.config.root)
    assert owner_root.resolve() == root.resolve()
