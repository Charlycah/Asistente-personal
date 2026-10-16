from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.living_conversation import (
    ConversationActivityState,
    ConversationalPresenceEngine,
    ConversationalPresencePolicy,
    ConversationalPresenceRequest,
    ConversationalPresenceStance,
    ConversationalPresenceStatus,
    ConversationalRealizationLayer,
    ConversationalRealizationRequest,
    ConversationalTurnRelation,
    ConversationOpportunity,
    ConversationTimingContext,
    ConversationTimingEngine,
    InMemoryConversationalPresenceRepository,
    IntellectualCompanionLayer,
    IntellectualCompanionPolicy,
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


def test_ready_presence_is_composed() -> None:
    result = ConversationalPresenceEngine().compose(request(), now=NOW)
    assert result.status is ConversationalPresenceStatus.READY
    assert result.text == result.request.realization.text


def test_spontaneous_reflection_is_reflective() -> None:
    result = ConversationalPresenceEngine().compose(request(), now=NOW)
    assert result.stance is ConversationalPresenceStance.REFLECTIVE
    assert result.turn_relation is ConversationalTurnRelation.SPONTANEOUS_ENTRY


def test_direct_user_turn_is_responsive() -> None:
    item = realization(kind="respond", explicit=True)
    result = ConversationalPresenceEngine().compose(
        request(realization=item, user_initiated=True), now=NOW
    )
    assert result.stance is ConversationalPresenceStance.RESPONSIVE
    assert result.turn_relation is ConversationalTurnRelation.DIRECT_REPLY


def test_later_user_turn_is_attentive_follow_up() -> None:
    item = realization(kind="respond", explicit=True)
    result = ConversationalPresenceEngine().compose(
        request(realization=item, user_initiated=True, prior_exchange_count=2), now=NOW
    )
    assert result.stance is ConversationalPresenceStance.ATTENTIVE
    assert result.turn_relation is ConversationalTurnRelation.FOLLOW_UP
    assert result.acknowledge_prior_turn is True


def test_resume_is_companionable_continuation() -> None:
    item = realization(kind="resume")
    result = ConversationalPresenceEngine().compose(
        request(realization=item, continuity_thread_id="thread:books"), now=NOW
    )
    assert result.stance is ConversationalPresenceStance.COMPANIONABLE
    assert result.turn_relation is ConversationalTurnRelation.CONTINUATION


def test_thread_id_alone_establishes_continuation() -> None:
    result = ConversationalPresenceEngine().compose(
        request(continuity_thread_id="thread:memory"), now=NOW
    )
    assert result.turn_relation is ConversationalTurnRelation.CONTINUATION


def test_spontaneous_intensity_is_capped() -> None:
    policy = ConversationalPresencePolicy(spontaneous_intensity_cap=0.40)
    result = ConversationalPresenceEngine(policy=policy).compose(request(), now=NOW)
    assert result.intensity == 0.40


def test_global_intensity_is_capped() -> None:
    item = realization(kind="ask", explicit=True)
    policy = ConversationalPresencePolicy(maximum_intensity=0.60)
    result = ConversationalPresenceEngine(policy=policy).compose(
        request(realization=item, user_initiated=True), now=NOW
    )
    assert result.intensity == 0.60


def test_continuation_intensity_respects_floor() -> None:
    policy = ConversationalPresencePolicy(continuation_intensity_floor=0.70)
    result = ConversationalPresenceEngine(policy=policy).compose(
        request(continuity_thread_id="thread:memory"), now=NOW
    )
    assert result.intensity == 0.70


def test_question_keeps_follow_up_open() -> None:
    item = realization(kind="ask", explicit=True)
    result = ConversationalPresenceEngine().compose(
        request(realization=item, user_initiated=True), now=NOW
    )
    assert result.keep_follow_up_open is True


def test_connection_keeps_follow_up_open() -> None:
    result = ConversationalPresenceEngine().compose(request(), now=NOW)
    assert result.keep_follow_up_open is True


def test_observation_does_not_force_follow_up() -> None:
    item = realization(kind="share")
    result = ConversationalPresenceEngine().compose(request(realization=item), now=NOW)
    assert result.keep_follow_up_open is False


def test_request_can_close_follow_up() -> None:
    result = ConversationalPresenceEngine().compose(
        request(permit_follow_up=False), now=NOW
    )
    assert result.keep_follow_up_open is False


def test_policy_can_disable_open_follow_up() -> None:
    policy = ConversationalPresencePolicy(allow_open_follow_up=False)
    result = ConversationalPresenceEngine(policy=policy).compose(request(), now=NOW)
    assert result.keep_follow_up_open is False


def test_sources_are_preserved() -> None:
    item = request()
    result = ConversationalPresenceEngine().compose(item, now=NOW)
    assert result.source_reference_ids == item.realization.source_reference_ids


def test_spontaneous_presence_requires_sources_by_default() -> None:
    item = replace(realization(), source_reference_ids=(), realization_id="")
    result = ConversationalPresenceEngine().compose(request(realization=item), now=NOW)
    assert result.status is ConversationalPresenceStatus.ABSTAINED
    assert result.rationale == ("spontaneous_presence_requires_sources",)


def test_user_initiated_presence_can_have_no_sources() -> None:
    item = replace(
        realization(kind="respond", explicit=True),
        source_reference_ids=(),
        realization_id="",
    )
    result = ConversationalPresenceEngine().compose(
        request(realization=item, user_initiated=True), now=NOW
    )
    assert result.status is ConversationalPresenceStatus.READY


def test_source_requirement_can_be_disabled() -> None:
    item = replace(realization(), source_reference_ids=(), realization_id="")
    policy = ConversationalPresencePolicy(
        require_sources_for_spontaneous_presence=False
    )
    result = ConversationalPresenceEngine(policy=policy).compose(
        request(realization=item), now=NOW
    )
    assert result.status is ConversationalPresenceStatus.READY


def test_abstained_realization_propagates() -> None:
    base = realization()
    abstained = replace(
        base,
        status="abstained",
        segments=(),
        rationale=("test_abstention",),
        realization_id="",
    )
    result = ConversationalPresenceEngine().compose(
        request(realization=abstained), now=NOW
    )
    assert result.status is ConversationalPresenceStatus.ABSTAINED
    assert result.stance is ConversationalPresenceStance.RESTRAINED
    assert result.intensity == 0.0
    assert result.text is None


def test_review_required_realization_propagates() -> None:
    base = realization(domain="personal_project")
    governed = base.request.contribution.request
    review_contribution = IntellectualCompanionLayer(
        policy=IntellectualCompanionPolicy(require_review_for_personal_projects=True)
    ).compose(governed, now=NOW)
    review = ConversationalRealizationLayer().realize(
        ConversationalRealizationRequest(
            contribution=review_contribution,
            owner="Carlos",
            requested_at=NOW,
        ),
        now=NOW,
    )
    result = ConversationalPresenceEngine().compose(
        request(realization=review), now=NOW
    )
    assert result.status is ConversationalPresenceStatus.REVIEW_REQUIRED
    assert result.intensity == 0.0


def test_request_rejects_blank_owner() -> None:
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_request_rejects_wrong_owner() -> None:
    with pytest.raises(ValueError, match="match"):
        request(owner="Cristina")


def test_request_rejects_negative_exchange_count() -> None:
    with pytest.raises(ValueError, match="negative"):
        request(prior_exchange_count=-1)


def test_request_rejects_blank_thread_id() -> None:
    with pytest.raises(ValueError, match="thread"):
        request(continuity_thread_id=" ")


def test_request_requires_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="aware"):
        request(requested_at=datetime(2026, 7, 11, 13, 0))


def test_compose_requires_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="aware"):
        ConversationalPresenceEngine().compose(
            request(), now=datetime(2026, 7, 11, 13, 0)
        )


def test_policy_rejects_invalid_intensity() -> None:
    with pytest.raises(ValueError, match="between"):
        ConversationalPresencePolicy(maximum_intensity=1.1)


def test_policy_rejects_spontaneous_cap_above_maximum() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        ConversationalPresencePolicy(
            maximum_intensity=0.5,
            spontaneous_intensity_cap=0.6,
        )


def test_repository_stores_and_retrieves() -> None:
    repository = InMemoryConversationalPresenceRepository()
    engine = ConversationalPresenceEngine(repository=repository)
    result = engine.compose(request(), now=NOW)
    assert repository.get(result.presence_id) == result
    assert repository.list_all() == (result,)
    assert engine.last_presence == result


def test_repository_rejects_duplicate() -> None:
    repository = InMemoryConversationalPresenceRepository()
    item = ConversationalPresenceEngine().compose(request(), now=NOW)
    repository.add(item)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(item)


def test_presence_is_immutable() -> None:
    item = ConversationalPresenceEngine().compose(request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        item.intensity = 0.0  # type: ignore[misc]


def test_presence_id_is_deterministic_for_same_inputs() -> None:
    item = request()
    first = ConversationalPresenceEngine().compose(item, now=NOW)
    second = ConversationalPresenceEngine().compose(item, now=NOW)
    assert first.presence_id == second.presence_id
