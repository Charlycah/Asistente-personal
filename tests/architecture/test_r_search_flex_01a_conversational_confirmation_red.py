from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.governed_local_library_conversation import GovernedLocalLibraryConversationV1
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
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


NOW = datetime(2026, 10, 17, 15, 0, tzinfo=timezone.utc)


class ForbiddenReader:
    def read_text(self, path: Path) -> str:
        raise AssertionError("Location confirmation must not read content")


def _interceptor(root: Path) -> GovernedLocalLibraryConversationInterceptionPort:
    root.mkdir(parents=True, exist_ok=True)
    library = GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(
            root=root,
            allowed_suffixes=(".txt",),
            max_catalogue_entries=20,
        )
    )
    conversation = GovernedLocalLibraryConversationV1(
        knowledge_runtime=OfficialKnowledgeRuntimeGateway(),
        library=library,
        document_reader=ForbiddenReader(),
        unified_runtime=OfficialUnifiedRetrievalExecutionRuntimeGateway(
            OfficialExternalRetrievalRuntimeGateway()
        ),
    )
    return GovernedLocalLibraryConversationInterceptionPort(conversation)


def _request(session_id: str, text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="test-owner",
        session_id=session_id,
        text=text,
    )


def _book(root: Path, name: str) -> None:
    (root / name).write_text("PRIVATE_CONTENT_SENTINEL", encoding="utf-8")


def test_single_typo_confirmation_locates_without_reading(tmp_path: Path) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    _book(root, "asimov.txt")

    initial = interceptor.intercept(
        _request("session-a", "Busc? en mi Biblioteca asimob"),
        now=NOW,
    )
    assert initial is not None
    assert initial.rationale == "local_library_disambiguation_required"

    confirmed = interceptor.intercept(
        _request("session-a", "sí, ese"),
        now=NOW + timedelta(seconds=10),
    )
    assert confirmed is not None
    assert confirmed.rationale == "local_library_location_completed"
    assert "asimov.txt" in confirmed.response_text
    assert "PRIVATE_CONTENT_SENTINEL" not in confirmed.response_text


def test_multiple_typo_candidates_reject_ambiguous_yes(tmp_path: Path) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    _book(root, "asimov.txt")
    _book(root, "asimon.txt")

    initial = interceptor.intercept(
        _request("session-a", "Busc? en mi Biblioteca asimob"),
        now=NOW,
    )
    assert initial is not None
    assert initial.rationale == "local_library_disambiguation_required"

    ambiguous = interceptor.intercept(
        _request("session-a", "sí, ese"),
        now=NOW + timedelta(seconds=10),
    )
    assert ambiguous is not None
    assert ambiguous.rationale == "local_library_disambiguation_required"
    assert "PRIVATE_CONTENT_SENTINEL" not in ambiguous.response_text


def test_typo_confirmation_is_session_scoped(tmp_path: Path) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    _book(root, "asimov.txt")

    initial = interceptor.intercept(
        _request("session-a", "Busc? en mi Biblioteca asimob"),
        now=NOW,
    )
    assert initial is not None
    assert initial.rationale == "local_library_disambiguation_required"

    other_session = interceptor.intercept(
        _request("session-b", "s?, ese"),
        now=NOW + timedelta(seconds=10),
    )
    assert other_session is None

def test_r_search_flex_01a_accented_confirmation_variants():
    from app.governed_local_library_runtime_wiring import (
        GovernedLocalLibraryConversationInterceptionPort,
    )

    confirm = (
        GovernedLocalLibraryConversationInterceptionPort
        ._is_candidate_confirmation
    )

    assert confirm("s\u00ed, ese")
    assert confirm("s\u00ed, esa")
    assert confirm("si, ese")
    assert confirm("si, esa")
    assert not confirm("no, ese")
