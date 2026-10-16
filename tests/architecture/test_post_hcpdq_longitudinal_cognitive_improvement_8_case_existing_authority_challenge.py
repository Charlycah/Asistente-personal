from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from app.memory_consolidation import OfficialMemoryGateway
from app.productive_governed_learning_wiring import (
    ProductiveGovernedLearningOutcome,
    ProductiveGovernedLearningWiring,
)
from core.llm_provider import LLMRequest
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)

from .test_cross_capability_memory_planning import _planning
from .test_post_m409_1_governed_learning_productive_end_to_end_wiring_v1 import (
    _response,
)
from .test_post_m409_1_m369_explicit_human_learning_approval_v1 import (
    _evaluation,
)


class LongitudinalDisposition(StrEnum):
    IMPROVED = "improved"
    UNCHANGED = "unchanged"
    NOT_COMPARABLE = "not_comparable"
    CAUSAL_LINEAGE_INSUFFICIENT = "causal_lineage_insufficient"


@dataclass(frozen=True)
class LongitudinalObservation:
    disposition: LongitudinalDisposition
    before_has_learned_constraint: bool
    after_has_learned_constraint: bool
    recalled_memory_ids: tuple[str, ...]
    learning_memory_ids: tuple[str, ...]
    establishes_global_improvement: bool = False
    creates_learning: bool = False
    writes_memory: bool = False
    executes_actions: bool = False


def _runtime(root: Path) -> MemoryRuntimeIntegration:
    return MemoryRuntimeIntegration(MemoryRuntimeConfig(root_path=root))


def _learn(runtime: MemoryRuntimeIntegration, *, response_text: str = "Sí"):
    evaluation = _evaluation()
    wiring = ProductiveGovernedLearningWiring(
        OfficialMemoryGateway(runtime, owner="Carlos")
    )
    return wiring.execute(
        evaluation,
        _response(evaluation, response_text),
        current_turn_text=response_text,
    )


def _planning_pair(
    runtime: MemoryRuntimeIntegration,
    text: str,
    *,
    owner: str = "Carlos",
):
    base = LLMRequest(prompt=text)
    before = _planning(base, owner=owner)
    enriched = runtime.enrich(
        owner=owner,
        text=text,
        request=base,
    )
    after = _planning(enriched.request, owner=owner)
    return enriched, before, after


def _contains_constraint(contribution) -> bool:
    return any(
        "ruff antes de pytest" in line.casefold()
        for line in contribution.prompt_lines
    )


def _observe(
    *,
    learned,
    enriched,
    before,
    after,
) -> LongitudinalObservation:
    learning_ids = tuple(getattr(learned, "stored_memory_ids", ()))
    recalled_ids = tuple(enriched.recalled_memory_ids)
    before_has = _contains_constraint(before)
    after_has = _contains_constraint(after)
    linked = bool(learning_ids) and recalled_ids == learning_ids

    if after == before:
        disposition = LongitudinalDisposition.UNCHANGED
    elif not linked:
        disposition = LongitudinalDisposition.CAUSAL_LINEAGE_INSUFFICIENT
    elif not before_has and after_has:
        disposition = LongitudinalDisposition.IMPROVED
    else:
        disposition = LongitudinalDisposition.NOT_COMPARABLE

    return LongitudinalObservation(
        disposition=disposition,
        before_has_learned_constraint=before_has,
        after_has_learned_constraint=after_has,
        recalled_memory_ids=recalled_ids,
        learning_memory_ids=learning_ids,
    )


def _assert_governed(result: LongitudinalObservation) -> None:
    assert result.establishes_global_improvement is False
    assert result.creates_learning is False
    assert result.writes_memory is False
    assert result.executes_actions is False


def test_lci1_approved_learning_improves_later_same_family_planning(tmp_path):
    runtime = _runtime(tmp_path / "memory")
    learned = _learn(runtime)
    enriched, before, after = _planning_pair(
        runtime,
        "Planificá la validación del proyecto con Ruff y pytest.",
    )
    result = _observe(
        learned=learned,
        enriched=enriched,
        before=before,
        after=after,
    )

    assert learned.outcome is ProductiveGovernedLearningOutcome.STORED
    assert result.disposition is LongitudinalDisposition.IMPROVED
    assert result.before_has_learned_constraint is False
    assert result.after_has_learned_constraint is True
    assert "recalled_memory_planning_evidence_applied" in after.rationale
    _assert_governed(result)


def test_lci2_contextual_rewording_preserves_improvement(tmp_path):
    runtime = _runtime(tmp_path / "memory")
    learned = _learn(runtime)
    enriched, before, after = _planning_pair(
        runtime,
        "Antes de entregar, ¿qué validación debería ejecutar primero?",
    )
    result = _observe(
        learned=learned,
        enriched=enriched,
        before=before,
        after=after,
    )

    assert result.disposition is LongitudinalDisposition.IMPROVED
    assert enriched.recalled_memory_ids == learned.stored_memory_ids
    _assert_governed(result)


def test_lci3_improvement_survives_runtime_reconstruction(tmp_path):
    root = tmp_path / "memory"
    learned = _learn(_runtime(root))
    runtime = _runtime(root)
    enriched, before, after = _planning_pair(
        runtime,
        "Planificá la validación con Ruff y pytest.",
    )
    result = _observe(
        learned=learned,
        enriched=enriched,
        before=before,
        after=after,
    )

    assert result.disposition is LongitudinalDisposition.IMPROVED
    assert enriched.recalled_memory_ids == learned.stored_memory_ids
    _assert_governed(result)


def test_lci4_rejected_learning_cannot_manufacture_improvement(tmp_path):
    runtime = _runtime(tmp_path / "memory")
    rejected = _learn(runtime, response_text="No")
    enriched, before, after = _planning_pair(
        runtime,
        "Planificá la validación con Ruff y pytest.",
    )
    result = _observe(
        learned=rejected,
        enriched=enriched,
        before=before,
        after=after,
    )

    assert rejected.outcome is ProductiveGovernedLearningOutcome.REJECTED
    assert result.disposition is LongitudinalDisposition.UNCHANGED
    assert before == after
    _assert_governed(result)


def test_lci5_irrelevant_learning_does_not_improve_unrelated_family(tmp_path):
    runtime = _runtime(tmp_path / "memory")
    learned = _learn(runtime)
    enriched, before, after = _planning_pair(
        runtime,
        "Planificá qué cocinar hoy.",
    )
    result = _observe(
        learned=learned,
        enriched=enriched,
        before=before,
        after=after,
    )

    assert result.disposition is LongitudinalDisposition.UNCHANGED
    assert enriched.recalled_memory_ids == ()
    assert before == after
    _assert_governed(result)


def test_lci6_owner_isolation_blocks_cross_owner_improvement(tmp_path):
    runtime = _runtime(tmp_path / "memory")
    learned = _learn(runtime)
    enriched, before, after = _planning_pair(
        runtime,
        "Planificá la validación con Ruff y pytest.",
        owner="Cristina",
    )
    result = _observe(
        learned=learned,
        enriched=enriched,
        before=before,
        after=after,
    )

    assert result.disposition is LongitudinalDisposition.UNCHANGED
    assert enriched.recalled_memory_ids == ()
    assert before == after
    _assert_governed(result)


def test_lci7_missing_exact_learning_lineage_cannot_claim_improvement(tmp_path):
    runtime = _runtime(tmp_path / "memory")
    runtime.store_governed_learning(
        owner="Carlos",
        text="Prefiero ejecutar Ruff antes de pytest.",
        confidence=0.95,
        metadata={"source": "unlinked-control"},
        idempotency_key="unlinked-control",
    )
    enriched, before, after = _planning_pair(
        runtime,
        "Planificá la validación con Ruff y pytest.",
    )

    class Unlinked:
        stored_memory_ids = ("private:999",)

    result = _observe(
        learned=Unlinked(),
        enriched=enriched,
        before=before,
        after=after,
    )

    assert _contains_constraint(after) is True
    assert result.disposition is (
        LongitudinalDisposition.CAUSAL_LINEAGE_INSUFFICIENT
    )
    _assert_governed(result)


def test_lci8_local_improvement_never_becomes_global_self_improvement(tmp_path):
    runtime = _runtime(tmp_path / "memory")
    learned = _learn(runtime)
    enriched, before, after = _planning_pair(
        runtime,
        "Planificá la validación con Ruff y pytest.",
    )
    result = _observe(
        learned=learned,
        enriched=enriched,
        before=before,
        after=after,
    )

    assert result.disposition is LongitudinalDisposition.IMPROVED
    assert result.establishes_global_improvement is False
    assert result.creates_learning is False
    assert result.writes_memory is False
    assert result.executes_actions is False
