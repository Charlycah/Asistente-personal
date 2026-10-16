from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.long_term_experience_evaluation import (
    ExperienceObservation,
    ExperienceOutcome,
    InMemoryLongTermExperienceRepository,
    LongTermExperienceAction,
    LongTermExperienceConfig,
    LongTermExperienceEvaluation,
    LongTermExperienceRequest,
    LongTermExperienceStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m159_companion_reliability_model import evaluate as reliability_evaluate

EVAL_NOW = NOW + timedelta(days=10)
BASE_RELIABILITY = reliability_evaluate(now=NOW + timedelta(minutes=5))


def reliability(*, created_at=NOW + timedelta(days=1), owner="Carlos", **changes):
    request = BASE_RELIABILITY.request
    if owner != request.owner:
        request = replace(request, owner=owner)
    values = {"request": request, "created_at": created_at, "reliability_id": ""}
    values.update(changes)
    return replace(BASE_RELIABILITY, **values)


def observation(
    observation_id="exp:1",
    source=None,
    occurred_at=NOW + timedelta(days=1),
    owner="Carlos",
    outcome=ExperienceOutcome.SUCCESS,
    satisfaction=0.95,
    continuity_quality=0.9,
    consent_alignment=0.95,
    reliability_quality=0.9,
    contexts=("desktop:home", "mobile:walking"),
    explicit_user_feedback=True,
    excluded=False,
):
    source = source or reliability(created_at=occurred_at)
    return ExperienceObservation(
        observation_id=observation_id,
        owner=owner,
        reliability_id=source.reliability_id,
        occurred_at=occurred_at,
        outcome=outcome,
        satisfaction=satisfaction,
        continuity_quality=continuity_quality,
        consent_alignment=consent_alignment,
        reliability_quality=reliability_quality,
        context_ids=contexts,
        explicit_user_feedback=explicit_user_feedback,
        excluded=excluded,
    )


def sources():
    return tuple(reliability(created_at=NOW + timedelta(days=day)) for day in (1, 3, 5))


def observations(items=None, **changes):
    items = items or sources()
    return tuple(
        observation(
            observation_id=f"exp:{index}",
            source=source,
            occurred_at=source.created_at,
            **changes,
        )
        for index, source in enumerate(items, 1)
    )


def request(*, results=None, items=None, owner="Carlos", **changes):
    results = results if results is not None else sources()
    values = {
        "owner": owner,
        "reliability_results": results,
        "observations": items if items is not None else observations(results),
    }
    values.update(changes)
    return LongTermExperienceRequest(**values)


def evaluate(*, config=None, now=EVAL_NOW, **changes):
    return LongTermExperienceEvaluation(config).evaluate(request(**changes), now=now)


def test_positive_long_term_experience():
    result = evaluate()
    assert result.status is LongTermExperienceStatus.POSITIVE
    assert result.action is LongTermExperienceAction.DECLARE_POSITIVE
    assert result.positive and result.observation_count == 3


def test_mixed_long_term_experience():
    result = evaluate(
        items=observations(
            outcome=ExperienceOutcome.NEUTRAL,
            satisfaction=0.6,
            continuity_quality=0.6,
            consent_alignment=0.7,
            reliability_quality=0.6,
        )
    )
    assert result.status is LongTermExperienceStatus.MIXED


def test_negative_long_term_experience():
    result = evaluate(
        items=observations(
            outcome=ExperienceOutcome.ABANDONED,
            satisfaction=0.1,
            continuity_quality=0.2,
            consent_alignment=0.3,
            reliability_quality=0.2,
        )
    )
    assert result.status is LongTermExperienceStatus.NEGATIVE
    assert result.negative_ratio == 1


def test_negative_ratio_prevents_positive_classification():
    result_sources = sources()
    items = list(observations(result_sources))
    items[0] = observation(
        observation_id="exp:failure",
        source=result_sources[0],
        occurred_at=result_sources[0].created_at,
        outcome=ExperienceOutcome.FAILURE,
        satisfaction=1,
        continuity_quality=1,
        consent_alignment=1,
        reliability_quality=1,
    )
    assert (
        evaluate(results=result_sources, items=tuple(items)).status
        is LongTermExperienceStatus.MIXED
    )


@pytest.mark.parametrize(
    ("outcome", "factor"),
    [
        (ExperienceOutcome.SUCCESS, 1.0),
        (ExperienceOutcome.PARTIAL_SUCCESS, 0.7),
        (ExperienceOutcome.NEUTRAL, 0.5),
        (ExperienceOutcome.FAILURE, 0.2),
        (ExperienceOutcome.ABANDONED, 0.0),
    ],
)
def test_outcome_factor_is_explicit(outcome, factor):
    item = observation(
        outcome=outcome,
        satisfaction=0,
        continuity_quality=0,
        consent_alignment=0,
        reliability_quality=0,
    )
    assert item.experience_score == pytest.approx(factor / 5)


def test_insufficient_observation_count():
    result_sources = sources()[:2]
    result = evaluate(results=result_sources, items=observations(result_sources))
    assert result.status is LongTermExperienceStatus.INSUFFICIENT
    assert result.insufficient


def test_insufficient_observation_span():
    result_sources = tuple(
        reliability(created_at=NOW + timedelta(hours=x)) for x in (1, 2, 3)
    )
    result = evaluate(results=result_sources, items=observations(result_sources))
    assert result.status is LongTermExperienceStatus.INSUFFICIENT


def test_span_boundary_is_accepted():
    result_sources = tuple(
        reliability(created_at=NOW + timedelta(hours=x)) for x in (1, 13, 25)
    )
    result = evaluate(results=result_sources, items=observations(result_sources))
    assert result.status is LongTermExperienceStatus.POSITIVE


def test_not_requested_is_not_applicable():
    assert (
        evaluate(evaluation_requested=False).status
        is LongTermExperienceStatus.NOT_APPLICABLE
    )


def test_no_reliability_results_is_not_applicable():
    assert (
        evaluate(results=(), items=()).status is LongTermExperienceStatus.NOT_APPLICABLE
    )


def test_reliability_owner_mismatch_is_blocked():
    other = reliability(owner="Other")
    assert (
        evaluate(results=(other,), items=()).status is LongTermExperienceStatus.BLOCKED
    )


def test_observation_owner_mismatch_is_blocked():
    result_sources = sources()
    assert (
        evaluate(
            results=result_sources, items=observations(result_sources, owner="Other")
        ).status
        is LongTermExperienceStatus.BLOCKED
    )


def test_unknown_reliability_reference_is_blocked():
    result_sources = sources()
    item = replace(observations(result_sources)[0], reliability_id="unknown")
    assert (
        evaluate(results=result_sources, items=(item,)).status
        is LongTermExperienceStatus.BLOCKED
    )


def test_low_confidence_reliability_requires_review():
    source = reliability(confidence=0.5)
    item = observation(source=source)
    assert (
        evaluate(results=(source,), items=(item,)).status
        is LongTermExperienceStatus.REVIEW_REQUIRED
    )


def test_old_reliability_requires_review():
    source = reliability(created_at=NOW - timedelta(days=100))
    assert (
        evaluate(results=(source,), items=()).status
        is LongTermExperienceStatus.REVIEW_REQUIRED
    )


def test_future_reliability_requires_review():
    source = reliability(created_at=EVAL_NOW + timedelta(days=1))
    assert (
        evaluate(results=(source,), items=()).status
        is LongTermExperienceStatus.REVIEW_REQUIRED
    )


def test_explicit_feedback_can_be_required():
    result_sources = sources()
    config = LongTermExperienceConfig(require_explicit_feedback=True)
    result = evaluate(
        results=result_sources,
        items=observations(result_sources, explicit_user_feedback=False),
        config=config,
    )
    assert result.status is LongTermExperienceStatus.REVIEW_REQUIRED


def test_one_explicit_feedback_satisfies_requirement():
    result_sources = sources()
    items = list(observations(result_sources, explicit_user_feedback=False))
    items[-1] = replace(items[-1], explicit_user_feedback=True)
    config = LongTermExperienceConfig(require_explicit_feedback=True)
    assert evaluate(results=result_sources, items=tuple(items), config=config).positive


def test_excluded_observations_do_not_count():
    result_sources = sources()
    items = observations(result_sources, excluded=True)
    assert evaluate(results=result_sources, items=items).insufficient


def test_old_observations_do_not_count():
    source = reliability(created_at=NOW + timedelta(days=1))
    item = observation(source=source, occurred_at=NOW - timedelta(days=100))
    assert evaluate(results=(source,), items=(item,)).insufficient


def test_future_observations_do_not_count():
    source = reliability(created_at=NOW + timedelta(days=1))
    item = observation(source=source, occurred_at=EVAL_NOW + timedelta(days=1))
    assert evaluate(results=(source,), items=(item,)).insufficient


def test_duplicate_observations_are_deduplicated():
    result_sources = sources()
    items = observations(result_sources)
    result = evaluate(
        results=result_sources, items=(items[0], items[0], items[1], items[2])
    )
    assert result.observation_count == 3


def test_duplicate_reliability_results_are_deduplicated():
    result_sources = sources()
    result = evaluate(
        results=result_sources + (result_sources[0],),
        items=observations(result_sources),
    )
    assert len(result.matched_reliability_ids) == 3


def test_latest_matched_reliability_is_selected():
    result_sources = sources()
    result = evaluate(results=result_sources, items=observations(result_sources))
    assert result.selected_reliability_result is result_sources[-1]


def test_full_lineage_is_preserved():
    result = evaluate()
    source = result.selected_reliability_result
    assert source is not None
    assert result.selected_permission_result is source.selected_permission_result
    assert result.selected_continuity is source.selected_continuity
    assert result.selected_timing_evaluation is source.selected_timing_evaluation
    assert result.selected_candidate is source.selected_candidate
    assert result.selected_opportunity is source.selected_opportunity


def test_confidence_is_conservative_minimum():
    result_sources = list(sources())
    result_sources[1] = replace(result_sources[1], confidence=0.7, reliability_id="")
    result = evaluate(
        results=tuple(result_sources), items=observations(tuple(result_sources))
    )
    assert result.confidence == 0.7


def test_input_limits_are_blocked():
    source = sources()[0]
    config = LongTermExperienceConfig(maximum_reliability_results=1)
    assert (
        evaluate(results=(source, source), items=(), config=config).status
        is LongTermExperienceStatus.BLOCKED
    )


def test_observation_limit_is_blocked():
    result_sources = sources()
    items = observations(result_sources)
    config = LongTermExperienceConfig(maximum_observations=2)
    assert (
        evaluate(results=result_sources, items=items, config=config).status
        is LongTermExperienceStatus.BLOCKED
    )


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_observation_scores_validate(value):
    with pytest.raises(ValueError):
        observation(satisfaction=value)


def test_observation_requires_timezone():
    with pytest.raises(ValueError):
        observation(occurred_at=NOW.replace(tzinfo=None))


def test_context_ids_are_unique():
    with pytest.raises(ValueError):
        observation(contexts=("desktop", "desktop"))


def test_config_threshold_order_is_validated():
    with pytest.raises(ValueError):
        LongTermExperienceConfig(positive_threshold=0.4, negative_threshold=0.5)


def test_config_durations_are_positive():
    with pytest.raises(ValueError):
        LongTermExperienceConfig(minimum_observation_span=timedelta(0))


def test_result_is_immutable_and_deterministic():
    first = evaluate()
    second = evaluate()
    assert first.evaluation_id == second.evaluation_id
    with pytest.raises(FrozenInstanceError):
        first.experience_score = 0  # type: ignore[misc]


def test_repository_is_append_only():
    repository = InMemoryLongTermExperienceRepository()
    result = evaluate()
    repository.add(result)
    assert repository.get(result.evaluation_id) is result
    assert repository.list_all() == (result,)
    with pytest.raises(ValueError):
        repository.add(result)


def test_repository_matches_protocol():
    from core.long_term_experience_evaluation import LongTermExperienceRepository

    assert isinstance(
        InMemoryLongTermExperienceRepository(), LongTermExperienceRepository
    )


def test_all_execution_and_learning_flags_are_false():
    result = evaluate()
    names = (
        "memory_write_allowed",
        "learning_allowed",
        "personality_change_allowed",
        "policy_change_allowed",
        "knowledge_evolution_allowed",
        "conversation_start_allowed",
        "scheduling_allowed",
        "prompt_generation_allowed",
        "response_realization_allowed",
        "provider_call_allowed",
        "automation_allowed",
        "platform_mutation_allowed",
    )
    assert not any(getattr(result, name) for name in names)


def test_active_result_rejects_broken_lineage():
    result = evaluate()
    with pytest.raises(ValueError):
        replace(result, selected_permission_result=None, evaluation_id="")


def test_inactive_result_rejects_lineage():
    result = evaluate(evaluation_requested=False)
    with pytest.raises(ValueError):
        replace(result, selected_reliability_result=sources()[0], evaluation_id="")


def test_result_rejects_execution_authority():
    result = evaluate()
    with pytest.raises(ValueError):
        replace(result, learning_allowed=True, evaluation_id="")


def test_result_rejects_inconsistent_identity():
    with pytest.raises(ValueError):
        replace(evaluate(), evaluation_id="bad")
