from datetime import UTC, datetime

import pytest

from core.adaptive_personality import (
    AdaptiveDeliveryTone,
    AdaptivePersonalityAuthority,
    AdaptivePersonalityProfile,
    AdaptivePersonalityRequest,
    AdaptiveResponseDetail,
    AdaptiveResponseStructure,
)
from core.stable_personality import (
    PersonalityExpression,
    PersonalityTrait,
    StablePersonalitySnapshot,
)

NOW = datetime(2026, 8, 1, 22, 0, tzinfo=UTC)


def stable(
    expression: PersonalityExpression = PersonalityExpression.NEUTRAL,
) -> StablePersonalitySnapshot:
    return StablePersonalitySnapshot(
        expression=expression,
        active_traits=(
            PersonalityTrait.CALM,
            PersonalityTrait.PRECISE,
            PersonalityTrait.SUPPORTIVE,
            PersonalityTrait.RESPECTFUL,
            PersonalityTrait.CONSISTENT,
        ),
        consistency_score=0.9,
        reason="identidad estable",
        guidance=("preservar identidad",),
        created_at=NOW,
        snapshot_id="stable-1",
    )


def test_request_validates_normalized_ranges_and_explicit_values() -> None:
    with pytest.raises(ValueError):
        AdaptivePersonalityRequest(task_complexity=1.1)
    with pytest.raises(ValueError):
        AdaptivePersonalityRequest(urgency=-0.1)
    with pytest.raises(ValueError):
        AdaptivePersonalityRequest(requested_detail="unknown")


def test_authority_preserves_stable_traits_and_identity() -> None:
    profile = AdaptivePersonalityAuthority().adapt(stable())
    assert profile.normalized_traits == stable().normalized_traits
    assert profile.identity_changed is False
    assert profile.creates_parallel_brain is False
    assert "single_cognitive_core_preserved" in profile.rationale


def test_stable_expression_controls_delivery_tone() -> None:
    authority = AdaptivePersonalityAuthority()
    assert authority.adapt(stable(PersonalityExpression.WARM)).normalized_tone is (
        AdaptiveDeliveryTone.WARM
    )
    assert authority.adapt(stable(PersonalityExpression.DIRECT)).normalized_tone is (
        AdaptiveDeliveryTone.DIRECT
    )
    assert authority.adapt(stable(PersonalityExpression.REPAIRING)).normalized_tone is (
        AdaptiveDeliveryTone.REPAIRING
    )


def test_sensitive_context_becomes_careful_without_changing_identity() -> None:
    profile = AdaptivePersonalityAuthority().adapt(
        stable(PersonalityExpression.WARM),
        AdaptivePersonalityRequest(sensitive=True),
    )
    assert profile.normalized_tone is AdaptiveDeliveryTone.CAREFUL
    assert profile.stable_expression is PersonalityExpression.WARM
    assert profile.identity_changed is False


def test_explicit_user_preferences_control_detail_and_structure() -> None:
    profile = AdaptivePersonalityAuthority().adapt(
        stable(),
        AdaptivePersonalityRequest(
            requested_detail=AdaptiveResponseDetail.BRIEF,
            requested_structure=AdaptiveResponseStructure.PLAIN,
        ),
    )
    assert profile.normalized_detail is AdaptiveResponseDetail.BRIEF
    assert profile.normalized_structure is AdaptiveResponseStructure.PLAIN


def test_complexity_and_urgency_have_deterministic_defaults() -> None:
    authority = AdaptivePersonalityAuthority()
    detailed = authority.adapt(
        stable(), AdaptivePersonalityRequest(task_complexity=0.9)
    )
    urgent = authority.adapt(stable(), AdaptivePersonalityRequest(urgency=0.9))
    assert detailed.normalized_detail is AdaptiveResponseDetail.DETAILED
    assert detailed.normalized_structure is AdaptiveResponseStructure.STEPWISE
    assert urgent.normalized_detail is AdaptiveResponseDetail.BRIEF
    assert urgent.normalized_structure is AdaptiveResponseStructure.PLAIN


def test_profile_rejects_identity_or_parallel_brain_mutation() -> None:
    kwargs = dict(
        stable_snapshot_id="stable-1",
        stable_traits=(PersonalityTrait.CALM,),
        stable_expression=PersonalityExpression.NEUTRAL,
        delivery_tone=AdaptiveDeliveryTone.NEUTRAL,
        response_detail=AdaptiveResponseDetail.BALANCED,
        response_structure=AdaptiveResponseStructure.BULLETED,
        rationale=("governed",),
    )
    with pytest.raises(ValueError):
        AdaptivePersonalityProfile(**kwargs, identity_changed=True)
    with pytest.raises(ValueError):
        AdaptivePersonalityProfile(**kwargs, creates_parallel_brain=True)


def test_authority_has_no_learning_persistence_or_second_identity_api() -> None:
    authority = AdaptivePersonalityAuthority()
    assert not hasattr(authority, "learn_personality")
    assert not hasattr(authority, "persist_profile")
    assert not hasattr(authority, "create_identity")
    assert not hasattr(authority, "spawn_agent")
    assert not hasattr(authority, "call_llm")
