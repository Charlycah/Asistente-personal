from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.governed_reasoning import (
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ContextAssemblyStatus,
    ContextualCaseClaimProjectionStatus,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedContextualCaseClaimProjector,
    GovernedContextualCaseRoleGrounder,
    GovernedContextualRuleGroundingCompiler,
    GovernedContextualRuleInstantiator,
    GovernedInferenceEngine,
    GovernedTemporaryConcreteRuleAdmissionBoundary,
    InMemoryInferenceRuleRegistry,
    ReasoningContextBundle,
    ReasoningQuery,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)
from core.scope_guard import ScopeDomain, ScopeGuardManager

SCOPE = "session:case-claim-projection-v1"
RULE_SOURCE = "conversation:case-claim-projection-v1/turn-1"
CASE_SOURCE = "conversation:case-claim-projection-v1/turn-2"
NOW = datetime(2026, 8, 17, 22, 0, tzinfo=timezone.utc)
RULE_TEXT = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)
CASE_TEXT = (
    "La estación depende exclusivamente del sensor T para recibir temperatura. "
    "El sensor T dejó de responder y no existe alternativa."
)


def test_supported_case_projects_exactly_three_contextual_claims() -> None:
    projection = _projection()

    assert projection.normalized_status is ContextualCaseClaimProjectionStatus.PROJECTED
    assert tuple((c.subject, c.object_value) for c in projection.claims) == (
        ("La estación", "exclusive"),
        ("sensor T", "unavailable"),
        ("La estación", "false"),
    )
    assert all(c.predicate.startswith("ctx-predicate-") for c in projection.claims)


def test_projected_claims_preserve_non_authoritative_epistemology() -> None:
    projection = _projection()

    assert all(c.normalized_type is ClaimType.HYPOTHESIS for c in projection.claims)
    assert all(c.normalized_origin is ClaimOrigin.HUMAN for c in projection.claims)
    assert all(c.normalized_status is ClaimStatus.PROPOSED for c in projection.claims)
    assert all(c.owner == "shared" for c in projection.claims)


def test_claim_subjects_come_from_bindings_and_predicates_from_spec() -> None:
    spec = _spec()
    grounding = _ground_case(CASE_TEXT, spec=spec)
    projection = _projector().project(
        spec=spec,
        case_grounding=grounding,
        scope_reference=SCOPE,
        owner="shared",
        created_at=NOW,
    )

    by_role = {item.role_id: item.entity_reference for item in grounding.bindings}
    expected = tuple(
        (by_role[item.role_id], item.predicate_id, item.object_value)
        for item in spec.conditions
    )
    actual = tuple(
        (c.subject, c.predicate, c.object_value) for c in projection.claims
    )
    assert actual == expected


def test_unknown_alternative_produces_no_claims_and_never_false() -> None:
    case = (
        "La estación depende exclusivamente del sensor T para recibir temperatura. "
        "El sensor T dejó de responder."
    )
    grounding = _ground_case(case)
    projection = _projector().project(
        spec=_spec(),
        case_grounding=grounding,
        scope_reference=SCOPE,
        owner="shared",
        created_at=NOW,
    )

    assert (
        projection.normalized_status
        is ContextualCaseClaimProjectionStatus.INSUFFICIENT
    )
    assert projection.claims == ()
    assert "false" not in repr(projection)


def test_ambiguous_or_unsupported_case_projects_no_partial_claims() -> None:
    ambiguous = _ground_case(
        "La estación depende exclusivamente de sensor T y sensor U para recibir "
        "temperatura. El sensor T dejó de responder y no existe alternativa."
    )
    unsupported = _ground_case(
        "La estación depende exclusivamente del sensor T para recibir temperatura. "
        "El sensor T funciona y no existe alternativa."
    )

    for grounding, status in (
        (ambiguous, ContextualCaseClaimProjectionStatus.AMBIGUOUS),
        (unsupported, ContextualCaseClaimProjectionStatus.UNSUPPORTED),
    ):
        result = _projector().project(
            spec=_spec(),
            case_grounding=grounding,
            scope_reference=SCOPE,
            owner="shared",
            created_at=NOW,
        )
        assert result.normalized_status is status
        assert result.claims == ()


def test_scope_and_rule_provenance_mismatch_fail_closed() -> None:
    spec = _spec()
    grounding = _ground_case(CASE_TEXT, spec=spec)
    wrong_rule = replace(grounding, source_rule_candidate_id="rule:other")

    scope_result = _projector().project(
        spec=spec,
        case_grounding=grounding,
        scope_reference="session:other",
        owner="shared",
        created_at=NOW,
    )
    provenance_result = _projector().project(
        spec=spec,
        case_grounding=wrong_rule,
        scope_reference=SCOPE,
        owner="shared",
        created_at=NOW,
    )
    assert (
        scope_result.normalized_status
        is ContextualCaseClaimProjectionStatus.SCOPE_MISMATCH
    )
    assert (
        provenance_result.normalized_status
        is ContextualCaseClaimProjectionStatus.PROVENANCE_MISMATCH
    )
    assert scope_result.claims == provenance_result.claims == ()


def test_projection_is_deterministic_immutable_and_non_authoritative() -> None:
    first = _projection()
    second = _projection()

    assert first.source_fingerprint == second.source_fingerprint
    assert tuple(c.claim_id for c in first.claims) == tuple(
        c.claim_id for c in second.claims
    )
    for name in (
        "persists_results",
        "establishes_truth",
        "creates_memory",
        "modifies_memory",
        "creates_learning_candidate",
        "modifies_learning",
        "modifies_world_model",
        "registers_claims",
        "registers_rule",
        "authorizes_inference",
        "executes_actions",
        "grants_authority",
        "uses_provider",
        "uses_retrieval",
    ):
        assert getattr(first, name) is False
    with pytest.raises(FrozenInstanceError):
        first.scope_reference = "changed"  # type: ignore[misc]


def test_projected_claims_feed_inference_without_projector_invocation() -> None:
    spec = _spec()
    grounding = _ground_case(CASE_TEXT, spec=spec)
    projection = _projector().project(
        spec=spec,
        case_grounding=grounding,
        scope_reference=SCOPE,
        owner="shared",
        created_at=NOW,
    )
    candidate = GovernedContextualRuleInstantiator().instantiate(
        spec=spec,
        bindings=grounding.bindings,
        scope_reference=SCOPE,
    )
    registry = InMemoryInferenceRuleRegistry()
    GovernedTemporaryConcreteRuleAdmissionBoundary().admit(
        candidate=candidate,
        registry=registry,
        scope_reference=SCOPE,
        allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        admitted_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )
    context = _context(projection.claims)
    result = GovernedInferenceEngine(registry).infer(
        context,
        now=NOW + timedelta(minutes=1),
        scope_reference=SCOPE,
    ).results[0]

    assert result.output_claim is not None
    assert result.normalized_status.value == "review_required"


def test_projector_has_no_registry_runtime_provider_or_persistence_wiring() -> None:
    import core.governed_reasoning.contextual_case_claim_projection as module

    path = module.__file__
    assert path is not None
    source = Path(path).read_text(encoding="utf-8")
    for forbidden in (
        "OfficialConversationGateway",
        "InMemoryInferenceRuleRegistry",
        "ClaimRepository",
        "GovernedInferenceEngine",
        "sqlite3",
        "write_text(",
        "llm",
    ):
        assert forbidden not in source


def _spec():
    candidate = GovernedContextualRuleInterpretationProducer().produce(
        RULE_TEXT,
        source_reference=RULE_SOURCE,
        scope_reference=SCOPE,
    )
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=SCOPE,
    )
    compilation = GovernedContextualRuleGroundingCompiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference=SCOPE,
    )
    assert compilation.instantiation_spec is not None
    return compilation.instantiation_spec


def _ground_case(text: str, *, spec=None):
    return GovernedContextualCaseRoleGrounder().ground(
        case_text=text,
        spec=spec or _spec(),
        scope_reference=SCOPE,
        source_reference=CASE_SOURCE,
    )


def _projector() -> GovernedContextualCaseClaimProjector:
    return GovernedContextualCaseClaimProjector()


def _projection():
    spec = _spec()
    return _projector().project(
        spec=spec,
        case_grounding=_ground_case(CASE_TEXT, spec=spec),
        scope_reference=SCOPE,
        owner="shared",
        created_at=NOW,
    )


def _context(claims):
    query = ReasoningQuery(
        "temporary contextual case claims",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        as_of=NOW,
    )
    decision = ScopeGuardManager().observe_turn(
        query.text,
        proposed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        now=NOW,
    ).decision
    return ReasoningContextBundle(
        query=query,
        status=ContextAssemblyStatus.READY,
        scope_decision=decision,
        claims=claims,
        evidence=(),
        decisions=(),
        created_at=NOW,
    )
