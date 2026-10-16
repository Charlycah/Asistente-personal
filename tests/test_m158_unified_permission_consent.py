from dataclasses import FrozenInstanceError, replace
from datetime import timedelta
from functools import lru_cache

import pytest

from core.capability_registry import PermissionScope
from core.cross_context_continuity import (
    CrossContextContinuity,
    CrossContextContinuityRequest,
)
from core.unified_permission_consent import (
    InMemoryUnifiedPermissionConsentRepository,
    PermissionRequirement,
    UnifiedConsentGrant,
    UnifiedPermissionConsent,
    UnifiedPermissionConsentAction,
    UnifiedPermissionConsentConfig,
    UnifiedPermissionConsentRequest,
    UnifiedPermissionConsentStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m157_cross_context_continuity import context, timing


@lru_cache(maxsize=None)
def continuity(*, partial=False, owner="Carlos", now=NOW + timedelta(minutes=3)):
    result = timing(partial=partial, owner=owner)
    request = CrossContextContinuityRequest(
        owner=owner,
        timing_results=(result,),
        source_context=context("desktop:home", owner=owner),
        target_context=context(
            "mobile:walking",
            kind="mobile",
            owner=owner,
            observed_at=NOW + timedelta(minutes=2),
        ),
    )
    return CrossContextContinuity().evaluate(request, now=now)


def requirement(
    name="conversation_presence",
    scope=PermissionScope.DEVICE,
    contexts=(),
    explicit=True,
):
    return PermissionRequirement(name, scope, contexts, explicit)


def grant(
    name="conversation_presence",
    scope=PermissionScope.DEVICE,
    contexts=("desktop:home", "mobile:walking"),
    owner="Carlos",
    **changes,
):
    values = dict(
        grant_id="grant:1",
        owner=owner,
        capability_name=name,
        scope=scope,
        context_ids=contexts,
        granted_at=NOW,
    )
    values.update(changes)
    return UnifiedConsentGrant(**values)


def request(*, results=None, requirements=None, grants=None, owner="Carlos", **changes):
    values = dict(
        owner=owner,
        continuity_results=results
        if results is not None
        else (continuity(owner=owner),),
        requirements=requirements if requirements is not None else (requirement(),),
        grants=grants if grants is not None else (grant(owner=owner),),
    )
    values.update(changes)
    return UnifiedPermissionConsentRequest(**values)


def evaluate(*, config=None, now=NOW + timedelta(minutes=4), **changes):
    return UnifiedPermissionConsent(config=config).evaluate(request(**changes), now=now)


def test_satisfied_permission_consent():
    result = evaluate()
    assert result.status is UnifiedPermissionConsentStatus.SATISFIED
    assert result.action is UnifiedPermissionConsentAction.DECLARE_SATISFIED
    assert result.consent_satisfied
    assert result.matched_grant_ids == ("grant:1",)


def test_partial_continuity_produces_partial_consent():
    result = evaluate(results=(continuity(partial=True),))
    assert result.status is UnifiedPermissionConsentStatus.SATISFIED_PARTIAL
    assert result.partial_consent


def test_partial_continuity_can_require_review():
    result = evaluate(
        results=(continuity(partial=True),),
        config=UnifiedPermissionConsentConfig(allow_partial_continuity=False),
    )
    assert result.status is UnifiedPermissionConsentStatus.REVIEW_REQUIRED


def test_missing_grant_requires_consent():
    result = evaluate(grants=())
    assert result.status is UnifiedPermissionConsentStatus.CONSENT_REQUIRED
    assert result.explicit_consent_required
    assert result.confirmation_required


def test_non_explicit_requirement_is_satisfied_without_grant():
    result = evaluate(requirements=(requirement(explicit=False),), grants=())
    assert result.status is UnifiedPermissionConsentStatus.SATISFIED


def test_explicit_denial_wins():
    result = evaluate(grants=(grant(denied=True),))
    assert result.status is UnifiedPermissionConsentStatus.DENIED
    assert result.consent_denied


def test_revoked_grant_requires_consent():
    assert (
        evaluate(grants=(grant(revoked=True),)).status
        is UnifiedPermissionConsentStatus.CONSENT_REQUIRED
    )


def test_expired_grant_requires_consent():
    item = grant(expires_at=NOW + timedelta(minutes=1))
    assert (
        evaluate(grants=(item,), now=NOW + timedelta(minutes=4)).status
        is UnifiedPermissionConsentStatus.CONSENT_REQUIRED
    )


def test_expiry_boundary_is_inclusive():
    item = grant(expires_at=NOW + timedelta(minutes=4))
    assert evaluate(grants=(item,), now=NOW + timedelta(minutes=4)).consent_satisfied


def test_future_grant_is_not_active():
    item = grant(granted_at=NOW + timedelta(minutes=10))
    assert (
        evaluate(grants=(item,)).status
        is UnifiedPermissionConsentStatus.CONSENT_REQUIRED
    )


def test_wrong_scope_does_not_match():
    assert (
        evaluate(grants=(grant(scope=PermissionScope.READ),)).status
        is UnifiedPermissionConsentStatus.CONSENT_REQUIRED
    )


def test_wrong_capability_does_not_match():
    assert (
        evaluate(grants=(grant(name="camera"),)).status
        is UnifiedPermissionConsentStatus.CONSENT_REQUIRED
    )


def test_context_coverage_is_required():
    assert (
        evaluate(grants=(grant(contexts=("desktop:home",)),)).status
        is UnifiedPermissionConsentStatus.CONSENT_REQUIRED
    )


def test_requirement_can_target_one_context():
    req = requirement(contexts=("desktop:home",))
    result = evaluate(requirements=(req,), grants=(grant(contexts=("desktop:home",)),))
    assert result.consent_satisfied


def test_requirement_outside_continuity_is_blocked():
    result = evaluate(requirements=(requirement(contexts=("car:other",)),))
    assert result.status is UnifiedPermissionConsentStatus.BLOCKED


def test_owner_mismatch_on_continuity_is_blocked():
    result = evaluate(results=(continuity(owner="Other"),))
    assert result.status is UnifiedPermissionConsentStatus.BLOCKED


def test_owner_mismatch_on_grant_is_blocked():
    assert (
        evaluate(grants=(grant(owner="Other"),)).status
        is UnifiedPermissionConsentStatus.BLOCKED
    )


def test_not_requested_is_not_applicable():
    assert (
        evaluate(evaluation_requested=False).status
        is UnifiedPermissionConsentStatus.NOT_APPLICABLE
    )


def test_no_requirements_is_not_applicable():
    assert (
        evaluate(requirements=()).status
        is UnifiedPermissionConsentStatus.NOT_APPLICABLE
    )


def test_no_continuity_is_not_applicable():
    assert evaluate(results=()).status is UnifiedPermissionConsentStatus.NOT_APPLICABLE


def test_stale_continuity_requires_review():
    old = continuity(now=NOW - timedelta(hours=3))
    assert (
        evaluate(results=(old,)).status
        is UnifiedPermissionConsentStatus.REVIEW_REQUIRED
    )


def test_low_confidence_requires_review():
    source = continuity()
    source = replace(source, confidence=0.6, continuity_id="")
    assert (
        evaluate(results=(source,)).status
        is UnifiedPermissionConsentStatus.REVIEW_REQUIRED
    )


def test_duplicate_continuity_is_deduplicated():
    source = continuity()
    result = evaluate(results=(source, source))
    assert result.selected_continuity is source


def test_duplicate_requirement_is_blocked():
    req = requirement()
    assert (
        evaluate(requirements=(req, req)).status
        is UnifiedPermissionConsentStatus.BLOCKED
    )


def test_input_limits_are_enforced():
    config = UnifiedPermissionConsentConfig(maximum_requirements=1)
    result = evaluate(requirements=(requirement("a"), requirement("b")), config=config)
    assert result.status is UnifiedPermissionConsentStatus.BLOCKED


def test_continuity_limit_is_enforced():
    source = continuity()
    result = evaluate(
        results=(source, source),
        config=UnifiedPermissionConsentConfig(maximum_continuity_results=1),
    )
    assert result.status is UnifiedPermissionConsentStatus.BLOCKED


def test_grant_limit_is_enforced():
    grants = (grant(), replace(grant(), grant_id="grant:2"))
    assert (
        evaluate(
            grants=grants, config=UnifiedPermissionConsentConfig(maximum_grants=1)
        ).status
        is UnifiedPermissionConsentStatus.BLOCKED
    )


def test_exact_lineage_is_preserved():
    source = continuity()
    result = evaluate(results=(source,))
    assert result.selected_continuity is source
    assert result.selected_timing_evaluation is source.selected_timing_evaluation
    assert result.selected_candidate is source.selected_candidate
    assert result.selected_opportunity is source.selected_opportunity


def test_all_downstream_authorizations_are_false():
    result = evaluate()
    names = (
        "permission_grant_allowed",
        "consent_prompt_allowed",
        "conversation_start_allowed",
        "conversational_activation_allowed",
        "device_handoff_allowed",
        "context_transfer_allowed",
        "channel_selection_allowed",
        "scheduling_allowed",
        "prompt_generation_allowed",
        "response_realization_allowed",
        "provider_call_allowed",
        "automation_allowed",
        "platform_mutation_allowed",
    )
    assert all(not getattr(result, name) for name in names)


def test_result_is_frozen():
    with pytest.raises(FrozenInstanceError):
        evaluate().confidence = 0.1


def test_requirement_is_frozen():
    with pytest.raises(FrozenInstanceError):
        requirement().capability_name = "x"


def test_grant_is_frozen():
    with pytest.raises(FrozenInstanceError):
        grant().owner = "x"


def test_deterministic_identifier():
    req = request()
    engine = UnifiedPermissionConsent()
    first = engine.evaluate(req, now=NOW + timedelta(minutes=4))
    second = UnifiedPermissionConsent().evaluate(req, now=NOW + timedelta(minutes=4))
    assert first.evaluation_id == second.evaluation_id


def test_repository_round_trip():
    repository = InMemoryUnifiedPermissionConsentRepository()
    result = UnifiedPermissionConsent(repository=repository).evaluate(
        request(), now=NOW + timedelta(minutes=4)
    )
    assert repository.get(result.evaluation_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryUnifiedPermissionConsentRepository()
    engine = UnifiedPermissionConsent(repository=repository)
    req = request()
    engine.evaluate(req, now=NOW + timedelta(minutes=4))
    with pytest.raises(ValueError, match="already exists"):
        engine.evaluate(req, now=NOW + timedelta(minutes=4))


@pytest.mark.parametrize("field", ["capability_name"])
def test_requirement_rejects_blank(field):
    with pytest.raises(ValueError):
        PermissionRequirement(" ", PermissionScope.DEVICE)


def test_requirement_rejects_duplicate_contexts():
    with pytest.raises(ValueError):
        requirement(contexts=("a", "a"))


def test_grant_rejects_empty_contexts():
    with pytest.raises(ValueError):
        grant(contexts=())


def test_grant_rejects_naive_timestamp():
    with pytest.raises(ValueError):
        grant(granted_at=NOW.replace(tzinfo=None))


def test_grant_rejects_expiry_before_grant():
    with pytest.raises(ValueError):
        grant(expires_at=NOW - timedelta(seconds=1))


def test_grant_rejects_denied_and_revoked():
    with pytest.raises(ValueError):
        grant(denied=True, revoked=True)


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError):
        request(owner=" ")


def test_config_rejects_invalid_limits():
    with pytest.raises(ValueError):
        UnifiedPermissionConsentConfig(maximum_grants=0)


def test_config_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        UnifiedPermissionConsentConfig(minimum_confidence=1.1)


def test_config_rejects_invalid_age():
    with pytest.raises(ValueError):
        UnifiedPermissionConsentConfig(maximum_result_age=timedelta(0))


def test_engine_rejects_naive_now():
    with pytest.raises(ValueError):
        UnifiedPermissionConsent().evaluate(request(), now=NOW.replace(tzinfo=None))


def test_multiple_requirements_all_satisfied():
    requirements = (
        requirement("conversation_presence"),
        requirement("microphone", PermissionScope.DEVICE),
    )
    grants = (grant(), grant(name="microphone", grant_id="grant:2"))
    result = evaluate(requirements=requirements, grants=grants)
    assert result.status is UnifiedPermissionConsentStatus.SATISFIED
    assert len(result.satisfied_requirements) == 2


def test_one_missing_requirement_requires_consent():
    requirements = (requirement("conversation_presence"), requirement("microphone"))
    result = evaluate(requirements=requirements, grants=(grant(),))
    assert result.status is UnifiedPermissionConsentStatus.CONSENT_REQUIRED
    assert result.missing_requirements == (requirements[1],)


def test_denial_precedes_missing_requirement():
    requirements = (requirement("conversation_presence"), requirement("microphone"))
    result = evaluate(requirements=requirements, grants=(grant(denied=True),))
    assert result.status is UnifiedPermissionConsentStatus.DENIED


def test_newest_matching_grant_is_selected():
    older = grant(grant_id="old")
    newer = grant(grant_id="new", granted_at=NOW + timedelta(minutes=1))
    result = evaluate(grants=(older, newer))
    assert result.matched_grant_ids == ("new",)


def test_case_insensitive_owner_matching():
    result = evaluate(
        owner="carlos",
        results=(continuity(owner="Carlos"),),
        grants=(grant(owner="CARLOS"),),
    )
    assert result.consent_satisfied


def test_case_insensitive_capability_matching():
    result = evaluate(
        requirements=(requirement("Conversation_Presence"),),
        grants=(grant(name="conversation_presence"),),
    )
    assert result.consent_satisfied
