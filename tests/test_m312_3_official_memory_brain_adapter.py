from __future__ import annotations

from dataclasses import dataclass, field

from application.brain import (
    BrainQuery,
    BrainService,
    OfficialMemoryBrainAdapter,
)
from core.memory import MemoryItem, MemoryQuery
from domain.brain import BrainMemoryType
from infrastructure.brain import AtomicJsonBrainRepository


@dataclass
class RecordingOfficialMemoryGateway:
    items: list[MemoryItem]
    recall_queries: list[MemoryQuery] = field(default_factory=list)
    remember_calls: int = 0

    def remember(self, item: MemoryItem) -> None:
        del item
        self.remember_calls += 1
        raise AssertionError("M312.3 adapter must never write official memory")

    def recall(self, query: MemoryQuery) -> list[MemoryItem]:
        self.recall_queries.append(query)
        return list(self.items)


def build_service(tmp_path, gateway):
    adapter = OfficialMemoryBrainAdapter(gateway=gateway, owner="Carlos")
    repository = AtomicJsonBrainRepository(tmp_path / ".roby" / "brain")
    return BrainService(repository, readers=(adapter,))


def test_m312_3_reads_official_memory_through_brain(tmp_path):
    gateway = RecordingOfficialMemoryGateway(
        items=[
            MemoryItem(
                content="Carlos prefiere cambios quirúrgicos.",
                metadata={
                    "memory_id": "abc123",
                    "category": "preference",
                    "confidence": 0.9,
                },
            )
        ]
    )
    service = build_service(tmp_path, gateway)

    recalled = service.recall(BrainQuery(text="quirúrgicos"))

    assert len(recalled) == 1
    assert recalled[0].memory_id == "official:abc123"
    assert recalled[0].normalized_type == BrainMemoryType.PROFILE
    assert recalled[0].subject == "Carlos"
    assert recalled[0].source == "official_memory"
    assert recalled[0].metadata["read_only"] is True
    assert gateway.remember_calls == 0


def test_m312_3_passes_query_and_limit_to_official_gateway(tmp_path):
    gateway = RecordingOfficialMemoryGateway(items=[])
    service = build_service(tmp_path, gateway)

    service.recall(BrainQuery(text="ROBY", limit=7))

    assert gateway.recall_queries == [
        MemoryQuery(text="ROBY", metadata={"limit": 7})
    ]


def test_m312_3_skips_official_memory_for_non_profile_query(tmp_path):
    gateway = RecordingOfficialMemoryGateway(items=[])
    service = build_service(tmp_path, gateway)

    recalled = service.recall(
        BrainQuery(memory_type=BrainMemoryType.GOAL)
    )

    assert recalled == ()
    assert gateway.recall_queries == []


def test_m312_3_default_brain_service_remains_disconnected(tmp_path):
    gateway = RecordingOfficialMemoryGateway(
        items=[MemoryItem(content="No debería aparecer.")]
    )
    repository = AtomicJsonBrainRepository(tmp_path / ".roby" / "brain")
    service = BrainService(repository)

    assert service.recall(BrainQuery()) == ()
    assert gateway.recall_queries == []
