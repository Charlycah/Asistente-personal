from datetime import datetime, timezone

from core.governed_reasoning import (
    BoundedSituationalHypothesisStatus,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    GovernedBoundedExplicitTurnPropositionGrounder,
    GovernedBoundedSituationalHypothesisFormer,
    GovernedExplicitTurnContextualClaimGrouper,
    GovernedExplicitTurnTransientClaimProjector,
    GovernedSituationalHypothesisTransientClaimProjector,
    SituationalHypothesisTransientClaimProjectionStatus,
)

NOW = datetime(2026, 9, 13, 22, 0, tzinfo=timezone.utc)
OWNER = "owner:cih-2o"
SCOPE = "session:cih-2o"
SOURCE = "conversation:cih-2o/turn:1"
WITNESS = "Mañana viene alguien a casa y todavía me falta organizar varias cosas."


def _hypothesis(text: str = WITNESS):
    grounding = GovernedBoundedExplicitTurnPropositionGrounder().ground(
        text, source_reference=SOURCE, scope_reference=SCOPE
    )
    projection = GovernedExplicitTurnTransientClaimProjector().project(
        grounding=grounding,
        scope_reference=SCOPE,
        owner=OWNER,
        created_at=NOW,
    )
    grouping = GovernedExplicitTurnContextualClaimGrouper().group(
        projection=projection
    )
    hypothesis = GovernedBoundedSituationalHypothesisFormer().form(
        grouping=grouping,
        projection=projection,
    )
    return hypothesis


def test_cih_2o_projects_modal_system_hypothesis_claim() -> None:
    hypothesis = _hypothesis()
    result = GovernedSituationalHypothesisTransientClaimProjector().project(
        hypothesis=hypothesis,
        owner=OWNER,
        created_at=NOW,
    )

    assert (
        result.status
        is SituationalHypothesisTransientClaimProjectionStatus.PROJECTED
    )
    assert result.claim is not None
    assert result.claim.subject == "current_turn_situation"
    assert result.claim.predicate == "may_be"
    assert result.claim.object_value == "organization_related"
    assert result.claim.normalized_type is ClaimType.HYPOTHESIS
    assert result.claim.normalized_origin is ClaimOrigin.SYSTEM
    assert result.claim.normalized_status is ClaimStatus.PROPOSED
    assert result.claim.evidence_links == ()
    assert result.claim.confidence is None
    assert result.claim.rule_reference is None


def test_cih_2o_preserves_full_situational_hypothesis_lineage() -> None:
    hypothesis = _hypothesis()
    result = GovernedSituationalHypothesisTransientClaimProjector().project(
        hypothesis=hypothesis,
        owner=OWNER,
        created_at=NOW,
    )

    assert result.source_hypothesis_id == hypothesis.hypothesis_id
    assert result.source_hypothesis_fingerprint == hypothesis.source_fingerprint
    assert (
        result.source_grouping_fingerprint
        == hypothesis.source_grouping_fingerprint
    )
    assert (
        result.source_projection_fingerprint
        == hypothesis.source_projection_fingerprint
    )
    assert result.source_claim_ids == hypothesis.source_claim_ids
    assert (
        result.semantic_support_claim_ids
        == hypothesis.semantic_support_claim_ids
    )


def test_cih_2o_is_deterministic_for_same_hypothesis_and_owner() -> None:
    hypothesis = _hypothesis()
    projector = GovernedSituationalHypothesisTransientClaimProjector()
    first = projector.project(hypothesis=hypothesis, owner=OWNER, created_at=NOW)
    later = projector.project(
        hypothesis=hypothesis,
        owner=OWNER,
        created_at=datetime(2026, 9, 13, 22, 5, tzinfo=timezone.utc),
    )

    assert first.claim is not None and later.claim is not None
    assert first.claim.claim_id == later.claim.claim_id
    assert first.claim.fingerprint == later.claim.fingerprint
    assert first.source_fingerprint == later.source_fingerprint


def test_cih_2o_fails_closed_for_non_formed_hypothesis() -> None:
    hypothesis = _hypothesis(
        "Mañana viene alguien a casa y mañana viene otra persona a casa."
    )
    assert hypothesis.status is not BoundedSituationalHypothesisStatus.FORMED

    result = GovernedSituationalHypothesisTransientClaimProjector().project(
        hypothesis=hypothesis,
        owner=OWNER,
        created_at=NOW,
    )
    assert (
        result.status
        is not SituationalHypothesisTransientClaimProjectionStatus.PROJECTED
    )
    assert result.claim is None


def test_cih_2o_creates_only_transient_claim_object_without_authority_effects() -> None:
    result = GovernedSituationalHypothesisTransientClaimProjector().project(
        hypothesis=_hypothesis(),
        owner=OWNER,
        created_at=NOW,
    )

    assert result.creates_claims is True
    assert result.registers_claims is False
    assert result.creates_evidence is False
    assert result.registers_evidence is False
    assert result.establishes_truth is False
    assert result.establishes_falsity is False
    assert result.establishes_causality is False
    assert result.infers_intent is False
    assert result.infers_need is False
    assert result.infers_priority is False
    assert result.infers_action is False
    assert result.registers_rules is False
    assert result.authorizes_inference is False
    assert result.authorizes_action is False
    assert result.executes_actions is False
    assert result.persists_results is False
    assert result.modifies_memory is False
    assert result.modifies_learning is False
    assert result.modifies_world_model is False
    assert result.modifies_planning is False
    assert result.uses_provider is False
    assert result.uses_retrieval is False
    assert result.grants_authority is False
    assert result.starts_background_process is False
