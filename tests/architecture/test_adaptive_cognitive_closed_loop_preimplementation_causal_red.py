from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from app.memory_consolidation import OfficialMemoryGateway
from app.official_conversation_gateway import OfficialConversationGateway
from app.productive_governed_learning_wiring import (
    ProductiveGovernedLearningOutcome,
    ProductiveGovernedLearningWiring,
)
from core.cognitive_maturity import CognitiveCycleNodeState
from core.llm_provider import LLMRequest
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)

from .test_cross_capability_memory_planning import _planning
from .test_post_m409_1_governed_learning_productive_end_to_end_wiring_v1 import (
    _response,
)
from .test_post_m409_1_m369_explicit_human_learning_approval_v1 import _evaluation


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


def _later_planning(runtime: MemoryRuntimeIntegration, text: str, *, owner="Carlos"):
    base = LLMRequest(prompt=text)
    enriched = runtime.enrich(owner=owner, text=text, request=base)
    return (
        enriched,
        _planning(base, owner=owner),
        _planning(request=enriched.request, owner=owner),
    )


def test_control_approved_learning_changes_later_planning_evidence(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    learned = _learn(runtime)
    enriched, baseline, later = _later_planning(
        runtime,
        "Antes de entregar, planificá la validación del proyecto con Ruff y pytest.",
    )

    assert learned.outcome is ProductiveGovernedLearningOutcome.STORED
    assert enriched.context_included is True
    assert baseline.prompt_lines != later.prompt_lines
    assert "recalled_memory_planning_evidence_applied" in later.rationale
    assert any("ruff antes de pytest" in line for line in later.prompt_lines)


def test_control_rejected_learning_preserves_later_planning_baseline(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    rejected = _learn(runtime, response_text="No")
    enriched, baseline, later = _later_planning(
        runtime,
        "Antes de entregar, planificá la validación del proyecto con Ruff y pytest.",
    )

    assert rejected.outcome is ProductiveGovernedLearningOutcome.REJECTED
    assert enriched.context_included is False
    assert baseline == later


def test_control_irrelevant_episode_does_not_receive_adaptive_effect(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    _learn(runtime)
    enriched, baseline, later = _later_planning(runtime, "Planificá qué cocinar hoy")

    assert enriched.context_included is False
    assert baseline == later


def test_control_owner_scope_isolation_blocks_cross_owner_effect(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    _learn(runtime)
    enriched, baseline, later = _later_planning(
        runtime,
        "Planificá la validación con Ruff y pytest",
        owner="Cristina",
    )

    assert enriched.context_included is False
    assert baseline == later


def test_control_contextual_transfer_does_not_require_literal_repetition(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    _learn(runtime)
    enriched, baseline, later = _later_planning(
        runtime,
        "Antes de entregar, ¿qué validación debería ejecutar primero?",
    )

    assert enriched.context_included is True
    assert baseline.prompt_lines != later.prompt_lines
    assert any("ruff antes de pytest" in line for line in later.prompt_lines)


def test_control_review_only_candidate_is_never_auto_accepted() -> None:
    candidate = SimpleNamespace(
        disposition="review_required",
        accepted_as_knowledge=False,
        persistence_authorized=False,
    )
    assert candidate.accepted_as_knowledge is False
    assert candidate.persistence_authorized is False


def test_red_post_turn_reflection_exposes_explicit_review_only_learning_candidate() -> (
    None
):
    class Turn:
        response_text = "respuesta"
        response_path = "provider"
        status = "completed"
        session_id = "adaptive-red"

    class Runtime:
        def converse(self, text, now=None):
            return Turn()

    candidate = SimpleNamespace(
        disposition="review_required",
        accepted_as_knowledge=False,
        persistence_authorized=False,
    )
    reflection = SimpleNamespace(
        response_path="provider",
        learning_candidate=candidate,
    )
    gateway = OfficialConversationGateway(Runtime())

    gateway.submit_observed(
        "experiencia evaluable",
        post_turn_observer=lambda _turn: reflection,
    )

    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert (
        cycle.node("post_turn_reflection").state is CognitiveCycleNodeState.PARTICIPATED
    )
    learning = cycle.node("learning_candidate")
    assert learning.state is CognitiveCycleNodeState.PARTICIPATED
    assert learning.evidence_codes == ("learning_candidate:review_required",)
