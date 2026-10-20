from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.governed_local_library_conversation import (
    GovernedLocalLibraryConversationV1,
)
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

NOW = datetime(2026, 10, 17, 2, 30, tzinfo=timezone.utc)


class RecordingReader:
    def __init__(self) -> None:
        self.calls: list[Path] = []

    def read_text(self, path: Path) -> str:
        self.calls.append(path)
        return path.read_text(encoding="utf-8")


def _runtime(tmp_path: Path):
    root = tmp_path / "library"
    root.mkdir()
    (root / "Robots e Imperio.txt").write_text(
        "CONTENIDO_INTERNO_NO_SOLICITADO",
        encoding="utf-8",
    )

    reader = RecordingReader()
    conversation = GovernedLocalLibraryConversationV1(
        knowledge_runtime=OfficialKnowledgeRuntimeGateway(),
        library=GovernedLocalLibraryCatalogueV1(
            GovernedLocalLibraryConfig(
                root=root,
                allowed_suffixes=(".txt",),
                max_catalogue_entries=20,
            )
        ),
        document_reader=reader,
        unified_runtime=OfficialUnifiedRetrievalExecutionRuntimeGateway(
            OfficialExternalRetrievalRuntimeGateway()
        ),
    )
    return GovernedLocalLibraryConversationInterceptionPort(conversation), (
        conversation,
        reader,
    )


@pytest.mark.parametrize(
    "utterance",
    (
        "Buscá en la biblioteca el libro Robots e Imperio.",
        "Buscá en la biblioteca el libro Robots e Imperio, "
        "pero no lo leas.",
    ),
)
def test_s4_location_does_not_read_or_retrieve(
    tmp_path: Path,
    utterance: str,
) -> None:
    interceptor, (conversation, reader) = _runtime(tmp_path)

    before = conversation.unified_runtime.snapshot.evaluations
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="s4-red-location",
        text=utterance,
    )

    response = interceptor.intercept(request, now=NOW)

    assert response is not None

    after = conversation.unified_runtime.snapshot.evaluations

    observations = {
        "utterance": utterance,
        "response_text": response.response_text,
        "reader_calls": [str(path) for path in reader.calls],
        "evaluations_before": before,
        "evaluations_after": after,
    }

    assert "Robots e Imperio.txt" in response.response_text, observations
    assert (
        "CONTENIDO_INTERNO_NO_SOLICITADO"
        not in response.response_text
    ), observations
    assert reader.calls == [], observations
    assert after == before, observations


@pytest.mark.parametrize(
    "utterance",
    (
        "Leé el libro Robots e Imperio de mi biblioteca.",
        "Buscá en la biblioteca el libro Robots e Imperio y leelo.",
        "Buscá en la biblioteca el libro Robots e Imperio y narrámelo.",
    ),
)
def test_s4_explicit_reading_uses_existing_retrieval(
    tmp_path: Path,
    utterance: str,
) -> None:
    interceptor, (conversation, reader) = _runtime(tmp_path)

    before = conversation.unified_runtime.snapshot.evaluations
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="s4-red-explicit-reading",
        text=utterance,
    )

    response = interceptor.intercept(request, now=NOW)
    after = conversation.unified_runtime.snapshot.evaluations

    observations = {
        "utterance": utterance,
        "response_text": (
            None if response is None else response.response_text
        ),
        "reader_calls": [str(path) for path in reader.calls],
        "evaluations_before": before,
        "evaluations_after": after,
    }

    assert response is not None, observations
    assert (
        "CONTENIDO_INTERNO_NO_SOLICITADO"
        in response.response_text
    ), observations
    assert len(reader.calls) == 1, observations
    assert reader.calls[0].name == "Robots e Imperio.txt", observations
    assert after == before + 1, observations
