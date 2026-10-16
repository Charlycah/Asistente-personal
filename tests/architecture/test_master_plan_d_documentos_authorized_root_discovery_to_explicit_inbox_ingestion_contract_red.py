from __future__ import annotations

import inspect
import os
from pathlib import Path

import pytest

from app.document_reading import DocumentReadingService
from core.document_inbox import DocumentInboxManager, DocumentRecord


def _source_api():
    from app.personal_document_source import (
        PersonalDocumentRootDiscoveryAdapter,
        build_personal_document_source_from_environment,
    )

    return (
        PersonalDocumentRootDiscoveryAdapter,
        build_personal_document_source_from_environment,
    )


class RecordingReader(DocumentReadingService):
    def __init__(self) -> None:
        self.paths: list[Path] = []

    def read_text(self, path: Path) -> str:
        self.paths.append(Path(path))
        return "contenido gobernado"


class RecordingInbox(DocumentInboxManager):
    def __init__(self) -> None:
        super().__init__()
        self.ingest_text_calls: list[dict[str, object]] = []

    def ingest_text(self, content: str, **kwargs) -> DocumentRecord:
        self.ingest_text_calls.append({"content": content, **kwargs})
        return super().ingest_text(content, **kwargs)


def _adapter(
    root: Path,
    *,
    max_candidates: int = 100,
    reader: DocumentReadingService | None = None,
    inbox: DocumentInboxManager | None = None,
):
    adapter_type, _ = _source_api()
    return adapter_type(
        root=root,
        max_candidates=max_candidates,
        reader=reader or RecordingReader(),
        document_inbox=inbox or RecordingInbox(),
    )


def test_red_1_source_adapter_and_environment_builder_exist():
    adapter_type, builder = _source_api()

    assert inspect.isclass(adapter_type)
    assert callable(builder)


def test_red_2_environment_builder_requires_explicit_source_root(
    tmp_path: Path,
    monkeypatch,
):
    _, builder = _source_api()
    monkeypatch.delenv("ROBY_PERSONAL_DOCUMENTS_ROOT", raising=False)
    inbox = RecordingInbox()

    assert builder(document_inbox=inbox, reader=RecordingReader()) is None

    monkeypatch.setenv("ROBY_PERSONAL_DOCUMENTS_ROOT", str(tmp_path))
    adapter = builder(document_inbox=inbox, reader=RecordingReader())

    assert adapter is not None
    assert Path(adapter.root) == tmp_path.resolve()


def test_red_3_discovery_is_bounded_filtered_and_deterministic(tmp_path: Path):
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "ignored.py").write_text("x", encoding="utf-8")
    (tmp_path / "ignored.log").write_text("x", encoding="utf-8")
    (tmp_path / "c.pdf").write_bytes(b"%PDF")
    adapter = _adapter(tmp_path, max_candidates=2)

    first = adapter.discover()
    second = adapter.discover()

    assert first.truncated is True
    assert [item.relative_path for item in first.candidates] == ["a.txt", "b.md"]
    assert first == second
    assert all(item.candidate_id for item in first.candidates)
    assert all(
        not item.source_reference.startswith("local-library:")
        for item in first.candidates
    )


def test_red_4_candidate_preserves_relative_path_and_source_provenance(
    tmp_path: Path,
):
    nested = tmp_path / "nested"
    nested.mkdir()
    source = nested / "note.txt"
    source.write_text("hello", encoding="utf-8")
    adapter = _adapter(tmp_path)

    result = adapter.discover()
    candidate = result.candidates[0]

    assert candidate.relative_path == "nested/note.txt"
    assert candidate.suffix == ".txt"
    assert candidate.size_bytes == source.stat().st_size
    assert candidate.modified_ns == source.stat().st_mtime_ns
    assert candidate.source_reference
    assert "nested/note.txt" in candidate.source_reference
    assert "local-library:" not in candidate.source_reference


def test_red_5_discovery_does_not_ingest(tmp_path: Path):
    (tmp_path / "note.txt").write_text("hello", encoding="utf-8")
    inbox = RecordingInbox()
    adapter = _adapter(tmp_path, inbox=inbox)

    result = adapter.discover()

    assert result.candidates
    assert inbox.ingest_text_calls == []
    assert inbox.repository.list_all() == ()


def test_red_6_explicit_selected_candidate_uses_existing_reader_and_inbox(
    tmp_path: Path,
):
    source = tmp_path / "note.txt"
    source.write_text("hello", encoding="utf-8")
    reader = RecordingReader()
    inbox = RecordingInbox()
    adapter = _adapter(tmp_path, reader=reader, inbox=inbox)
    candidate = adapter.discover().candidates[0]

    record = adapter.ingest_selected(candidate.candidate_id)

    assert isinstance(record, DocumentRecord)
    assert reader.paths == [source.resolve()]
    assert len(inbox.ingest_text_calls) == 1
    assert inbox.ingest_text_calls[0]["content"] == "contenido gobernado"
    assert record.document_id
    assert inbox.repository.get(record.document_id) is record


def test_red_7_selected_source_is_revalidated_and_escape_fails_closed(
    tmp_path: Path,
):
    source = tmp_path / "note.txt"
    source.write_text("hello", encoding="utf-8")
    adapter = _adapter(tmp_path)
    candidate = adapter.discover().candidates[0]
    source.unlink()

    with pytest.raises((FileNotFoundError, ValueError)):
        adapter.ingest_selected(candidate.candidate_id)

    outside = tmp_path.parent / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    try:
        with pytest.raises((KeyError, ValueError)):
            adapter.ingest_selected("../outside.txt")
    finally:
        outside.unlink(missing_ok=True)


@pytest.mark.skipif(
    not hasattr(os, "symlink"),
    reason="platform does not expose symlink support",
)
def test_red_8_external_symlink_is_not_discovered_or_ingested(tmp_path: Path):
    outside = tmp_path.parent / "external.txt"
    outside.write_text("outside", encoding="utf-8")
    link = tmp_path / "linked.txt"
    try:
        try:
            link.symlink_to(outside)
        except OSError:
            pytest.skip("symlink creation unavailable on this platform")
        adapter = _adapter(tmp_path)

        result = adapter.discover()

        assert all(item.relative_path != "linked.txt" for item in result.candidates)
        with pytest.raises((KeyError, ValueError)):
            adapter.ingest_selected("linked.txt")
    finally:
        link.unlink(missing_ok=True)
        outside.unlink(missing_ok=True)


def test_red_9_supported_personal_document_suffixes_are_exact(tmp_path: Path):
    supported = (
        ".txt",
        ".md",
        ".csv",
        ".json",
        ".html",
        ".htm",
        ".docx",
        ".pdf",
        ".epub",
    )
    for index, suffix in enumerate(supported):
        (tmp_path / f"doc-{index}{suffix}").write_bytes(b"x")
    (tmp_path / "code.py").write_text("x", encoding="utf-8")
    (tmp_path / "trace.log").write_text("x", encoding="utf-8")
    adapter = _adapter(tmp_path)

    suffixes = {item.suffix for item in adapter.discover().candidates}

    assert suffixes == set(supported)


def test_guardrail_10_no_hardcoded_personal_root_or_library_identity():
    files = (
        Path("app/runtime_environment_wiring.py"),
        Path("app/runtime_root_factory.py"),
        Path("core/document_inbox.py"),
    )
    source = "\n".join(path.read_text(encoding="utf-8") for path in files)

    assert "D:\\Documentos" not in source
    assert "D:/Documentos" not in source
    assert "local-library:" not in source


def test_guardrail_11_existing_document_inbox_remains_lifecycle_authority():
    source = inspect.getsource(DocumentInboxManager)

    assert "def ingest_text(" in source
    assert "def recall(" in source
    assert "def archive(" in source
    assert "def ingest_path(" in source


def test_guardrail_12_no_automatic_downstream_cognition_or_second_inbox():
    protected = (
        Path("app/runtime_environment_wiring.py"),
        Path("app/runtime_root_factory.py"),
    )
    source = "\n".join(path.read_text(encoding="utf-8") for path in protected)

    assert "ROBY_PERSONAL_DOCUMENTS_ROOT" not in source
    assert "PersonalDocumentRootDiscoveryAdapter" not in source
