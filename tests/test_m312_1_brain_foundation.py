from datetime import datetime, timedelta, timezone

from application.brain import BrainQuery, BrainService
from domain.brain import BrainMemory, BrainMemoryStatus, BrainMemoryType
from infrastructure.brain import AtomicJsonBrainRepository


def build_service(tmp_path):
    return BrainService(AtomicJsonBrainRepository(tmp_path / ".roby" / "brain"))


def test_m312_1_remembers_and_recalls_without_runtime_wiring(tmp_path):
    service = build_service(tmp_path)
    memory = BrainMemory(
        content="M311 quedó validado como versión estable.",
        memory_type=BrainMemoryType.EPISODE,
        subject="ROBY XI.2",
        importance=0.95,
        source="user_confirmation",
    )

    service.remember(memory)

    assert service.recall(BrainQuery(text="M311")) == (memory,)


def test_m312_1_persists_atomically_as_valid_json(tmp_path):
    service = build_service(tmp_path)
    service.remember(
        BrainMemory(
            content="Crear BrainService sin conectar el runtime.",
            memory_type=BrainMemoryType.GOAL,
            subject="M312",
            source="project_plan",
        )
    )

    reloaded = build_service(tmp_path).recall(BrainQuery(subject="M312"))

    assert len(reloaded) == 1
    assert not list((tmp_path / ".roby" / "brain").glob("*.tmp"))


def test_m312_1_deduplicates_and_merges_metadata(tmp_path):
    service = build_service(tmp_path)
    original = BrainMemory(
        content="No tocar los motores estables.",
        memory_type=BrainMemoryType.PROFILE,
        subject="development_method",
        importance=0.7,
        confidence=0.8,
        source="user_statement",
        tags=("stability",),
    )
    service.remember(original)
    refreshed = service.remember(
        BrainMemory(
            content="No tocar los motores estables.",
            memory_type=BrainMemoryType.PROFILE,
            subject="development_method",
            importance=0.95,
            confidence=1.0,
            source="user_confirmation",
            tags=("surgical_changes",),
            metadata={"confirmed": True},
        )
    )

    recalled = service.recall(BrainQuery(subject="development_method"))

    assert len(recalled) == 1
    assert refreshed.memory_id == original.memory_id
    assert refreshed.importance == 0.95
    assert refreshed.metadata == {"confirmed": True}
    assert refreshed.tags == ("stability", "surgical_changes")


def test_m312_1_filters_and_expires_memories(tmp_path):
    service = build_service(tmp_path)
    now = datetime(2026, 7, 23, 20, 0, tzinfo=timezone.utc)
    expired = BrainMemory(
        content="Contexto temporal",
        memory_type=BrainMemoryType.WORKING,
        expires_at=now - timedelta(seconds=1),
        source="conversation",
    )
    service.remember(expired)

    assert service.recall(BrainQuery(), now=now) == ()
    assert service.expire(now=now) == 1
    archived = service.recall(
        BrainQuery(status=BrainMemoryStatus.ARCHIVED, include_expired=True), now=now
    )
    assert archived[0].memory_id == expired.memory_id


def test_m312_1_updates_and_forgets_by_id(tmp_path):
    service = build_service(tmp_path)
    memory = service.remember(
        BrainMemory(
            content="M312 está planificado.",
            memory_type=BrainMemoryType.GOAL,
            subject="M312",
            source="project_plan",
        )
    )

    updated = service.update(memory.memory_id, content="M312 está activo.")

    assert updated.content == "M312 está activo."
    assert service.forget(memory.memory_id) is True
    assert service.forget(memory.memory_id) is False
    assert service.recall(BrainQuery(include_expired=True)) == ()


def test_m312_1_rejects_naive_timestamps():
    try:
        BrainMemory(
            content="invalid",
            memory_type=BrainMemoryType.EPISODE,
            created_at=datetime(2026, 7, 23),
        )
    except ValueError as error:
        assert "timezone-aware" in str(error)
    else:
        raise AssertionError("naive timestamps must be rejected")
