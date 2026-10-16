from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.governed_local_library_conversation import GovernedLocalLibraryConversationV1
from app.governed_local_library_runtime_wiring import (
    GovernedLocalLibraryConversationInterceptionPort,
)
from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from app.unified_capability_orchestrator import UnifiedCapabilityOrchestrator
from app.unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.governed_local_library.initiative import (
    governed_local_library_read_descriptor,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

NOW = datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc)


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


class CandidateInstructionPort:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def intercept(self, request, *, now):
        del now
        self.calls.append(request.text)
        if "proponé" not in request.text.casefold():
            return None
        return GovernedOperationalInterception(
            response_text="Instrucciones de candidatos preservadas.",
            rationale="candidate_instruction_completed",
        )


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="session-g1",
        text=text,
    )


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
    library_port = GovernedLocalLibraryConversationInterceptionPort(conversation)
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register_descriptor(
        governed_local_library_read_descriptor(),
        interceptor=library_port,
    )
    instruction_port = CandidateInstructionPort()
    registry.register(
        name="research.candidate.presentation",
        description="Preserva instrucciones posteriores sobre candidatos.",
        interceptor=instruction_port,
        semantic_triggers=("proponé",),
    )
    registry.set_orchestrator(UnifiedCapabilityOrchestrator(registry))
    return registry, catalogue, instruction_port


def _complex_request() -> str:
    return (
        "Buscá en mi Biblioteca material sobre explicaciones rivales.\n\n"
        "Usá únicamente material que encuentres realmente en mi Biblioteca.\n"
        "No uses Internet ni inventes títulos.\n\n"
        "Proponé hasta 5 candidatos y conservá la evidencia encontrada.\n"
        "Todavía no empieces la investigación."
    )


def test_g1_complex_request_bounds_the_cap17_retrieval_query(tmp_path: Path) -> None:
    root = tmp_path / "library"
    (root / "explicaciones rivales.txt").parent.mkdir(parents=True)
    (root / "explicaciones rivales.txt").write_text(
        "Evidencia local gobernada.", encoding="utf-8"
    )
    registry, catalogue, _ = _runtime(root)

    registry.intercept(_request(_complex_request()), now=NOW)

    assert catalogue.queries
    query = catalogue.queries[-1].casefold()
    assert "proponé" not in query
    assert "todavía no empieces" not in query
    assert "no uses internet" not in query


def test_g1_complex_request_preserves_downstream_instruction(tmp_path: Path) -> None:
    root = tmp_path / "library"
    (root / "explicaciones rivales.txt").parent.mkdir(parents=True)
    (root / "explicaciones rivales.txt").write_text(
        "Evidencia local gobernada.", encoding="utf-8"
    )
    registry, _, instruction_port = _runtime(root)

    registry.intercept(_request(_complex_request()), now=NOW)

    assert instruction_port.calls
    assert any("proponé" in item.casefold() for item in instruction_port.calls)


def test_g1_complex_request_keeps_real_cap17_grounding(tmp_path: Path) -> None:
    root = tmp_path / "library"
    (root / "material sobre explicaciones rivales.txt").parent.mkdir(parents=True)
    (root / "material sobre explicaciones rivales.txt").write_text(
        "Evidencia local gobernada.", encoding="utf-8"
    )
    registry, _, _ = _runtime(root)

    result = registry.intercept(_request(_complex_request()), now=NOW)

    assert result is not None
    assert "Evidencia local gobernada." in result.response_text


def test_g1_simple_cap17_request_remains_on_existing_path(tmp_path: Path) -> None:
    root = tmp_path / "library"
    (root / "Asimov.txt").parent.mkdir(parents=True)
    (root / "Asimov.txt").write_text("Grounded Asimov", encoding="utf-8")
    registry, catalogue, instruction_port = _runtime(root)

    result = registry.intercept(
        _request("Buscá en mi Biblioteca Asimov"),
        now=NOW,
    )

    assert result is not None
    assert result.rationale == "local_library_read_completed"
    assert result.response_text == "Grounded Asimov\n\n---\nFuente: Asimov.txt"
    assert catalogue.queries == ["Asimov"]
    assert instruction_port.calls == []
