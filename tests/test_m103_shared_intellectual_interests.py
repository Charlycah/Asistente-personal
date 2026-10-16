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
    ConversationalRhythmRegulator,
    ConversationalRhythmRequest,
    ConversationOpportunity,
    ConversationTimingContext,
    ConversationTimingEngine,
    InMemorySharedIntellectualInterestsRepository,
    IntellectualCompanionLayer,
    IntellectualCompanionRequest,
    IntellectualInterestEvidence,
    IntellectualInterestEvidenceKind,
    LivingConversationContext,
    LivingConversationManager,
    ReflectionGenerator,
    SharedIntellectualInterests,
    SharedIntellectualInterestsPolicy,
    SharedIntellectualInterestsRequest,
    SharedIntellectualInterestStatus,
    SharedIntellectualInterestStrength,
)

NOW = datetime(2026, 7, 11, 15, 0, tzinfo=timezone.utc)


def rhythm(*, feedback_kind="acceptance", confidence=0.9):
    opportunity = ConversationOpportunity(
        kind="reflect",
        reason="Conecta con una conversación anterior.",
        value_score=0.94,
        relevance_score=0.93,
        confidence=0.95,
        content_hint="la memoria transforma nuestra lectura",
        source_reference_ids=("book:borges",),
    )
    context = LivingConversationContext(owner="Carlos")
    governance = LivingConversationManager().evaluate(context, opportunity, now=NOW)
    timing = ConversationTimingEngine().evaluate(
        ConversationTimingContext(
            conversation=context,
            activity=ConversationActivityState.AVAILABLE,
            cognitive_load=0.1,
            local_hour=15,
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
            domain="literature",
            thesis="La memoria vuelve interpretable el pasado.",
            concepts=("identidad", "tiempo"),
            requested_at=NOW,
        ),
        now=NOW,
    )
    realization = ConversationalRealizationLayer().realize(
        ConversationalRealizationRequest(
            contribution=contribution, owner="Carlos", requested_at=NOW
        ),
        now=NOW,
    )
    presence = ConversationalPresenceEngine().compose(
        ConversationalPresenceRequest(
            realization=realization, owner="Carlos", requested_at=NOW
        ),
        now=NOW,
    )
    feedback = ConversationalFeedbackLoop().assess(
        ConversationalFeedbackRequest(
            presence=presence,
            owner="Carlos",
            signals=(
                ConversationalFeedbackSignal(
                    kind=feedback_kind,
                    origin="explicit",
                    confidence=confidence,
                    evidence="user signal",
                ),
            ),
            requested_at=NOW,
        ),
        now=NOW,
    )
    return ConversationalRhythmRegulator().regulate(
        ConversationalRhythmRequest(
            feedback=feedback, owner="Carlos", requested_at=NOW
        ),
        now=NOW,
    )


def evidence(
    topic="Borges",
    kind="explicit",
    confidence=0.9,
    source="turn:1",
    note="",
):
    return IntellectualInterestEvidence(
        topic=topic,
        kind=kind,
        confidence=confidence,
        source_reference_id=source,
        note=note,
    )


def request(*items, rhythm_decision=None, owner="Carlos"):
    return SharedIntellectualInterestsRequest(
        rhythm=rhythm_decision or rhythm(),
        owner=owner,
        evidence=tuple(items),
        requested_at=NOW,
    )


def test_explicit_interest_is_identified():
    result = SharedIntellectualInterests().assess(request(evidence()), now=NOW)
    assert result.status is SharedIntellectualInterestStatus.IDENTIFIED
    assert result.interests[0].topic == "Borges"
    assert result.interests[0].explicit is True


def test_repeated_engagement_can_be_established():
    result = SharedIntellectualInterests().assess(
        request(evidence(kind="repeated_engagement", confidence=0.9)), now=NOW
    )
    assert (
        result.interests[0].strength is SharedIntellectualInterestStrength.ESTABLISHED
    )


def test_low_accepted_confidence_requires_review():
    result = SharedIntellectualInterests().assess(
        request(evidence(confidence=0.5)), now=NOW
    )
    assert result.status is SharedIntellectualInterestStatus.REVIEW_REQUIRED


def test_below_minimum_is_insufficient():
    result = SharedIntellectualInterests().assess(
        request(evidence(confidence=0.3)), now=NOW
    )
    assert result.status is SharedIntellectualInterestStatus.INSUFFICIENT
    assert result.interests == ()


def test_empty_evidence_is_insufficient():
    assert (
        SharedIntellectualInterests().assess(request(), now=NOW).status
        is SharedIntellectualInterestStatus.INSUFFICIENT
    )


def test_same_topic_is_aggregated_case_insensitively():
    result = SharedIntellectualInterests().assess(
        request(
            evidence("Borges"), evidence("borges", kind="deepening", source="turn:2")
        ),
        now=NOW,
    )
    assert len(result.interests) == 1
    assert result.interests[0].evidence_count == 2


def test_reinforcement_can_make_core_interest():
    result = SharedIntellectualInterests().assess(
        request(
            evidence(confidence=0.95),
            evidence(kind="deepening", confidence=0.95, source="turn:2"),
        ),
        now=NOW,
    )
    assert result.interests[0].strength is SharedIntellectualInterestStrength.CORE


def test_sources_are_deduplicated_preserving_order():
    result = SharedIntellectualInterests().assess(
        request(evidence(), evidence(kind="deepening")), now=NOW
    )
    assert result.interests[0].source_reference_ids == ("turn:1",)


def test_interests_are_sorted_by_score():
    result = SharedIntellectualInterests().assess(
        request(
            evidence("A", confidence=0.7),
            evidence("B", confidence=0.95, source="turn:2"),
        ),
        now=NOW,
    )
    assert [item.topic for item in result.interests] == ["B", "A"]


def test_tie_is_sorted_by_topic():
    result = SharedIntellectualInterests().assess(
        request(evidence("Zulu"), evidence("Alpha", source="turn:2")), now=NOW
    )
    assert [item.topic for item in result.interests] == ["Alpha", "Zulu"]


def test_maximum_interest_limit_is_applied():
    policy = SharedIntellectualInterestsPolicy(maximum_interests=1)
    result = SharedIntellectualInterests(policy=policy).assess(
        request(evidence("A"), evidence("B", source="turn:2")), now=NOW
    )
    assert len(result.interests) == 1
    assert "interest_limit_applied" in result.rationale


def test_review_rhythm_propagates_review():
    result = SharedIntellectualInterests().assess(
        request(evidence(), rhythm_decision=rhythm(confidence=0.5)), now=NOW
    )
    assert result.status is SharedIntellectualInterestStatus.REVIEW_REQUIRED


def test_not_actionable_rhythm_is_not_applicable():
    result = SharedIntellectualInterests().assess(
        request(evidence(), rhythm_decision=rhythm(confidence=0.2)), now=NOW
    )
    assert result.status is SharedIntellectualInterestStatus.NOT_APPLICABLE


def test_closing_rhythm_does_not_erase_interest():
    result = SharedIntellectualInterests().assess(
        request(evidence(), rhythm_decision=rhythm(feedback_kind="rejection")), now=NOW
    )
    assert result.interests
    assert "rhythm_discourages_immediate_activation" in result.rationale


def test_repository_stores_assessment():
    repository = InMemorySharedIntellectualInterestsRepository()
    service = SharedIntellectualInterests(repository=repository)
    result = service.assess(request(evidence()), now=NOW)
    assert repository.get(result.assessment_id) == result
    assert service.last_assessment == result


def test_duplicate_assessment_is_rejected():
    repository = InMemorySharedIntellectualInterestsRepository()
    service = SharedIntellectualInterests(repository=repository)
    result = service.assess(request(evidence()), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_deterministic_for_same_time():
    first = SharedIntellectualInterests().assess(request(evidence()), now=NOW)
    second = SharedIntellectualInterests().assess(request(evidence()), now=NOW)
    assert first.assessment_id == second.assessment_id


def test_assessment_is_immutable():
    result = SharedIntellectualInterests().assess(request(evidence()), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.status = "insufficient"


def test_evidence_is_immutable():
    item = evidence()
    with pytest.raises(FrozenInstanceError):
        item.topic = "Other"


@pytest.mark.parametrize(
    "kind", [item.value for item in IntellectualInterestEvidenceKind]
)
def test_all_evidence_kinds_are_supported(kind):
    result = SharedIntellectualInterests().assess(request(evidence(kind=kind)), now=NOW)
    assert result.interests[0].topic == "Borges"


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_evidence_confidence_is_bounded(value):
    with pytest.raises(ValueError):
        evidence(confidence=value)


def test_blank_topic_is_rejected():
    with pytest.raises(ValueError, match="topic"):
        evidence(topic="   ")


def test_blank_source_is_rejected():
    with pytest.raises(ValueError, match="source"):
        evidence(source=" ")


def test_owner_must_match_rhythm_owner():
    with pytest.raises(ValueError, match="match"):
        request(evidence(), owner="Cristina")


def test_naive_request_time_is_rejected():
    with pytest.raises(ValueError, match="aware"):
        SharedIntellectualInterestsRequest(
            rhythm=rhythm(), owner="Carlos", requested_at=datetime(2026, 7, 11)
        )


def test_naive_evaluation_time_is_rejected():
    with pytest.raises(ValueError, match="aware"):
        SharedIntellectualInterests().assess(
            request(evidence()), now=datetime(2026, 7, 11)
        )


def test_policy_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        SharedIntellectualInterestsPolicy(minimum_evidence_confidence=1.2)


def test_policy_rejects_zero_limit():
    with pytest.raises(ValueError):
        SharedIntellectualInterestsPolicy(maximum_interests=0)


def test_topic_whitespace_is_normalized():
    assert evidence(topic="  filosofía   de la mente ").topic == "filosofía de la mente"


def test_note_whitespace_is_normalized():
    assert evidence(note="  vuelve   varias veces ").note == "vuelve varias veces"
