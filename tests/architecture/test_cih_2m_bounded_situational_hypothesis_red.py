from datetime import datetime, timezone

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning import (
    BoundedSituationalHypothesisKind,
    BoundedSituationalHypothesisStatus,
    GovernedBoundedExplicitTurnPropositionGrounder,
    GovernedBoundedSituationalHypothesisFormer,
    GovernedExplicitTurnContextualClaimGrouper,
    GovernedExplicitTurnTransientClaimProjector,
)

NOW = datetime(2026, 9, 13, 21, 30, tzinfo=timezone.utc)
SCOPE = "session:cih-2m"
SOURCE = "conversation:cih-2m/turn:1"
OWNER = "owner:cih-2m"
WITNESS = "Mañana viene alguien a casa y todavía me falta organizar varias cosas."


def _inputs(text: str = WITNESS):
    grounding = GovernedBoundedExplicitTurnPropositionGrounder().ground(
        text, source_reference=SOURCE, scope_reference=SCOPE
    )
    projection = GovernedExplicitTurnTransientClaimProjector().project(
        grounding=grounding, scope_reference=SCOPE, owner=OWNER, created_at=NOW
    )
    grouping = GovernedExplicitTurnContextualClaimGrouper().group(
        projection=projection
    )
    return grouping, projection


def test_cih_2m_forms_only_bounded_organization_hypothesis() -> None:
    grouping, projection = _inputs()
    result = GovernedBoundedSituationalHypothesisFormer().form(
        grouping=grouping, projection=projection
    )

    assert result.status is BoundedSituationalHypothesisStatus.FORMED
    assert (
        result.situational_kind
        is BoundedSituationalHypothesisKind.ORGANIZATION_RELATED
    )
    assert result.epistemic_level is EpistemicLevel.HYPOTHESIS
    assert result.source_claim_ids == tuple(c.claim_id for c in projection.claims)
    support = tuple(
        c.claim_id
        for c in projection.claims
        if c.predicate == "falta_organizar"
    )
    assert result.semantic_support_claim_ids == support
    assert len(support) == 1
    assert "may describe an organization-related situation" in result.proposition
    assert result.establishes_truth is False
    assert result.establishes_causality is False
    assert result.infers_intent is False
    assert result.infers_need is False
    assert result.infers_priority is False
    assert result.infers_action is False
    assert result.creates_claims is False
    assert result.registers_rules is False
    assert result.authorizes_inference is False
    assert result.authorizes_action is False


def test_cih_2m_is_deterministic_for_same_inputs() -> None:
    grouping, projection = _inputs()
    former = GovernedBoundedSituationalHypothesisFormer()
    first = former.form(grouping=grouping, projection=projection)
    second = former.form(grouping=grouping, projection=projection)
    assert first.hypothesis_id == second.hypothesis_id
    assert first.source_fingerprint == second.source_fingerprint


def test_cih_2m_fails_closed_without_explicit_semantic_support() -> None:
    grouping, projection = _inputs(
        "Mañana viene alguien a casa y mañana viene otra persona a casa."
    )
    result = GovernedBoundedSituationalHypothesisFormer().form(
        grouping=grouping, projection=projection
    )
    assert result.status is not BoundedSituationalHypothesisStatus.FORMED
    assert result.situational_kind is None
    assert result.semantic_support_claim_ids == ()


def test_cih_2m_rejects_lineage_mismatch() -> None:
    grouping, _ = _inputs()
    _, other_projection = _inputs(
        "Mañana viene alguien a casa y todavía me falta organizar documentos."
    )
    result = GovernedBoundedSituationalHypothesisFormer().form(
        grouping=grouping, projection=other_projection
    )
    assert result.status is BoundedSituationalHypothesisStatus.UNSUPPORTED
    assert result.situational_kind is None


def test_cih_2m_never_creates_operational_or_persistent_effects() -> None:
    grouping, projection = _inputs()
    result = GovernedBoundedSituationalHypothesisFormer().form(
        grouping=grouping, projection=projection
    )
    assert result.read_only is True
    assert result.session_local is True
    assert result.transient is True
    assert result.consultative is True
    assert result.persists_results is False
    assert result.creates_facts is False
    assert result.modifies_memory is False
    assert result.modifies_learning is False
    assert result.modifies_world_model is False
    assert result.modifies_planning is False
    assert result.uses_provider is False
    assert result.uses_retrieval is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False
