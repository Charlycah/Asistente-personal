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

NOW = datetime(2026, 10, 1, 15, 0, tzinfo=timezone.utc)
SENTINEL = "PRIVATE_BOOK_CONTENT_SENTINEL"


class Reader:
    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")


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
        document_reader=Reader(),
        unified_runtime=OfficialUnifiedRetrievalExecutionRuntimeGateway(
            OfficialExternalRetrievalRuntimeGateway()
        ),
    )
    return GovernedLocalLibraryConversationInterceptionPort(conversation)


def _request(
    text: str,
    session_id: str = "search-reuse-01",
) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


def _book(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "Yo robot.txt").write_text(
        SENTINEL,
        encoding="utf-8",
    )


def _assert_search_without_reading(result: object) -> None:
    assert result is not None
    assert result.rationale != "local_library_read_completed"
    assert SENTINEL not in result.response_text


def test_library_direct_search_does_not_read_content(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    _book(root)
    interceptor = _interceptor(root)

    result = interceptor.intercept(
        _request("Buscá Yo robot en la Biblioteca"),
        now=NOW,
    )

    _assert_search_without_reading(result)
    assert result is not None
    assert result.rationale == "local_library_location_completed"
    assert "Yo robot" in result.response_text


def test_library_search_follow_up_preserves_search_intent(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    _book(root)
    interceptor = _interceptor(root)

    initial = interceptor.intercept(
        _request("Buscá en mi Biblioteca"),
        now=NOW,
    )
    assert initial is not None
    assert initial.rationale == "local_library_query_required"

    result = interceptor.intercept(
        _request("Yo robot"),
        now=NOW + timedelta(seconds=10),
    )

    _assert_search_without_reading(result)
    assert result is not None
    assert result.rationale == "local_library_location_completed"
    assert "Yo robot" in result.response_text


def test_library_explicit_read_preserves_content_access(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    _book(root)
    interceptor = _interceptor(root)

    result = interceptor.intercept(
        _request("Lee el libro Yo robot de mi biblioteca"),
        now=NOW,
    )

    assert result is not None
    assert result.rationale == "local_library_read_completed"
    assert SENTINEL in result.response_text


def test_library_explicit_read_disambiguation_preserves_intent(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()

    (root / "literatura_historia.txt").write_text(
        SENTINEL,
        encoding="utf-8",
    )
    (root / "literatura_ensayo.txt").write_text(
        "OTHER_PRIVATE_CONTENT",
        encoding="utf-8",
    )

    interceptor = _interceptor(root)

    initial = interceptor.intercept(
        _request("Le\u00e9 en mi Biblioteca literatura"),
        now=NOW,
    )

    assert initial is not None
    assert initial.rationale == "local_library_disambiguation_required"
    assert SENTINEL not in initial.response_text

    selected = interceptor.intercept(
        _request("literatura_historia"),
        now=NOW + timedelta(seconds=10),
    )

    assert selected is not None
    assert selected.rationale == "local_library_read_completed"
    assert SENTINEL in selected.response_text
