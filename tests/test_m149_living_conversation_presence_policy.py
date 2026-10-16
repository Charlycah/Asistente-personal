from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.living_conversation_presence_awareness import (
    LivingConversationPresenceAwarenessKind,
    LivingConversationPresenceAwarenessStatus,
)
from core.living_conversation_presence_policy import (
    InMemoryLivingConversationPresencePolicyRepository,
    LivingConversationPresenceEligibility,
    LivingConversationPresencePolicy,
    LivingConversationPresencePolicyAction,
    LivingConversationPresencePolicyConfig,
    LivingConversationPresencePolicyRequest,
    LivingConversationPresencePolicyStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m148_living_conversation_presence_awareness import assess as awareness


def request(*, results=(), owner="Carlos", **changes):
    if not results:
        results = (awareness(),)
    values = {"owner": owner, "awareness_results": results}
    values.update(changes)
    return LivingConversationPresencePolicyRequest(**values)


def evaluate(*, results=(), owner="Carlos", config=None, now=NOW, **changes):
    return LivingConversationPresencePolicy(config=config).evaluate(
        request(results=results, owner=owner, **changes), now=now
    )


def awareness_with_kind(kind: LivingConversationPresenceAwarenessKind):
    source = awareness()
    flags = {
        LivingConversationPresenceAwarenessKind.STABLE: (True, False, False, False),
        LivingConversationPresenceAwarenessKind.TRANSITIONAL: (
            False,
            True,
            False,
            False,
        ),
        LivingConversationPresenceAwarenessKind.UNCERTAIN: (False, False, True, False),
        LivingConversationPresenceAwarenessKind.INTERRUPTED: (
            False,
            False,
            False,
            True,
        ),
    }[kind]
    state = replace(
        source.states[0],
        awareness_kind=kind,
        stable_presence=flags[0],
        transition_present=flags[1],
        uncertainty_present=flags[2],
        continuity_interrupted=flags[3],
        state_id="",
    )
    return replace(source, states=(state,), awareness_id="")


def partial_awareness():
    source = awareness()
    state = replace(source.states[0], partial_context=True, state_id="")
    return replace(
        source,
        status=LivingConversationPresenceAwarenessStatus.AWARE_PARTIAL,
        partial_context=True,
        states=(state,),
        awareness_id="",
    )


def test_stable_awareness_is_eligible():
    result = evaluate()
    assert result.status is LivingConversationPresencePolicyStatus.ELIGIBLE
    assert result.action is LivingConversationPresencePolicyAction.MARK_ELIGIBLE
    assert result.presence_context_eligible
    assert not result.presence_context_inhibited


def test_partial_stable_awareness_is_partially_eligible():
    result = evaluate(results=(partial_awareness(),))
    assert result.status is LivingConversationPresencePolicyStatus.ELIGIBLE_PARTIAL
    assert (
        result.action is LivingConversationPresencePolicyAction.MARK_PARTIALLY_ELIGIBLE
    )
    assert result.partial_context


@pytest.mark.parametrize(
    ("kind", "eligibility"),
    [
        (
            LivingConversationPresenceAwarenessKind.STABLE,
            LivingConversationPresenceEligibility.ELIGIBLE,
        ),
        (
            LivingConversationPresenceAwarenessKind.TRANSITIONAL,
            LivingConversationPresenceEligibility.INHIBITED_TRANSITION,
        ),
        (
            LivingConversationPresenceAwarenessKind.UNCERTAIN,
            LivingConversationPresenceEligibility.INHIBITED_UNCERTAINTY,
        ),
        (
            LivingConversationPresenceAwarenessKind.INTERRUPTED,
            LivingConversationPresenceEligibility.INHIBITED_INTERRUPTION,
        ),
    ],
)
def test_awareness_kind_maps_to_policy(kind, eligibility):
    result = evaluate(results=(awareness_with_kind(kind),))
    assert result.evaluations[0].eligibility is eligibility


@pytest.mark.parametrize(
    "kind",
    [
        LivingConversationPresenceAwarenessKind.TRANSITIONAL,
        LivingConversationPresenceAwarenessKind.UNCERTAIN,
        LivingConversationPresenceAwarenessKind.INTERRUPTED,
    ],
)
def test_non_stable_awareness_is_inhibited(kind):
    result = evaluate(results=(awareness_with_kind(kind),))
    assert result.status is LivingConversationPresencePolicyStatus.INHIBITED
    assert result.action is LivingConversationPresencePolicyAction.INHIBIT
    assert result.presence_context_inhibited
    assert not result.presence_context_eligible


def test_policy_not_declared_is_not_applicable():
    assert (
        evaluate(policy_declared=False).status
        is LivingConversationPresencePolicyStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        evaluate(owner="Other").status is LivingConversationPresencePolicyStatus.BLOCKED
    )


def test_empty_awareness_is_not_applicable():
    req = LivingConversationPresencePolicyRequest(owner="Carlos", awareness_results=())
    result = LivingConversationPresencePolicy().evaluate(req, now=NOW)
    assert result.status is LivingConversationPresencePolicyStatus.NOT_APPLICABLE


def test_inactive_awareness_is_not_applicable():
    source = awareness(awareness_declared=False)
    assert (
        evaluate(results=(source,)).status
        is LivingConversationPresencePolicyStatus.NOT_APPLICABLE
    )


def test_result_limit_is_enforced():
    source = awareness()
    result = evaluate(
        results=(source, source),
        config=LivingConversationPresencePolicyConfig(maximum_awareness_results=1),
    )
    assert result.status is LivingConversationPresencePolicyStatus.BLOCKED


def test_stale_awareness_requires_review():
    source = replace(awareness(), created_at=NOW - timedelta(hours=3), awareness_id="")
    assert (
        evaluate(results=(source,)).status
        is LivingConversationPresencePolicyStatus.REVIEW_REQUIRED
    )


def test_future_awareness_requires_review():
    source = replace(
        awareness(), created_at=NOW + timedelta(minutes=1), awareness_id=""
    )
    assert (
        evaluate(results=(source,)).status
        is LivingConversationPresencePolicyStatus.REVIEW_REQUIRED
    )


def test_low_confidence_requires_review():
    source = replace(awareness(), confidence=0.69, awareness_id="")
    assert (
        evaluate(results=(source,)).status
        is LivingConversationPresencePolicyStatus.REVIEW_REQUIRED
    )


def test_partial_awareness_can_require_review():
    result = evaluate(
        results=(partial_awareness(),),
        config=LivingConversationPresencePolicyConfig(allow_partial_context=False),
    )
    assert result.status is LivingConversationPresencePolicyStatus.REVIEW_REQUIRED


def test_latest_awareness_is_selected():
    old = awareness()
    new = replace(old, created_at=NOW + timedelta(minutes=1), awareness_id="")
    result = evaluate(results=(old, new), now=NOW + timedelta(minutes=2))
    assert result.source_awareness is new


def test_duplicate_awareness_is_deduplicated():
    source = awareness()
    assert evaluate(results=(source, source)).source_awareness is source


def test_source_awareness_is_preserved_exactly():
    source = awareness()
    assert evaluate(results=(source,)).source_awareness is source


def test_source_state_is_preserved_exactly():
    source = awareness()
    assert evaluate(results=(source,)).evaluations[0].source_state is source.states[0]


def test_confidence_is_bounded_by_source():
    result = evaluate()
    assert result.confidence <= result.source_awareness.confidence


def test_policy_id_is_deterministic():
    req = request()
    first = LivingConversationPresencePolicy().evaluate(req, now=NOW)
    second = LivingConversationPresencePolicy().evaluate(req, now=NOW)
    assert first.policy_id == second.policy_id


def test_evaluation_id_is_deterministic():
    assert (
        evaluate().evaluations[0].evaluation_id
        == evaluate().evaluations[0].evaluation_id
    )


def test_repository_stores_result():
    repository = InMemoryLivingConversationPresencePolicyRepository()
    result = LivingConversationPresencePolicy(repository=repository).evaluate(
        request(), now=NOW
    )
    assert repository.get(result.policy_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryLivingConversationPresencePolicyRepository()
    result = LivingConversationPresencePolicy(repository=repository).evaluate(
        request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        evaluate().confidence = 0.1


def test_evaluation_is_immutable():
    with pytest.raises(FrozenInstanceError):
        evaluate().evaluations[0].confidence = 0.1


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        LivingConversationPresencePolicyRequest(owner=owner, awareness_results=())


def test_owner_is_trimmed():
    assert request(owner=" Carlos ").owner == "Carlos"


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        LivingConversationPresencePolicy().evaluate(
            request(), now=NOW.replace(tzinfo=None)
        )


@pytest.mark.parametrize("value", [0, -1])
def test_invalid_result_limit_is_rejected(value):
    with pytest.raises(ValueError, match="limit"):
        LivingConversationPresencePolicyConfig(maximum_awareness_results=value)


def test_invalid_age_is_rejected():
    with pytest.raises(ValueError, match="age"):
        LivingConversationPresencePolicyConfig(maximum_result_age=timedelta(0))


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_confidence_is_rejected(value):
    with pytest.raises(ValueError, match="confidence"):
        LivingConversationPresencePolicyConfig(minimum_confidence=value)


def test_review_requires_confirmation():
    source = replace(awareness(), confidence=0.1, awareness_id="")
    assert evaluate(results=(source,)).confirmation_required


def test_eligible_does_not_require_confirmation():
    assert not evaluate().confirmation_required


def test_inhibited_does_not_require_confirmation():
    result = evaluate(
        results=(
            awareness_with_kind(LivingConversationPresenceAwarenessKind.UNCERTAIN),
        )
    )
    assert not result.confirmation_required


def test_inhibited_result_does_not_claim_partial_context():
    source = partial_awareness()
    state = replace(
        source.states[0],
        awareness_kind=LivingConversationPresenceAwarenessKind.UNCERTAIN,
        stable_presence=False,
        uncertainty_present=True,
        state_id="",
    )
    source = replace(source, states=(state,), awareness_id="")
    result = evaluate(results=(source,))
    assert result.status is LivingConversationPresencePolicyStatus.INHIBITED
    assert not result.partial_context


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
def test_downstream_capabilities_remain_forbidden(field):
    assert getattr(evaluate(), field) is False


def test_policy_only_marks_eligibility_not_conversation_decision():
    result = evaluate()
    assert result.presence_context_eligible
    assert not result.conversation_decision_allowed
    assert not result.conversational_activation_allowed


def test_inhibition_rationale_is_explicit():
    result = evaluate(
        results=(
            awareness_with_kind(LivingConversationPresenceAwarenessKind.INTERRUPTED),
        )
    )
    assert result.rationale == ("presence_context_inhibited",)
