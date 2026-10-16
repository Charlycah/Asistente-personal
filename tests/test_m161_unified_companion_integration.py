from dataclasses import FrozenInstanceError, replace

import pytest

from core.companion_reliability_model import CompanionReliabilityStatus
from core.long_term_experience_evaluation import LongTermExperienceStatus
from core.unified_companion_integration import (
    InMemoryUnifiedCompanionIntegrationRepository,
    UnifiedCompanionIntegration,
    UnifiedCompanionIntegrationAction,
    UnifiedCompanionIntegrationConfig,
    UnifiedCompanionIntegrationRequest,
    UnifiedCompanionIntegrationResult,
    UnifiedCompanionIntegrationStatus,
)
from tests.test_m160_long_term_experience_evaluation import (
    EVAL_NOW,
)
from tests.test_m160_long_term_experience_evaluation import (
    evaluate as experience_evaluate,
)

NOW = EVAL_NOW
BASE = experience_evaluate(now=NOW)


def request(result=BASE, **changes):
    values = {"owner": "Carlos", "experience_result": result}
    values.update(changes)
    return UnifiedCompanionIntegrationRequest(**values)


def integrate(result=BASE, *, config=None, now=NOW, **changes):
    return UnifiedCompanionIntegration(config=config).integrate(
        request(result, **changes), now=now
    )


def experience_with(
    *, experience_status=None, reliability_status=None, confidence=None
):
    reliability = BASE.selected_reliability_result
    assert reliability is not None
    if reliability_status is not None or confidence is not None:
        reliability = replace(
            reliability,
            status=reliability_status or reliability.status,
            confidence=confidence if confidence is not None else reliability.confidence,
            reliable=(reliability_status or reliability.status)
            is CompanionReliabilityStatus.RELIABLE,
            degraded=(reliability_status or reliability.status)
            is CompanionReliabilityStatus.DEGRADED,
            unavailable=(reliability_status or reliability.status)
            is CompanionReliabilityStatus.UNAVAILABLE,
            confirmation_required=(reliability_status or reliability.status)
            is CompanionReliabilityStatus.REVIEW_REQUIRED,
            reliability_id="",
        )
    status = experience_status or BASE.status
    return replace(
        BASE,
        status=status,
        action={
            LongTermExperienceStatus.POSITIVE: "declare_positive",
            LongTermExperienceStatus.MIXED: "declare_mixed",
            LongTermExperienceStatus.NEGATIVE: "declare_negative",
        }.get(status, BASE.action),
        selected_reliability_result=reliability,
        selected_permission_result=reliability.selected_permission_result,
        selected_continuity=reliability.selected_continuity,
        selected_timing_evaluation=reliability.selected_timing_evaluation,
        selected_candidate=reliability.selected_candidate,
        selected_opportunity=reliability.selected_opportunity,
        positive=status is LongTermExperienceStatus.POSITIVE,
        mixed=status is LongTermExperienceStatus.MIXED,
        negative=status is LongTermExperienceStatus.NEGATIVE,
        insufficient=status is LongTermExperienceStatus.INSUFFICIENT,
        confirmation_required=status is LongTermExperienceStatus.REVIEW_REQUIRED,
        confidence=confidence if confidence is not None else BASE.confidence,
        evaluation_id="",
    )


def test_ready_unified_companion_integration():
    result = integrate()
    assert result.status is UnifiedCompanionIntegrationStatus.READY
    assert result.action is UnifiedCompanionIntegrationAction.DECLARE_READY
    assert result.ready and not result.degraded and not result.hold


def test_preserves_complete_m160_to_m150_lineage():
    result = integrate()
    assert result.selected_experience_result is BASE
    assert result.selected_reliability_result is BASE.selected_reliability_result
    assert len(result.stage_reference_ids) == 7
    assert result.stage_reference_ids[0] == BASE.evaluation_id


def test_mixed_experience_is_degraded_by_default():
    result = integrate(
        experience_with(experience_status=LongTermExperienceStatus.MIXED)
    )
    assert result.status is UnifiedCompanionIntegrationStatus.DEGRADED
    assert result.action is UnifiedCompanionIntegrationAction.DECLARE_DEGRADED


def test_policy_can_hold_mixed_experience():
    config = UnifiedCompanionIntegrationConfig(allow_mixed_experience=False)
    result = integrate(
        experience_with(experience_status=LongTermExperienceStatus.MIXED), config=config
    )
    assert result.status is UnifiedCompanionIntegrationStatus.HOLD


def test_negative_experience_holds():
    result = integrate(
        experience_with(experience_status=LongTermExperienceStatus.NEGATIVE)
    )
    assert result.status is UnifiedCompanionIntegrationStatus.HOLD
    assert result.confirmation_required


def test_degraded_reliability_degrades_integration():
    result = integrate(
        experience_with(reliability_status=CompanionReliabilityStatus.DEGRADED)
    )
    assert result.status is UnifiedCompanionIntegrationStatus.DEGRADED


def test_unavailable_reliability_holds():
    result = integrate(
        experience_with(reliability_status=CompanionReliabilityStatus.UNAVAILABLE)
    )
    assert result.status is UnifiedCompanionIntegrationStatus.HOLD


def test_low_confidence_holds():
    result = integrate(experience_with(confidence=0.5))
    assert result.status is UnifiedCompanionIntegrationStatus.HOLD
    assert result.rationale == ("unified_companion_confidence_below_threshold",)


def test_confidence_boundary_is_accepted():
    config = UnifiedCompanionIntegrationConfig(minimum_confidence=BASE.confidence)
    assert integrate(config=config).status is UnifiedCompanionIntegrationStatus.READY


def test_not_requested_is_not_applicable():
    result = integrate(integration_requested=False)
    assert result.status is UnifiedCompanionIntegrationStatus.NOT_APPLICABLE
    assert not result.stage_reference_ids


def test_not_applicable_experience_is_not_applicable():
    source = experience_evaluate(evaluation_requested=False, now=NOW)
    result = integrate(source)
    assert result.status is UnifiedCompanionIntegrationStatus.NOT_APPLICABLE


def test_blocked_experience_is_blocked():
    source = experience_evaluate(
        results=(
            replace(
                BASE.selected_reliability_result,
                request=replace(
                    BASE.selected_reliability_result.request, owner="Other"
                ),
                reliability_id="",
            ),
        ),
        items=(),
        now=NOW,
    )
    result = integrate(source)
    assert result.status is UnifiedCompanionIntegrationStatus.BLOCKED


@pytest.mark.parametrize(
    "status",
    [LongTermExperienceStatus.INSUFFICIENT, LongTermExperienceStatus.REVIEW_REQUIRED],
)
def test_experience_without_lineage_is_blocked(status):
    source = experience_evaluate(results=(), items=(), now=NOW)
    source = replace(
        source,
        status=status,
        action="declare_insufficient"
        if status is LongTermExperienceStatus.INSUFFICIENT
        else "hold",
        insufficient=status is LongTermExperienceStatus.INSUFFICIENT,
        confirmation_required=status is LongTermExperienceStatus.REVIEW_REQUIRED,
        evaluation_id="",
    )
    assert integrate(source).status is UnifiedCompanionIntegrationStatus.BLOCKED


def test_repository_stores_result_and_exposes_last():
    repository = InMemoryUnifiedCompanionIntegrationRepository()
    engine = UnifiedCompanionIntegration(repository=repository)
    result = engine.integrate(request(), now=NOW)
    assert repository.get(result.integration_id) is result
    assert repository.list_all() == (result,)
    assert engine.last_integration is result


def test_empty_repository_has_no_last_integration():
    assert UnifiedCompanionIntegration().last_integration is None


def test_duplicate_result_is_rejected():
    repository = InMemoryUnifiedCompanionIntegrationRepository()
    engine = UnifiedCompanionIntegration(repository=repository)
    result = engine.integrate(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_owner_is_required():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_owner_must_match_experience_owner():
    with pytest.raises(ValueError, match="match experience owner"):
        request(owner="Other")


def test_cycle_label_is_required():
    with pytest.raises(ValueError, match="cycle label"):
        request(cycle_label=" ")


def test_minimum_confidence_must_be_bounded():
    with pytest.raises(ValueError, match="between zero and one"):
        UnifiedCompanionIntegrationConfig(minimum_confidence=1.1)


def test_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        integrate(now=NOW.replace(tzinfo=None))


def test_result_is_immutable():
    result = integrate()
    with pytest.raises(FrozenInstanceError):
        result.ready = False


def test_identifier_is_deterministic():
    assert integrate().integration_id == integrate().integration_id


def test_identifier_changes_with_cycle_label():
    assert integrate().integration_id != integrate(cycle_label="other").integration_id


def test_bad_identifier_is_rejected():
    result = integrate()
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(result, integration_id="bad")


def test_stage_references_are_unique():
    result = integrate()
    assert len(result.stage_reference_ids) == len(set(result.stage_reference_ids))


def test_all_execution_capabilities_remain_forbidden():
    result = integrate()
    fields = (
        "activation_allowed",
        "conversation_start_allowed",
        "device_selection_allowed",
        "channel_selection_allowed",
        "context_transfer_allowed",
        "scheduling_allowed",
        "prompt_generation_allowed",
        "response_realization_allowed",
        "provider_call_allowed",
        "automation_allowed",
        "platform_mutation_allowed",
    )
    assert not any(getattr(result, field) for field in fields)


def test_result_rejects_execution_authorization():
    result = integrate()
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, activation_allowed=True, integration_id="")


def test_inactive_result_cannot_expose_lineage():
    result = integrate(integration_requested=False)
    with pytest.raises(ValueError, match="inactive integration"):
        replace(result, selected_experience_result=BASE, integration_id="")


def test_active_result_requires_full_lineage():
    result = integrate()
    with pytest.raises(ValueError, match="full lineage"):
        replace(result, selected_candidate=None, integration_id="")


def test_result_rejects_inconsistent_flags():
    result = integrate()
    with pytest.raises(ValueError, match="flags are inconsistent"):
        replace(result, ready=False, integration_id="")


def test_repository_protocol_is_runtime_checkable():
    from core.unified_companion_integration import UnifiedCompanionIntegrationRepository

    assert isinstance(
        InMemoryUnifiedCompanionIntegrationRepository(),
        UnifiedCompanionIntegrationRepository,
    )


def test_public_result_type_is_exposed():
    assert (
        UnifiedCompanionIntegrationResult.__name__
        == "UnifiedCompanionIntegrationResult"
    )
