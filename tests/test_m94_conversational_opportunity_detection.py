from datetime import datetime, timedelta, timezone

import pytest

from core.living_conversation import (
    ConversationalOpportunityDetector,
    ConversationOpportunityKind,
    ConversationSignal,
    ConversationSignalKind,
    ConversationSignalSensitivity,
    InMemoryOpportunityDetectionRepository,
    LivingConversationContext,
    LivingConversationManager,
    OpportunityDetectionPolicy,
    OpportunityDetectionRecord,
)

NOW = datetime(2026, 7, 11, 0, 0, tzinfo=timezone.utc)


def context(**overrides: object) -> LivingConversationContext:
    values = {"owner": "carlos", "mode": "home", "user_present": True}
    values.update(overrides)
    return LivingConversationContext(**values)


def signal(**overrides: object) -> ConversationSignal:
    values = {
        "kind": "memory_connection",
        "summary": "a prior idea connects with the current topic",
        "source_id": "memory-1",
        "relevance": 0.9,
        "novelty": 0.8,
        "confidence": 0.85,
        "occurred_at": NOW - timedelta(minutes=5),
        "topic": "living conversation",
        "content_hint": "connect the present design with an earlier reflection",
    }
    values.update(overrides)
    return ConversationSignal(**values)


def test_signal_normalizes_enums() -> None:
    item = signal(sensitivity="public")
    assert item.kind is ConversationSignalKind.MEMORY_CONNECTION
    assert item.sensitivity is ConversationSignalSensitivity.PUBLIC


def test_signal_has_stable_fingerprint() -> None:
    assert signal().fingerprint == signal().fingerprint


def test_signal_rejects_blank_summary() -> None:
    with pytest.raises(ValueError):
        signal(summary=" ")


def test_signal_rejects_invalid_score() -> None:
    with pytest.raises(ValueError):
        signal(novelty=1.1)


def test_signal_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError):
        signal(occurred_at=datetime(2026, 7, 11))


def test_policy_rejects_non_positive_age() -> None:
    with pytest.raises(ValueError):
        OpportunityDetectionPolicy(maximum_signal_age_seconds=0)


def test_policy_rejects_non_positive_capacity() -> None:
    with pytest.raises(ValueError):
        OpportunityDetectionPolicy(maximum_opportunities=0)


def test_memory_signal_becomes_reflection_opportunity() -> None:
    record = ConversationalOpportunityDetector().detect(context(), [signal()], now=NOW)
    item = record.opportunities[0]
    assert item.kind is ConversationOpportunityKind.REFLECT
    assert item.source_reference_ids == ("memory-1",)


def test_value_combines_relevance_and_novelty() -> None:
    record = ConversationalOpportunityDetector().detect(context(), [signal()], now=NOW)
    assert record.opportunities[0].value_score == 0.86


def test_user_turn_is_ranked_first() -> None:
    signals = [
        signal(source_id="high", relevance=1.0, novelty=1.0),
        signal(
            kind="user_turn",
            source_id="turn",
            relevance=0.6,
            novelty=0.5,
        ),
    ]
    record = ConversationalOpportunityDetector().detect(context(), signals, now=NOW)
    assert record.opportunities[0].kind is ConversationOpportunityKind.RESPOND


def test_signal_kinds_map_to_expected_opportunity_kinds() -> None:
    expected = {
        "user_turn": "respond",
        "unfinished_topic": "resume",
        "memory_connection": "reflect",
        "reflection_ready": "reflect",
        "new_knowledge": "share",
        "routine_transition": "ask",
        "shared_interest": "share",
        "context_change": "ask",
        "external_event": "share",
    }
    detector = ConversationalOpportunityDetector()
    for index, (kind, opportunity_kind) in enumerate(expected.items()):
        record = detector.detect(
            context(),
            [signal(kind=kind, source_id=f"source-{index}")],
            now=NOW + timedelta(seconds=index),
        )
        assert record.opportunities[0].kind.value == opportunity_kind


def test_low_relevance_is_rejected() -> None:
    record = ConversationalOpportunityDetector().detect(
        context(), [signal(relevance=0.2)], now=NOW
    )
    assert not record.opportunities
    assert record.rejected_signal_reasons == (
        ("memory-1", "relevance_below_detection_minimum"),
    )


def test_low_confidence_is_rejected() -> None:
    record = ConversationalOpportunityDetector().detect(
        context(), [signal(confidence=0.2)], now=NOW
    )
    assert record.rejected_signal_reasons[0][1] == "confidence_below_detection_minimum"


def test_low_novelty_is_rejected() -> None:
    record = ConversationalOpportunityDetector().detect(
        context(), [signal(novelty=0.1)], now=NOW
    )
    assert record.rejected_signal_reasons[0][1] == "novelty_below_detection_minimum"


def test_stale_signal_is_rejected() -> None:
    old = NOW - timedelta(days=8)
    record = ConversationalOpportunityDetector().detect(
        context(), [signal(occurred_at=old)], now=NOW
    )
    assert record.rejected_signal_reasons[0][1] == "signal_is_stale"


def test_future_signal_is_rejected() -> None:
    record = ConversationalOpportunityDetector().detect(
        context(), [signal(occurred_at=NOW + timedelta(seconds=1))], now=NOW
    )
    assert record.rejected_signal_reasons[0][1] == "signal_is_from_the_future"


def test_guest_context_accepts_public_signal() -> None:
    record = ConversationalOpportunityDetector().detect(
        context(mode="guests", guests_present=True),
        [signal(sensitivity="public")],
        now=NOW,
    )
    assert len(record.opportunities) == 1


def test_guest_context_rejects_personal_signal() -> None:
    record = ConversationalOpportunityDetector().detect(
        context(mode="guests", guests_present=True), [signal()], now=NOW
    )
    assert record.rejected_signal_reasons[0][1] == (
        "guest_context_blocks_non_public_signal"
    )


def test_sensitive_context_rejects_sensitive_signal() -> None:
    record = ConversationalOpportunityDetector().detect(
        context(sensitive_context=True),
        [signal(sensitivity="sensitive")],
        now=NOW,
    )
    assert record.rejected_signal_reasons[0][1] == (
        "sensitive_signal_requires_separate_review"
    )


def test_sensitive_signal_outside_sensitive_context_requires_review() -> None:
    record = ConversationalOpportunityDetector().detect(
        context(), [signal(sensitivity="sensitive")], now=NOW
    )
    assert record.opportunities[0].requires_review is True


def test_duplicate_source_is_rejected() -> None:
    record = ConversationalOpportunityDetector().detect(
        context(), [signal(), signal(summary="duplicate")], now=NOW
    )
    assert len(record.opportunities) == 1
    assert record.rejected_signal_reasons == (
        ("memory-1#duplicate", "duplicate_source_id"),
    )


def test_capacity_is_enforced() -> None:
    detector = ConversationalOpportunityDetector(
        policy=OpportunityDetectionPolicy(maximum_opportunities=1)
    )
    record = detector.detect(
        context(), [signal(source_id="a"), signal(source_id="b")], now=NOW
    )
    assert len(record.opportunities) == 1
    assert any(
        reason == "opportunity_capacity_reached"
        for _, reason in record.rejected_signal_reasons
    )


def test_detection_is_persisted() -> None:
    repository = InMemoryOpportunityDetectionRepository()
    detector = ConversationalOpportunityDetector(repository=repository)
    record = detector.detect(context(), [signal()], now=NOW)
    assert repository.get(record.detection_id) == record
    assert detector.last_detection == record


def test_repository_rejects_duplicate_record() -> None:
    repository = InMemoryOpportunityDetectionRepository()
    record = OpportunityDetectionRecord(
        context=context(),
        accepted_signal_ids=(),
        rejected_signal_reasons=(),
        opportunities=(),
        detected_at=NOW,
    )
    repository.add(record)
    with pytest.raises(ValueError):
        repository.add(record)


def test_detection_record_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError):
        OpportunityDetectionRecord(
            context=context(),
            accepted_signal_ids=(),
            rejected_signal_reasons=(),
            opportunities=(),
            detected_at=datetime(2026, 7, 11),
        )


def test_m94_output_is_accepted_by_m93_boundary() -> None:
    record = ConversationalOpportunityDetector().detect(context(), [signal()], now=NOW)
    decision = LivingConversationManager().evaluate(
        context(), record.opportunities[0], now=NOW + timedelta(seconds=1)
    )
    assert decision.opportunity == record.opportunities[0]


def test_empty_signal_collection_produces_auditable_empty_record() -> None:
    record = ConversationalOpportunityDetector().detect(context(), [], now=NOW)
    assert record.opportunities == ()
    assert record.accepted_signal_ids == ()


def test_detector_does_not_mutate_input_collection() -> None:
    signals = [signal()]
    ConversationalOpportunityDetector().detect(context(), signals, now=NOW)
    assert signals == [signal()]


def test_system_prompt_states_non_authority_boundary() -> None:
    text = " ".join(ConversationalOpportunityDetector.system_prompt_lines())
    assert "no autoriza" in text
    assert "no genera lenguaje" in text
    assert "procedencia" in text
