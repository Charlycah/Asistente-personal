from datetime import datetime, timezone

import pytest

from core.living_conversation import (
    ConversationContextMode,
    ConversationDisposition,
    ConversationOpportunity,
    ConversationOpportunityKind,
    InMemoryLivingConversationDecisionRepository,
    LivingConversationContext,
    LivingConversationDecision,
    LivingConversationManager,
    LivingConversationPolicy,
)

NOW = datetime(2026, 7, 10, 23, 0, tzinfo=timezone.utc)


def opportunity(**overrides: object) -> ConversationOpportunity:
    values = {
        "kind": "reflect",
        "reason": "a relevant connection may enrich the conversation",
        "value_score": 0.9,
        "relevance_score": 0.85,
        "confidence": 0.8,
        "content_hint": "connect the current topic with a prior reflection",
    }
    values.update(overrides)
    return ConversationOpportunity(**values)


def context(**overrides: object) -> LivingConversationContext:
    values = {"owner": "carlos", "mode": "home", "user_present": True}
    values.update(overrides)
    return LivingConversationContext(**values)


def test_opportunity_normalizes_kind_and_computes_score() -> None:
    item = opportunity()
    assert item.kind is ConversationOpportunityKind.REFLECT
    assert item.score == 0.8625


def test_opportunity_rejects_invalid_score() -> None:
    with pytest.raises(ValueError):
        opportunity(value_score=1.1)


def test_opportunity_rejects_duplicate_references() -> None:
    with pytest.raises(ValueError):
        opportunity(source_reference_ids=("a", "a"))


def test_context_normalizes_mode() -> None:
    item = context()
    assert item.mode is ConversationContextMode.HOME


def test_context_rejects_blank_owner() -> None:
    with pytest.raises(ValueError):
        context(owner=" ")


def test_private_mode_rejects_guests() -> None:
    with pytest.raises(ValueError):
        context(mode="private", guests_present=True)


def test_policy_rejects_unordered_thresholds() -> None:
    with pytest.raises(ValueError):
        LivingConversationPolicy(defer_threshold=0.8, intervention_threshold=0.7)


def test_policy_forbids_unsolicited_sensitive_content() -> None:
    with pytest.raises(ValueError):
        LivingConversationPolicy(allow_unsolicited_sensitive_content=True)


def test_policy_forbids_guest_personalization() -> None:
    with pytest.raises(ValueError):
        LivingConversationPolicy(allow_guest_personalization=True)


def test_decision_has_stable_identity() -> None:
    first = LivingConversationDecision(
        context(), opportunity(), "intervene", ("reason",), created_at=NOW
    )
    second = LivingConversationDecision(
        context(), opportunity(), "intervene", ("reason",), created_at=NOW
    )
    assert first.decision_id == second.decision_id


def test_decision_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError):
        LivingConversationDecision(
            context(),
            opportunity(),
            "intervene",
            ("reason",),
            created_at=datetime(2026, 7, 10),
        )


def test_repository_rejects_duplicates() -> None:
    repository = InMemoryLivingConversationDecisionRepository()
    decision = LivingConversationDecision(
        context(), opportunity(), "intervene", ("reason",), created_at=NOW
    )
    repository.add(decision)
    with pytest.raises(ValueError):
        repository.add(decision)


def test_do_not_disturb_always_silences() -> None:
    decision = LivingConversationManager().evaluate(
        context(do_not_disturb=True), opportunity(), now=NOW
    )
    assert decision.disposition is ConversationDisposition.REMAIN_SILENT


def test_absent_user_defers_without_scheduling() -> None:
    decision = LivingConversationManager().evaluate(
        context(user_present=False), opportunity(), now=NOW
    )
    assert decision.disposition is ConversationDisposition.DEFER
    assert "no_message_is_emitted_or_scheduled" in decision.rationale


def test_wait_opportunity_preserves_silence() -> None:
    decision = LivingConversationManager().evaluate(
        context(), opportunity(kind="wait"), now=NOW
    )
    assert decision.disposition is ConversationDisposition.REMAIN_SILENT


def test_guest_context_blocks_personalized_reference() -> None:
    decision = LivingConversationManager().evaluate(
        context(mode="guests", guests_present=True),
        opportunity(source_reference_ids=("relationship-1",)),
        now=NOW,
    )
    assert decision.disposition is ConversationDisposition.REMAIN_SILENT


def test_sensitive_context_requires_review() -> None:
    decision = LivingConversationManager().evaluate(
        context(sensitive_context=True), opportunity(), now=NOW
    )
    assert decision.disposition is ConversationDisposition.REVIEW_REQUIRED


def test_low_confidence_defers() -> None:
    decision = LivingConversationManager().evaluate(
        context(), opportunity(confidence=0.4), now=NOW
    )
    assert decision.disposition is ConversationDisposition.DEFER


def test_explicit_user_turn_receives_response() -> None:
    decision = LivingConversationManager().evaluate(
        context(explicit_user_turn=True),
        opportunity(value_score=0.2, relevance_score=0.2),
        now=NOW,
    )
    assert decision.should_intervene is True


def test_high_value_unsolicited_opportunity_may_intervene() -> None:
    decision = LivingConversationManager().evaluate(context(), opportunity(), now=NOW)
    assert decision.disposition is ConversationDisposition.INTERVENE


def test_medium_value_opportunity_defers() -> None:
    decision = LivingConversationManager().evaluate(
        context(),
        opportunity(value_score=0.55, relevance_score=0.5, confidence=0.7),
        now=NOW,
    )
    assert decision.disposition is ConversationDisposition.DEFER


def test_low_value_opportunity_remains_silent() -> None:
    decision = LivingConversationManager().evaluate(
        context(),
        opportunity(value_score=0.2, relevance_score=0.2, confidence=0.7),
        now=NOW,
    )
    assert decision.disposition is ConversationDisposition.REMAIN_SILENT


def test_evaluation_is_persisted() -> None:
    repository = InMemoryLivingConversationDecisionRepository()
    manager = LivingConversationManager(repository=repository)
    decision = manager.evaluate(context(), opportunity(), now=NOW)
    assert repository.get(decision.decision_id) == decision
    assert manager.last_decision == decision


def test_system_prompt_states_non_execution_boundary() -> None:
    text = " ".join(LivingConversationManager.system_prompt_lines())
    assert "silencio" in text
    assert "no emite mensajes" in text
    assert "Privacidad" in text
