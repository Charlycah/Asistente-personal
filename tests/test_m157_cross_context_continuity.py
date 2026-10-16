from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.cross_context_continuity import (
    CrossContextContinuity,
    CrossContextContinuityAction,
    CrossContextContinuityConfig,
    CrossContextContinuityRequest,
    CrossContextContinuityStatus,
    CrossContextKind,
    CrossContextReference,
    InMemoryCrossContextContinuityRepository,
)
from core.living_conversation_conversation_timing_evaluation import (
    LivingConversationConversationTimingEvaluation,
    LivingConversationConversationTimingEvaluationRequest,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m155_living_conversation_conversation_candidate import (
    build as candidate,
)
from tests.test_m155_living_conversation_conversation_candidate import partial_decision


def timing(*, partial=False, now=NOW, owner="Carlos", **changes):
    source = candidate(results=(partial_decision(),)) if partial else candidate()
    request = LivingConversationConversationTimingEvaluationRequest(
        owner=owner,
        candidate_results=(source,),
        **changes,
    )
    return LivingConversationConversationTimingEvaluation().evaluate(request, now=now)


def context(
    context_id,
    *,
    kind=CrossContextKind.DESKTOP,
    owner="Carlos",
    observed_at=NOW,
    device_id=None,
    session_reference_id="session:roby",
    continuity_thread_id="thread:roby",
    available=True,
    authenticated=True,
):
    return CrossContextReference(
        context_id=context_id,
        owner=owner,
        kind=kind,
        observed_at=observed_at,
        device_id=device_id,
        session_reference_id=session_reference_id,
        continuity_thread_id=continuity_thread_id,
        available=available,
        authenticated=authenticated,
    )


def request(*, results=(), owner="Carlos", source=None, target=None, **changes):
    if not results:
        results = (timing(),)
    source = source or context("desktop:home")
    target = target or context(
        "mobile:walking",
        kind=CrossContextKind.MOBILE,
        observed_at=NOW + timedelta(minutes=2),
        device_id="phone",
    )
    values = {
        "owner": owner,
        "timing_results": results,
        "source_context": source,
        "target_context": target,
    }
    values.update(changes)
    return CrossContextContinuityRequest(**values)


def evaluate(*, config=None, now=NOW + timedelta(minutes=3), **changes):
    return CrossContextContinuity(config=config).evaluate(request(**changes), now=now)


def test_cross_context_continuity_is_established():
    result = evaluate()
    assert result.status is CrossContextContinuityStatus.CONTINUOUS
    assert result.action is CrossContextContinuityAction.DECLARE_CONTINUITY
    assert result.continuity_established


def test_partial_timing_establishes_partial_continuity():
    result = evaluate(results=(timing(partial=True),))
    assert result.status is CrossContextContinuityStatus.CONTINUOUS_PARTIAL
    assert result.partial_context


def test_partial_context_can_require_review():
    result = evaluate(
        results=(timing(partial=True),),
        config=CrossContextContinuityConfig(allow_partial_context=False),
    )
    assert result.status is CrossContextContinuityStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_deferred_timing_interrupts_continuity():
    result = evaluate(results=(timing(not_before=NOW + timedelta(minutes=10)),))
    assert result.status is CrossContextContinuityStatus.INTERRUPTED
    assert result.continuity_interrupted


def test_not_timely_interrupts_continuity():
    result = evaluate(results=(timing(expires_at=NOW - timedelta(seconds=1)),))
    assert result.status is CrossContextContinuityStatus.INTERRUPTED


def test_context_gap_exceeded_interrupts():
    result = evaluate(
        target=context(
            "mobile:late",
            kind="mobile",
            observed_at=NOW + timedelta(hours=1),
        )
    )
    assert result.status is CrossContextContinuityStatus.INTERRUPTED
    assert result.rationale == ("cross_context_gap_exceeded",)


def test_gap_boundary_is_inclusive():
    result = evaluate(
        target=context(
            "mobile:boundary",
            kind="mobile",
            observed_at=NOW + timedelta(minutes=30),
        )
    )
    assert result.continuity_established


def test_reverse_temporal_order_interrupts():
    result = evaluate(
        target=context(
            "mobile:past",
            kind="mobile",
            observed_at=NOW - timedelta(seconds=1),
        )
    )
    assert result.status is CrossContextContinuityStatus.INTERRUPTED
    assert result.rationale == ("cross_context_temporal_order_invalid",)


def test_same_context_is_not_applicable():
    source = context("desktop:same")
    result = evaluate(source=source, target=source)
    assert result.status is CrossContextContinuityStatus.NOT_APPLICABLE


def test_not_requested_is_not_applicable():
    assert (
        evaluate(continuity_requested=False).status
        is CrossContextContinuityStatus.NOT_APPLICABLE
    )


def test_empty_results_are_not_applicable():
    req = request(results=(timing(),))
    req = replace(req, timing_results=())
    result = CrossContextContinuity().evaluate(req, now=NOW + timedelta(minutes=3))
    assert result.status is CrossContextContinuityStatus.NOT_APPLICABLE


def test_request_owner_must_match_contexts():
    result = evaluate(source=context("desktop:other", owner="Other"))
    assert result.status is CrossContextContinuityStatus.BLOCKED


def test_request_owner_must_match_timing_result():
    result = evaluate(results=(timing(owner="Other"),))
    assert result.status is CrossContextContinuityStatus.BLOCKED


def test_unauthenticated_context_is_blocked_by_default():
    result = evaluate(target=context("mobile:guest", authenticated=False))
    assert result.status is CrossContextContinuityStatus.BLOCKED


def test_authentication_requirement_can_be_disabled():
    result = evaluate(
        target=context("mobile:guest", authenticated=False),
        config=CrossContextContinuityConfig(require_authenticated_contexts=False),
    )
    assert result.status is CrossContextContinuityStatus.CONTINUOUS


def test_unavailable_context_interrupts_when_lineage_exists():
    result = evaluate(target=context("mobile:offline", available=False))
    assert result.status is CrossContextContinuityStatus.INTERRUPTED


def test_shared_session_can_be_required():
    result = evaluate(
        target=context("mobile:new", session_reference_id="session:new"),
        config=CrossContextContinuityConfig(require_shared_session_reference=True),
    )
    assert result.status is CrossContextContinuityStatus.INTERRUPTED


def test_matching_session_satisfies_requirement():
    result = evaluate(
        config=CrossContextContinuityConfig(require_shared_session_reference=True)
    )
    assert result.continuity_established


def test_missing_session_fails_when_required():
    result = evaluate(
        target=context("mobile:none", session_reference_id=None),
        config=CrossContextContinuityConfig(require_shared_session_reference=True),
    )
    assert result.status is CrossContextContinuityStatus.INTERRUPTED


def test_shared_thread_can_be_required():
    result = evaluate(
        target=context("mobile:new", continuity_thread_id="thread:new"),
        config=CrossContextContinuityConfig(require_shared_continuity_thread=True),
    )
    assert result.status is CrossContextContinuityStatus.INTERRUPTED


def test_matching_thread_satisfies_requirement():
    result = evaluate(
        config=CrossContextContinuityConfig(require_shared_continuity_thread=True)
    )
    assert result.continuity_established


def test_result_limit_is_enforced_before_deduplication():
    source = timing()
    result = evaluate(
        results=(source, source),
        config=CrossContextContinuityConfig(maximum_timing_results=1),
    )
    assert result.status is CrossContextContinuityStatus.BLOCKED


def test_duplicate_results_are_deduplicated():
    source = timing()
    result = evaluate(results=(source, source))
    assert result.selected_timing_evaluation is source


def test_full_timing_beats_partial():
    full = timing()
    partial = timing(partial=True)
    result = evaluate(results=(partial, full))
    assert result.selected_timing_evaluation is full


def test_partial_beats_deferred():
    partial = timing(partial=True)
    deferred = timing(not_before=NOW + timedelta(minutes=10))
    result = evaluate(results=(deferred, partial))
    assert result.selected_timing_evaluation is partial


def test_confidence_breaks_equal_status_tie():
    low = timing()
    high = replace(low, confidence=0.95, timing_evaluation_id="")
    result = evaluate(results=(low, high))
    assert result.selected_timing_evaluation is high


def test_recency_breaks_equal_status_tie():
    old = timing()
    new = replace(
        old,
        created_at=NOW + timedelta(minutes=1),
        timing_evaluation_id="",
    )
    result = evaluate(results=(old, new), now=NOW + timedelta(minutes=3))
    assert result.selected_timing_evaluation is new


@pytest.mark.parametrize(
    "source",
    [
        lambda: replace(
            timing(), created_at=NOW - timedelta(hours=3), timing_evaluation_id=""
        ),
        lambda: replace(
            timing(), created_at=NOW + timedelta(minutes=5), timing_evaluation_id=""
        ),
        lambda: replace(timing(), confidence=0.69, timing_evaluation_id=""),
    ],
)
def test_invalid_timing_source_requires_review(source):
    result = evaluate(results=(source(),), now=NOW + timedelta(minutes=3))
    assert result.status is CrossContextContinuityStatus.REVIEW_REQUIRED


def test_lineage_is_preserved_exactly():
    source = timing()
    req = request(results=(source,))
    result = CrossContextContinuity().evaluate(req, now=NOW + timedelta(minutes=3))
    assert result.selected_timing_evaluation is source
    assert result.selected_candidate is source.selected_candidate
    assert result.selected_opportunity is source.selected_opportunity
    assert result.source_context is req.source_context
    assert result.target_context is req.target_context


def test_all_downstream_permissions_are_false():
    result = evaluate()
    fields = (
        "device_handoff_allowed",
        "context_transfer_allowed",
        "conversation_start_allowed",
        "conversational_activation_allowed",
        "channel_selection_allowed",
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
    )
    assert not any(getattr(result, field) for field in fields)


def test_result_id_is_deterministic():
    req = request()
    first = CrossContextContinuity().evaluate(req, now=NOW + timedelta(minutes=3))
    second = CrossContextContinuity().evaluate(req, now=NOW + timedelta(minutes=3))
    assert first.continuity_id == second.continuity_id


def test_repository_round_trip_and_duplicate_guard():
    repository = InMemoryCrossContextContinuityRepository()
    engine = CrossContextContinuity(repository=repository)
    result = engine.evaluate(request(), now=NOW + timedelta(minutes=3))
    assert repository.get(result.continuity_id) is result
    assert repository.list_all() == (result,)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        evaluate().confidence = 0.1


@pytest.mark.parametrize(
    ("kind", "value"),
    [(item, item.value) for item in CrossContextKind],
)
def test_context_kind_accepts_enum_values(kind, value):
    assert context(f"context:{value}", kind=value).kind is kind


@pytest.mark.parametrize(
    "config",
    [
        CrossContextContinuityConfig(maximum_timing_results=1),
        CrossContextContinuityConfig(maximum_result_age=timedelta(seconds=1)),
        CrossContextContinuityConfig(maximum_context_gap=timedelta(seconds=1)),
        CrossContextContinuityConfig(minimum_confidence=0),
        CrossContextContinuityConfig(minimum_confidence=1),
    ],
)
def test_valid_configs_are_immutable(config):
    with pytest.raises(FrozenInstanceError):
        config.minimum_confidence = 0.5


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"maximum_timing_results": 0}, "limit"),
        ({"maximum_result_age": timedelta(0)}, "age"),
        ({"maximum_context_gap": timedelta(0)}, "gap"),
        ({"minimum_confidence": -0.1}, "confidence"),
        ({"minimum_confidence": 1.1}, "confidence"),
    ],
)
def test_invalid_configs_are_rejected(changes, message):
    with pytest.raises(ValueError, match=message):
        CrossContextContinuityConfig(**changes)


def test_blank_request_owner_is_rejected():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_blank_context_id_is_rejected():
    with pytest.raises(ValueError, match="fields"):
        context(" ")


def test_blank_context_owner_is_rejected():
    with pytest.raises(ValueError, match="fields"):
        context("desktop", owner=" ")


def test_naive_context_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        context("desktop", observed_at=NOW.replace(tzinfo=None))


def test_blank_optional_reference_is_rejected():
    with pytest.raises(ValueError, match="session_reference_id"):
        context("desktop", session_reference_id=" ")


def test_naive_evaluation_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        CrossContextContinuity().evaluate(request(), now=NOW.replace(tzinfo=None))


def test_protocol_repository_shape_is_runtime_checkable():
    repository = InMemoryCrossContextContinuityRepository()
    assert hasattr(repository, "add")
    assert hasattr(repository, "get")
    assert hasattr(repository, "list_all")
