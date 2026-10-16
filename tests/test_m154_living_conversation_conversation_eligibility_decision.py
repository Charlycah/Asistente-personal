from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.living_conversation_conversation_eligibility_decision import (
    InMemoryLivingConversationConversationEligibilityDecisionRepository,
    LivingConversationConversationEligibilityDecision,
    LivingConversationConversationEligibilityDecisionAction,
    LivingConversationConversationEligibilityDecisionConfig,
    LivingConversationConversationEligibilityDecisionRequest,
    LivingConversationConversationEligibilityDecisionStatus,
)
from core.living_conversation_conversation_readiness import (
    LivingConversationConversationReadinessStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m153_living_conversation_conversation_readiness import (
    assess as readiness,
)
from tests.test_m153_living_conversation_conversation_readiness import (
    deferred_selection,
    partial_selection,
)


def partial_readiness():
    return readiness(results=(partial_selection(),))


def not_ready():
    return readiness(results=(deferred_selection(),))


def request(*, results=(), owner="Carlos", **changes):
    if not results:
        results = (readiness(),)
    values = {"owner": owner, "readiness_results": results}
    values.update(changes)
    return LivingConversationConversationEligibilityDecisionRequest(**values)


def assess(*, results=(), owner="Carlos", config=None, now=NOW, **changes):
    return LivingConversationConversationEligibilityDecision(config=config).evaluate(
        request(results=results, owner=owner, **changes), now=now
    )


def test_ready_is_eligible():
    result = assess()
    assert (
        result.status
        is LivingConversationConversationEligibilityDecisionStatus.ELIGIBLE
    )
    assert (
        result.action
        is LivingConversationConversationEligibilityDecisionAction.DECLARE_ELIGIBLE
    )
    assert result.eligible
    assert not result.partial_context
    assert not result.not_eligible


def test_partial_ready_is_partially_eligible():
    result = assess(results=(partial_readiness(),))
    assert (
        result.status
        is LivingConversationConversationEligibilityDecisionStatus.ELIGIBLE_PARTIAL
    )
    assert result.action is (
        LivingConversationConversationEligibilityDecisionAction.DECLARE_ELIGIBLE_PARTIAL
    )
    assert result.eligible
    assert result.partial_context


def test_not_ready_is_not_eligible():
    result = assess(results=(not_ready(),))
    assert (
        result.status
        is LivingConversationConversationEligibilityDecisionStatus.NOT_ELIGIBLE
    )
    assert (
        result.action
        is LivingConversationConversationEligibilityDecisionAction.DECLARE_NOT_ELIGIBLE
    )
    assert result.not_eligible
    assert not result.eligible


def test_ready_beats_partial_and_not_ready():
    full = readiness()
    result = assess(results=(not_ready(), partial_readiness(), full))
    assert result.selected_readiness is full


def test_partial_beats_not_ready():
    partial = partial_readiness()
    assert assess(results=(not_ready(), partial)).selected_readiness is partial


def test_confidence_breaks_same_status_tie():
    low = readiness()
    high = replace(low, confidence=0.95, readiness_id="")
    assert assess(results=(low, high)).selected_readiness is high


def test_recency_breaks_same_status_and_confidence_tie():
    old = readiness()
    new = replace(old, created_at=NOW + timedelta(minutes=1), readiness_id="")
    result = assess(results=(old, new), now=NOW + timedelta(minutes=2))
    assert result.selected_readiness is new


def test_not_requested_is_not_applicable():
    assert (
        assess(decision_requested=False).status
        is LivingConversationConversationEligibilityDecisionStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        assess(owner="Other").status
        is LivingConversationConversationEligibilityDecisionStatus.BLOCKED
    )


def test_empty_input_is_not_applicable():
    result = LivingConversationConversationEligibilityDecision().evaluate(
        LivingConversationConversationEligibilityDecisionRequest(
            owner="Carlos", readiness_results=()
        ),
        now=NOW,
    )
    assert (
        result.status
        is LivingConversationConversationEligibilityDecisionStatus.NOT_APPLICABLE
    )


def test_result_limit_is_enforced():
    source = readiness()
    result = assess(
        results=(source, source),
        config=LivingConversationConversationEligibilityDecisionConfig(
            maximum_readiness_results=1
        ),
    )
    assert (
        result.status is LivingConversationConversationEligibilityDecisionStatus.BLOCKED
    )


def test_stale_only_requires_review():
    source = replace(readiness(), created_at=NOW - timedelta(hours=3), readiness_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationConversationEligibilityDecisionStatus.REVIEW_REQUIRED
    )


def test_future_only_requires_review():
    source = replace(
        readiness(), created_at=NOW + timedelta(minutes=1), readiness_id=""
    )
    assert (
        assess(results=(source,)).status
        is LivingConversationConversationEligibilityDecisionStatus.REVIEW_REQUIRED
    )


def test_low_confidence_only_requires_review():
    source = replace(readiness(), confidence=0.69, readiness_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationConversationEligibilityDecisionStatus.REVIEW_REQUIRED
    )


def test_partial_can_require_review():
    result = assess(
        results=(partial_readiness(),),
        config=LivingConversationConversationEligibilityDecisionConfig(
            allow_partial_context=False
        ),
    )
    assert (
        result.status
        is LivingConversationConversationEligibilityDecisionStatus.REVIEW_REQUIRED
    )


def test_duplicate_is_deduplicated():
    source = readiness()
    assert assess(results=(source, source)).selected_readiness is source


def test_sources_are_preserved_exactly():
    source = readiness()
    result = assess(results=(source,))
    assert result.selected_readiness is source
    assert result.selected_opportunity is source.selected_opportunity


def test_confidence_is_source_confidence():
    result = assess()
    assert result.confidence == result.selected_readiness.confidence


def test_id_is_deterministic():
    req = request()
    first = LivingConversationConversationEligibilityDecision().evaluate(req, now=NOW)
    second = LivingConversationConversationEligibilityDecision().evaluate(req, now=NOW)
    assert first.decision_id == second.decision_id


def test_repository_round_trip():
    repository = InMemoryLivingConversationConversationEligibilityDecisionRepository()
    result = LivingConversationConversationEligibilityDecision(
        repository=repository
    ).evaluate(request(), now=NOW)
    assert repository.get(result.decision_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryLivingConversationConversationEligibilityDecisionRepository()
    result = LivingConversationConversationEligibilityDecision(
        repository=repository
    ).evaluate(request(), now=NOW)
    with pytest.raises(ValueError):
        repository.add(result)


def test_request_normalizes_owner_and_tuple():
    source = readiness()
    req = LivingConversationConversationEligibilityDecisionRequest(
        owner=" Carlos ", readiness_results=[source]
    )
    assert req.owner == "Carlos"
    assert req.readiness_results == (source,)


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError):
        LivingConversationConversationEligibilityDecisionRequest(
            owner=" ", readiness_results=()
        )


@pytest.mark.parametrize(
    "field",
    [
        "conversation_start_allowed",
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


def test_result_is_frozen():
    result = assess()
    with pytest.raises(FrozenInstanceError):
        result.eligible = False


def test_config_rejects_nonpositive_limit():
    with pytest.raises(ValueError):
        LivingConversationConversationEligibilityDecisionConfig(
            maximum_readiness_results=0
        )


def test_config_rejects_nonpositive_age():
    with pytest.raises(ValueError):
        LivingConversationConversationEligibilityDecisionConfig(
            maximum_result_age=timedelta(0)
        )


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_config_rejects_invalid_confidence(confidence):
    with pytest.raises(ValueError):
        LivingConversationConversationEligibilityDecisionConfig(
            minimum_confidence=confidence
        )


def test_naive_evaluation_time_is_rejected():
    with pytest.raises(ValueError):
        LivingConversationConversationEligibilityDecision().evaluate(
            request(), now=NOW.replace(tzinfo=None)
        )


def test_review_requires_confirmation():
    source = replace(readiness(), confidence=0.1, readiness_id="")
    assert assess(results=(source,)).confirmation_required


def test_eligible_does_not_require_confirmation():
    assert not assess().confirmation_required


def test_not_ready_status_is_preserved_as_not_eligible_source():
    source = not_ready()
    result = assess(results=(source,))
    assert source.status is LivingConversationConversationReadinessStatus.NOT_READY
    assert result.selected_readiness is source
    assert result.not_eligible


def test_eligible_rationale_is_explicit():
    assert assess().rationale == (
        "ready_presence_opportunity_is_eligible_for_decision_pipeline",
    )


def test_partial_rationale_is_explicit():
    assert assess(results=(partial_readiness(),)).rationale == (
        "partial_readiness_is_partially_eligible_for_decision_pipeline",
    )


def test_not_eligible_rationale_is_explicit():
    assert assess(results=(not_ready(),)).rationale == (
        "not_ready_presence_opportunity_is_not_eligible",
    )
