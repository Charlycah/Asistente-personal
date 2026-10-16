from datetime import datetime, timedelta, timezone

import pytest

from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService
from core.provider_router import ProviderRouter
from core.working_memory import (
    WorkingMemory,
    WorkingMemoryItem,
    WorkingMemoryKind,
    WorkingMemoryManager,
)


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta con memoria de trabajo", provider=self.name)


def test_working_memory_item_validates_required_fields():
    with pytest.raises(ValueError):
        WorkingMemoryItem(content=" ")

    with pytest.raises(ValueError):
        WorkingMemoryItem(content="x", source=" ")

    with pytest.raises(ValueError):
        WorkingMemoryItem(content="x", priority=0)

    with pytest.raises(ValueError):
        WorkingMemoryItem(content="x", confidence=1.2)

    with pytest.raises(ValueError):
        WorkingMemoryItem(content="x", ttl_seconds=0)

    with pytest.raises(ValueError):
        WorkingMemoryItem(content="x", created_at=datetime(2026, 7, 8))


def test_working_memory_item_expires_after_ttl():
    created_at = datetime.now(timezone.utc)
    item = WorkingMemoryItem(
        content="pensamiento temporal",
        created_at=created_at,
        ttl_seconds=10,
    )

    assert item.is_expired(created_at + timedelta(seconds=9)) is False
    assert item.is_expired(created_at + timedelta(seconds=10)) is True


def test_working_memory_keeps_items_sorted_by_priority():
    memory = WorkingMemory()

    memory.remember("dato menor", priority=2)
    memory.remember("dato crítico", priority=9)

    assert memory.current_focus is not None
    assert memory.current_focus.content == "dato crítico"
    assert memory.items[0].priority > memory.items[1].priority


def test_working_memory_respects_capacity():
    memory = WorkingMemory(capacity=2)

    for index in range(4):
        memory.remember(f"pensamiento {index}", priority=index + 1)

    assert len(memory.items) == 2
    assert memory.items[0].content == "pensamiento 3"
    assert memory.items[1].content == "pensamiento 2"


def test_working_memory_update_and_remove_item():
    memory = WorkingMemory()
    item = memory.remember("borrador", priority=3)

    updated = memory.update(item.item_id, content="borrador revisado", priority=8)

    assert updated is not None
    assert updated.content == "borrador revisado"
    assert memory.current_focus is not None
    assert memory.current_focus.priority == 8
    assert memory.remove(item.item_id) is True
    assert memory.get(item.item_id) is None


def test_working_memory_expire_removes_old_items():
    created_at = datetime.now(timezone.utc)
    memory = WorkingMemory()
    memory.add(
        WorkingMemoryItem(
            content="expirable",
            created_at=created_at,
            ttl_seconds=5,
        )
    )
    memory.remember("estable", ttl_seconds=None)

    expired = memory.expire(created_at + timedelta(seconds=6))

    assert len(expired) == 1
    assert expired[0].content == "expirable"
    assert len(memory.items) == 1
    assert memory.items[0].content == "estable"


def test_working_memory_filters_by_kind():
    memory = WorkingMemory()

    memory.remember("pregunta abierta", kind=WorkingMemoryKind.QUESTION)
    memory.remember("dato contextual", kind=WorkingMemoryKind.CONTEXT)

    questions = memory.list_items(kind=WorkingMemoryKind.QUESTION)

    assert len(questions) == 1
    assert questions[0].content == "pregunta abierta"


def test_working_memory_system_prompt_lines_include_active_thoughts():
    memory = WorkingMemory()
    memory.remember(
        "Cristina necesita recordatorio suave",
        kind=WorkingMemoryKind.CONTEXT,
        priority=8,
    )

    lines = memory.system_prompt_lines()

    assert "Memoria de trabajo actual de ROBY:" in lines
    assert any("Cristina necesita recordatorio suave" in line for line in lines)


def test_working_memory_manager_captures_user_input():
    manager = WorkingMemoryManager()

    manager.capture_user_input("Carlos pregunta por vacaciones")

    focus = manager.memory.current_focus
    assert focus is not None
    assert focus.normalized_kind is WorkingMemoryKind.USER_INPUT
    assert focus.metadata["person"] == "Carlos"


def test_working_memory_manager_captures_attention_focus():
    manager = WorkingMemoryManager()

    manager.capture_attention_focus("Recordatorio de Cristina", score=92)

    focus = manager.memory.current_focus
    assert focus is not None
    assert focus.normalized_kind is WorkingMemoryKind.ATTENTION
    assert focus.priority == 9
    assert focus.metadata["score"] == "92"


def test_working_memory_snapshot_is_serializable():
    memory = WorkingMemory()
    memory.remember("mantener contexto", kind=WorkingMemoryKind.FACT)

    snapshot = memory.to_dict()

    assert snapshot["capacity"] == 20
    assert snapshot["items"][0]["kind"] == "fact"
    assert snapshot["current_focus"]["content"] == "mantener contexto"


def test_cognitive_pipeline_can_inject_working_memory_into_system_prompt(tmp_path):
    provider = RecordingProvider()
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    working_memory = WorkingMemoryManager()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
        working_memory=working_memory,
    )

    result = pipeline.process_turn("Necesito sostener varias ideas para razonar")

    assert result.working_memory is working_memory
    assert working_memory.memory.current_focus is not None
    assert "Memoria de trabajo actual de ROBY:" in result.system_prompt
    assert "Necesito sostener varias ideas" in result.system_prompt
    assert provider.requests[0].system_prompt == result.system_prompt
