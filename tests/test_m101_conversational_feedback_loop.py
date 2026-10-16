from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.living_conversation import (
    ConversationActivityState,
    ConversationalAdjustment,
    ConversationalFeedbackLoop,
    ConversationalFeedbackPolicy,
    ConversationalFeedbackRequest,
    ConversationalFeedbackSignal,
    ConversationalFeedbackSignalKind,
    ConversationalFeedbackStatus,
    ConversationalPresenceEngine,
    ConversationalPresenceRequest,
    ConversationalRealizationLayer,
    ConversationalRealizationRequest,
    ConversationOpportunity,
    ConversationTimingContext,
    ConversationTimingEngine,
    InMemoryConversationalFeedbackRepository,
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


def test_acceptance_is_assessed():
    result = ConversationalFeedbackLoop().assess(feedback_request(), now=NOW)
    assert result.status is ConversationalFeedbackStatus.ASSESSED
    assert result.dominant_signal is ConversationalFeedbackSignalKind.ACCEPTANCE
    assert result.adjustments == (ConversationalAdjustment.MAINTAIN,)


def test_correction_recommends_correction_and_confirmation():
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal("correction"),)), now=NOW
    )
    assert result.adjustments == (
        ConversationalAdjustment.CORRECT,
        ConversationalAdjustment.SEEK_CONFIRMATION,
    )


def test_confusion_recommends_clarity_and_lower_intensity():
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal("confusion"),)), now=NOW
    )
    assert result.adjustments == (
        ConversationalAdjustment.CLARIFY,
        ConversationalAdjustment.REDUCE_INTENSITY,
    )
    assert result.recommended_intensity < result.request.presence.intensity


def test_rejection_closes_follow_up():
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal("rejection"),)), now=NOW
    )
    assert result.keep_follow_up_open is False


def test_deepening_opens_follow_up_and_increases_intensity():
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal("deepening"),)), now=NOW
    )
    assert result.keep_follow_up_open is True
    assert result.recommended_intensity > result.request.presence.intensity


def test_disengagement_reduces_intensity():
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal("disengagement"),)), now=NOW
    )
    assert result.recommended_intensity < result.request.presence.intensity


def test_no_signal_is_insufficient():
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal("no_signal", "system", 1.0, ""),)), now=NOW
    )
    assert result.status is ConversationalFeedbackStatus.INSUFFICIENT
    assert result.adjustments == (ConversationalAdjustment.NONE,)


def test_low_confidence_is_insufficient():
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal(confidence=0.2),)), now=NOW
    )
    assert result.status is ConversationalFeedbackStatus.INSUFFICIENT


def test_mid_confidence_requires_review():
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal(confidence=0.5),)), now=NOW
    )
    assert result.status is ConversationalFeedbackStatus.REVIEW_REQUIRED


def test_implicit_confidence_is_capped():
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=(signal(origin="implicit", confidence=0.99),)), now=NOW
    )
    assert result.confidence == 0.72


def test_highest_effective_confidence_wins():
    signals = (
        signal("acceptance", confidence=0.7),
        signal("confusion", confidence=0.9),
    )
    result = ConversationalFeedbackLoop().assess(
        feedback_request(signals=signals), now=NOW
    )
    assert result.dominant_signal is ConversationalFeedbackSignalKind.CONFUSION


def test_non_ready_presence_is_not_applicable():
    base = realization()
    abstained = replace(
        base, status="abstained", segments=(), rationale=("test",), realization_id=""
    )
    item = ConversationalPresenceEngine().compose(
        request(realization=abstained), now=NOW
    )
    result = ConversationalFeedbackLoop().assess(
        feedback_request(presence=item), now=NOW
    )
    assert result.status is ConversationalFeedbackStatus.NOT_APPLICABLE
    assert result.keep_follow_up_open is False


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError, match="owner"):
        feedback_request(owner=" ")


def test_request_rejects_wrong_owner():
    with pytest.raises(ValueError, match="match"):
        feedback_request(owner="Cristina")


def test_request_requires_signals():
    with pytest.raises(ValueError, match="signal"):
        feedback_request(signals=())


def test_request_rejects_negative_window():
    with pytest.raises(ValueError, match="negative"):
        feedback_request(observation_window_seconds=-1)


def test_request_requires_aware_timestamp():
    with pytest.raises(ValueError, match="aware"):
        feedback_request(requested_at=datetime(2026, 7, 11, 13, 0))


def test_no_signal_must_be_only_signal():
    signals = (signal("no_signal", "system", 1.0, ""), signal())
    with pytest.raises(ValueError, match="only signal"):
        feedback_request(signals=signals)


def test_signal_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="between"):
        signal(confidence=1.1)


def test_signal_requires_evidence():
    with pytest.raises(ValueError, match="evidence"):
        signal(evidence=" ")


def test_no_signal_rejects_evidence():
    with pytest.raises(ValueError, match="cannot carry"):
        signal("no_signal", "system", 1.0, "unexpected")


def test_policy_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="between"):
        ConversationalFeedbackPolicy(minimum_confidence=1.1)


def test_policy_rejects_review_above_minimum():
    with pytest.raises(ValueError, match="cannot exceed"):
        ConversationalFeedbackPolicy(minimum_confidence=0.4, review_threshold=0.5)


def test_policy_rejects_implicit_cap_below_minimum():
    with pytest.raises(ValueError, match="cannot be below"):
        ConversationalFeedbackPolicy(
            minimum_confidence=0.7, implicit_confidence_cap=0.6
        )


def test_policy_rejects_invalid_delta():
    with pytest.raises(ValueError, match="between -1 and 1"):
        ConversationalFeedbackPolicy(deepening_intensity_delta=1.1)


def test_assess_requires_aware_timestamp():
    with pytest.raises(ValueError, match="aware"):
        ConversationalFeedbackLoop().assess(
            feedback_request(), now=datetime(2026, 7, 11, 13, 0)
        )


def test_repository_stores_and_retrieves():
    repository = InMemoryConversationalFeedbackRepository()
    loop = ConversationalFeedbackLoop(repository=repository)
    result = loop.assess(feedback_request(), now=NOW)
    assert repository.get(result.assessment_id) == result
    assert loop.last_assessment == result


def test_repository_rejects_duplicate():
    repository = InMemoryConversationalFeedbackRepository()
    result = ConversationalFeedbackLoop().assess(feedback_request(), now=NOW)
    repository.add(result)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_assessment_is_immutable():
    result = ConversationalFeedbackLoop().assess(feedback_request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.confidence = 0.0  # type: ignore[misc]


def test_assessment_id_is_deterministic():
    item = feedback_request()
    first = ConversationalFeedbackLoop().assess(item, now=NOW)
    second = ConversationalFeedbackLoop().assess(item, now=NOW)
    assert first.assessment_id == second.assessment_id


def test_intensity_is_clamped_at_zero():
    policy = ConversationalFeedbackPolicy(disengagement_intensity_delta=-1.0)
    result = ConversationalFeedbackLoop(policy=policy).assess(
        feedback_request(signals=(signal("disengagement"),)), now=NOW
    )
    assert result.recommended_intensity == 0.0


def test_intensity_is_clamped_at_one():
    policy = ConversationalFeedbackPolicy(deepening_intensity_delta=1.0)
    result = ConversationalFeedbackLoop(policy=policy).assess(
        feedback_request(signals=(signal("deepening"),)), now=NOW
    )
    assert result.recommended_intensity == 1.0
