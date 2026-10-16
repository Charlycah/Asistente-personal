from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.living_conversation_conversation_timing_evaluation import (
    InMemoryLivingConversationConversationTimingEvaluationRepository,
    LivingConversationConversationTimingEvaluation,
    LivingConversationConversationTimingEvaluationAction,
    LivingConversationConversationTimingEvaluationConfig,
    LivingConversationConversationTimingEvaluationRequest,
    LivingConversationConversationTimingEvaluationStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m155_living_conversation_conversation_candidate import (
    build as candidate,
)
from tests.test_m155_living_conversation_conversation_candidate import (
    not_eligible_decision,
    partial_decision,
)


def partial_candidate():
    return candidate(results=(partial_decision(),))


def withheld_candidate():
    return candidate(results=(not_eligible_decision(),))


def request(*, results=(), owner="Carlos", **changes):
    if not results:
        results = (candidate(),)
    values = {"owner": owner, "candidate_results": results}
    values.update(changes)
    return LivingConversationConversationTimingEvaluationRequest(**values)


def evaluate(*, results=(), owner="Carlos", config=None, now=NOW, **changes):
    return LivingConversationConversationTimingEvaluation(config=config).evaluate(
        request(results=results, owner=owner, **changes), now=now
    )


def test_full_candidate_is_timely_now():
    result = evaluate()
    assert result.status is LivingConversationConversationTimingEvaluationStatus.TIMELY
    assert (
        result.action
        is LivingConversationConversationTimingEvaluationAction.DECLARE_TIMELY
    )
    assert result.timely_now


def test_partial_candidate_is_timely_partial():
    result = evaluate(results=(partial_candidate(),))
    assert (
        result.status
        is LivingConversationConversationTimingEvaluationStatus.TIMELY_PARTIAL
    )
    assert result.partial_context


def test_withheld_candidate_is_not_timely():
    result = evaluate(results=(withheld_candidate(),))
    assert (
        result.status is LivingConversationConversationTimingEvaluationStatus.NOT_TIMELY
    )
    assert result.not_timely


def test_future_window_defers():
    result = evaluate(not_before=NOW + timedelta(minutes=10))
    assert (
        result.status is LivingConversationConversationTimingEvaluationStatus.DEFERRED
    )
    assert result.deferred


def test_expired_window_is_not_timely():
    result = evaluate(expires_at=NOW - timedelta(seconds=1))
    assert (
        result.status is LivingConversationConversationTimingEvaluationStatus.NOT_TIMELY
    )


def test_window_boundaries_are_inclusive():
    assert evaluate(not_before=NOW).timely_now
    assert evaluate(expires_at=NOW).timely_now


def test_full_beats_partial_and_withheld():
    full = candidate()
    result = evaluate(results=(withheld_candidate(), partial_candidate(), full))
    assert result.selected_candidate is full


def test_partial_beats_withheld():
    partial = partial_candidate()
    assert (
        evaluate(results=(withheld_candidate(), partial)).selected_candidate is partial
    )


def test_confidence_breaks_tie():
    low = candidate()
    high = replace(low, confidence=0.95, candidate_id="")
    assert evaluate(results=(low, high)).selected_candidate is high


def test_recency_breaks_tie():
    old = candidate()
    new = replace(old, created_at=NOW + timedelta(minutes=1), candidate_id="")
    assert (
        evaluate(results=(old, new), now=NOW + timedelta(minutes=2)).selected_candidate
        is new
    )


def test_not_requested_is_not_applicable():
    assert (
        evaluate(evaluation_requested=False).status
        is LivingConversationConversationTimingEvaluationStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        evaluate(owner="Other").status
        is LivingConversationConversationTimingEvaluationStatus.BLOCKED
    )


def test_empty_is_not_applicable():
    req = LivingConversationConversationTimingEvaluationRequest(
        owner="Carlos", candidate_results=()
    )
    assert (
        LivingConversationConversationTimingEvaluation().evaluate(req, now=NOW).status
        is LivingConversationConversationTimingEvaluationStatus.NOT_APPLICABLE
    )


def test_limit_is_enforced():
    source = candidate()
    result = evaluate(
        results=(source, source),
        config=LivingConversationConversationTimingEvaluationConfig(
            maximum_candidate_results=1
        ),
    )
    assert result.status is LivingConversationConversationTimingEvaluationStatus.BLOCKED


@pytest.mark.parametrize(
    "source",
    [
        lambda: replace(
            candidate(), created_at=NOW - timedelta(hours=3), candidate_id=""
        ),
        lambda: replace(
            candidate(), created_at=NOW + timedelta(minutes=1), candidate_id=""
        ),
        lambda: replace(candidate(), confidence=0.69, candidate_id=""),
    ],
)
def test_invalid_source_requires_review(source):
    assert (
        evaluate(results=(source(),)).status
        is LivingConversationConversationTimingEvaluationStatus.REVIEW_REQUIRED
    )


def test_partial_can_require_review():
    result = evaluate(
        results=(partial_candidate(),),
        config=LivingConversationConversationTimingEvaluationConfig(
            allow_partial_context=False
        ),
    )
    assert (
        result.status
        is LivingConversationConversationTimingEvaluationStatus.REVIEW_REQUIRED
    )


def test_duplicate_is_deduplicated():
    source = candidate()
    assert evaluate(results=(source, source)).selected_candidate is source


def test_lineage_is_preserved_exactly():
    source = candidate()
    result = evaluate(results=(source,))
    assert result.selected_candidate is source
    assert result.selected_opportunity is source.selected_opportunity


def test_id_is_deterministic():
    req = request()
    first = LivingConversationConversationTimingEvaluation().evaluate(req, now=NOW)
    second = LivingConversationConversationTimingEvaluation().evaluate(req, now=NOW)
    assert first.timing_evaluation_id == second.timing_evaluation_id


def test_repository_round_trip_and_duplicate_guard():
    repository = InMemoryLivingConversationConversationTimingEvaluationRepository()
    result = LivingConversationConversationTimingEvaluation(
        repository=repository
    ).evaluate(request(), now=NOW)
    assert repository.get(result.timing_evaluation_id) is result
    assert repository.list_all() == (result,)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        evaluate().confidence = 0.1


def test_request_normalizes_owner_and_tuple():
    source = candidate()
    req = LivingConversationConversationTimingEvaluationRequest(
        owner="  Carlos  ", candidate_results=[source]
    )
    assert req.owner == "Carlos"
    assert req.candidate_results == (source,)


@pytest.mark.parametrize("owner", ["", "   "])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        LivingConversationConversationTimingEvaluationRequest(
            owner=owner, candidate_results=()
        )


def test_invalid_window_is_rejected():
    with pytest.raises(ValueError, match="start"):
        request(not_before=NOW + timedelta(minutes=1), expires_at=NOW)


def test_naive_window_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        request(not_before=NOW.replace(tzinfo=None))


@pytest.mark.parametrize(
    "changes",
    [
        {"maximum_candidate_results": 0},
        {"maximum_result_age": timedelta(0)},
        {"minimum_confidence": -0.1},
        {"minimum_confidence": 1.1},
    ],
)
def test_invalid_config_is_rejected(changes):
    with pytest.raises(ValueError):
        LivingConversationConversationTimingEvaluationConfig(**changes)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        LivingConversationConversationTimingEvaluation().evaluate(
            request(), now=NOW.replace(tzinfo=None)
        )


@pytest.mark.parametrize(
    "field",
    [
        "conversation_start_allowed",
        "conversational_activation_allowed",
        "timing_selection_allowed",
        "scheduling_allowed",
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
    assert getattr(evaluate(), field) is False


def test_result_rejects_capability_authorization():
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(evaluate(), scheduling_allowed=True, timing_evaluation_id="")


def test_result_rejects_wrong_id():
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(evaluate(), timing_evaluation_id="wrong")


def test_active_requires_source():
    with pytest.raises(ValueError, match="requires source"):
        replace(evaluate(), selected_candidate=None, timing_evaluation_id="")


def test_inactive_cannot_expose_active_values():
    inactive = evaluate(evaluation_requested=False)
    with pytest.raises(ValueError, match="inactive timing"):
        replace(inactive, confidence=0.8, timing_evaluation_id="")


def test_review_requires_confirmation():
    source = replace(candidate(), confidence=0.1, candidate_id="")
    assert evaluate(results=(source,)).confirmation_required
