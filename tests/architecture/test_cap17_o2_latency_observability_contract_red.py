"""R-CAP17-O2 RED: causal latency evidence on existing CAP-17 boundaries.

No production modifications, timers, filesystem writes or network operations.
"""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path

from app.governed_local_library_conversation import (
    GovernedLocalLibraryConversationResult,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.governed_local_library.models import GovernedLibrarySearchResult


def test_cap17_o2_existing_nested_epub_lookup_remains_available(tmp_path: Path) -> None:
    """Characterization: O2 must not replace the canonical search authority."""
    nested = tmp_path / "Robots e Imperio (15050)"
    nested.mkdir()
    (nested / "Robots e Imperio - Isaac Asimov.epub").write_bytes(b"fixture")
    library = GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=tmp_path)
    )
    found = library.search("Robots e Imperio - Isaac Asimov.epub", max_results=5)
    assert len(found.matches) == 1
    assert found.matches[0].relative_path.startswith("Robots e Imperio (15050)/")


def test_cap17_o2_search_exposes_scan_and_match_durations() -> None:
    """RED: the search boundary must expose distinct monotonic stage durations."""
    names = {field.name for field in fields(GovernedLibrarySearchResult)}
    assert {"catalogue_scan_elapsed_ms", "matching_elapsed_ms"} <= names, (
        "O2 RED: search result has no distinct catalogue/matching timing evidence"
    )


def test_cap17_o2_conversation_exposes_last_stage_and_elapsed_evidence() -> None:
    """RED: expose the last reached phase and elapsed times without lateral state."""
    names = {field.name for field in fields(GovernedLocalLibraryConversationResult)}
    assert {"last_completed_stage", "stage_elapsed_ms"} <= names, (
        "O2 RED: conversational result has no per-request causal stage evidence"
    )
