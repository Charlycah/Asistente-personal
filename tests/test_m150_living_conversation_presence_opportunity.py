from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta

import pytest

from core.living_conversation_presence_opportunity import (
    InMemoryLivingConversationPresenceOpportunityRepository,
    LivingConversationPresenceOpportunity,
    LivingConversationPresenceOpportunityAction,
    LivingConversationPresenceOpportunityConfig,
    LivingConversationPresenceOpportunityKind,
    LivingConversationPresenceOpportunityRequest,
    LivingConversationPresenceOpportunityStatus,
)
from core.living_conversation_presence_policy import (
    LivingConversationPresencePolicyStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m149_living_conversation_presence_policy import evaluate as policy


def request(*, results=(), owner="Carlos", **changes):
    if not results:
        results = (policy(),)
    values = {"owner": owner, "policy_results": results}
    values.update(changes)
    return LivingConversationPresenceOpportunityRequest(**values)


def assess(*, results=(), owner="Carlos", config=None, now=NOW, **changes):
    return LivingConversationPresenceOpportunity(config=config).evaluate(
        request(results=results, owner=owner, **changes), now=now
    )


def partial_policy():
    source = policy()
    return replace(
        source,
        status=LivingConversationPresencePolicyStatus.ELIGIBLE_PARTIAL,
        partial_context=True,
        policy_id="",
    )


def inhibited_policy():
    source = policy()
    return replace(
        source,
        status=LivingConversationPresencePolicyStatus.INHIBITED,
        action="inhibit",
        presence_context_eligible=False,
        presence_context_inhibited=True,
        partial_context=False,
        policy_id="",
    )


def test_eligible_policy_declares_available_opportunity():
    result = assess()
    assert result.status is LivingConversationPresenceOpportunityStatus.AVAILABLE
    assert (
        result.action is LivingConversationPresenceOpportunityAction.DECLARE_AVAILABLE
    )
    assert result.kind is LivingConversationPresenceOpportunityKind.AVAILABLE
    assert result.opportunity_available
    assert not result.opportunity_inhibited


def test_partial_policy_declares_partial_opportunity():
    result = assess(results=(partial_policy(),))
    assert (
        result.status is LivingConversationPresenceOpportunityStatus.AVAILABLE_PARTIAL
    )
    assert result.action is LivingConversationPresenceOpportunityAction.DECLARE_PARTIAL
    assert result.kind is LivingConversationPresenceOpportunityKind.AVAILABLE_PARTIAL
    assert result.partial_context


def test_inhibited_policy_produces_inhibited_opportunity():
    result = assess(results=(inhibited_policy(),))
    assert result.status is LivingConversationPresenceOpportunityStatus.INHIBITED
    assert result.action is LivingConversationPresenceOpportunityAction.INHIBIT
    assert result.kind is LivingConversationPresenceOpportunityKind.INHIBITED_BY_POLICY
    assert result.opportunity_inhibited


def test_not_declared_is_not_applicable():
    assert (
        assess(opportunity_declared=False).status
        is LivingConversationPresenceOpportunityStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        assess(owner="Other").status
        is LivingConversationPresenceOpportunityStatus.BLOCKED
    )


def test_empty_input_is_not_applicable():
    result = LivingConversationPresenceOpportunity().evaluate(
        LivingConversationPresenceOpportunityRequest(owner="Carlos", policy_results=()),
        now=NOW,
    )
    assert result.status is LivingConversationPresenceOpportunityStatus.NOT_APPLICABLE


def test_result_limit_is_enforced():
    source = policy()
    result = assess(
        results=(source, source),
        config=LivingConversationPresenceOpportunityConfig(maximum_policy_results=1),
    )
    assert result.status is LivingConversationPresenceOpportunityStatus.BLOCKED


def test_stale_policy_requires_review():
    source = replace(policy(), created_at=NOW - timedelta(hours=3), policy_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationPresenceOpportunityStatus.REVIEW_REQUIRED
    )


def test_future_policy_requires_review():
    source = replace(policy(), created_at=NOW + timedelta(minutes=1), policy_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationPresenceOpportunityStatus.REVIEW_REQUIRED
    )


def test_low_confidence_requires_review():
    source = replace(policy(), confidence=0.69, policy_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationPresenceOpportunityStatus.REVIEW_REQUIRED
    )


def test_partial_policy_can_require_review():
    result = assess(
        results=(partial_policy(),),
        config=LivingConversationPresenceOpportunityConfig(allow_partial_context=False),
    )
    assert result.status is LivingConversationPresenceOpportunityStatus.REVIEW_REQUIRED


def test_latest_policy_is_selected():
    old = policy()
    new = replace(old, created_at=NOW + timedelta(minutes=1), policy_id="")
    result = assess(results=(old, new), now=NOW + timedelta(minutes=2))
    assert result.source_policy is new


def test_duplicate_policy_is_deduplicated():
    source = policy()
    assert assess(results=(source, source)).source_policy is source


def test_source_policy_is_preserved_exactly():
    source = policy()
    assert assess(results=(source,)).source_policy is source


def test_confidence_is_bounded_by_source():
    result = assess()
    assert result.confidence <= result.source_policy.confidence


def test_opportunity_id_is_deterministic():
    req = request()
    first = LivingConversationPresenceOpportunity().evaluate(req, now=NOW)
    second = LivingConversationPresenceOpportunity().evaluate(req, now=NOW)
    assert first.opportunity_id == second.opportunity_id


def test_repository_round_trip():
    repository = InMemoryLivingConversationPresenceOpportunityRepository()
    result = LivingConversationPresenceOpportunity(repository=repository).evaluate(
        request(), now=NOW
    )
    assert repository.get(result.opportunity_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryLivingConversationPresenceOpportunityRepository()
    result = LivingConversationPresenceOpportunity(repository=repository).evaluate(
        request(), now=NOW
    )
    with pytest.raises(ValueError):
        repository.add(result)


def test_request_normalizes_owner_and_tuple():
    source = policy()
    req = LivingConversationPresenceOpportunityRequest(
        owner=" Carlos ", policy_results=[source]
    )
    assert req.owner == "Carlos"
    assert req.policy_results == (source,)


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError):
        LivingConversationPresenceOpportunityRequest(owner=" ", policy_results=())


@pytest.mark.parametrize(
    "changes",
    [
        {"maximum_policy_results": 0},
        {"maximum_result_age": timedelta(0)},
        {"minimum_confidence": -0.1},
        {"minimum_confidence": 1.1},
    ],
)
def test_invalid_config_is_rejected(changes):
    with pytest.raises(ValueError):
        LivingConversationPresenceOpportunityConfig(**changes)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError):
        assess(now=datetime(2026, 7, 11))


def test_result_is_frozen():
    with pytest.raises(FrozenInstanceError):
        assess().confidence = 0.1


@pytest.mark.parametrize(
    "field",
    [
        "conversation_decision_allowed",
        "conversational_activation_allowed",
        "timing_selection_allowed",
        "prompt_generation_allowed",
        "response_realization_allowed",
        "identity_inference_allowed",
        "activity_inference_allowed",
        "intent_inference_allowed",
        "behavior_adaptation_allowed",
        "provider_call_allowed",
        "automation_allowed",
        "platform_mutation_allowed",
    ],
)
def test_downstream_capabilities_are_forbidden(field):
    assert getattr(assess(), field) is False


@pytest.mark.parametrize(
    ("source_factory", "status", "available", "inhibited"),
    [
        (policy, LivingConversationPresenceOpportunityStatus.AVAILABLE, True, False),
        (
            partial_policy,
            LivingConversationPresenceOpportunityStatus.AVAILABLE_PARTIAL,
            True,
            False,
        ),
        (
            inhibited_policy,
            LivingConversationPresenceOpportunityStatus.INHIBITED,
            False,
            True,
        ),
    ],
)
def test_outcome_flags_are_consistent(source_factory, status, available, inhibited):
    result = assess(results=(source_factory(),))
    assert result.status is status
    assert result.opportunity_available is available
    assert result.opportunity_inhibited is inhibited


def test_review_requires_confirmation():
    source = replace(policy(), confidence=0.1, policy_id="")
    assert assess(results=(source,)).confirmation_required


@pytest.mark.parametrize(
    "status",
    [
        LivingConversationPresencePolicyStatus.REVIEW_REQUIRED,
        LivingConversationPresencePolicyStatus.BLOCKED,
        LivingConversationPresencePolicyStatus.NOT_APPLICABLE,
    ],
)
def test_inactive_policy_results_are_not_consumed(status):
    source = policy()
    source = replace(
        source,
        status=status,
        action="hold"
        if status is LivingConversationPresencePolicyStatus.REVIEW_REQUIRED
        else "withhold"
        if status is LivingConversationPresencePolicyStatus.BLOCKED
        else "none",
        source_awareness=None,
        evaluations=(),
        confidence=0.0,
        presence_context_eligible=False,
        presence_context_inhibited=False,
        partial_context=False,
        confirmation_required=status
        is LivingConversationPresencePolicyStatus.REVIEW_REQUIRED,
        policy_id="",
    )
    assert (
        assess(results=(source,)).status
        is LivingConversationPresenceOpportunityStatus.NOT_APPLICABLE
    )
