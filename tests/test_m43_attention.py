from datetime import datetime

import pytest

from core.attention import (
    AttentionEngine,
    AttentionKind,
    AttentionLevel,
    AttentionManager,
    AttentionSignal,
)
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService
from core.provider_router import ProviderRouter


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta con atención", provider=self.name)


def test_attention_signal_validates_required_fields():
    with pytest.raises(ValueError):
        AttentionSignal(description=" ")

    with pytest.raises(ValueError):
        AttentionSignal(description="x", urgency=0)

    with pytest.raises(ValueError):
        AttentionSignal(description="x", importance=11)

    with pytest.raises(ValueError):
        AttentionSignal(description="x", confidence=1.2)

    with pytest.raises(ValueError):
        AttentionSignal(
            description="x",
            created_at=datetime(2026, 7, 8),
        )


def test_attention_engine_prioritizes_cristina_reminders():
    engine = AttentionEngine()

    item = engine.evaluate(
        AttentionSignal(
            description="Recordar medicación",
            kind=AttentionKind.REMINDER,
            person="Cristina",
            source="reminders",
            urgency=10,
            importance=10,
        )
    )

    assert item.level is AttentionLevel.IMMEDIATE
    assert item.can_interrupt is True
    assert item.score == 100
    assert "person=Cristina" in item.reason


def test_attention_engine_demotes_low_value_information():
    engine = AttentionEngine()

    item = engine.evaluate(
        AttentionSignal(
            description="Noticia menor sin relación con la casa",
            kind=AttentionKind.INFORMATION,
            source="news",
            urgency=1,
            importance=1,
        )
    )

    assert item.level is AttentionLevel.IGNORE
    assert item.can_interrupt is False
    assert item.score < 20


def test_attention_manager_keeps_items_sorted_by_score():
    manager = AttentionManager()

    manager.submit(
        AttentionSignal(
            description="Correo promocional",
            kind=AttentionKind.INFORMATION,
            source="gmail",
            urgency=1,
            importance=1,
        )
    )
    manager.submit(
        AttentionSignal(
            description="Ayudar a Cristina con recordatorio",
            kind=AttentionKind.REMINDER,
            person="Cristina",
            source="reminders",
            urgency=9,
            importance=10,
        )
    )

    assert manager.current_focus is not None
    assert manager.current_focus.person == "Cristina"
    assert manager.items[0].score > manager.items[1].score


def test_attention_manager_limits_queue_size():
    manager = AttentionManager(max_items=2)

    for index in range(4):
        manager.submit(
            AttentionSignal(
                description=f"Evento {index}",
                source="test",
                urgency=index + 1,
                importance=index + 1,
            )
        )

    assert len(manager.items) == 2
    assert manager.items[0].description == "Evento 3"


def test_attention_manager_system_prompt_lines_include_focus():
    manager = AttentionManager()
    manager.submit_user_input("Carlos pregunta por Júpiter")

    lines = manager.system_prompt_lines()

    assert "Estado de atención de ROBY:" in lines
    assert "- Foco atencional: Carlos pregunta por Júpiter" in lines
    assert any(line.startswith("- Puntaje:") for line in lines)


def test_attention_manager_snapshot_is_serializable():
    manager = AttentionManager()
    manager.submit_user_input("Ayudame con la agenda", person="Carlos")

    snapshot = manager.to_dict()

    assert snapshot["current_focus"]["person"] == "Carlos"
    assert snapshot["items"][0]["kind"] == "user_input"
    assert snapshot["items"][0]["source"] == "conversation"


def test_attention_manager_clear_removes_focus():
    manager = AttentionManager()
    manager.submit_user_input("Recordame algo")

    manager.clear()

    assert manager.current_focus is None
    assert manager.items == ()


def test_cognitive_pipeline_can_inject_attention_into_system_prompt(tmp_path):
    provider = RecordingProvider()
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    attention = AttentionManager()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
        attention=attention,
    )

    result = pipeline.process_turn("Necesito implementar atención para Cristina")

    assert result.attention is attention
    assert attention.current_focus is not None
    assert attention.current_focus.signal.kind is AttentionKind.USER_INPUT
    assert "Estado de atención de ROBY:" in result.system_prompt
    assert "Necesito implementar atención para Cristina" in result.system_prompt
    assert provider.requests[0].system_prompt == result.system_prompt
