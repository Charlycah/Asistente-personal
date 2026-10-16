from dataclasses import FrozenInstanceError, replace
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
    InMemoryLivingConversationIntegrationRepository,
    IntellectualCompanionLayer,
    IntellectualCompanionRequest,
    IntellectualCuriosityEngine,
    IntellectualCuriosityRequest,
    IntellectualInterestEvidence,
    LivingConversationContext,
    LivingConversationIntegration,
    LivingConversationIntegrationPolicy,
    LivingConversationIntegrationRequest,
    LivingConversationIntegrationStatus,
    LivingConversationIntegrator,
    LivingConversationManager,
    LivingConversationNextMove,
    ReflectionGenerator,
    SharedIntellectualInterests,
    SharedIntellectualInterestsRequest,
)
from core.living_conversation_runtime_integration import (
    LivingConversationRuntimeProjection,
    project_living_conversation_integration,
)

NOW = datetime(2026, 7, 11, 21, 0, tzinfo=timezone.utc)


def curiosity_plan(*, feedback_kind="acceptance", confidence=0.95, silence=0.0):
    opportunity = ConversationOpportunity(
        kind="reflect",
        reason="shared intellectual thread",
        value_score=0.95,
        relevance_score=0.94,
        confidence=0.96,
        content_hint="memory and identity",
        source_reference_ids=("source:root",),
    )
    context = LivingConversationContext(owner="Carlos")
    governance = LivingConversationManager().evaluate(context, opportunity, now=NOW)
    timing = ConversationTimingEngine().evaluate(
        ConversationTimingContext(
            conversation=context,
            activity=ConversationActivityState.AVAILABLE,
            cognitive_load=0.1,
            local_hour=18,
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
            thesis="Memory reshapes identity.",
            concepts=("memory", "identity"),
            requested_at=NOW,
        ),
        now=NOW,
    )
    realization = ConversationalRealizationLayer().realize(
        ConversationalRealizationRequest(
            contribution=contribution,
            owner="Carlos",
            requested_at=NOW,
        ),
        now=NOW,
    )
    presence = ConversationalPresenceEngine().compose(
        ConversationalPresenceRequest(
            realization=realization,
            owner="Carlos",
            requested_at=NOW,
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
    rhythm = ConversationalRhythmRegulator().regulate(
        ConversationalRhythmRequest(
            feedback=feedback,
            owner="Carlos",
            silence_seconds=silence,
            requested_at=NOW,
        ),
        now=NOW,
    )
    interests = SharedIntellectualInterests().assess(
        SharedIntellectualInterestsRequest(
            rhythm=rhythm,
            owner="Carlos",
            evidence=(
                IntellectualInterestEvidence(
                    topic="Borges",
                    kind="explicit",
                    confidence=confidence,
                    source_reference_id="turn:1",
                ),
            ),
            requested_at=NOW,
        ),
        now=NOW,
    )
    return IntellectualCuriosityEngine().generate(
        IntellectualCuriosityRequest(
            interests=interests,
            owner="Carlos",
            requested_at=NOW,
        ),
        now=NOW,
    )


def request(plan=None, **kwargs):
    return LivingConversationIntegrationRequest(
        curiosity=plan or curiosity_plan(),
        owner="Carlos",
        requested_at=NOW,
        **kwargs,
    )


def test_m105_projects_to_neutral_runtime_contract_without_authority_transfer():
    integration = LivingConversationIntegrator().integrate(request(), now=NOW)
    projection = project_living_conversation_integration(integration)

    assert isinstance(projection, LivingConversationRuntimeProjection)
    assert projection.owner == integration.request.owner
    assert projection.status is integration.status
    assert projection.next_move is integration.next_move
    assert projection.integration_id == integration.integration_id
    assert projection.stage_reference_ids == integration.stage_reference_ids
    assert projection.source_kind == "m105_living_conversation_integration"


def test_integrates_complete_living_conversation_cycle():
    result = LivingConversationIntegrator().integrate(request(), now=NOW)
    assert result.status is LivingConversationIntegrationStatus.READY
    assert result.next_move is LivingConversationNextMove.EXPLORE
    assert result.eligible_for_activation is True
    assert result.selected_prompt is not None


def test_integration_preserves_top_curiosity_prompt():
    plan = curiosity_plan()
    result = LivingConversationIntegrator().integrate(request(plan), now=NOW)
    assert result.selected_prompt == plan.prompts[0]


def test_integration_exposes_ten_ordered_stage_references():
    result = LivingConversationIntegrator().integrate(request(), now=NOW)
    assert len(result.stage_reference_ids) == 10
    assert result.stage_reference_ids[-1] == result.request.curiosity.plan_id


def test_integration_references_are_unique():
    result = LivingConversationIntegrator().integrate(request(), now=NOW)
    assert len(result.stage_reference_ids) == len(set(result.stage_reference_ids))


def test_low_confidence_chain_requires_review():
    plan = curiosity_plan(confidence=0.5)
    result = LivingConversationIntegrator().integrate(request(plan), now=NOW)
    assert result.status is LivingConversationIntegrationStatus.REVIEW_REQUIRED
    assert result.next_move is LivingConversationNextMove.CLARIFY
    assert result.eligible_for_activation is False


def test_rejection_closes_the_cycle():
    result = LivingConversationIntegrator().integrate(
        request(curiosity_plan(feedback_kind="rejection")), now=NOW
    )
    assert result.status is LivingConversationIntegrationStatus.PAUSED
    assert result.next_move is LivingConversationNextMove.CLOSE


def test_long_silence_preserves_user_floor_and_waits():
    result = LivingConversationIntegrator().integrate(
        request(curiosity_plan(silence=30.0)), now=NOW
    )
    assert result.status is LivingConversationIntegrationStatus.PAUSED
    assert result.next_move is LivingConversationNextMove.WAIT
    assert result.preserve_user_floor is True


def test_policy_can_allow_preserved_user_floor():
    engine = LivingConversationIntegrator(
        policy=LivingConversationIntegrationPolicy(
            block_when_user_floor_is_preserved=False,
        )
    )
    result = engine.integrate(request(curiosity_plan(silence=30.0)), now=NOW)
    assert result.status in {
        LivingConversationIntegrationStatus.READY,
        LivingConversationIntegrationStatus.PAUSED,
    }


def test_repository_stores_result():
    repository = InMemoryLivingConversationIntegrationRepository()
    engine = LivingConversationIntegrator(repository=repository)
    result = engine.integrate(request(), now=NOW)
    assert repository.get(result.integration_id) == result
    assert repository.list_all() == (result,)
    assert engine.last_integration == result


def test_empty_repository_has_no_last_integration():
    assert LivingConversationIntegrator().last_integration is None


def test_duplicate_integration_is_rejected():
    repository = InMemoryLivingConversationIntegrationRepository()
    result = LivingConversationIntegrator(repository=repository).integrate(
        request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_request_requires_owner():
    with pytest.raises(ValueError, match="owner"):
        LivingConversationIntegrationRequest(
            curiosity=curiosity_plan(), owner=" ", requested_at=NOW
        )


def test_request_owner_must_match_curiosity_owner():
    with pytest.raises(ValueError, match="match curiosity owner"):
        LivingConversationIntegrationRequest(
            curiosity=curiosity_plan(), owner="Cristina", requested_at=NOW
        )


def test_cycle_label_must_not_be_blank():
    with pytest.raises(ValueError, match="cycle label"):
        request(cycle_label=" ")


def test_request_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="aware"):
        LivingConversationIntegrationRequest(
            curiosity=curiosity_plan(),
            owner="Carlos",
            requested_at=datetime(2026, 7, 11),
        )


def test_integration_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="aware"):
        LivingConversationIntegrator().integrate(request(), now=datetime(2026, 7, 11))


def test_result_is_immutable():
    result = LivingConversationIntegrator().integrate(request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.status = "paused"


def test_request_is_immutable():
    item = request()
    with pytest.raises(FrozenInstanceError):
        item.owner = "Cristina"


def test_policy_is_immutable():
    policy = LivingConversationIntegrationPolicy()
    with pytest.raises(FrozenInstanceError):
        policy.require_generated_curiosity = False


def test_integration_id_is_deterministic():
    item = request()
    first = LivingConversationIntegrator().integrate(item, now=NOW)
    second = LivingConversationIntegrator().integrate(item, now=NOW)
    assert first.integration_id == second.integration_id


def test_integration_id_changes_with_cycle_label():
    first = LivingConversationIntegrator().integrate(request(), now=NOW)
    second = LivingConversationIntegrator().integrate(
        request(cycle_label="another-cycle"), now=NOW
    )
    assert first.integration_id != second.integration_id


def test_inconsistent_integration_id_is_rejected():
    result = LivingConversationIntegrator().integrate(request(), now=NOW)
    with pytest.raises(ValueError, match="inconsistent"):
        replace(result, integration_id="invalid")


@pytest.mark.parametrize("status", list(LivingConversationIntegrationStatus))
def test_status_enum_round_trip(status):
    assert LivingConversationIntegrationStatus(status.value) is status


@pytest.mark.parametrize("move", list(LivingConversationNextMove))
def test_next_move_enum_round_trip(move):
    assert LivingConversationNextMove(move.value) is move


def test_result_requires_stage_references():
    ready = LivingConversationIntegrator().integrate(request(), now=NOW)
    with pytest.raises(ValueError, match="references"):
        LivingConversationIntegration(
            request=ready.request,
            status="ready",
            next_move="explore",
            selected_prompt=ready.selected_prompt,
            eligible_for_activation=True,
            preserve_user_floor=False,
            stage_reference_ids=(),
            rationale=("valid",),
            created_at=NOW,
        )


def test_result_rejects_duplicate_stage_references():
    ready = LivingConversationIntegrator().integrate(request(), now=NOW)
    with pytest.raises(ValueError, match="unique"):
        replace(ready, stage_reference_ids=("same", "same"), integration_id="")


def test_result_requires_rationale():
    ready = LivingConversationIntegrator().integrate(request(), now=NOW)
    with pytest.raises(ValueError, match="rationale"):
        replace(ready, rationale=(), integration_id="")


def test_paused_result_cannot_select_prompt():
    ready = LivingConversationIntegrator().integrate(request(), now=NOW)
    with pytest.raises(ValueError, match="cannot select"):
        replace(
            ready,
            status="paused",
            next_move="wait",
            eligible_for_activation=False,
            integration_id="",
        )


def test_non_ready_result_cannot_be_eligible():
    ready = LivingConversationIntegrator().integrate(request(), now=NOW)
    with pytest.raises(ValueError, match="only ready"):
        replace(ready, status="review_required", integration_id="")


def test_ready_activation_requires_prompt():
    ready = LivingConversationIntegrator().integrate(request(), now=NOW)
    with pytest.raises(ValueError, match="requires a selected prompt"):
        replace(ready, selected_prompt=None, integration_id="")


def test_custom_cycle_label_is_preserved():
    result = LivingConversationIntegrator().integrate(
        request(cycle_label="phase-x-final"), now=NOW
    )
    assert result.request.cycle_label == "phase-x-final"


def test_integration_does_not_modify_curiosity_plan():
    plan = curiosity_plan()
    original = plan
    LivingConversationIntegrator().integrate(request(plan), now=NOW)
    assert plan == original
