from datetime import datetime

import pytest

from core.attention import AttentionManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.knowledge_gateway import (
    KnowledgeAnswer,
    KnowledgeContext,
    KnowledgeGatewayEngine,
    KnowledgeGatewayManager,
    KnowledgeNeed,
    KnowledgeRequest,
    KnowledgeSourceKind,
    KnowledgeSourceResult,
)
from core.learning import ExperientialLearningManager
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService
from core.mental_state import ROBYMentalState
from core.planning import PlanningManager
from core.provider_router import ProviderRouter
from core.reasoning import ReasoningManager
from core.working_memory import WorkingMemoryKind, WorkingMemoryManager


class StaticKnowledgeProvider:
    def __init__(
        self,
        name: str,
        source_kind: KnowledgeSourceKind,
        content: str,
        confidence: float,
    ) -> None:
        self.name = name
        self.source_kind = source_kind
        self.content = content
        self.confidence = confidence
        self.requests: list[KnowledgeRequest] = []

    def retrieve(self, request: KnowledgeRequest) -> KnowledgeSourceResult:
        self.requests.append(request)
        return KnowledgeSourceResult(
            self.content,
            provider=self.name,
            source_kind=self.source_kind,
            confidence=self.confidence,
            citations=(f"{self.name}:source",),
        )


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta con gateway", provider=self.name)


def test_knowledge_request_validates_fields():
    with pytest.raises(ValueError):
        KnowledgeRequest(" ")

    with pytest.raises(ValueError):
        KnowledgeRequest("noticias", person=" ")

    with pytest.raises(ValueError):
        KnowledgeRequest("noticias", confidence_required=1.5)

    with pytest.raises(ValueError):
        KnowledgeRequest("noticias", created_at=datetime(2026, 7, 8))


def test_knowledge_source_result_validates_content_and_confidence():
    with pytest.raises(ValueError):
        KnowledgeSourceResult(" ", provider="web")

    with pytest.raises(ValueError):
        KnowledgeSourceResult("ok", provider=" ")

    with pytest.raises(ValueError):
        KnowledgeSourceResult("ok", provider="web", confidence=-0.1)

    with pytest.raises(ValueError):
        KnowledgeSourceResult(
            "ok",
            provider="web",
            retrieved_at=datetime(2026, 7, 8),
        )


def test_knowledge_answer_requires_selected_result_when_external():
    request = KnowledgeRequest("Qué superficie tiene Júpiter?")

    with pytest.raises(ValueError):
        KnowledgeAnswer(
            request=request,
            used_external_knowledge=True,
            summary="Necesita fuente",
        )


def test_engine_detects_current_information_need():
    engine = KnowledgeGatewayEngine()
    context = KnowledgeContext(query="Tenés alguna noticia importante hoy?")

    request = engine.build_request(context)

    assert request.normalized_need is KnowledgeNeed.CURRENT_INFORMATION
    assert KnowledgeSourceKind.WEB in request.normalized_sources
    assert KnowledgeSourceKind.NEWS in request.normalized_sources


def test_engine_detects_explanation_need():
    engine = KnowledgeGatewayEngine()
    context = KnowledgeContext(query='Conocés el libro "Sapiens"?')

    request = engine.build_request(context)

    assert request.normalized_need is KnowledgeNeed.EXPLAIN_TOPIC
    assert KnowledgeSourceKind.ENCYCLOPEDIA in request.normalized_sources
    assert KnowledgeSourceKind.LLM in request.normalized_sources


def test_manager_selects_best_compatible_provider():
    weak = StaticKnowledgeProvider(
        "weak-web",
        KnowledgeSourceKind.WEB,
        "respuesta débil",
        0.65,
    )
    strong = StaticKnowledgeProvider(
        "strong-news",
        KnowledgeSourceKind.NEWS,
        "noticia importante verificada",
        0.91,
    )
    manager = KnowledgeGatewayManager(providers=(weak, strong))

    answer = manager.ask("Hay alguna noticia importante hoy?")

    assert answer.used_external_knowledge is True
    assert answer.selected_result is not None
    assert answer.selected_result.provider == "strong-news"
    assert answer.summary == "noticia importante verificada"
    assert manager.last_answer is answer
    assert len(manager.history) == 1


def test_manager_reports_missing_provider_without_failing():
    manager = KnowledgeGatewayManager()

    answer = manager.ask("Qué superficie tiene Júpiter?")

    assert answer.used_external_knowledge is False
    assert answer.selected_result is None
    assert "no hay proveedor" in answer.summary


def test_gateway_stores_external_knowledge_in_working_memory():
    memory = WorkingMemoryManager()
    provider = StaticKnowledgeProvider(
        "encyclopedia",
        KnowledgeSourceKind.ENCYCLOPEDIA,
        "Júpiter es el planeta más grande del sistema solar.",
        0.95,
    )
    manager = KnowledgeGatewayManager(providers=(provider,))

    answer = manager.ask(
        "Qué superficie tiene Júpiter?",
        working_memory=memory,
    )

    assert answer.used_external_knowledge is True
    assert memory.memory.current_focus is not None
    assert memory.memory.current_focus.source == "knowledge_gateway"
    assert memory.memory.current_focus.normalized_kind is WorkingMemoryKind.FACT


def test_gateway_system_prompt_lines_describe_last_answer():
    provider = StaticKnowledgeProvider(
        "llm-helper",
        KnowledgeSourceKind.LLM,
        "Resumen del libro solicitado.",
        0.9,
    )
    manager = KnowledgeGatewayManager(providers=(provider,))
    empty_lines = manager.system_prompt_lines()
    manager.ask('Conocés el libro "Sapiens"?')
    lines = manager.system_prompt_lines()

    assert empty_lines == (
        "Knowledge Gateway de ROBY:",
        "- Sin consultas externas activas",
    )
    assert "Knowledge Gateway de ROBY:" in lines
    assert any("llm-helper" in line for line in lines)
    assert any("0.90" in line for line in lines)


def test_cognitive_pipeline_can_inject_knowledge_gateway(tmp_path):
    provider = RecordingProvider()
    knowledge_provider = StaticKnowledgeProvider(
        "news-provider",
        KnowledgeSourceKind.NEWS,
        "Hay una noticia relevante para revisar.",
        0.92,
    )
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    identity = ROBYIdentity()
    mental_state = ROBYMentalState()
    attention = AttentionManager()
    working_memory = WorkingMemoryManager()
    reasoning = ReasoningManager()
    planning = PlanningManager()
    learning = ExperientialLearningManager()
    gateway = KnowledgeGatewayManager(providers=(knowledge_provider,))
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
        identity=identity,
        mental_state=mental_state,
        attention=attention,
        working_memory=working_memory,
        reasoning=reasoning,
        planning=planning,
        learning=learning,
        knowledge_gateway=gateway,
    )

    result = pipeline.process_turn("Tenés alguna noticia importante hoy?")

    assert result.knowledge_gateway is gateway
    assert gateway.last_answer is not None
    assert gateway.last_answer.used_external_knowledge is True
    assert "Knowledge Gateway de ROBY:" in result.system_prompt
    assert "news-provider" in result.system_prompt
    if provider.requests:
        assert provider.requests[0].system_prompt == result.system_prompt
