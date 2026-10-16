from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.living_conversation import (
    ConversationOpportunity,
    ConversationTimingContext,
    ConversationTimingEngine,
    InMemoryReflectionDraftRepository,
    LivingConversationContext,
    LivingConversationManager,
    ReflectionDraft,
    ReflectionForm,
    ReflectionGenerationPolicy,
    ReflectionGenerator,
    ReflectionStatus,
    ReflectionTone,
)

NOW = datetime(2026, 7, 11, 15, 0, tzinfo=timezone.utc)


def context(**changes: object) -> LivingConversationContext:
    base = LivingConversationContext(owner="Carlos", mode="home")
    return replace(base, **changes)


def opportunity(**changes: object) -> ConversationOpportunity:
    base = ConversationOpportunity(
        kind="reflect",
        reason="Una idea previa conecta con el tema actual.",
        value_score=0.92,
        relevance_score=0.91,
        confidence=0.90,
        content_hint="la paciencia también puede ser una forma de inteligencia",
        source_reference_ids=("memory:42",),
    )
    return replace(base, **changes)


def decisions(
    item: ConversationOpportunity | None = None,
    conversation: LivingConversationContext | None = None,
):
    item = item or opportunity()
    conversation = conversation or context()
    governance = LivingConversationManager().evaluate(conversation, item, now=NOW)
    timing = ConversationTimingEngine().evaluate(
        ConversationTimingContext(
            conversation=conversation,
            activity="available",
            cognitive_load=0.2,
            local_hour=15,
        ),
        item,
        now=NOW,
    )
    return governance, timing


def test_generated_reflection_is_structured() -> None:
    draft = ReflectionGenerator().generate(*decisions(), now=NOW)
    assert draft.status is ReflectionStatus.GENERATED
    assert draft.form is ReflectionForm.CONNECTION
    assert draft.tone is ReflectionTone.THOUGHTFUL
    assert draft.opening
    assert draft.key_points
    assert draft.closing_question == "¿Cómo la ves?"


def test_generated_text_combines_components() -> None:
    draft = ReflectionGenerator().generate(*decisions(), now=NOW)
    assert draft.text is not None
    assert "paciencia" in draft.text
    assert "idea previa" in draft.text


@pytest.mark.parametrize(
    ("kind", "form", "tone"),
    [
        ("respond", ReflectionForm.RESPONSE, ReflectionTone.WARM),
        ("ask", ReflectionForm.QUESTION, ReflectionTone.CURIOUS),
        ("reflect", ReflectionForm.CONNECTION, ReflectionTone.THOUGHTFUL),
        ("share", ReflectionForm.OBSERVATION, ReflectionTone.NEUTRAL),
        ("resume", ReflectionForm.CONTINUATION, ReflectionTone.WARM),
    ],
)
def test_kind_maps_to_form_and_tone(
    kind: str, form: ReflectionForm, tone: ReflectionTone
) -> None:
    item = opportunity(kind=kind)
    draft = ReflectionGenerator().generate(*decisions(item), now=NOW)
    assert draft.form is form
    assert draft.tone is tone


def test_response_can_be_generated_without_sources() -> None:
    item = opportunity(kind="respond", source_reference_ids=())
    draft = ReflectionGenerator().generate(*decisions(item), now=NOW)
    assert draft.status is ReflectionStatus.GENERATED
    assert draft.text == item.content_hint


def test_non_response_without_sources_abstains() -> None:
    item = opportunity(source_reference_ids=())
    draft = ReflectionGenerator().generate(*decisions(item), now=NOW)
    assert draft.status is ReflectionStatus.ABSTAINED
    assert draft.rationale == ("source_reference_is_required",)


def test_missing_content_hint_abstains() -> None:
    item = opportunity(content_hint=None)
    draft = ReflectionGenerator().generate(*decisions(item), now=NOW)
    assert draft.status is ReflectionStatus.ABSTAINED
    assert draft.text is None


def test_governance_defer_abstains() -> None:
    item = opportunity(value_score=0.5, relevance_score=0.5, confidence=0.8)
    draft = ReflectionGenerator().generate(*decisions(item), now=NOW)
    assert draft.rationale == ("governance_does_not_authorize_intervention",)


def test_timing_defer_abstains() -> None:
    item = opportunity()
    conversation = context()
    governance = LivingConversationManager().evaluate(conversation, item, now=NOW)
    timing = ConversationTimingEngine().evaluate(
        ConversationTimingContext(
            conversation=conversation,
            activity="busy",
            cognitive_load=0.2,
            local_hour=15,
        ),
        item,
        now=NOW,
    )
    draft = ReflectionGenerator().generate(governance, timing, now=NOW)
    assert draft.rationale == ("timing_window_is_not_open",)


def test_review_required_is_preserved() -> None:
    item = opportunity(requires_review=True)
    draft = ReflectionGenerator().generate(*decisions(item), now=NOW)
    assert draft.status is ReflectionStatus.REVIEW_REQUIRED
    assert draft.text is None


@pytest.mark.parametrize("kind", ["wait", "silence"])
def test_restraint_opportunities_never_generate(kind: str) -> None:
    item = opportunity(kind=kind)
    governance, timing = decisions(item, context(explicit_user_turn=True))
    draft = ReflectionGenerator().generate(governance, timing, now=NOW)
    assert draft.status is ReflectionStatus.ABSTAINED


def test_context_mismatch_is_rejected() -> None:
    item = opportunity()
    governance, _ = decisions(item)
    _, timing = decisions(item, context(mode="work"))
    with pytest.raises(ValueError, match="contexts must match"):
        ReflectionGenerator().generate(governance, timing, now=NOW)


def test_opportunity_mismatch_is_rejected() -> None:
    governance, _ = decisions(opportunity(content_hint="uno"))
    _, timing = decisions(opportunity(content_hint="dos"))
    with pytest.raises(ValueError, match="same opportunity"):
        ReflectionGenerator().generate(governance, timing, now=NOW)


def test_length_limit_causes_abstention() -> None:
    item = opportunity(content_hint="x" * 90)
    generator = ReflectionGenerator(
        policy=ReflectionGenerationPolicy(maximum_text_length=80)
    )
    draft = generator.generate(*decisions(item), now=NOW)
    assert draft.status is ReflectionStatus.ABSTAINED
    assert draft.rationale == ("generated_draft_exceeds_length_limit",)


def test_policy_rejects_small_length_limit() -> None:
    with pytest.raises(ValueError):
        ReflectionGenerationPolicy(maximum_text_length=79)


def test_policy_rejects_sensitive_bypass() -> None:
    with pytest.raises(ValueError):
        ReflectionGenerationPolicy(allow_sensitive_without_review=True)


def test_draft_is_persisted() -> None:
    repository = InMemoryReflectionDraftRepository()
    generator = ReflectionGenerator(repository=repository)
    draft = generator.generate(*decisions(), now=NOW)
    assert repository.get(draft.reflection_id) == draft
    assert generator.last_draft == draft


def test_repository_rejects_duplicate_draft() -> None:
    repository = InMemoryReflectionDraftRepository()
    draft = ReflectionGenerator(repository=repository).generate(*decisions(), now=NOW)
    with pytest.raises(ValueError):
        repository.add(draft)


def test_reflection_id_is_deterministic() -> None:
    first = ReflectionGenerator().generate(*decisions(), now=NOW)
    second = ReflectionGenerator().generate(*decisions(), now=NOW)
    assert first.reflection_id == second.reflection_id


def test_draft_is_immutable() -> None:
    draft = ReflectionGenerator().generate(*decisions(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        draft.opening = "cambio"  # type: ignore[misc]


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError):
        ReflectionGenerator().generate(*decisions(), now=datetime(2026, 7, 11, 15, 0))


def test_non_generated_draft_cannot_contain_content() -> None:
    governance, timing = decisions()
    with pytest.raises(ValueError):
        ReflectionDraft(
            opportunity=governance.opportunity,
            governance_decision_id=governance.decision_id,
            timing_decision_id=timing.timing_id,
            status="abstained",
            form="connection",
            tone="thoughtful",
            opening="No permitido",
            key_points=(),
            closing_question=None,
            source_reference_ids=("memory:42",),
            rationale=("test",),
            generated_at=NOW,
        )


def test_sources_are_preserved_exactly() -> None:
    item = opportunity(source_reference_ids=("memory:42", "document:7"))
    draft = ReflectionGenerator().generate(*decisions(item), now=NOW)
    assert draft.source_reference_ids == item.source_reference_ids


def test_system_prompt_documents_non_execution_boundary() -> None:
    lines = ReflectionGenerator.system_prompt_lines()
    assert any("No habla" in line for line in lines)
    assert any("no llama a un LLM" in line for line in lines)
    assert any("No inventa hechos" in line for line in lines)
