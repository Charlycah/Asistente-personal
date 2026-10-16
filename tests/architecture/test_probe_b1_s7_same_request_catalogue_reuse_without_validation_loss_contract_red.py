from __future__ import annotations

from pathlib import Path

import pytest

from app.document_reading import DocumentReadingService
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.governed_local_library.handoff import (
    GovernedLibrarySelection,
    GovernedLocalDocumentRetrievalRequest,
    GovernedLocalDocumentRetrieverV1,
)
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep
from core.knowledge_source_policy import KnowledgeSourceKind


def _library(root: Path) -> GovernedLocalLibraryCatalogueV1:
    return GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=root, max_catalogue_entries=100)
    )


def _step(query: str) -> KnowledgeRetrievalStep:
    return KnowledgeRetrievalStep(
        source=KnowledgeSourceKind.LOCAL_DOCUMENTS,
        priority=1,
        required=True,
        query=query,
    )


def _selection(result, *, source_reference: str | None = None):
    entry = result.matches[0]
    return GovernedLibrarySelection(
        query=result.query,
        entry_id=entry.entry_id,
        source_reference=source_reference or entry.source_reference,
        catalogue_fingerprint=result.catalogue_fingerprint,
    )


def _request(query: str, selection: GovernedLibrarySelection):
    return GovernedLocalDocumentRetrievalRequest(
        step=_step(query),
        selection=selection,
    )


def _retriever(library: GovernedLocalLibraryCatalogueV1):
    return GovernedLocalDocumentRetrieverV1(
        library=library,
        document_reader=DocumentReadingService(),
    )


def _count_catalogues(library: GovernedLocalLibraryCatalogueV1):
    original = library.catalogue
    calls = 0

    def counted_catalogue():
        nonlocal calls
        calls += 1
        return original()

    library.catalogue = counted_catalogue  # type: ignore[method-assign]
    return lambda: calls


def test_b1_s7_valid_same_request_selection_does_not_recatalogue(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "Robots e Imperio.txt").write_text("contenido", encoding="utf-8")
    library = _library(root)
    catalogue_calls = _count_catalogues(library)

    result = library.search("Robots e Imperio", max_results=10)
    artifact = _retriever(library).retrieve_selected(
        _request(result.query, _selection(result))
    )

    assert artifact.content == "contenido"
    assert catalogue_calls() == 1


def test_b1_s7_same_request_reuse_still_rejects_stale_selected_entry(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    book = root / "Robots e Imperio.txt"
    book.write_text("contenido", encoding="utf-8")
    library = _library(root)
    catalogue_calls = _count_catalogues(library)
    result = library.search("Robots e Imperio", max_results=10)
    selection = _selection(result)

    book.write_text("contenido cambiado", encoding="utf-8")

    with pytest.raises(ValueError):
        _retriever(library).retrieve_selected(_request(result.query, selection))
    assert catalogue_calls() == 1


def test_b1_s7_same_request_reuse_still_rejects_provenance_mismatch(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    (root / "Robots e Imperio.txt").write_text("contenido", encoding="utf-8")
    library = _library(root)
    catalogue_calls = _count_catalogues(library)
    result = library.search("Robots e Imperio", max_results=10)
    selection = _selection(
        result,
        source_reference="local-library:wrong:Robots e Imperio.txt",
    )

    with pytest.raises(ValueError):
        _retriever(library).retrieve_selected(_request(result.query, selection))
    assert catalogue_calls() == 1
