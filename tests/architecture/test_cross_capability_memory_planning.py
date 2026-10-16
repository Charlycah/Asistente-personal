from __future__ import annotations

from datetime import datetime, timezone

from core.adaptive_cognition import ExecutivePlanStatus
from core.llm_provider import LLMRequest
from core.memory_planning_evidence import (
    METADATA_KEY,
    MemoryPlanningEvidence,
    decode_memory_planning_evidence,
    encode_memory_planning_evidence,
)
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)
from core.planning_runtime_integration import PlanningRuntimeContributor
from tests.test_m192_planning_runtime_integration import Source, plan

NOW = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)


def _planning(request: LLMRequest, *, owner: str = "Carlos"):
    return PlanningRuntimeContributor(Source(plan(owner=owner))).contribute(
        owner=owner,
        session_id="main",
        text="Planificá el viaje en tren",
        request=request,
        now=NOW,
    )


def _evidence(*, owner: str = "Carlos") -> MemoryPlanningEvidence:
    return MemoryPlanningEvidence(
        memory_id="private:7",
        owner=owner,
        scope="private",
        content="Para viajes largos prefiero ir en tren.",
        category="user_preference",
        confidence=0.95,
        recall_score=0.82,
        provenance="governed_human_approved_learning",
    )


def test_recalled_memory_materially_changes_planning_contribution(tmp_path) -> None:
    runtime = MemoryRuntimeIntegration(MemoryRuntimeConfig(root_path=tmp_path))
    runtime.store_governed_learning(
        owner="Carlos",
        text="Prefiero ejecutar Ruff antes de pytest.",
        confidence=0.95,
        metadata={"source": "cci-04"},
        idempotency_key="cci-04-validation-preference",
    )
    base = LLMRequest(prompt="Planificá la validación con Ruff y pytest")
    enriched = runtime.enrich(
        owner="Carlos",
        text="Planificá la validación con Ruff y pytest",
        request=base,
    )
    without_memory = _planning(base)
    with_memory = _planning(enriched.request)
    assert without_memory.prompt_lines != with_memory.prompt_lines
    assert any("ruff" in line and "pytest" in line for line in with_memory.prompt_lines)
    assert "recalled_memory_planning_evidence_applied" in with_memory.rationale
    assert enriched.recalled_memory_ids[0] in with_memory.reference_ids


def test_no_recall_preserves_baseline_planning(tmp_path) -> None:
    runtime = MemoryRuntimeIntegration(MemoryRuntimeConfig(root_path=tmp_path))
    base = LLMRequest(prompt="Planificá la auditoría")
    enriched = runtime.enrich(
        owner="Carlos",
        text="Planificá la auditoría",
        request=base,
    )
    assert enriched.recalled_count == 0
    assert _planning(base) == _planning(enriched.request)


def test_owner_mismatch_memory_evidence_is_ignored() -> None:
    metadata = {
        METADATA_KEY: encode_memory_planning_evidence(
            (_evidence(owner="Cristina"),)
        )
    }
    result = _planning(LLMRequest(prompt="Planificá", metadata=metadata))
    assert "recalled_memory_planning_evidence_applied" not in result.rationale


def test_malformed_memory_evidence_fails_closed() -> None:
    request = LLMRequest(prompt="Planificá", metadata={METADATA_KEY: "not-json"})
    result = _planning(request)
    assert "recalled_memory_planning_evidence_applied" not in result.rationale


def test_memory_planning_evidence_is_advisory_only() -> None:
    item = _evidence()
    assert item.read_only
    assert not item.creates_goals
    assert not item.executes_actions
    assert not item.writes_memory


def test_memory_evidence_requires_provenance() -> None:
    values = _evidence().__dict__ | {"provenance": ""}
    try:
        MemoryPlanningEvidence(**values)
    except ValueError as exc:
        assert "provenance" in str(exc)
    else:
        raise AssertionError("missing provenance must fail closed")


def test_decoding_preserves_memory_identity_and_scope() -> None:
    item = _evidence()
    decoded = decode_memory_planning_evidence(
        {METADATA_KEY: encode_memory_planning_evidence((item,))},
        owner="Carlos",
    )
    assert decoded == (item,)
    assert decoded[0].memory_id == "private:7"
    assert decoded[0].scope == "private"


def test_memory_evidence_does_not_change_plan_authority() -> None:
    metadata = {METADATA_KEY: encode_memory_planning_evidence((_evidence(),))}
    result = _planning(LLMRequest(prompt="Planificá", metadata=metadata))
    assert result.status.value == "applied"
    assert any("no ejecutar" in line.lower() for line in result.prompt_lines)
    assert plan().normalized_status is ExecutivePlanStatus.APPROVED
