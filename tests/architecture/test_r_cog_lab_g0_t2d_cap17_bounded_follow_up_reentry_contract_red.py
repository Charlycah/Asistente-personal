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


def _request(session_id: str, text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


def _open_disambiguation(
    interceptor: GovernedLocalLibraryConversationInterceptionPort,
    root: Path,
) -> None:
    (root / "literatura_historia.txt").write_text("Historia", encoding="utf-8")
    (root / "literatura_ensayo.txt").write_text("Ensayo", encoding="utf-8")
    result = interceptor.intercept(
        _request("session-a", "Buscá en mi Biblioteca literatura"),
        now=NOW,
    )
    assert result is not None
    assert result.rationale == "local_library_disambiguation_required"


def test_t2d_query_required_follow_up_reenters_existing_cap17(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    (root / "Isaac Asimov.txt").write_text("Grounded Asimov", encoding="utf-8")

    initial = interceptor.intercept(
        _request("session-a", "Buscá literatura en mi Biblioteca"),
        now=NOW,
    )
    assert initial is not None
    assert initial.rationale == "local_library_query_required"

    result = interceptor.intercept(
        _request("session-a", "Isaac Asimov"),
        now=NOW + timedelta(seconds=10),
    )

    assert result is not None
    assert result.rationale == "local_library_read_completed"
    assert result.response_text == "Grounded Asimov\n\n---\nFuente: Isaac Asimov.txt"


def test_t2d_triggerless_follow_up_reenters_existing_cap17(tmp_path: Path) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    _open_disambiguation(interceptor, root)
    (root / "Isaac Asimov.txt").write_text("Grounded Asimov", encoding="utf-8")

    result = interceptor.intercept(
        _request("session-a", "Isaac Asimov"),
        now=NOW + timedelta(seconds=10),
    )

    assert result is not None
    assert result.rationale == "local_library_read_completed"
    assert result.response_text == "Grounded Asimov\n\n---\nFuente: Isaac Asimov.txt"


def test_t2d_natural_books_follow_up_remains_under_cap17(tmp_path: Path) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    _open_disambiguation(interceptor, root)

    result = interceptor.intercept(
        _request("session-a", "Libros de Isaac Asimov"),
        now=NOW + timedelta(seconds=10),
    )

    assert result is not None
    assert result.rationale.startswith("local_library_")


def test_t2d_unrelated_turn_is_not_captured(tmp_path: Path) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    _open_disambiguation(interceptor, root)

    result = interceptor.intercept(
        _request("session-a", "¿Qué temperatura hace afuera?"),
        now=NOW + timedelta(seconds=10),
    )

    assert result is None


def test_t2d_pending_follow_up_is_session_scoped(tmp_path: Path) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    _open_disambiguation(interceptor, root)

    result = interceptor.intercept(
        _request("session-b", "Isaac Asimov"),
        now=NOW + timedelta(seconds=10),
    )

    assert result is None


def test_t2d_pending_follow_up_expires(tmp_path: Path) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    _open_disambiguation(interceptor, root)

    result = interceptor.intercept(
        _request("session-a", "Isaac Asimov"),
        now=NOW + timedelta(seconds=301),
    )

    assert result is None


def test_t2d_pending_follow_up_can_be_cancelled(tmp_path: Path) -> None:
    root = tmp_path / "library"
    interceptor = _interceptor(root)
    _open_disambiguation(interceptor, root)

    cancelled = interceptor.intercept(
        _request("session-a", "cancelá la búsqueda"),
        now=NOW + timedelta(seconds=10),
    )
    assert cancelled is not None
    assert cancelled.rationale == "local_library_clarification_cancelled"

    after = interceptor.intercept(
        _request("session-a", "Isaac Asimov"),
        now=NOW + timedelta(seconds=20),
    )
    assert after is None
