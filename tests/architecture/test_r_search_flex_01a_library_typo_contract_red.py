from __future__ import annotations

from pathlib import Path

import pytest

from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.governed_local_library.conversation_selection import (
    GovernedLibraryConversationalSelectionV1,
    GovernedLibrarySelectionDisposition,
)


def _library(
    root: Path,
    *,
    max_catalogue_entries: int = 20,
) -> GovernedLocalLibraryCatalogueV1:
    return GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(
            root=root,
            max_catalogue_entries=max_catalogue_entries,
            allowed_suffixes=(".txt", ".epub"),
            follow_symlinks=False,
        )
    )


def _book(root: Path, filename: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / filename
    path.write_text("PRIVATE_CONTENT_SENTINEL", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("query", "filename"),
    (
        ("robot", "robot.epub"),
        ("rob", "robot.epub"),
    ),
)
def test_existing_matching_precedes_typo_fallback(
    tmp_path: Path,
    query: str,
    filename: str,
) -> None:
    _book(tmp_path, filename)

    result = _library(tmp_path).search(query, max_results=5)

    assert len(result.matches) == 1
    assert result.matches[0].filename == filename


@pytest.mark.parametrize(
    ("query", "filename"),
    (
        ("asimob", "asimov.epub"),
        ("yo robto", "Yo robot.epub"),
    ),
)
def test_small_typo_returns_bounded_candidate(
    tmp_path: Path,
    query: str,
    filename: str,
) -> None:
    _book(tmp_path, filename)

    result = _library(tmp_path).search(query, max_results=5)

    assert len(result.matches) == 1
    assert result.matches[0].filename == filename
    assert result.bounded is False


def test_typo_candidate_requires_confirmation(
    tmp_path: Path,
) -> None:
    _book(tmp_path, "asimov.epub")

    result = _library(tmp_path).search("asimob", max_results=5)
    decision = GovernedLibraryConversationalSelectionV1().decide(result)

    assert result.matches
    assert (
        decision.disposition
        is GovernedLibrarySelectionDisposition.NEEDS_DISAMBIGUATION
    )
    assert decision.selection is None


def test_multiple_typo_candidates_require_disambiguation(
    tmp_path: Path,
) -> None:
    _book(tmp_path, "asimov.epub")
    _book(tmp_path, "asimon.epub")

    result = _library(tmp_path).search("asimob", max_results=5)
    decision = GovernedLibraryConversationalSelectionV1().decide(result)

    assert len(result.matches) == 2
    assert (
        decision.disposition
        is GovernedLibrarySelectionDisposition.NEEDS_DISAMBIGUATION
    )
    assert decision.selection is None


def test_unrelated_query_does_not_invent_matches(
    tmp_path: Path,
) -> None:
    _book(tmp_path, "asimov.epub")

    result = _library(tmp_path).search(
        "meteorologia cuantica",
        max_results=5,
    )

    assert result.matches == ()


def test_typo_search_preserves_truncation(
    tmp_path: Path,
) -> None:
    _book(tmp_path, "asimov.epub")
    _book(tmp_path, "other.txt")

    result = _library(
        tmp_path,
        max_catalogue_entries=1,
    ).search("asimob", max_results=5)

    assert result.bounded is True


def test_typo_search_does_not_read_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _book(tmp_path, "asimov.epub")

    def forbidden_read(*args: object, **kwargs: object) -> None:
        raise AssertionError("Catalogue must not read document content")

    monkeypatch.setattr(Path, "read_text", forbidden_read)
    monkeypatch.setattr(Path, "read_bytes", forbidden_read)

    result = _library(tmp_path).search("asimob", max_results=5)

    assert result.matches
