from __future__ import annotations

import importlib
import inspect
from datetime import datetime, timezone
from pathlib import Path

from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from app.unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep
from core.knowledge_source_policy import KnowledgeSourceKind

NOW = datetime(2026, 8, 31, 20, 30, tzinfo=timezone.utc)
SELECTION_MODULE = "core.governed_local_library.conversation_selection"
CONVERSATION_MODULE = "app.governed_local_library_conversation"


class Reader:
    def __init__(self) -> None:
        self.calls: list[Path] = []

    def read_text(self, path: Path) -> str:
        self.calls.append(path)
        return path.read_text(encoding="utf-8")


def _selection_api():
    module = importlib.import_module(SELECTION_MODULE)
    return (
        module.GovernedLibrarySelectionDisposition,
        module.GovernedLibraryConversationalSelectionV1,
    )


def _conversation_type():
    module = importlib.import_module(CONVERSATION_MODULE)
    return module.GovernedLocalLibraryConversationV1


def _library(root: Path) -> GovernedLocalLibraryCatalogueV1:
    root.mkdir(parents=True, exist_ok=True)
    return GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(
            root=root,
            allowed_suffixes=(".txt",),
            max_catalogue_entries=20,
        )
    )


def _conversation(root: Path, reader: Reader):
    conversation_type = _conversation_type()
    return conversation_type(
        knowledge_runtime=OfficialKnowledgeRuntimeGateway(),
        library=_library(root),
        document_reader=reader,
        unified_runtime=OfficialUnifiedRetrievalExecutionRuntimeGateway(
            OfficialExternalRetrievalRuntimeGateway()
        ),
    )


def test_cap17_biblioteca_is_classified_as_local_documents() -> None:
    assessment = OfficialKnowledgeRuntimeGateway().assess(
        "Buscá en la biblioteca algo sobre Marte"
    )
    assert assessment.need.local_documents_available is True
    assert assessment.need.preferred_sources == (KnowledgeSourceKind.LOCAL_DOCUMENTS,)


def test_cap17_mis_libros_is_classified_as_local_documents() -> None:
    assessment = OfficialKnowledgeRuntimeGateway().assess(
        "Fijate en mis libros si hay algo sobre Asimov"
    )
    assert assessment.need.local_documents_available is True
    assert assessment.need.preferred_sources == (KnowledgeSourceKind.LOCAL_DOCUMENTS,)


def test_cap17_library_request_does_not_fall_through_to_web() -> None:
    assessment = OfficialKnowledgeRuntimeGateway().assess(
        "Buscá en la biblioteca termodinámica"
    )
    assert assessment.need.explicit_external_request is False
    assert assessment.need.preferred_sources == (KnowledgeSourceKind.LOCAL_DOCUMENTS,)


def test_cap17_zero_matches_produces_no_match_without_reading(tmp_path: Path) -> None:
    disposition, selector_type = _selection_api()
    library = _library(tmp_path / "library")
    result = selector_type().decide(library.search("atlas", max_results=5))
    assert result.disposition is disposition.NO_MATCH
    assert result.selection is None
    assert result.candidates == ()


def test_cap17_one_match_produces_explicit_selection(tmp_path: Path) -> None:
    disposition, selector_type = _selection_api()
    root = tmp_path / "library"
    library = _library(root)
    (root / "atlas.txt").write_text("Atlas content", encoding="utf-8")
    search = library.search("atlas", max_results=5)
    result = selector_type().decide(search)
    assert result.disposition is disposition.SELECTED
    assert result.selection is not None
    assert result.selection.entry_id == search.matches[0].entry_id
    assert result.selection.source_reference == search.matches[0].source_reference
    assert result.selection.catalogue_fingerprint == search.catalogue_fingerprint


def test_cap17_multiple_matches_require_disambiguation(tmp_path: Path) -> None:
    disposition, selector_type = _selection_api()
    root = tmp_path / "library"
    library = _library(root)
    (root / "atlas_alpha.txt").write_text("A", encoding="utf-8")
    (root / "atlas_beta.txt").write_text("B", encoding="utf-8")
    result = selector_type().decide(library.search("atlas", max_results=5))
    assert result.disposition is disposition.NEEDS_DISAMBIGUATION
    assert result.selection is None
    assert len(result.candidates) == 2


def test_cap17_multiple_matches_never_choose_first_implicitly(tmp_path: Path) -> None:
    _, selector_type = _selection_api()
    root = tmp_path / "library"
    library = _library(root)
    (root / "atlas_alpha.txt").write_text("A", encoding="utf-8")
    (root / "atlas_beta.txt").write_text("B", encoding="utf-8")
    search = library.search("atlas", max_results=5)
    result = selector_type().decide(search)
    assert result.selection is None
    assert all(candidate.entry_id != "" for candidate in result.candidates)


def test_cap17_disambiguation_candidates_remain_bounded(tmp_path: Path) -> None:
    disposition, selector_type = _selection_api()
    root = tmp_path / "library"
    library = _library(root)
    for index in range(6):
        (root / f"atlas_{index}.txt").write_text(str(index), encoding="utf-8")
    search = library.search("atlas", max_results=3)
    result = selector_type().decide(search)
    assert result.disposition is disposition.NEEDS_DISAMBIGUATION
    assert len(result.candidates) == 3
    assert result.bounded is True


def test_cap17_unique_user_request_uses_certified_handoff_and_binding(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    reader = Reader()
    conversation = _conversation(root, reader)
    (root / "atlas.txt").write_text("Grounded Atlas", encoding="utf-8")
    result = conversation.handle_user_request(
        owner="Carlos",
        text="Buscá en la biblioteca atlas",
        search_query="atlas",
        now=NOW,
    )
    assert result.status.value == "completed"
    assert len(reader.calls) == 1


def test_cap17_unique_user_request_enters_existing_unified_runtime(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    reader = Reader()
    conversation = _conversation(root, reader)
    (root / "atlas.txt").write_text("Grounded Atlas", encoding="utf-8")
    before = conversation.unified_runtime.snapshot.evaluations
    conversation.handle_user_request(
        owner="Carlos",
        text="Consultá la biblioteca atlas",
        search_query="atlas",
        now=NOW,
    )
    assert conversation.unified_runtime.snapshot.evaluations == before + 1


def test_cap17_provenance_survives_to_conversational_result(tmp_path: Path) -> None:
    root = tmp_path / "library"
    reader = Reader()
    conversation = _conversation(root, reader)
    (root / "atlas.txt").write_text("Grounded Atlas", encoding="utf-8")
    result = conversation.handle_user_request(
        owner="Carlos",
        text="Revisá la biblioteca atlas",
        search_query="atlas",
        now=NOW,
    )
    assert result.artifact is not None
    assert result.source_reference in result.artifact.references


def test_cap17_ambiguity_performs_zero_document_reads(tmp_path: Path) -> None:
    root = tmp_path / "library"
    reader = Reader()
    conversation = _conversation(root, reader)
    (root / "atlas_alpha.txt").write_text("A", encoding="utf-8")
    (root / "atlas_beta.txt").write_text("B", encoding="utf-8")
    result = conversation.handle_user_request(
        owner="Carlos",
        text="Buscá en la biblioteca atlas",
        search_query="atlas",
        now=NOW,
    )
    assert result.status.value == "needs_disambiguation"
    assert reader.calls == []


def test_cap17_conversational_access_exposes_no_memory_or_learning_actions() -> None:
    conversation_type = _conversation_type()
    public = {
        name.casefold() for name in dir(conversation_type) if not name.startswith("_")
    }
    assert "remember" not in public
    assert "learn" not in public
    assert "admit" not in public
    assert "persist" not in public


def test_cap17_conversational_access_does_not_change_retrieval_step_schema() -> None:
    _conversation_type()
    fields = tuple(inspect.signature(KnowledgeRetrievalStep).parameters)
    assert fields == ("source", "priority", "required", "query", "step_id")


def test_cap17_conversational_access_does_not_modify_roby_config(
    tmp_path: Path,
) -> None:
    config = Path(".roby/config.json")
    before = config.read_bytes() if config.exists() else None
    reader = Reader()
    conversation = _conversation(tmp_path / "library", reader)
    result = conversation.handle_user_request(
        owner="Carlos",
        text="Buscá en la biblioteca atlas",
        search_query="atlas",
        now=NOW,
    )
    assert result.status.value == "no_match"
    after = config.read_bytes() if config.exists() else None
    assert after == before
