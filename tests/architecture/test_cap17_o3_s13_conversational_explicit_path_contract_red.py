"""R-CAP17-O3-S13: intentional RED for governed conversational explicit paths.

Only temporary text fixtures; no changes to production, real library, or M377.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.governed_local_library_conversation import (
    GovernedLocalLibraryConversationV1,
)
from app.governed_local_library_runtime_wiring import (
    GovernedLocalLibraryConversationInterceptionPort,
)
from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from app.unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)

NOW = datetime(2026, 10, 11, 20, 0, tzinfo=timezone.utc)
RELATIVE = "Robots e Imperio (15050)/Robots e Imperio - Isaac Asimov.txt"


class Reader:
    def __init__(self) -> None:
        self.calls: list[Path] = []

    def read_text(self, path: Path) -> str:
        self.calls.append(path)
        return path.read_text(encoding="utf-8")


def _setup(tmp_path: Path):
    root = tmp_path / "library"
    nested = root / "Robots e Imperio (15050)"
    nested.mkdir(parents=True)
    (root / "Robots e Imperio - Isaac Asimov.txt").write_text(
        "root copy", encoding="utf-8"
    )
    (nested / "Robots e Imperio - Isaac Asimov.txt").write_text(
        "nested copy", encoding="utf-8"
    )
    library = GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(
            root=root, allowed_suffixes=(".txt",), max_catalogue_entries=1
        )
    )
    reader = Reader()
    runtime = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    conversation = GovernedLocalLibraryConversationV1(
        knowledge_runtime=OfficialKnowledgeRuntimeGateway(),
        library=library,
        document_reader=reader,
        unified_runtime=runtime,
    )
    return conversation, library, reader, runtime


def test_o3_s13_explicit_path_reaches_nested_document_with_truncated_catalogue(
    tmp_path: Path,
) -> None:
    conversation, library, reader, _ = _setup(tmp_path)
    assert library.catalogue().truncated
    result = conversation.handle_user_request(
        owner="Owner",
        text=f'Buscá en la biblioteca "{RELATIVE}"',
        search_query=RELATIVE,
        now=NOW,
    )
    assert result.status.value == "completed"
    assert result.artifact is not None
    assert result.artifact.content == "nested copy"
    assert len(reader.calls) == 1
    assert reader.calls[0] == library.resolve_entry(RELATIVE)


def test_o3_s13_explicit_path_never_enumerates_catalogue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    conversation, library, reader, _ = _setup(tmp_path)

    def forbidden_scan():
        raise AssertionError("explicit path must not enumerate catalogue")

    monkeypatch.setattr(library, "_scan_entries", forbidden_scan)
    result = conversation.handle_admitted_request(
        owner="Owner", search_query=RELATIVE, now=NOW
    )
    assert result.status.value == "completed"
    assert len(reader.calls) == 1


def test_o3_s13_explicit_path_preserves_real_provenance_and_safe_label(
    tmp_path: Path,
) -> None:
    conversation, library, _, _ = _setup(tmp_path)
    entry = library.lookup_explicit_relative_path(RELATIVE)
    result = conversation.handle_admitted_request(
        owner="Owner", search_query=RELATIVE, now=NOW
    )
    assert result.status.value == "completed"
    assert result.source_reference == entry.source_reference
    assert result.artifact is not None
    assert entry.source_reference in result.artifact.references
    assert result.safe_source_label == entry.filename


def test_o3_s13_explicit_path_uses_existing_unified_runtime(
    tmp_path: Path,
) -> None:
    conversation, _, reader, runtime = _setup(tmp_path)
    before = runtime.snapshot.evaluations
    result = conversation.handle_admitted_request(
        owner="Owner", search_query=RELATIVE, now=NOW
    )
    assert result.status.value == "completed"
    assert runtime.snapshot.evaluations == before + 1
    assert len(reader.calls) == 1


def test_o3_s13_invalid_explicit_path_fails_closed_without_document_read(
    tmp_path: Path,
) -> None:
    conversation, _, reader, _ = _setup(tmp_path)
    with pytest.raises((ValueError, PermissionError, FileNotFoundError)):
        conversation.handle_admitted_request(
            owner="Owner", search_query="../outside.txt", now=NOW
        )
    assert reader.calls == []


def test_o3_s13_unadmitted_request_does_not_read_document(
    tmp_path: Path,
) -> None:
    conversation, _, reader, _ = _setup(tmp_path)
    with pytest.raises(ValueError):
        conversation.handle_user_request(
            owner="Owner",
            text="¿Qué hora es?",
            search_query=RELATIVE,
            now=NOW,
        )
    assert reader.calls == []


def test_o3_s13_wiring_extracts_quoted_nested_path_without_altering_query(
    tmp_path: Path,
) -> None:
    conversation, _, _, _ = _setup(tmp_path)
    port = GovernedLocalLibraryConversationInterceptionPort(conversation)
    text = f'Buscá en la biblioteca "{RELATIVE}" y decime de qué trata'
    assert port._search_query(text) == RELATIVE
