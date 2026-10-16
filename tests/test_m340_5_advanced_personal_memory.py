from datetime import UTC, datetime

from app.memory_consolidation import OfficialMemoryGateway
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)


def _gateway(tmp_path):
    runtime = MemoryRuntimeIntegration(
        MemoryRuntimeConfig(
            root_path=tmp_path / "memory",
            canonical_joint_owner=True,
        )
    )
    return OfficialMemoryGateway(runtime, owner="Carlos y Cristina"), runtime


def _request(owner: str, text: str):
    return GovernedConversationPipelineRequest(
        owner=owner,
        session_id="m340-5",
        text=text,
    )


def test_m340_5_stores_attributed_memory_in_joint_store(tmp_path):
    gateway, runtime = _gateway(tmp_path)
    result = gateway.intercept(
        _request("Carlos", "Recordá sobre Cristina: prefiere té"),
        now=datetime.now(UTC),
    )
    records = runtime.search(owner="Carlos y Cristina", query=None)
    assert result.rationale == "advanced_personal_memory_profile_store_completed"
    assert records[0].metadata["recorded_by"] == "Carlos"
    assert records[0].metadata["subject"] == "Cristina"
    assert records[0].metadata["status"] == "active"


def test_m340_5_inspects_only_active_profile_memories(tmp_path):
    gateway, runtime = _gateway(tmp_path)
    runtime.store_explicit(
        owner="Carlos y Cristina",
        text="prefiere té",
        metadata={
            "source": "test",
            "status": "active",
            "subject": "Cristina",
        },
    )
    result = gateway.intercept(
        _request("Carlos", "Qué recordás sobre Cristina"),
        now=datetime.now(UTC),
    )
    assert "prefiere té" in result.response_text
    assert "origen: test" in result.response_text


def test_m340_5_corrects_memory_by_explicit_identifier(tmp_path):
    gateway, runtime = _gateway(tmp_path)
    stored = runtime.store_explicit(owner="Carlos", text="prefiero café")
    memory_id = int(stored.stored_memory_ids[0].split(":", 1)[1])
    result = gateway.intercept(
        _request("Carlos", f"Corregí recuerdo {memory_id}: prefiero té"),
        now=datetime.now(UTC),
    )
    record = runtime.private_store("Carlos").get(memory_id)
    assert result.response_text == "Recuerdo corregido."
    assert record is not None
    assert record.content == "prefiero té"
    assert record.metadata["corrected_by"] == "Carlos"


def test_m340_5_archives_without_deleting_memory(tmp_path):
    gateway, runtime = _gateway(tmp_path)
    stored = runtime.store_explicit(owner="Carlos", text="dato anterior")
    memory_id = int(stored.stored_memory_ids[0].split(":", 1)[1])
    result = gateway.intercept(
        _request("Carlos", f"Archivá recuerdo {memory_id}"),
        now=datetime.now(UTC),
    )
    record = runtime.private_store("Carlos").get(memory_id)
    assert "archivado" in result.response_text.casefold()
    assert record is not None
    assert record.metadata["status"] == "archived"


def test_m340_5_requires_profile_separator(tmp_path):
    gateway, _ = _gateway(tmp_path)
    result = gateway.intercept(
        _request("Carlos", "Recordá sobre Cristina prefiere té"),
        now=datetime.now(UTC),
    )
    assert result.rationale == "advanced_personal_memory_format_missing"


def test_m340_5_preserves_legacy_personal_memory_command(tmp_path):
    gateway, runtime = _gateway(tmp_path)
    result = gateway.intercept(
        _request("Carlos", "Recordá que prefiero respuestas breves"),
        now=datetime.now(UTC),
    )
    assert result.rationale == "official_memory_explicit_store_completed"
    assert runtime.count(owner="Carlos") == 1


def test_m340_5_rejects_unknown_memory_subject(tmp_path):
    gateway, runtime = _gateway(tmp_path)
    result = gateway.intercept(
        _request("Carlos", "Recordá sobre Ana: prefiere té"),
        now=datetime.now(UTC),
    )
    assert result.rationale == "advanced_personal_memory_subject_rejected"
    assert runtime.count(owner="Carlos y Cristina") == 0
