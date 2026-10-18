"""R-CAP17-O1: narrow contractual characterization of observed library lookup."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from app.governed_local_library_conversation import (
    GovernedLocalLibraryConversationResult,
    GovernedLocalLibraryConversationStatus,
)
from app.governed_local_library_runtime_wiring import (
    GovernedLocalLibraryConversationInterceptionPort,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)


def test_cap17_o1_nested_epub_exact_name_is_searchable(tmp_path: Path) -> None:
    """Existing behavior: EPUB nested in a named folder remains discoverable."""
    folder = tmp_path / "Robots e Imperio (15050)"
    folder.mkdir()
    (folder / "Robots e Imperio - Isaac Asimov.epub").write_bytes(b"fixture")
    library = GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=tmp_path)
    )

    by_folder = library.search("Robots e Imperio (15050)", max_results=5)
    by_filename = library.search(
        "Robots e Imperio - Isaac Asimov.epub", max_results=5
    )

    assert len(by_folder.matches) == 1
    assert len(by_filename.matches) == 1
    assert by_folder.matches[0].entry_id == by_filename.matches[0].entry_id


def test_cap17_o1_truncated_no_match_is_not_reported_as_exhaustive(
    tmp_path: Path,
) -> None:
    """RED: a partial scan must not yield an unqualified definitive no-match."""
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "z.txt").write_text("z", encoding="utf-8")
    library = GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=tmp_path, max_catalogue_entries=1)
    )
    search = library.search("z.txt", max_results=5)
    assert not search.matches
    assert search.bounded is True

    class _StubKnowledge:
        @staticmethod
        def assess(_text):
            return SimpleNamespace(
                need=SimpleNamespace(local_documents_available=True)
            )

    class _StubConversation:
        knowledge_runtime = _StubKnowledge()

        @staticmethod
        def locate_admitted_request(*, owner, search_query, now):
            assert search_query == "z.txt"
            return GovernedLocalLibraryConversationResult(
                status=GovernedLocalLibraryConversationStatus.NO_MATCH,
                query=search_query,
                bounded=search.bounded,
            )

    interceptor = GovernedLocalLibraryConversationInterceptionPort(
        _StubConversation()
    )
    request = SimpleNamespace(
        text="Buscá en mi Biblioteca z.txt",
        session_id="o1-test",
        owner="owner",
    )
    response = interceptor.intercept(request, now=datetime.now(timezone.utc))
    assert response is not None
    assert "No encontré coincidencias" not in response.response_text
    response_lower = response.response_text.casefold()
    assert "incomplet" in response_lower or "límite" in response_lower


def test_cap17_o1_compound_query_keeps_book_title_only() -> None:
    """RED: the question about the document must not become the filename query."""
    query = (
        "Buscá en mi Biblioteca el documento Robots e Imperio "
        "y decime qué información contiene sobre Robots e inteligencia artificial, "
        "indicando la fuente consultada."
    )
    extracted = GovernedLocalLibraryConversationInterceptionPort._search_query(
        query
    )
    assert extracted == "Robots e Imperio"
