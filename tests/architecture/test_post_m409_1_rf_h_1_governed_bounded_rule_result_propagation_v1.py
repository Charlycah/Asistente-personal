from __future__ import annotations

from datetime import datetime, timedelta, timezone

from core.governed_reasoning import (
    Claim,
    ClaimCondition,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ContextAssemblyStatus,
    GovernedInferenceEngine,
    InferenceRule,
    InferenceStatus,
    ReasoningContextBundle,
    ReasoningQuery,
)
from core.scope_guard import ScopeDomain, ScopeGuardManager

NOW = datetime(2026, 8, 18, 18, 30, tzinfo=timezone.utc)
SCOPE = "session:rf-h-1"


class _OrderedRegistry:
    def __init__(self, rules: tuple[InferenceRule, ...]) -> None:
        self._rules = rules

    def register(self, rule: InferenceRule) -> InferenceRule:
        raise AssertionError("read-only test registry")

    def get(self, rule_id: str, version: str | None = None) -> InferenceRule | None:
        for rule in self._rules:
            if rule.rule_id == rule_id and (version is None or rule.version == version):
                return rule
        return None

    def list(self) -> tuple[InferenceRule, ...]:
        return self._rules


def test_neral_result_can_feed_velar_once_inside_same_inference_run() -> None:
    run = _infer(
        (
            _neral(scope_reference=SCOPE),
            _velar(valid_until=NOW + timedelta(minutes=30)),
        ),
        _base_context(),
    )
    neral = _result(run, "rf-h.neral")
    velar = _result(run, "rf-h.velar")

    assert neral.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert neral.output_claim is not None
    assert neral.output_claim.subject == "reconstruct_experiment"
    assert neral.output_claim.object_value == "unavailable"

    assert velar.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert velar.output_claim is not None
    assert velar.output_claim.subject == "reproduce_experiment"
    assert velar.output_claim.object_value == "unavailable"
    assert neral.output_claim.claim_id in velar.input_claim_ids


def test_propagated_review_required_input_cannot_be_epistemically_strengthened(
) -> None:
    source = _neral(requires_review=True)
    target = _velar(requires_review=False)
    run = _infer((source, target), _base_context())
    result = _result(run, target.rule_id)

    assert result.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert result.output_claim is not None
    assert result.output_claim.normalized_status is ClaimStatus.REVIEW_REQUIRED


def test_only_one_additional_pass_is_allowed_no_a_to_b_to_c() -> None:
    run = _infer((_neral(), _velar(), _third_hop()), _base_context())

    assert _result(run, "rf-h.neral").output_claim is not None
    assert _result(run, "rf-h.velar").output_claim is not None
    third = _result(run, "rf-h.third")
    assert third.normalized_status is InferenceStatus.NOT_APPLICABLE
    assert third.output_claim is None


def test_registry_order_does_not_control_propagation() -> None:
    context = _base_context()
    source_first = _infer((_neral(), _velar()), context)
    target_first = _infer((_velar(), _neral()), context)

    for run in (source_first, target_first):
        result = _result(run, "rf-h.velar")
        assert result.normalized_status is InferenceStatus.REVIEW_REQUIRED
        assert result.output_claim is not None
        assert result.output_claim.subject == "reproduce_experiment"

    assert _result(source_first, "rf-h.velar") == _result(target_first, "rf-h.velar")


def test_missing_source_premise_prevents_velar_propagation() -> None:
    context = _base_context(include_resource_unavailable=False)
    run = _infer((_neral(), _velar()), context)

    assert (
        _result(run, "rf-h.neral").normalized_status
        is InferenceStatus.NOT_APPLICABLE
    )
    assert (
        _result(run, "rf-h.velar").normalized_status
        is InferenceStatus.NOT_APPLICABLE
    )


def test_cross_scope_source_rule_cannot_propagate() -> None:
    source = _neral(scope_reference="session:other")
    run = _infer((source, _velar()), _base_context(), scope_reference=SCOPE)

    assert _result(run, source.rule_id).normalized_status is InferenceStatus.REJECTED
    assert (
        _result(run, "rf-h.velar").normalized_status
        is InferenceStatus.NOT_APPLICABLE
    )


def test_expired_source_rule_cannot_propagate() -> None:
    source = _neral(valid_until=NOW)
    run = _infer((source, _velar()), _base_context(), now=NOW)

    assert _result(run, source.rule_id).normalized_status is InferenceStatus.REJECTED
    assert (
        _result(run, "rf-h.velar").normalized_status
        is InferenceStatus.NOT_APPLICABLE
    )


def test_expired_target_rule_stays_rejected_even_when_source_applies() -> None:
    target = _velar(valid_until=NOW)
    run = _infer((_neral(), target), _base_context(), now=NOW)

    assert _result(run, "rf-h.neral").output_claim is not None
    assert _result(run, target.rule_id).normalized_status is InferenceStatus.REJECTED
    assert _result(run, target.rule_id).output_claim is None


def test_existing_semantically_identical_claim_is_not_reinjected() -> None:
    context = _base_context(include_reconstruct_unavailable=True)
    run = _infer((_neral(), _velar()), context)
    velar = _result(run, "rf-h.velar")

    assert velar.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert velar.input_claim_ids == tuple(
        sorted(("explicit-required-for", "explicit-reconstruct-unavailable"))
    )


def test_original_context_remains_unchanged_after_bounded_propagation() -> None:
    context = _base_context()
    claims_before = context.claims
    context_id_before = context.context_id

    run = _infer((_neral(), _velar()), context)

    assert _result(run, "rf-h.velar").output_claim is not None
    assert context.claims == claims_before
    assert context.context_id == context_id_before
    assert all(
        claim.normalized_type is not ClaimType.RULE_RESULT
        for claim in context.claims
    )


def test_base_outputs_are_deduplicated_for_propagation_inputs() -> None:
    duplicate = InferenceRule(
        rule_id="rf-h.neral-duplicate",
        version="1.0.0",
        description="Second bounded source with same concrete conclusion.",
        conditions=_neral().conditions,
        conclusion_subject="reconstruct_experiment",
        conclusion_predicate="ctx-predicate-capability",
        conclusion_object="unavailable",
        allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        base_confidence=0.6,
        requires_review=True,
    )
    run = _infer((_neral(), duplicate, _velar()), _base_context())
    velar = _result(run, "rf-h.velar")

    propagated_ids = [
        claim_id
        for claim_id in velar.input_claim_ids
        if claim_id not in {"explicit-required-for"}
    ]
    assert len(propagated_ids) == 1


def test_non_applicable_and_rejected_results_never_become_propagation_inputs() -> None:
    context = _base_context(include_resource_unavailable=False)
    run = _infer((_neral(), _velar()), context)
    velar = _result(run, "rf-h.velar")

    assert velar.input_claim_ids == ()
    assert velar.output_claim is None


def _infer(
    rules: tuple[InferenceRule, ...],
    context: ReasoningContextBundle,
    *,
    now: datetime = NOW,
    scope_reference: str = SCOPE,
):
    return GovernedInferenceEngine(_OrderedRegistry(rules)).infer(
        context,
        now=now,
        scope_reference=scope_reference,
    )


def _result(run, rule_id: str):
    return next(item for item in run.results if item.rule_id == rule_id)


def _neral(
    *,
    requires_review: bool = True,
    scope_reference: str | None = None,
    valid_until: datetime | None = None,
) -> InferenceRule:
    temporary = scope_reference is not None or valid_until is not None
    resolved_scope = (scope_reference or SCOPE) if temporary else None
    valid_from = NOW - timedelta(minutes=1) if temporary else None
    resolved_until = valid_until or (NOW + timedelta(minutes=30) if temporary else None)
    return InferenceRule(
        rule_id="rf-h.neral",
        version="1.0.0",
        description="Concrete bounded Neral source rule.",
        conditions=(
            ClaimCondition(
                "ctx-predicate-dependency",
                values=("exclusive",),
                subject="researcher",
            ),
            ClaimCondition(
                "ctx-predicate-availability",
                values=("unavailable",),
                subject="encrypted_record",
            ),
            ClaimCondition(
                "ctx-predicate-alternative",
                values=("false",),
                subject="researcher",
            ),
        ),
        conclusion_subject="reconstruct_experiment",
        conclusion_predicate="ctx-predicate-capability",
        conclusion_object="unavailable",
        allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        base_confidence=0.7,
        requires_review=requires_review,
        source_fingerprint="a" * 64 if temporary else None,
        scope_reference=resolved_scope,
        valid_from=valid_from,
        valid_until=resolved_until,
        temporary=temporary,
    )


def _velar(
    *,
    requires_review: bool = True,
    valid_until: datetime | None = None,
) -> InferenceRule:
    temporary = valid_until is not None
    return InferenceRule(
        rule_id="rf-h.velar",
        version="1.0.0",
        description="Concrete bounded Velar target rule.",
        conditions=(
            ClaimCondition(
                "ctx-predicate-required-for",
                values=("reproduce_experiment",),
                subject="reconstruct_experiment",
            ),
            ClaimCondition(
                "ctx-predicate-capability",
                values=("unavailable",),
                subject="reconstruct_experiment",
            ),
        ),
        conclusion_subject="reproduce_experiment",
        conclusion_predicate="ctx-predicate-capability",
        conclusion_object="unavailable",
        allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        base_confidence=0.65,
        requires_review=requires_review,
        source_fingerprint="b" * 64 if temporary else None,
        scope_reference=SCOPE if temporary else None,
        valid_from=NOW - timedelta(minutes=1) if temporary else None,
        valid_until=valid_until,
        temporary=temporary,
    )


def _third_hop() -> InferenceRule:
    return InferenceRule(
        rule_id="rf-h.third",
        version="1.0.0",
        description="Third-hop control that must remain outside v1 propagation.",
        conditions=(
            ClaimCondition(
                "ctx-predicate-capability",
                values=("unavailable",),
                subject="reproduce_experiment",
            ),
        ),
        conclusion_subject="publish_experiment",
        conclusion_predicate="ctx-predicate-capability",
        conclusion_object="unavailable",
        allowed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        requires_review=True,
    )


def _claim(claim_id: str, subject: str, predicate: str, value: str) -> Claim:
    return Claim(
        subject=subject,
        predicate=predicate,
        object_value=value,
        claim_type=ClaimType.HYPOTHESIS,
        origin=ClaimOrigin.HUMAN,
        status=ClaimStatus.PROPOSED,
        owner="shared",
        created_at=NOW,
        claim_id=claim_id,
    )


def _base_context(
    *,
    include_resource_unavailable: bool = True,
    include_reconstruct_unavailable: bool = False,
) -> ReasoningContextBundle:
    claims = [
        _claim(
            "explicit-dependency",
            "researcher",
            "ctx-predicate-dependency",
            "exclusive",
        ),
        _claim(
            "explicit-alternative",
            "researcher",
            "ctx-predicate-alternative",
            "false",
        ),
        _claim(
            "explicit-required-for",
            "reconstruct_experiment",
            "ctx-predicate-required-for",
            "reproduce_experiment",
        ),
    ]
    if include_resource_unavailable:
        claims.append(
            _claim(
                "explicit-record-unavailable",
                "encrypted_record",
                "ctx-predicate-availability",
                "unavailable",
            )
        )
    if include_reconstruct_unavailable:
        claims.append(
            _claim(
                "explicit-reconstruct-unavailable",
                "reconstruct_experiment",
                "ctx-predicate-capability",
                "unavailable",
            )
        )
    query = ReasoningQuery(
        "rf-h bounded propagation",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        as_of=NOW,
    )
    scope = (
        ScopeGuardManager()
        .observe_turn(
            "rf-h bounded propagation",
            proposed_domains=(ScopeDomain.PERSONAL_OPERATIONS,),
            now=NOW,
        )
        .decision
    )
    return ReasoningContextBundle(
        query=query,
        status=ContextAssemblyStatus.READY,
        scope_decision=scope,
        claims=tuple(claims),
        evidence=(),
        decisions=(),
        created_at=NOW,
    )
