from datetime import datetime

import pytest

from core.attention import AttentionManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.knowledge_gateway import (
    KnowledgeGatewayManager,
    KnowledgeRequest,
    KnowledgeSourceKind,
    KnowledgeSourceResult,
)
from core.learning import ExperientialLearningManager
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService
from core.mental_state import ROBYMentalState
from core.planning import PlanningContext, PlanningManager
from core.provider_router import ProviderRouter
from core.reasoning import ReasoningContext, ReasoningManager
from core.reflection import (
    ReflectionContext,
    ReflectionEngine,
    ReflectionFocus,
    ReflectionInsight,
    ReflectionJudgement,
    ReflectionManager,
    ReflectionResult,
)
from core.working_memory import WorkingMemoryManager


class StaticKnowledgeProvider:
    name = "encyclopedia"
    source_kind = KnowledgeSourceKind.ENCYCLOPEDIA

    def retrieve(self, request: KnowledgeRequest) -> KnowledgeSourceResult:
        return KnowledgeSourceResult(
            "Respuesta externa confiable.",
            provider=self.name,
            source_kind=self.source_kind,
            confidence=0.9,
        )


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta con reflexión", provider=self.name)


def test_reflection_context_validates_subject_and_timestamp():
    with pytest.raises(ValueError):
        ReflectionContext(" ")

    with pytest.raises(ValueError):
        ReflectionContext("evaluar", created_at=datetime(2026, 7, 8))


def test_reflection_insight_validates_description_and_confidence():
    with pytest.raises(ValueError):
        ReflectionInsight(" ")

    with pytest.raises(ValueError):
        ReflectionInsight("ok", confidence=1.5)


def test_reflection_result_requires_insights_and_valid_confidence():
    insight = ReflectionInsight("ROBY observó el resultado.")

    with pytest.raises(ValueError):
        ReflectionResult(
            subject="evaluar",
            judgement=ReflectionJudgement.GOOD,
            summary="ok",
            confidence=0.8,
            insights=(),
        )

    with pytest.raises(ValueError):
        ReflectionResult(
            subject="evaluar",
            judgement=ReflectionJudgement.GOOD,
            summary="ok",
            confidence=-0.1,
            insights=(insight,),
        )


def test_reflection_engine_evaluates_reasoning_and_plan():
    identity = ROBYIdentity()
    attention = AttentionManager()
    working_memory = WorkingMemoryManager()
    reasoning = ReasoningManager()
    planning = PlanningManager()
    reasoning_result = reasoning.reason(
        ReasoningContext(
            query="Organizar recordatorios de Cristina",
            identity=identity,
            attention=attention,
            working_memory=working_memory,
        )
    )
    plan = planning.create_plan(
        PlanningContext(
            goal="Organizar recordatorios de Cristina",
            identity=identity,
            attention=attention,
            working_memory=working_memory,
            reasoning=reasoning,
            reasoning_result=reasoning_result,
        )
    )

    result = ReflectionEngine().reflect(
        ReflectionContext(
            subject="Organizar recordatorios de Cristina",
            identity=identity,
            attention=attention,
            working_memory=working_memory,
            reasoning=reasoning,
            reasoning_result=reasoning_result,
            planning=planning,
            plan=plan,
            focus=ReflectionFocus.PLAN,
        )
    )

    assert result.normalized_focus is ReflectionFocus.PLAN
    assert result.normalized_judgement in {
        ReflectionJudgement.GOOD,
        ReflectionJudgement.ACCEPTABLE,
    }
    assert any(
        insight.normalized_focus is ReflectionFocus.DECISION
        for insight in result.insights
    )
    assert any(
        insight.normalized_focus is ReflectionFocus.PLAN for insight in result.insights
    )
    assert working_memory.memory.current_focus is not None
    assert working_memory.memory.current_focus.source == "reflection"


def test_reflection_marks_low_confidence_knowledge_as_uncertain():
    request = KnowledgeRequest("noticia importante", confidence_required=0.6)
    low_result = KnowledgeSourceResult(
        "dato dudoso",
        provider="web",
        source_kind=KnowledgeSourceKind.WEB,
        confidence=0.4,
    )
    from core.knowledge_gateway import KnowledgeAnswer

    answer = KnowledgeAnswer(
        request=request,
        used_external_knowledge=True,
        summary="dato dudoso",
        selected_result=low_result,
    )

    result = ReflectionEngine().reflect(
        ReflectionContext(
            subject="noticia importante",
            knowledge_result=answer,
            focus=ReflectionFocus.KNOWLEDGE,
        )
    )

    assert result.normalized_judgement is ReflectionJudgement.UNCERTAIN
    assert result.needs_follow_up is True
    assert "Verificar" in result.recommendation


def test_reflection_manager_keeps_history_and_prompt_lines():
    manager = ReflectionManager()
    empty_lines = manager.system_prompt_lines()

    result = manager.reflect(ReflectionContext("evaluar comportamiento"))
    lines = manager.system_prompt_lines()

    assert empty_lines == ("Reflexión: sin revisión metacognitiva reciente.",)
    assert manager.last_result is result
    assert manager.history == (result,)
    assert "Reflexión metacognitiva de ROBY:" in lines
    assert any("Juicio" in line for line in lines)


def test_reflection_result_serializes_and_exposes_prompt_lines():
    result = ReflectionEngine().reflect(ReflectionContext("evaluar decisión"))

    data = result.to_dict()
    lines = result.system_prompt_lines()

    assert data["subject"] == "evaluar decisión"
    assert data["judgement"] in {item.value for item in ReflectionJudgement}
    assert data["insights"]
    assert "Reflexión metacognitiva de ROBY:" in lines


def test_cognitive_pipeline_can_inject_reflection(tmp_path):
    provider = RecordingProvider()
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    reflection = ReflectionManager()
    gateway = KnowledgeGatewayManager(providers=(StaticKnowledgeProvider(),))
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
        identity=ROBYIdentity(),
        mental_state=ROBYMentalState(),
        attention=AttentionManager(),
        working_memory=WorkingMemoryManager(),
        reasoning=ReasoningManager(),
        planning=PlanningManager(),
        learning=ExperientialLearningManager(),
        knowledge_gateway=gateway,
        reflection=reflection,
    )

    result = pipeline.process_turn("Conocés el libro Sapiens?")

    assert result.reflection is reflection
    assert reflection.last_result is not None
    assert "Reflexión metacognitiva de ROBY:" in result.system_prompt
    if provider.requests:
        assert provider.requests[0].system_prompt == result.system_prompt
