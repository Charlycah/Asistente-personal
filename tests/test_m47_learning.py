from datetime import datetime

import pytest

from core.attention import AttentionManager, AttentionSignal
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.learning import (
    ExperientialLearningEngine,
    ExperientialLearningManager,
    LearnedExperience,
    LearningContext,
    LearningSignal,
    LearningSignalKind,
    LearningStrength,
)
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService
from core.mental_state import ROBYMentalState
from core.planning import PlanningContext, PlanningManager
from core.provider_router import ProviderRouter
from core.reasoning import ReasoningContext, ReasoningManager
from core.working_memory import WorkingMemoryKind, WorkingMemoryManager


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta aprendida", provider=self.name)


def test_learning_signal_validates_required_fields():
    with pytest.raises(ValueError):
        LearningSignal(" ")

    with pytest.raises(ValueError):
        LearningSignal("Cristina prefiere aviso suave", person=" ")

    with pytest.raises(ValueError):
        LearningSignal("Cristina prefiere aviso suave", confidence=1.2)

    with pytest.raises(ValueError):
        LearningSignal(
            "Cristina prefiere aviso suave",
            occurred_at=datetime(2026, 7, 8),
        )


def test_learned_experience_validates_lesson_confidence_and_timestamp():
    with pytest.raises(ValueError):
        LearnedExperience(" ")

    with pytest.raises(ValueError):
        LearnedExperience("x", confidence=-0.1)

    with pytest.raises(ValueError):
        LearnedExperience("x", created_at=datetime(2026, 7, 8))


def test_learning_engine_creates_personalized_experience():
    signal = LearningSignal(
        "prefiere recordatorios suaves diez minutos antes",
        kind=LearningSignalKind.PREFERENCE,
        person="Cristina",
        confidence=0.9,
    )

    experience = ExperientialLearningEngine().learn(LearningContext(signal=signal))

    assert experience.person == "Cristina"
    assert experience.normalized_kind is LearningSignalKind.PREFERENCE
    assert experience.normalized_strength is LearningStrength.HIGH
    assert "Cristina" in experience.lesson
    assert "preferencia" in experience.lesson
    assert experience.confidence == 0.9


def test_learning_engine_uses_reasoning_and_plan_as_evidence():
    memory = WorkingMemoryManager()
    reasoning = ReasoningManager()
    reasoning_result = reasoning.reason(
        ReasoningContext(
            query="Cómo recordar mejor a Cristina?",
            identity=ROBYIdentity(),
            working_memory=memory,
        )
    )
    planning = PlanningManager()
    plan = planning.create_plan(
        PlanningContext(
            goal="Ajustar recordatorios de Cristina",
            identity=ROBYIdentity(),
            working_memory=memory,
            reasoning=reasoning,
        )
    )
    signal = LearningSignal(
        "Cristina respondió mejor al segundo aviso",
        kind=LearningSignalKind.REMINDER,
        person="Cristina",
        confidence=0.75,
    )

    experience = ExperientialLearningEngine().learn(
        LearningContext(
            signal=signal,
            identity=ROBYIdentity(),
            working_memory=memory,
            reasoning=reasoning,
            reasoning_result=reasoning_result,
            planning=planning,
            plan=plan,
        )
    )

    assert experience.confidence > signal.confidence
    assert reasoning_result.conclusion in experience.evidence
    assert plan.goal.description in experience.evidence
    assert memory.memory.current_focus is not None
    assert memory.memory.current_focus.source == "learning"
    assert memory.memory.current_focus.normalized_kind is WorkingMemoryKind.FACT


def test_learning_manager_merges_repeated_experiences():
    manager = ExperientialLearningManager()

    first = manager.observe(
        "Carlos revisa noticias por la mañana",
        kind=LearningSignalKind.ROUTINE,
        person="Carlos",
        confidence=0.7,
    )
    second = manager.observe(
        "Carlos revisa noticias por la mañana",
        kind=LearningSignalKind.ROUTINE,
        person="Carlos",
        confidence=0.7,
    )

    assert len(manager.experiences) == 1
    assert second.experience_id == first.experience_id
    assert second.confidence > first.confidence
    assert manager.relevant_for("Carlos") == (second,)


def test_learning_manager_capacity_and_snapshot():
    manager = ExperientialLearningManager(capacity=2)
    manager.observe("uno", confidence=0.6)
    manager.observe("dos", confidence=0.6)
    manager.observe("tres", confidence=0.6)

    snapshot = manager.to_dict()

    assert len(manager.experiences) == 2
    assert snapshot["capacity"] == 2
    assert snapshot["last_experience"] is not None
    assert len(snapshot["experiences"]) == 2

    with pytest.raises(ValueError):
        ExperientialLearningManager(capacity=0)


def test_learning_system_prompt_lines_describe_experiences():
    manager = ExperientialLearningManager()
    empty_lines = manager.system_prompt_lines()
    manager.observe(
        "prefiere avisos tranquilos",
        kind=LearningSignalKind.PREFERENCE,
        person="Cristina",
        confidence=0.9,
    )
    lines = manager.system_prompt_lines()

    assert empty_lines == (
        "Aprendizaje experiencial de ROBY:",
        "- Sin experiencias aprendidas activas",
    )
    assert "Aprendizaje experiencial de ROBY:" in lines
    assert any("Cristina" in line for line in lines)
    assert any("high" in line for line in lines)


def test_learning_prioritizes_attention_context():
    attention = AttentionManager()
    attention.submit(
        AttentionSignal(
            "Cristina necesita un recordatorio importante",
            person="Cristina",
            urgency=9,
            importance=10,
            source="reminders",
        )
    )
    signal = LearningSignal(
        "El recordatorio importante debe anticiparse",
        kind=LearningSignalKind.REMINDER,
        person="Cristina",
        confidence=0.6,
    )

    experience = ExperientialLearningEngine().learn(
        LearningContext(signal=signal, attention=attention)
    )

    assert experience.confidence > signal.confidence


def test_cognitive_pipeline_can_inject_learning_into_system_prompt(tmp_path):
    provider = RecordingProvider()
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
    )

    result = pipeline.process_turn("Cristina prefiere recordatorios suaves")

    assert result.learning is learning
    assert learning.last_experience is not None
    assert "Aprendizaje experiencial de ROBY:" in result.system_prompt
    assert "Cristina prefiere recordatorios suaves" in result.system_prompt
    if provider.requests:
        assert provider.requests[0].system_prompt == result.system_prompt
