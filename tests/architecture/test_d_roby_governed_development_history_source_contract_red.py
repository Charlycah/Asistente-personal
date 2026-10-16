from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from app.document_reading import DocumentReadingService
from core.document_inbox import DocumentInboxManager, DocumentRecord

MODULE = "app.development_history_source"
ENVIRONMENT_KEY = "ROBY_DEVELOPMENT_HISTORY_ROOT"
HISTORICAL_TRUST = "HISTORICAL_DEVELOPMENT_MATERIAL"


def _source_api():
    from app.development_history_source import (
        DevelopmentHistoryRootDiscoveryAdapter,
        build_development_history_source_from_environment,
    )

    return (
        DevelopmentHistoryRootDiscoveryAdapter,
        build_development_history_source_from_environment,
    )


class RecordingReader(DocumentReadingService):
    def __init__(self) -> None:
        self.paths: list[Path] = []

    def read_text(self, path: Path) -> str:
        self.paths.append(Path(path))
        return "historical material"


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


def test_red_1_canonical_source_adapter_and_environment_builder_exist():
    adapter_type, builder = _source_api()

    assert inspect.isclass(adapter_type)
    assert callable(builder)


def test_red_2_environment_builder_requires_explicit_history_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _, builder = _source_api()
    monkeypatch.delenv(ENVIRONMENT_KEY, raising=False)
    inbox = RecordingInbox()

    assert builder(document_inbox=inbox, reader=RecordingReader()) is None

    monkeypatch.setenv(ENVIRONMENT_KEY, str(tmp_path))
    adapter = builder(document_inbox=inbox, reader=RecordingReader())

    assert adapter is not None
    assert Path(adapter.root) == tmp_path.resolve()


def test_red_3_discovery_is_bounded_deterministic_and_history_namespaced(
    tmp_path: Path,
):
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    (tmp_path / "a.py").write_text("a = 1", encoding="utf-8")
    (tmp_path / "c.log").write_text("c", encoding="utf-8")
    (tmp_path / "archive.zip").write_bytes(b"not extracted")
    adapter = _adapter(tmp_path, max_candidates=2)

    first = adapter.discover()
    second = adapter.discover()

    assert first.truncated is True
    assert [item.relative_path for item in first.candidates] == ["a.py", "b.md"]
    assert first == second
    assert all(item.candidate_id for item in first.candidates)
    assert all(
        item.source_reference.startswith("development-history:")
        for item in first.candidates
    )
    assert all(
        item.trust_classification == HISTORICAL_TRUST
        for item in first.candidates
    )


def test_red_4_candidate_preserves_relative_provenance_and_historical_trust(
    tmp_path: Path,
):
    nested = tmp_path / "certifications"
    nested.mkdir()
    source = nested / "decision.md"
    source.write_text("historical decision", encoding="utf-8")

    candidate = _adapter(tmp_path).discover().candidates[0]

    assert candidate.relative_path == "certifications/decision.md"
    assert candidate.suffix == ".md"
    assert candidate.size_bytes == source.stat().st_size
    assert candidate.modified_ns == source.stat().st_mtime_ns
    assert candidate.source_reference.startswith("development-history:")
    assert "certifications/decision.md" in candidate.source_reference
    assert candidate.trust_classification == HISTORICAL_TRUST


def test_red_5_discovery_is_read_only_and_does_not_read_or_ingest(
    tmp_path: Path,
):
    source = tmp_path / "history.txt"
    source.write_text("original", encoding="utf-8")
    before = source.read_bytes()
    reader = RecordingReader()
    inbox = RecordingInbox()

    result = _adapter(tmp_path, reader=reader, inbox=inbox).discover()

    assert result.candidates
    assert source.read_bytes() == before
    assert reader.paths == []
    assert inbox.ingest_text_calls == []
    assert inbox.repository.list_all() == ()


def test_red_6_external_symlink_is_not_discovered(tmp_path: Path):
    root = tmp_path / "history"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.md").write_text("secret", encoding="utf-8")
    link = root / "external"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is unavailable on this platform.")

    result = _adapter(root).discover()

    assert all("secret.md" not in item.relative_path for item in result.candidates)


def test_red_7_selection_revalidates_containment_and_candidate_identity(
    tmp_path: Path,
):
    source = tmp_path / "decision.md"
    source.write_text("old", encoding="utf-8")
    adapter = _adapter(tmp_path)
    candidate = adapter.discover().candidates[0]
    source.write_text("changed historical material", encoding="utf-8")

    with pytest.raises(ValueError, match="changed"):
        adapter.ingest_selected(candidate.candidate_id)


def test_red_8_explicit_selection_reuses_existing_reader_and_document_inbox(
    tmp_path: Path,
):
    source = tmp_path / "decision.md"
    source.write_text("historical decision", encoding="utf-8")
    reader = RecordingReader()
    inbox = RecordingInbox()
    adapter = _adapter(tmp_path, reader=reader, inbox=inbox)
    candidate = adapter.discover().candidates[0]

    record = adapter.ingest_selected(candidate.candidate_id)

    assert reader.paths == [source.resolve()]
    assert len(inbox.ingest_text_calls) == 1
    assert record.metadata.source_name == candidate.source_reference
    assert record.metadata.source_name.startswith("development-history:")


def test_red_9_unselected_or_unknown_candidate_cannot_be_ingested(tmp_path: Path):
    (tmp_path / "decision.md").write_text("history", encoding="utf-8")
    reader = RecordingReader()
    inbox = RecordingInbox()
    adapter = _adapter(tmp_path, reader=reader, inbox=inbox)

    with pytest.raises(KeyError):
        adapter.ingest_selected("not-a-discovered-candidate")

    assert reader.paths == []
    assert inbox.ingest_text_calls == []


def test_red_10_archives_and_arbitrary_binaries_are_not_ingestion_candidates(
    tmp_path: Path,
):
    (tmp_path / "history.zip").write_bytes(b"PK")
    (tmp_path / "program.exe").write_bytes(b"MZ")
    (tmp_path / "image.bin").write_bytes(b"binary")
    (tmp_path / "decision.md").write_text("readable", encoding="utf-8")

    adapter = _adapter(tmp_path)
    result = adapter.discover()

    assert [item.relative_path for item in result.candidates] == [
        "decision.md",
        "history.zip",
    ]
    archive = result.candidates[1]
    assert archive.source_kind.value == "opaque"
    with pytest.raises(ValueError):
        adapter.read_selected(archive.candidate_id)


def test_red_11_source_surface_has_no_cognitive_or_mutation_authority():
    adapter_type, _ = _source_api()
    public_surface = {
        name
        for name, _ in inspect.getmembers(adapter_type)
        if not name.startswith("_")
    }

    assert "discover" in public_surface
    assert "ingest_selected" in public_surface
    assert not public_surface.intersection(
        {
            "learn",
            "remember",
            "diagnose",
            "propose",
            "approve",
            "plan",
            "execute",
            "write",
            "delete",
            "rename",
            "patch",
        }
    )


def test_red_12_contract_does_not_hardcode_owner_deployment_path():
    test_source = inspect.getsource(inspect.getmodule(_source_api))

    assert "D:\\Roby" not in test_source
    assert ENVIRONMENT_KEY in test_source
