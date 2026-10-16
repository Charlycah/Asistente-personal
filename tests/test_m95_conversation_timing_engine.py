from datetime import datetime, timedelta, timezone

import pytest

from core.living_conversation import (
    ConversationActivityState,
    ConversationOpportunity,
    ConversationTimingContext,
    ConversationTimingDecision,
    ConversationTimingEngine,
    ConversationTimingPolicy,
    InMemoryConversationTimingRepository,
    LivingConversationContext,
    TimingRecommendation,
)

NOW = datetime(2026, 7, 11, 15, 0, tzinfo=timezone.utc)


def conversation(**overrides: object) -> LivingConversationContext:
    values = {"owner": "carlos", "mode": "home", "user_present": True}
    values.update(overrides)
    return LivingConversationContext(**values)


def timing_context(**overrides: object) -> ConversationTimingContext:
    values = {
        "conversation": conversation(),
        "activity": "available",
        "cognitive_load": 0.3,
        "local_hour": 15,
    }
    values.update(overrides)
    return ConversationTimingContext(**values)


def opportunity(**overrides: object) -> ConversationOpportunity:
    values = {
        "kind": "reflect",
        "reason": "a meaningful connection is available",
        "value_score": 0.85,
        "relevance_score": 0.9,
        "confidence": 0.85,
        "source_reference_ids": ("memory-1",),
    }
    values.update(overrides)
    return ConversationOpportunity(**values)


def test_context_normalizes_activity() -> None:
    assert timing_context().activity is ConversationActivityState.AVAILABLE


def test_context_rejects_invalid_cognitive_load() -> None:
    with pytest.raises(ValueError):
        timing_context(cognitive_load=1.1)


def test_context_rejects_invalid_local_hour() -> None:
    with pytest.raises(ValueError):
        timing_context(local_hour=24)


def test_context_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError):
        timing_context(last_spontaneous_intervention_at=datetime(2026, 7, 11))


def test_policy_rejects_non_positive_intervention_limit() -> None:
    with pytest.raises(ValueError):
        ConversationTimingPolicy(maximum_spontaneous_interventions_per_day=0)


def test_policy_rejects_equal_quiet_hour_boundaries() -> None:
    with pytest.raises(ValueError):
        ConversationTimingPolicy(quiet_hours_start=8, quiet_hours_end=8)


def test_natural_window_recommends_now() -> None:
    decision = ConversationTimingEngine().evaluate(
        timing_context(), opportunity(), now=NOW
    )
    assert decision.recommendation is TimingRecommendation.INTERVENE_NOW
    assert decision.recommendation is TimingRecommendation.INTERVENE_NOW
    assert decision.earliest_at == NOW


def test_explicit_user_turn_has_priority_over_busy_activity() -> None:
    item = opportunity(kind="respond")
    context = timing_context(
        conversation=conversation(explicit_user_turn=True),
        activity="busy",
        cognitive_load=1.0,
        local_hour=23,
    )
    decision = ConversationTimingEngine().evaluate(context, item, now=NOW)
    assert decision.recommendation is TimingRecommendation.INTERVENE_NOW


def test_do_not_disturb_defers_even_explicit_response() -> None:
    until = NOW + timedelta(hours=1)
    context = timing_context(
        conversation=conversation(explicit_user_turn=True, do_not_disturb=True),
        quiet_until=until,
    )
    decision = ConversationTimingEngine().evaluate(
        context, opportunity(kind="respond"), now=NOW
    )
    assert decision.recommendation is TimingRecommendation.DEFER
    assert decision.earliest_at == until


def test_absent_user_defers() -> None:
    context = timing_context(conversation=conversation(user_present=False))
    decision = ConversationTimingEngine().evaluate(context, opportunity(), now=NOW)
    assert decision.recommendation is TimingRecommendation.DEFER


def test_focused_activity_defers() -> None:
    decision = ConversationTimingEngine().evaluate(
        timing_context(activity="focused"), opportunity(), now=NOW
    )
    assert decision.rationale == ("activity_state_focused_blocks_interruption",)


def test_high_cognitive_load_defers() -> None:
    decision = ConversationTimingEngine().evaluate(
        timing_context(cognitive_load=0.9), opportunity(), now=NOW
    )
    assert decision.rationale == ("cognitive_load_exceeds_interruption_threshold",)


def test_quiet_hours_defer_until_end() -> None:
    decision = ConversationTimingEngine().evaluate(
        timing_context(local_hour=23), opportunity(), now=NOW
    )
    assert decision.recommendation is TimingRecommendation.DEFER
    assert decision.earliest_at == NOW + timedelta(hours=9)


def test_guest_context_waits_for_privacy() -> None:
    context = timing_context(
        conversation=conversation(mode="guests", guests_present=True)
    )
    decision = ConversationTimingEngine().evaluate(context, opportunity(), now=NOW)
    assert decision.recommendation is TimingRecommendation.WAIT_FOR_PRIVATE_CONTEXT


def test_explicit_response_is_allowed_with_guests() -> None:
    context = timing_context(
        conversation=conversation(
            mode="guests", guests_present=True, explicit_user_turn=True
        )
    )
    decision = ConversationTimingEngine().evaluate(
        context, opportunity(kind="respond"), now=NOW
    )
    assert decision.recommendation is TimingRecommendation.INTERVENE_NOW


def test_sensitive_context_waits_for_privacy() -> None:
    context = timing_context(conversation=conversation(sensitive_context=True))
    decision = ConversationTimingEngine().evaluate(context, opportunity(), now=NOW)
    assert decision.recommendation is TimingRecommendation.WAIT_FOR_PRIVATE_CONTEXT


def test_review_required_opportunity_stays_under_review() -> None:
    decision = ConversationTimingEngine().evaluate(
        timing_context(), opportunity(requires_review=True), now=NOW
    )
    assert decision.recommendation is TimingRecommendation.REVIEW_REQUIRED
    assert decision.earliest_at is None


def test_daily_budget_exhaustion_cancels() -> None:
    decision = ConversationTimingEngine().evaluate(
        timing_context(spontaneous_interventions_today=4), opportunity(), now=NOW
    )
    assert decision.recommendation is TimingRecommendation.CANCEL


def test_cooldown_defers_until_interval_ends() -> None:
    last = NOW - timedelta(minutes=10)
    decision = ConversationTimingEngine().evaluate(
        timing_context(last_spontaneous_intervention_at=last),
        opportunity(),
        now=NOW,
    )
    assert decision.earliest_at == last + timedelta(minutes=45)


def test_elapsed_cooldown_allows_intervention() -> None:
    last = NOW - timedelta(hours=1)
    decision = ConversationTimingEngine().evaluate(
        timing_context(last_spontaneous_intervention_at=last),
        opportunity(),
        now=NOW,
    )
    assert decision.recommendation is TimingRecommendation.INTERVENE_NOW


def test_window_beyond_opportunity_lifetime_is_cancelled() -> None:
    policy = ConversationTimingPolicy(
        default_deferral_seconds=3600,
        opportunity_lifetime_seconds=1800,
    )
    decision = ConversationTimingEngine(policy=policy).evaluate(
        timing_context(activity="busy"), opportunity(), now=NOW
    )
    assert decision.recommendation is TimingRecommendation.CANCEL
    assert decision.earliest_at is None


def test_decision_is_persisted() -> None:
    repository = InMemoryConversationTimingRepository()
    engine = ConversationTimingEngine(repository=repository)
    decision = engine.evaluate(timing_context(), opportunity(), now=NOW)
    assert repository.get(decision.timing_id) == decision
    assert engine.last_decision == decision


def test_repository_rejects_duplicate_decision() -> None:
    repository = InMemoryConversationTimingRepository()
    decision = ConversationTimingEngine(repository=repository).evaluate(
        timing_context(), opportunity(), now=NOW
    )
    with pytest.raises(ValueError):
        repository.add(decision)


def test_decision_rejects_naive_evaluation_timestamp() -> None:
    with pytest.raises(ValueError):
        ConversationTimingDecision(
            context=timing_context(),
            opportunity=opportunity(),
            recommendation="defer",
            rationale=("test",),
            evaluated_at=datetime(2026, 7, 11),
        )


def test_timing_id_is_deterministic_for_same_inputs() -> None:
    engine_a = ConversationTimingEngine()
    engine_b = ConversationTimingEngine()
    first = engine_a.evaluate(timing_context(), opportunity(), now=NOW)
    second = engine_b.evaluate(timing_context(), opportunity(), now=NOW)
    assert first.timing_id == second.timing_id


def test_system_prompt_documents_non_execution_boundary() -> None:
    lines = ConversationTimingEngine.system_prompt_lines()
    assert any("no agenda" in line for line in lines)
    assert any("no habla" in line for line in lines)
