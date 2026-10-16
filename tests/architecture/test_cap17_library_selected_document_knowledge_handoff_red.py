from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from app.document_reading import DocumentReadingService
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.knowledge_retrieval_execution import (
    KnowledgeRetrievalArtifact,
    KnowledgeRetriever,
)
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep
from core.knowledge_source_policy import KnowledgeSourceKind

MODULE = "core.governed_local_library.handoff"


def _handoff_api():
    module = importlib.import_module(MODULE)
    return (
        module.GovernedLibrarySelection,
        module.GovernedLocalDocumentRetrievalRequest,
        module.GovernedLocalDocumentRetrieverV1,
    )


def _library(root: Path, *, suffixes=(".txt", ".md", ".pdf", ".docx")):
    return GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(
            root=root,
            max_catalogue_entries=100,
            allowed_suffixes=suffixes,
            follow_symlinks=False,
        )
    )


def _step(query: str = "astronomia") -> KnowledgeRetrievalStep:
    return KnowledgeRetrievalStep(
        source=KnowledgeSourceKind.LOCAL_DOCUMENTS,
        priority=1,
        required=True,
        query=query,
    )


def _selection(result, entry):
    selection_type, _, _ = _handoff_api()
    return selection_type(
        query=result.query,
        entry_id=entry.entry_id,
        source_reference=entry.source_reference,
        catalogue_fingerprint=result.catalogue_fingerprint,
    )


def _request(step, selection):
    _, request_type, _ = _handoff_api()
    return request_type(step=step, selection=selection)


def _retriever(library, *, reader=None):
    _, _, retriever_type = _handoff_api()
    return retriever_type(
        library=library,
        document_reader=reader or DocumentReadingService(),
    )


def test_cap17_multiple_matches_are_not_auto_selected(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "astronomia-a.txt").write_text("A", encoding="utf-8")
    (root / "astronomia-b.txt").write_text("B", encoding="utf-8")
    library = _library(root)
    result = library.search("astronomia", max_results=10)
    retriever = _retriever(library)

    assert len(result.matches) == 2
    assert not isinstance(retriever, KnowledgeRetriever)
    assert not hasattr(retriever, "retrieve")


def test_cap17_explicit_selection_preserves_entry_identity(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    result = _library(root).search("atlas", max_results=10)
    entry = result.matches[0]

    selection = _selection(result, entry)

    assert selection.entry_id == entry.entry_id
    assert selection.source_reference == entry.source_reference
    assert selection.catalogue_fingerprint == result.catalogue_fingerprint


def test_cap17_selection_rejects_unknown_entry_id(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("atlas", max_results=10)
    selection_type, _, _ = _handoff_api()
    selection = selection_type(
        query=result.query,
        entry_id="unknown-entry",
        source_reference=result.matches[0].source_reference,
        catalogue_fingerprint=result.catalogue_fingerprint,
    )

    with pytest.raises(ValueError):
        _retriever(library).retrieve_selected(_request(_step("atlas"), selection))


def test_cap17_selection_rejects_stale_catalogue_fingerprint(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    book = root / "atlas.txt"
    book.write_text("Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("atlas", max_results=10)
    entry = result.matches[0]
    selection = _selection(result, entry)
    book.write_text("Atlas changed", encoding="utf-8")

    with pytest.raises(ValueError):
        _retriever(library).retrieve_selected(_request(_step("atlas"), selection))


def test_cap17_selection_rejects_source_reference_mismatch(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("atlas", max_results=10)
    entry = result.matches[0]
    selection_type, _, _ = _handoff_api()
    selection = selection_type(
        query=result.query,
        entry_id=entry.entry_id,
        source_reference="local-library:wrong:outside.txt",
        catalogue_fingerprint=result.catalogue_fingerprint,
    )

    with pytest.raises(ValueError):
        _retriever(library).retrieve_selected(_request(_step("atlas"), selection))


def test_cap17_selected_entry_resolves_through_library_owner(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    book = root / "atlas.txt"
    book.write_text("Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("atlas", max_results=10)
    selection = _selection(result, result.matches[0])

    artifact = _retriever(library).retrieve_selected(
        _request(_step("atlas"), selection)
    )

    assert artifact.content == "Atlas"
    assert library.resolve_entry(result.matches[0].relative_path) == book.resolve()


def test_cap17_content_is_read_through_existing_document_reader(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Grounded Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("atlas", max_results=10)
    selection = _selection(result, result.matches[0])

    class SpyReader(DocumentReadingService):
        def __init__(self) -> None:
            self.calls: list[Path] = []

        def read_text(self, path: Path) -> str:
            self.calls.append(path)
            return super().read_text(path)

    reader = SpyReader()
    artifact = _retriever(library, reader=reader).retrieve_selected(
        _request(_step("atlas"), selection)
    )

    assert artifact.content == "Grounded Atlas"
    assert len(reader.calls) == 1


def test_cap17_handoff_returns_canonical_local_documents_artifact(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("atlas", max_results=10)
    selection = _selection(result, result.matches[0])

    artifact = _retriever(library).retrieve_selected(
        _request(_step("atlas"), selection)
    )

    assert type(artifact) is KnowledgeRetrievalArtifact
    assert artifact.source is KnowledgeSourceKind.LOCAL_DOCUMENTS


def test_cap17_artifact_preserves_original_query(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    library = _library(root)
    query = "atlas"
    result = library.search(query, max_results=10)
    selection = _selection(result, result.matches[0])

    artifact = _retriever(library).retrieve_selected(
        _request(_step(query), selection)
    )

    assert artifact.query == query


def test_cap17_artifact_preserves_exact_library_provenance(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("atlas", max_results=10)
    entry = result.matches[0]
    selection = _selection(result, entry)

    artifact = _retriever(library).retrieve_selected(
        _request(_step("atlas"), selection)
    )

    assert artifact.references == (entry.source_reference,)


def test_cap17_handoff_does_not_mutate_library(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    book = root / "atlas.txt"
    book.write_text("Atlas", encoding="utf-8")
    before = book.read_bytes()
    library = _library(root)
    result = library.search("atlas", max_results=10)
    selection = _selection(result, result.matches[0])

    _retriever(library).retrieve_selected(_request(_step("atlas"), selection))

    assert book.read_bytes() == before
    assert sorted(item.name for item in root.iterdir()) == ["atlas.txt"]


def test_cap17_handoff_exposes_no_memory_or_learning_actions(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    retriever = _retriever(_library(root))

    assert not hasattr(retriever, "remember")
    assert not hasattr(retriever, "learn")
    assert not hasattr(retriever, "admit_knowledge")


def test_cap17_unsupported_document_format_fails_governedly(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "book.mobi").write_bytes(b"mobi")
    library = _library(root, suffixes=(".mobi",))
    result = library.search("book", max_results=10)
    selection = _selection(result, result.matches[0])

    with pytest.raises(ValueError, match="Formato no compatible"):
        _retriever(library).retrieve_selected(_request(_step("book"), selection))


def test_cap17_oversized_document_fails_governedly(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "large.txt").write_bytes(b"x" * 2_000_001)
    library = _library(root)
    result = library.search("large", max_results=10)
    selection = _selection(result, result.matches[0])

    with pytest.raises(ValueError, match="2 MB"):
        _retriever(library).retrieve_selected(_request(_step("large"), selection))


def test_cap17_zero_matches_produce_no_acquisition(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("quimica", max_results=10)
    retriever = _retriever(library)

    assert result.matches == ()
    assert not hasattr(retriever, "retrieve")


def test_cap17_selection_query_must_match_retrieval_step(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("atlas", max_results=10)
    selection = _selection(result, result.matches[0])

    with pytest.raises(ValueError):
        _retriever(library).retrieve_selected(_request(_step("mapas"), selection))


def test_cap17_handoff_does_not_modify_roby_config(tmp_path: Path) -> None:
    config_path = Path(".roby/config.json")
    before = config_path.read_bytes() if config_path.exists() else None
    root = tmp_path / "library"
    root.mkdir()
    (root / "atlas.txt").write_text("Atlas", encoding="utf-8")
    library = _library(root)
    result = library.search("atlas", max_results=10)
    selection = _selection(result, result.matches[0])

    _retriever(library).retrieve_selected(_request(_step("atlas"), selection))

    after = config_path.read_bytes() if config_path.exists() else None
    assert after == before
