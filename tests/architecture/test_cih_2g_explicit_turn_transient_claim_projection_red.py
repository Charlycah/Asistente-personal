from datetime import datetime, timezone

from core.governed_reasoning import (
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ExplicitTurnPropositionGroundingStatus,
    ExplicitTurnTransientClaimProjectionStatus,
    GovernedBoundedExplicitTurnPropositionGrounder,
    GovernedExplicitTurnTransientClaimProjector,
)

NOW = datetime(2026, 9, 13, 19, 0, tzinfo=timezone.utc)
TEXT = "Mañana viene alguien a casa y todavía me falta organizar varias cosas."


def _ground(text: str = TEXT, *, scope: str = "session-1"):
    return GovernedBoundedExplicitTurnPropositionGrounder().ground(
        text,
        source_reference="turn-1",
        scope_reference=scope,
    )


def test_cih_2g_projects_only_exact_transient_human_hypotheses() -> None:
    grounding = _ground()

    projection = GovernedExplicitTurnTransientClaimProjector().project(
        grounding=grounding,
        scope_reference="session-1",
        owner="owner-1",
        created_at=NOW,
    )

    assert projection.status is ExplicitTurnTransientClaimProjectionStatus.PROJECTED
    assert len(projection.claims) == len(grounding.propositions) == 2
    for proposition, claim in zip(
        grounding.propositions, projection.claims, strict=True
    ):
        assert claim.subject == proposition.subject
        assert claim.predicate == proposition.predicate
        assert claim.object_value == proposition.object_value
        assert claim.normalized_type is ClaimType.HYPOTHESIS
        assert claim.normalized_origin is ClaimOrigin.HUMAN
        assert claim.normalized_status is ClaimStatus.PROPOSED
        assert claim.evidence_links == ()
        assert claim.confidence is None
        assert claim.rule_reference is None
    assert projection.canonical_authority == "governed_reasoning"
    assert projection.read_only is True
    assert projection.session_local is True
    assert projection.transient is True
    assert projection.persists_results is False
    assert projection.registers_claims is False
    assert projection.authorizes_inference is False


def test_cih_2g_projection_is_deterministic_for_same_episode() -> None:
    grounding = _ground()
    projector = GovernedExplicitTurnTransientClaimProjector()

    first = projector.project(
        grounding=grounding,
        scope_reference="session-1",
        owner="owner-1",
        created_at=NOW,
    )
    second = projector.project(
        grounding=grounding,
        scope_reference="session-1",
        owner="owner-1",
        created_at=NOW,
    )

    assert [item.claim_id for item in first.claims] == [
        item.claim_id for item in second.claims
    ]
    assert first.source_fingerprint == second.source_fingerprint


def test_cih_2g_non_grounded_input_fails_closed() -> None:
    projector = GovernedExplicitTurnTransientClaimProjector()
    cases = (
        ("", ExplicitTurnTransientClaimProjectionStatus.INSUFFICIENT),
        ("¿Viene Juan mañana?", ExplicitTurnTransientClaimProjectionStatus.UNSUPPORTED),
        ("Ella viene mañana.", ExplicitTurnTransientClaimProjectionStatus.AMBIGUOUS),
    )

    for text, expected in cases:
        grounding = _ground(text)
        assert grounding.status is not ExplicitTurnPropositionGroundingStatus.GROUNDED
        projection = projector.project(
            grounding=grounding,
            scope_reference="session-1",
            owner="owner-1",
            created_at=NOW,
        )
        assert projection.status is expected
        assert projection.claims == ()


def test_cih_2g_scope_mismatch_fails_closed() -> None:
    projection = GovernedExplicitTurnTransientClaimProjector().project(
        grounding=_ground(scope="session-1"),
        scope_reference="session-2",
        owner="owner-1",
        created_at=NOW,
    )

    assert (
        projection.status is ExplicitTurnTransientClaimProjectionStatus.SCOPE_MISMATCH
    )
    assert projection.claims == ()


def test_cih_2g_projection_rejects_naive_timestamp_and_blank_owner() -> None:
    grounding = _ground()
    projector = GovernedExplicitTurnTransientClaimProjector()

    for owner, created_at in (
        ("", NOW),
        ("owner-1", datetime(2026, 9, 13, 19, 0)),
    ):
        try:
            projector.project(
                grounding=grounding,
                scope_reference="session-1",
                owner=owner,
                created_at=created_at,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("invalid projection identity/time must fail closed")
