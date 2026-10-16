from __future__ import annotations

from app.memory_consolidation import OfficialMemoryGateway
from application.brain import (
    BrainQuery,
    build_official_memory_brain_composition,
)
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)
from infrastructure.brain import AtomicJsonBrainRepository


def build_runtime(tmp_path):
    return MemoryRuntimeIntegration(
        MemoryRuntimeConfig(root_path=tmp_path / ".roby" / "memory")
    )


def test_m312_4_composes_real_official_gateway_for_read_only_recall(tmp_path):
    runtime = build_runtime(tmp_path)
    runtime.store_explicit(
        owner="Carlos",
        text="M312.3 quedó validado como base del adaptador.",
        metadata={"source": "test"},
    )
    composition = build_official_memory_brain_composition(
        brain_repository=AtomicJsonBrainRepository(tmp_path / ".roby" / "brain"),
        memory_gateway=OfficialMemoryGateway(runtime, owner="Carlos"),
        owner="Carlos",
    )

    recalled = composition.service.recall(BrainQuery(text="M312.3"))

    assert len(recalled) == 1
    assert recalled[0].source == "official_memory"
    assert recalled[0].metadata["read_only"] is True
    assert composition.gateway.status().stored_count == 1


def test_m312_4_brain_writes_only_to_its_own_repository(tmp_path):
    runtime = build_runtime(tmp_path)
    composition = build_official_memory_brain_composition(
        brain_repository=AtomicJsonBrainRepository(tmp_path / ".roby" / "brain"),
        memory_gateway=OfficialMemoryGateway(runtime, owner="Carlos"),
        owner="Carlos",
    )

    assert composition.gateway.status().stored_count == 0
    assert composition.service.recall(BrainQuery()) == ()
    assert composition.gateway.status().stored_count == 0


def test_m312_4_composition_requires_a_non_blank_owner(tmp_path):
    runtime = build_runtime(tmp_path)

    try:
        build_official_memory_brain_composition(
            brain_repository=AtomicJsonBrainRepository(tmp_path / ".roby" / "brain"),
            memory_gateway=OfficialMemoryGateway(runtime, owner="Carlos"),
            owner="   ",
        )
    except ValueError as error:
        assert str(error) == "brain composition owner must not be blank"
    else:
        raise AssertionError("blank owner should be rejected")


def test_m312_4_application_composition_depends_on_memory_contract_not_app_gateway():
    source = open("application/brain/composition.py", encoding="utf-8").read()

    assert "from app.memory_consolidation import OfficialMemoryGateway" not in source
    assert "memory_gateway: MemoryStore" in source
    assert "brain_repository: BrainRepository" in source
    assert "from infrastructure" not in source


def test_m312_4_composition_is_not_imported_by_runtime_root_factory():
    source = open("app/runtime_root_factory.py", encoding="utf-8").read()

    assert "build_official_memory_brain_composition" not in source
