from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.living_conversation_conversation_readiness import (
    InMemoryLivingConversationConversationReadinessRepository,
    LivingConversationConversationReadiness,
    LivingConversationConversationReadinessAction,
    LivingConversationConversationReadinessConfig,
    LivingConversationConversationReadinessRequest,
    LivingConversationConversationReadinessStatus,
)
from core.living_conversation_opportunity_selection import (
    LivingConversationOpportunitySelectionStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m152_living_conversation_opportunity_selection import (
    assess as selection,
)
from tests.test_m152_living_conversation_opportunity_selection import (
    deferred_prioritization,
    partial_prioritization,
)


def partial_selection():
    return selection(results=(partial_prioritization(),))


def deferred_selection():
    return selection(results=(deferred_prioritization(),))


def request(*, results=(), owner="Carlos", **changes):
    if not results:
        results = (selection(),)
    values = {"owner": owner, "selection_results": results}
    values.update(changes)
    return LivingConversationConversationReadinessRequest(**values)


def assess(*, results=(), owner="Carlos", config=None, now=NOW, **changes):
    return LivingConversationConversationReadiness(config=config).evaluate(
        request(results=results, owner=owner, **changes), now=now
    )


def test_selected_opportunity_is_ready():
    result = assess()
    assert result.status is LivingConversationConversationReadinessStatus.READY
    assert result.action is LivingConversationConversationReadinessAction.DECLARE_READY
    assert result.ready
    assert not result.partial_context
    assert not result.not_ready


def test_partial_selection_is_partially_ready():
    result = assess(results=(partial_selection(),))
    assert result.status is LivingConversationConversationReadinessStatus.READY_PARTIAL
    assert (
        result.action
        is LivingConversationConversationReadinessAction.DECLARE_READY_PARTIAL
    )
    assert result.ready
    assert result.partial_context


def test_deferred_selection_is_not_ready():
    result = assess(results=(deferred_selection(),))
    assert result.status is LivingConversationConversationReadinessStatus.NOT_READY
    assert (
        result.action is LivingConversationConversationReadinessAction.DECLARE_NOT_READY
    )
    assert result.not_ready
    assert not result.ready


def test_full_selection_beats_partial_and_deferred():
    full = selection()
    result = assess(results=(deferred_selection(), partial_selection(), full))
    assert result.selected_selection is full


def test_partial_beats_deferred():
    partial = partial_selection()
    result = assess(results=(deferred_selection(), partial))
    assert result.selected_selection is partial


def test_confidence_breaks_same_status_tie():
    low = selection()
    high = replace(low, confidence=0.95, selection_id="")
    assert assess(results=(low, high)).selected_selection is high


def test_recency_breaks_same_status_and_confidence_tie():
    old = selection()
    new = replace(old, created_at=NOW + timedelta(minutes=1), selection_id="")
    result = assess(results=(old, new), now=NOW + timedelta(minutes=2))
    assert result.selected_selection is new


def test_not_requested_is_not_applicable():
    assert (
        assess(readiness_requested=False).status
        is LivingConversationConversationReadinessStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        assess(owner="Other").status
        is LivingConversationConversationReadinessStatus.BLOCKED
    )


def test_empty_input_is_not_applicable():
    result = LivingConversationConversationReadiness().evaluate(
        LivingConversationConversationReadinessRequest(
            owner="Carlos", selection_results=()
        ),
        now=NOW,
    )
    assert result.status is LivingConversationConversationReadinessStatus.NOT_APPLICABLE


def test_result_limit_is_enforced():
    source = selection()
    result = assess(
        results=(source, source),
        config=LivingConversationConversationReadinessConfig(
            maximum_selection_results=1
        ),
    )
    assert result.status is LivingConversationConversationReadinessStatus.BLOCKED


def test_stale_only_requires_review():
    source = replace(selection(), created_at=NOW - timedelta(hours=3), selection_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationConversationReadinessStatus.REVIEW_REQUIRED
    )


def test_future_only_requires_review():
    source = replace(
        selection(), created_at=NOW + timedelta(minutes=1), selection_id=""
    )
    assert (
        assess(results=(source,)).status
        is LivingConversationConversationReadinessStatus.REVIEW_REQUIRED
    )


def test_low_confidence_only_requires_review():
    source = replace(selection(), confidence=0.69, selection_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationConversationReadinessStatus.REVIEW_REQUIRED
    )


def test_partial_can_require_review():
    result = assess(
        results=(partial_selection(),),
        config=LivingConversationConversationReadinessConfig(
            allow_partial_context=False
        ),
    )
    assert (
        result.status is LivingConversationConversationReadinessStatus.REVIEW_REQUIRED
    )


def test_duplicate_is_deduplicated():
    source = selection()
    assert assess(results=(source, source)).selected_selection is source


def test_sources_are_preserved_exactly():
    source = selection()
    result = assess(results=(source,))
    assert result.selected_selection is source
    assert result.selected_opportunity is source.selected_opportunity


def test_confidence_is_source_confidence():
    result = assess()
    assert result.confidence == result.selected_selection.confidence


def test_id_is_deterministic():
    req = request()
    first = LivingConversationConversationReadiness().evaluate(req, now=NOW)
    second = LivingConversationConversationReadiness().evaluate(req, now=NOW)
    assert first.readiness_id == second.readiness_id


def test_repository_round_trip():
    repository = InMemoryLivingConversationConversationReadinessRepository()
    result = LivingConversationConversationReadiness(repository=repository).evaluate(
        request(), now=NOW
    )
    assert repository.get(result.readiness_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryLivingConversationConversationReadinessRepository()
    result = LivingConversationConversationReadiness(repository=repository).evaluate(
        request(), now=NOW
    )
    with pytest.raises(ValueError):
        repository.add(result)


def test_request_normalizes_owner_and_tuple():
    source = selection()
    req = LivingConversationConversationReadinessRequest(
        owner=" Carlos ", selection_results=[source]
    )
    assert req.owner == "Carlos"
    assert req.selection_results == (source,)


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError):
        LivingConversationConversationReadinessRequest(owner=" ", selection_results=())


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


def test_result_is_frozen():
    result = assess()
    with pytest.raises(FrozenInstanceError):
        result.ready = False


def test_config_rejects_nonpositive_limit():
    with pytest.raises(ValueError):
        LivingConversationConversationReadinessConfig(maximum_selection_results=0)


def test_config_rejects_nonpositive_age():
    with pytest.raises(ValueError):
        LivingConversationConversationReadinessConfig(maximum_result_age=timedelta(0))


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_config_rejects_invalid_confidence(confidence):
    with pytest.raises(ValueError):
        LivingConversationConversationReadinessConfig(minimum_confidence=confidence)


def test_naive_evaluation_time_is_rejected():
    with pytest.raises(ValueError):
        LivingConversationConversationReadiness().evaluate(
            request(), now=NOW.replace(tzinfo=None)
        )


def test_review_requires_confirmation():
    source = replace(selection(), confidence=0.1, selection_id="")
    result = assess(results=(source,))
    assert result.confirmation_required


def test_ready_does_not_require_confirmation():
    assert not assess().confirmation_required


def test_deferred_selection_status_is_preserved_as_not_ready_source():
    source = deferred_selection()
    result = assess(results=(source,))
    assert source.status is LivingConversationOpportunitySelectionStatus.DEFERRED
    assert result.selected_selection is source
    assert result.not_ready


def test_ready_rationale_is_nonempty():
    assert assess().rationale == (
        "selected_presence_opportunity_is_conversation_ready",
    )


def test_partial_rationale_is_explicit():
    assert assess(results=(partial_selection(),)).rationale == (
        "partial_presence_opportunity_is_partially_ready",
    )


def test_not_ready_rationale_is_explicit():
    assert assess(results=(deferred_selection(),)).rationale == (
        "deferred_presence_opportunity_is_not_conversation_ready",
    )
