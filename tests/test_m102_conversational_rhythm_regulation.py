from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from core.living_conversation import (
    ConversationActivityState,
    ConversationalFeedbackLoop,
    ConversationalFeedbackRequest,
    ConversationalFeedbackSignal,
    ConversationalPresenceEngine,
    ConversationalPresenceRequest,
    ConversationalRealizationLayer,
    ConversationalRealizationRequest,
    ConversationalRhythm,
    ConversationalRhythmPolicy,
    ConversationalRhythmRegulator,
    ConversationalRhythmRequest,
    ConversationalRhythmStatus,
    ConversationOpportunity,
    ConversationTimingContext,
    ConversationTimingEngine,
    InMemoryConversationalRhythmRepository,
    IntellectualCompanionLayer,
    IntellectualCompanionRequest,
    LivingConversationContext,
    LivingConversationManager,
    ReflectionGenerator,
)

NOW = datetime(2026, 7, 11, 13, 0, tzinfo=timezone.utc)


def realization(
    *,
    kind: str = "reflect",
    explicit: bool = False,
    domain: str = "literature",
    sources: tuple[str, ...] = ("book:borges",),
):
    opportunity = ConversationOpportunity(
        kind=kind,
        reason="La idea conecta con una conversación anterior.",
        value_score=0.94,
        relevance_score=0.93,
        confidence=0.95,
        content_hint="la memoria transforma nuestra lectura del presente",
        source_reference_ids=sources,
    )
    context = LivingConversationContext(owner="Carlos", explicit_user_turn=explicit)
    governance = LivingConversationManager().evaluate(context, opportunity, now=NOW)
    timing = ConversationTimingEngine().evaluate(
        ConversationTimingContext(
            conversation=context,
            activity=ConversationActivityState.AVAILABLE,
            cognitive_load=0.1,
            local_hour=13,
        ),
        opportunity,
        now=NOW,
    )
    reflection = ReflectionGenerator().generate(governance, timing, now=NOW)
    contribution = IntellectualCompanionLayer().compose(
        IntellectualCompanionRequest(
            governance=governance,
            timing=timing,
            reflection=reflection,
            domain=domain,
            thesis="La memoria no conserva intacto el pasado: lo vuelve interpretable.",
            concepts=("identidad", "tiempo", "experiencia"),
            requested_at=NOW,
        ),
        now=NOW,
    )
    return ConversationalRealizationLayer().realize(
        ConversationalRealizationRequest(
            contribution=contribution,
            owner="Carlos",
            requested_at=NOW,
        ),
        now=NOW,
    )


def request(**changes):
    values = {
        "realization": realization(),
        "owner": "Carlos",
        "requested_at": NOW,
    }
    values.update(changes)
    return ConversationalPresenceRequest(**values)


def presence(**changes):
    values = {"realization": realization(), "owner": "Carlos", "requested_at": NOW}
    values.update(changes)
    return ConversationalPresenceEngine().compose(
        ConversationalPresenceRequest(**values), now=NOW
    )


def signal(kind="acceptance", origin="explicit", confidence=0.9, evidence="ok"):
    return ConversationalFeedbackSignal(
        kind=kind, origin=origin, confidence=confidence, evidence=evidence
    )


def feedback_request(**changes):
    values = {
        "presence": presence(),
        "owner": "Carlos",
        "signals": (signal(),),
        "requested_at": NOW,
    }
    values.update(changes)
    return ConversationalFeedbackRequest(**values)


def assessment(kind="acceptance", confidence=0.9):
    return ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal(kind, confidence=confidence),)), now=NOW
    )


def rhythm_request(**changes):
    values = {"feedback": assessment(), "owner": "Carlos", "requested_at": NOW}
    values.update(changes)
    return ConversationalRhythmRequest(**values)


def test_acceptance_uses_steady_rhythm():
    result = ConversationalRhythmRegulator().regulate(rhythm_request(), now=NOW)
    assert result.status is ConversationalRhythmStatus.REGULATED
    assert result.rhythm is ConversationalRhythm.STEADY


def test_deepening_uses_brisk_rhythm():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("deepening")), now=NOW
    )
    assert result.rhythm is ConversationalRhythm.BRISK


def test_confusion_uses_measured_rhythm():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("confusion")), now=NOW
    )
    assert result.rhythm is ConversationalRhythm.MEASURED


def test_correction_uses_measured_rhythm():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("correction")), now=NOW
    )
    assert result.rhythm is ConversationalRhythm.MEASURED


def test_rejection_closes_rhythm():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("rejection")), now=NOW
    )
    assert result.rhythm is ConversationalRhythm.CLOSING
    assert result.allow_follow_up_prompt is False


def test_disengagement_closes_rhythm():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("disengagement")), now=NOW
    )
    assert result.rhythm is ConversationalRhythm.CLOSING


def test_repeated_interruptions_pause():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(interruption_count=2), now=NOW
    )
    assert result.rhythm is ConversationalRhythm.PAUSED


def test_extended_silence_pauses():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(silence_seconds=20), now=NOW
    )
    assert result.rhythm is ConversationalRhythm.PAUSED


def test_long_user_response_is_measured():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(user_response_characters=240), now=NOW
    )
    assert result.rhythm is ConversationalRhythm.MEASURED


def test_review_feedback_is_measured():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment(confidence=0.5)), now=NOW
    )
    assert result.status is ConversationalRhythmStatus.REVIEW_REQUIRED
    assert result.rhythm is ConversationalRhythm.MEASURED


def test_insufficient_feedback_is_not_applicable():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment(confidence=0.2)), now=NOW
    )
    assert result.status is ConversationalRhythmStatus.NOT_APPLICABLE
    assert result.allow_follow_up_prompt is False


def test_observed_interval_can_slow_steady_rhythm():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(recent_turn_intervals_seconds=(1.8, 2.2)), now=NOW
    )
    assert result.interval_seconds == 2.0


def test_observed_interval_does_not_speed_below_policy():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(recent_turn_intervals_seconds=(0.1, 0.2)), now=NOW
    )
    assert result.interval_seconds == 1.0


def test_measured_limits_consecutive_turns():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("confusion")), now=NOW
    )
    assert result.maximum_consecutive_turns == 2


def test_closing_limits_consecutive_turns_to_one():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("rejection")), now=NOW
    )
    assert result.maximum_consecutive_turns == 1


def test_turn_limit_disables_prompt():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("deepening"), consecutive_roby_turns=3),
        now=NOW,
    )
    assert result.allow_follow_up_prompt is False


def test_deepening_can_keep_prompt_open():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("deepening"), consecutive_roby_turns=1),
        now=NOW,
    )
    assert result.allow_follow_up_prompt is True


def test_measured_preserves_user_floor():
    result = ConversationalRhythmRegulator().regulate(
        rhythm_request(feedback=assessment("confusion")), now=NOW
    )
    assert result.preserve_user_floor is True


def test_steady_does_not_force_user_floor():
    result = ConversationalRhythmRegulator().regulate(rhythm_request(), now=NOW)
    assert result.preserve_user_floor is False


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError, match="owner"):
        rhythm_request(owner=" ")


def test_request_rejects_wrong_owner():
    with pytest.raises(ValueError, match="match"):
        rhythm_request(owner="Cristina")


def test_request_rejects_negative_intervals():
    with pytest.raises(ValueError, match="interval"):
        rhythm_request(recent_turn_intervals_seconds=(-1.0,))


def test_request_rejects_negative_turns():
    with pytest.raises(ValueError, match="negative"):
        rhythm_request(consecutive_roby_turns=-1)


def test_request_rejects_negative_response_length():
    with pytest.raises(ValueError, match="negative"):
        rhythm_request(user_response_characters=-1)


def test_request_rejects_negative_interruptions():
    with pytest.raises(ValueError, match="negative"):
        rhythm_request(interruption_count=-1)


def test_request_rejects_negative_silence():
    with pytest.raises(ValueError, match="negative"):
        rhythm_request(silence_seconds=-1)


def test_request_requires_aware_timestamp():
    with pytest.raises(ValueError, match="aware"):
        rhythm_request(requested_at=datetime(2026, 7, 11, 13, 0))


def test_policy_rejects_negative_interval():
    with pytest.raises(ValueError, match="negative"):
        ConversationalRhythmPolicy(steady_interval_seconds=-1)


def test_policy_rejects_zero_turn_limit():
    with pytest.raises(ValueError, match="positive"):
        ConversationalRhythmPolicy(maximum_consecutive_turns=0)


def test_repository_round_trip_and_duplicate_protection():
    repository = InMemoryConversationalRhythmRepository()
    regulator = ConversationalRhythmRegulator(repository=repository)
    result = regulator.regulate(rhythm_request(), now=NOW)
    assert repository.get(result.decision_id) == result
    assert repository.list_all() == (result,)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_decision_is_immutable():
    result = ConversationalRhythmRegulator().regulate(rhythm_request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.interval_seconds = 9.0


def test_decision_id_is_deterministic():
    first = ConversationalRhythmRegulator().regulate(rhythm_request(), now=NOW)
    second = ConversationalRhythmRegulator().regulate(rhythm_request(), now=NOW)
    assert first.decision_id == second.decision_id


def test_regulator_rejects_naive_now():
    with pytest.raises(ValueError, match="aware"):
        ConversationalRhythmRegulator().regulate(
            rhythm_request(), now=datetime(2026, 7, 11, 13, 0)
        )
