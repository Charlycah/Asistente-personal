from __future__ import annotations

from datetime import datetime, timezone
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

NOW = datetime(2026, 10, 3, 18, 0, tzinfo=timezone.utc)


class Reader:
    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")


class RecordingCatalogue(GovernedLocalLibraryCatalogueV1):
    def __init__(self, config: GovernedLocalLibraryConfig) -> None:
        super().__init__(config)
        self.queries: list[str] = []

    def search(self, query: str, *, max_results: int):
        self.queries.append(query)
        return super().search(query, max_results=max_results)


def _runtime(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    catalogue = RecordingCatalogue(
        GovernedLocalLibraryConfig(
            root=root,
            allowed_suffixes=(".txt",),
            max_catalogue_entries=20,
        )
    )
    conversation = GovernedLocalLibraryConversationV1(
        knowledge_runtime=OfficialKnowledgeRuntimeGateway(),
        library=catalogue,
        document_reader=Reader(),
        unified_runtime=OfficialUnifiedRetrievalExecutionRuntimeGateway(
            OfficialExternalRetrievalRuntimeGateway()
        ),
    )
    return GovernedLocalLibraryConversationInterceptionPort(conversation), catalogue


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="probe-b1-s1",
        text=text,
    )


def test_probe_b1_s1_bounds_real_conversational_book_query(tmp_path: Path) -> None:
    root = tmp_path / "library"
    (root / "Robots e Imperio.txt").parent.mkdir(parents=True)
    (root / "Robots e Imperio.txt").write_text(
        "Grounded library evidence.", encoding="utf-8"
    )
    interceptor, catalogue = _runtime(root)

    result = interceptor.intercept(
        _request(
            "Roby, busca en la biblioteca el libro Robots e Imperio "
            "y decime cuando lo encontrás"
        ),
        now=NOW,
    )

    assert result is not None
    assert catalogue.queries == ["Robots e Imperio"]
    assert result.rationale == "local_library_read_completed"
    assert result.response_text == (
        "Grounded library evidence.\n\n---\nFuente: Robots e Imperio.txt"
    )


def test_probe_b1_s1_preserves_existing_simple_library_query(tmp_path: Path) -> None:
    root = tmp_path / "library"
    (root / "Robots e Imperio.txt").parent.mkdir(parents=True)
    (root / "Robots e Imperio.txt").write_text(
        "Grounded library evidence.", encoding="utf-8"
    )
    interceptor, catalogue = _runtime(root)

    result = interceptor.intercept(
        _request("Buscá en la biblioteca Robots e Imperio"),
        now=NOW,
    )

    assert result is not None
    assert catalogue.queries == ["Robots e Imperio"]
    assert result.rationale == "local_library_read_completed"
