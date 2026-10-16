from datetime import datetime, timezone

from core.governed_reasoning import (
    ExplicitTurnContextualGroupingStatus,
    ExplicitTurnContextualRelation,
    ExplicitTurnTransientClaimProjectionStatus,
    GovernedBoundedExplicitTurnPropositionGrounder,
    GovernedExplicitTurnContextualClaimGrouper,
    GovernedExplicitTurnTransientClaimProjector,
)

NOW = datetime(2026, 9, 13, 20, 45, tzinfo=timezone.utc)
SCOPE = "session:cih-2k"
SOURCE = "conversation:cih-2k/turn:1"
OWNER = "owner:cih-2k"
WITNESS = "Mañana viene alguien a casa y todavía me falta organizar varias cosas."


def _projection(text: str = WITNESS):
    grounding = GovernedBoundedExplicitTurnPropositionGrounder().ground(
        text,
        source_reference=SOURCE,
        scope_reference=SCOPE,
    )
    return GovernedExplicitTurnTransientClaimProjector().project(
        grounding=grounding,
        scope_reference=SCOPE,
        owner=OWNER,
        created_at=NOW,
    )


def test_cih_2k_groups_all_and_only_same_projection_claims() -> None:
    projection = _projection()
    assert projection.status is ExplicitTurnTransientClaimProjectionStatus.PROJECTED
    assert len(projection.claims) == 2

    grouping = GovernedExplicitTurnContextualClaimGrouper().group(
        projection=projection
    )

    assert grouping.status is ExplicitTurnContextualGroupingStatus.GROUPED
    assert (
        grouping.relation
        is ExplicitTurnContextualRelation.CO_PRESENT_IN_CURRENT_TURN
    )
    assert grouping.member_claim_ids == tuple(
        claim.claim_id for claim in projection.claims
    )
    assert grouping.source_reference == projection.source_reference
    assert grouping.scope_reference == projection.scope_reference
    assert (
        grouping.source_grounding_fingerprint
        == projection.source_grounding_fingerprint
    )
    assert grouping.source_projection_fingerprint == projection.source_fingerprint
    assert grouping.canonical_authority == "governed_reasoning"
    assert grouping.read_only is True
    assert grouping.session_local is True
    assert grouping.transient is True
    assert grouping.persists_results is False
    assert grouping.creates_claims is False
    assert grouping.registers_claims is False
    assert grouping.registers_rule is False
    assert grouping.establishes_truth is False
    assert grouping.establishes_causality is False
    assert grouping.infers_intent is False
    assert grouping.infers_need is False
    assert grouping.infers_priority is False
    assert grouping.infers_action is False
    assert grouping.authorizes_inference is False
    assert grouping.authorizes_action is False


def test_cih_2k_grouping_is_deterministic_for_same_projection() -> None:
    projection = _projection()
    grouper = GovernedExplicitTurnContextualClaimGrouper()

    first = grouper.group(projection=projection)
    second = grouper.group(projection=projection)

    assert first.member_claim_ids == second.member_claim_ids
    assert first.source_fingerprint == second.source_fingerprint


def test_cih_2k_single_claim_is_insufficient_and_does_not_fake_relation() -> None:
    projection = _projection("Mañana viene alguien a casa.")
    assert projection.status is ExplicitTurnTransientClaimProjectionStatus.PROJECTED
    assert len(projection.claims) == 1

    grouping = GovernedExplicitTurnContextualClaimGrouper().group(
        projection=projection
    )

    assert grouping.status is ExplicitTurnContextualGroupingStatus.INSUFFICIENT
    assert grouping.relation is None
    assert grouping.member_claim_ids == ()


def test_cih_2k_non_projected_inputs_preserve_fail_closed_status() -> None:
    cases = (
        ("", ExplicitTurnContextualGroupingStatus.INSUFFICIENT),
        ("¿Viene Juan mañana?", ExplicitTurnContextualGroupingStatus.UNSUPPORTED),
        ("Ella viene mañana.", ExplicitTurnContextualGroupingStatus.AMBIGUOUS),
    )
    grouper = GovernedExplicitTurnContextualClaimGrouper()

    for text, expected in cases:
        projection = _projection(text)
        grouping = grouper.group(projection=projection)

        assert grouping.status is expected
        assert grouping.relation is None
        assert grouping.member_claim_ids == ()


def test_cih_2k_grouping_never_creates_semantic_or_executive_effects() -> None:
    grouping = GovernedExplicitTurnContextualClaimGrouper().group(
        projection=_projection()
    )

    assert grouping.creates_evidence is False
    assert grouping.establishes_falsity is False
    assert grouping.infers_goal is False
    assert grouping.creates_memory is False
    assert grouping.modifies_memory is False
    assert grouping.creates_learning_candidate is False
    assert grouping.modifies_learning is False
    assert grouping.modifies_world_model is False
    assert grouping.uses_provider is False
    assert grouping.uses_retrieval is False
    assert grouping.executes_actions is False
    assert grouping.grants_authority is False
    assert grouping.starts_background_process is False
