from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.living_conversation import (
    ConversationActivityState,
    ConversationalAct,
    ConversationalRealizationLayer,
    ConversationalRealizationPolicy,
    ConversationalRealizationRequest,
    ConversationalRealizationStatus,
    ConversationOpportunity,
    ConversationTimingContext,
    ConversationTimingEngine,
    InMemoryConversationalRealizationRepository,
    IntellectualCompanionLayer,
    IntellectualCompanionPolicy,
    IntellectualCompanionRequest,
    LivingConversationContext,
    LivingConversationManager,
    ReflectionGenerator,
)

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)


def contribution(
    *,
    kind: str = "reflect",
    owner: str = "Carlos",
    explicit: bool = False,
    domain: str = "literature",
    closing: bool = True,
):
    opportunity = ConversationOpportunity(
        kind=kind,
        reason="La idea conecta con una conversación anterior.",
        value_score=0.94,
        relevance_score=0.93,
        confidence=0.95,
        content_hint="la memoria transforma nuestra lectura del presente",
        source_reference_ids=("book:borges",),
    )
    context = LivingConversationContext(owner=owner, explicit_user_turn=explicit)
    governance = LivingConversationManager().evaluate(context, opportunity, now=NOW)
    timing = ConversationTimingEngine().evaluate(
        ConversationTimingContext(
            conversation=context,
            activity=ConversationActivityState.AVAILABLE,
            cognitive_load=0.1,
            local_hour=12,
        ),
        opportunity,
        now=NOW,
    )
    reflection = ReflectionGenerator().generate(governance, timing, now=NOW)
    if not closing:
        reflection = replace(reflection, closing_question=None, reflection_id="")
    return IntellectualCompanionLayer().compose(
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


def request(**changes):
    values = {
        "contribution": contribution(),
        "owner": "Carlos",
        "requested_at": NOW,
    }
    values.update(changes)
    return ConversationalRealizationRequest(**values)


def test_ready_realization_is_produced() -> None:
    result = ConversationalRealizationLayer().realize(request(), now=NOW)
    assert result.status is ConversationalRealizationStatus.READY
    assert result.act is ConversationalAct.CONNECTION
    assert result.text is not None


def test_realization_preserves_sources() -> None:
    item = request()
    result = ConversationalRealizationLayer().realize(item, now=NOW)
    assert result.source_reference_ids == item.contribution.source_reference_ids


def test_natural_register_has_opening_and_two_key_points() -> None:
    result = ConversationalRealizationLayer().realize(request(), now=NOW)
    assert result.segments[0] == "veo una conexión interesante."
    assert len(result.segments) == 5


def test_concise_register_omits_opening_and_limits_points() -> None:
    result = ConversationalRealizationLayer().realize(
        request(register="concise"), now=NOW
    )
    assert result.segments[0].startswith("La memoria")
    assert len(result.segments) == 3


def test_deliberate_register_includes_all_key_points() -> None:
    result = ConversationalRealizationLayer().realize(
        request(register="deliberate"), now=NOW
    )
    assert len(result.segments) == 7
    assert any("experiencia" in segment for segment in result.segments)


def test_owner_can_be_addressed() -> None:
    result = ConversationalRealizationLayer().realize(
        request(address_owner=True), now=NOW
    )
    assert result.segments[0].startswith("Carlos, ")


def test_owner_address_can_be_disabled_by_policy() -> None:
    layer = ConversationalRealizationLayer(
        policy=ConversationalRealizationPolicy(allow_owner_address=False)
    )
    result = layer.realize(request(address_owner=True), now=NOW)
    assert result.status is ConversationalRealizationStatus.ABSTAINED
    assert result.text is None


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("respond", ConversationalAct.ANSWER),
        ("ask", ConversationalAct.QUESTION),
        ("reflect", ConversationalAct.CONNECTION),
        ("share", ConversationalAct.OBSERVATION),
        ("resume", ConversationalAct.CONTINUATION),
    ],
)
def test_contribution_kind_maps_to_act(kind: str, expected: ConversationalAct) -> None:
    item = contribution(kind=kind, explicit=kind == "respond")
    result = ConversationalRealizationLayer().realize(
        request(contribution=item), now=NOW
    )
    assert result.act is expected


def test_question_requires_closing_question_by_default() -> None:
    item = contribution(kind="ask", closing=False)
    result = ConversationalRealizationLayer().realize(
        request(contribution=item), now=NOW
    )
    assert result.status is ConversationalRealizationStatus.ABSTAINED
    assert result.rationale == ("question_realization_requires_closing_question",)


def test_question_requirement_can_be_relaxed() -> None:
    item = contribution(kind="ask", closing=False)
    layer = ConversationalRealizationLayer(
        policy=ConversationalRealizationPolicy(
            require_closing_question_for_questions=False
        )
    )
    result = layer.realize(request(contribution=item), now=NOW)
    assert result.status is ConversationalRealizationStatus.READY


def test_title_is_excluded_by_default() -> None:
    item = request()
    result = ConversationalRealizationLayer().realize(item, now=NOW)
    assert item.contribution.title not in result.text


def test_title_can_be_included() -> None:
    layer = ConversationalRealizationLayer(
        policy=ConversationalRealizationPolicy(allow_title_in_utterance=True)
    )
    item = request()
    result = layer.realize(item, now=NOW)
    assert f"{item.contribution.title}." in result.segments


def test_character_limit_abstains() -> None:
    layer = ConversationalRealizationLayer(
        policy=ConversationalRealizationPolicy(maximum_character_count=20)
    )
    result = layer.realize(request(), now=NOW)
    assert result.status is ConversationalRealizationStatus.ABSTAINED
    assert result.rationale == ("realization_exceeds_character_limit",)


def test_segment_limit_abstains() -> None:
    layer = ConversationalRealizationLayer(
        policy=ConversationalRealizationPolicy(maximum_segments=2)
    )
    result = layer.realize(request(), now=NOW)
    assert result.status is ConversationalRealizationStatus.ABSTAINED
    assert result.rationale == ("realization_exceeds_segment_limit",)


def test_review_required_is_preserved() -> None:
    base = contribution(domain="personal_project")
    governed = base.request
    review = IntellectualCompanionLayer(
        policy=IntellectualCompanionPolicy(require_review_for_personal_projects=True)
    ).compose(governed, now=NOW)
    result = ConversationalRealizationLayer().realize(
        request(contribution=review), now=NOW
    )
    assert result.status is ConversationalRealizationStatus.REVIEW_REQUIRED
    assert result.text is None


def test_abstained_contribution_remains_abstained() -> None:
    base = contribution()
    abstained = replace(
        base,
        status="abstained",
        title=None,
        thesis=None,
        key_points=(),
        closing_question=None,
        rationale=("test_abstention",),
        contribution_id="",
    )
    result = ConversationalRealizationLayer().realize(
        request(contribution=abstained), now=NOW
    )
    assert result.status is ConversationalRealizationStatus.ABSTAINED
    assert result.text is None


def test_request_rejects_blank_owner() -> None:
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_request_rejects_mismatched_owner() -> None:
    with pytest.raises(ValueError, match="match"):
        request(owner="Cristina")


def test_request_requires_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        request(requested_at=datetime(2026, 7, 11, 12, 0))


def test_realize_requires_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ConversationalRealizationLayer().realize(
            request(), now=datetime(2026, 7, 11, 12, 0)
        )


def test_repository_stores_and_retrieves() -> None:
    repository = InMemoryConversationalRealizationRepository()
    layer = ConversationalRealizationLayer(repository=repository)
    item = layer.realize(request(), now=NOW)
    assert repository.get(item.realization_id) == item
    assert repository.list_all() == (item,)
    assert layer.last_realization == item


def test_repository_rejects_duplicate() -> None:
    repository = InMemoryConversationalRealizationRepository()
    item = ConversationalRealizationLayer().realize(request(), now=NOW)
    repository.add(item)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(item)


def test_realization_is_immutable() -> None:
    item = ConversationalRealizationLayer().realize(request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        item.segments = ()  # type: ignore[misc]


def test_realization_id_is_deterministic() -> None:
    one = ConversationalRealizationLayer().realize(request(), now=NOW)
    two = ConversationalRealizationLayer().realize(request(), now=NOW)
    assert one.realization_id == two.realization_id


def test_realization_rejects_inconsistent_id() -> None:
    item = ConversationalRealizationLayer().realize(request(), now=NOW)
    with pytest.raises(ValueError, match="inconsistent"):
        replace(item, realization_id="bad")


def test_policy_rejects_non_positive_character_limit() -> None:
    with pytest.raises(ValueError, match="character"):
        ConversationalRealizationPolicy(maximum_character_count=0)


def test_policy_rejects_non_positive_segment_limit() -> None:
    with pytest.raises(ValueError, match="segment"):
        ConversationalRealizationPolicy(maximum_segments=0)


def test_text_has_normalized_terminal_punctuation() -> None:
    result = ConversationalRealizationLayer().realize(request(), now=NOW)
    assert all(segment.endswith((".", "!", "?")) for segment in result.segments)
