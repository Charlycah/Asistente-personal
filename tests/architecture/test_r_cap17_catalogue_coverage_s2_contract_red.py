"""R-CAP17-CATALOGUE-COVERAGE-S2: title extraction and bounded evidence.

Contract-only tests. All catalogue fixtures use tmp_path, never D:\\Biblioteca.
"""

from __future__ import annotations

import pytest

from app.governed_local_library_runtime_wiring import (
    GovernedLocalLibraryConversationInterceptionPort,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)


@pytest.mark.parametrize(
    ("utterance", "expected"),
    [
        (
            "Roby, buscá en mi biblioteca el libro Robots e Imperio.",
            "Robots e Imperio",
        ),
        (
            "Buscá en mi biblioteca el libro Robots e Imperio?",
            "Robots e Imperio",
        ),
        (
            "Buscá en mi biblioteca Robots e Imperio",
            "Robots e Imperio",
        ),
        (
            'Buscá en mi biblioteca "Robots e Imperio".',
            "Robots e Imperio",
        ),
        (
            "Buscá en mi biblioteca el documento Robots e Imperio "
            "y decime qué información contiene.",
            "Robots e Imperio",
        ),
    ],
)
def test_explicit_library_search_extracts_only_title(utterance, expected):
    extracted = GovernedLocalLibraryConversationInterceptionPort._search_query(
        utterance
    )
    assert extracted == expected


def test_positive_match_is_preserved_even_when_catalogue_is_bounded(tmp_path):
    (tmp_path / "a - Robots e Imperio - Isaac Asimov.epub").write_bytes(
        b"fixture"
    )
    (tmp_path / "z - Other book.epub").write_bytes(b"fixture")
    library = GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=tmp_path, max_catalogue_entries=1)
    )

    result = library.search("Robots e Imperio", max_results=5)
    assert result.bounded is True
    assert len(result.matches) == 1
    assert "Robots e Imperio" in result.matches[0].relative_path


def test_bounded_no_match_is_not_exhaustive(tmp_path):
    (tmp_path / "a - Other book.epub").write_bytes(b"fixture")
    (tmp_path / "z - Robots e Imperio.epub").write_bytes(b"fixture")
    library = GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=tmp_path, max_catalogue_entries=1)
    )

    result = library.search("Robots e Imperio", max_results=5)
    assert result.bounded is True
    assert not result.matches
