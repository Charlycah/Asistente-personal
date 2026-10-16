from __future__ import annotations

from datetime import datetime, timezone
from inspect import signature

from app.governed_reasoning_runtime import CanonicalProductiveReasoningSource
from core.cognitive_runtime_orchestration import CognitiveRuntimeOrchestrator
from core.governed_reasoning.orchestrator import GovernedReasoningOrchestrator
from core.reasoning_runtime_integration import ReasoningRuntimeContributor

NOW = datetime(2026, 9, 19, 20, 30, tzinfo=timezone.utc)
VISUAL_ARGUMENT = "visual_context_contribution"


def test_red_r2p_runtime_can_transport_one_same_turn_visual_to_reasoning() -> None:
    """The runtime must have an explicit turn-local visual -> reasoning seam."""
    runtime_parameters = signature(CognitiveRuntimeOrchestrator.enrich).parameters
    reasoning_parameters = signature(ReasoningRuntimeContributor.contribute).parameters

    assert "integrated_visual_context" in runtime_parameters
    assert VISUAL_ARGUMENT in reasoning_parameters


def test_red_r2p_official_reasoning_source_accepts_governed_visual_lineage() -> None:
    """The official source, not a parallel adapter, must admit visual lineage."""
    parameters = signature(CanonicalProductiveReasoningSource.__call__).parameters

    assert VISUAL_ARGUMENT in parameters


def test_red_r2p_reasoning_composes_visual_relation_before_inference() -> None:
    """The canonical reasoning authority must own the pre-inference composition."""
    parameters = signature(GovernedReasoningOrchestrator.reason).parameters

    assert VISUAL_ARGUMENT in parameters


def test_red_r2p_visual_lineage_participates_in_productive_episode_identity() -> None:
    """Different visual lineage must not silently reuse a stale turn episode."""
    from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway

    parameters = signature(
        OfficialGovernedReasoningRuntimeGateway.evaluate_productive_episode
    ).parameters

    assert VISUAL_ARGUMENT in parameters


def test_red_r2p_productive_chain_has_no_parallel_visual_evidence_authority() -> None:
    """Insertion must reuse the already-certified governed-reasoning authority."""
    import core.governed_reasoning.visual_evidence_relation as relation

    assert hasattr(relation, "GovernedVisualEvidenceRelationEvaluator")
    assert not hasattr(relation, "VisualEvidenceRelationManager")
    assert not hasattr(relation, "VisualEvidenceRelationStore")
    assert not hasattr(relation, "VisualEvidenceRelationRegistry")
