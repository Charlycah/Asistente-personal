from datetime import datetime, timezone

from core.controlled_autonomy import (
    ActionCandidate,
    DecisionPolicy,
    DecisionSituation,
    DeterministicDecisionPolicyEngine,
    DynamicPriorityAdjustment,
    ExperienceAwareDynamicPriorityProvider,
    ExperienceMemorySnapshot,
    ExperiencePattern,
    Reversibility,
    RiskAssessment,
    RiskLevel,
)

NOW = datetime(2026, 7, 27, 18, 0, tzinfo=timezone.utc)


class StaticMemory:
    def __init__(self, patterns: tuple[ExperiencePattern, ...]) -> None:
        self._snapshot = ExperienceMemorySnapshot(patterns)

    def remember(self, result):
        return None

    def snapshot(self) -> ExperienceMemorySnapshot:
        return self._snapshot


def _situation() -> DecisionSituation:
    return DecisionSituation(
        kind="runtime_component_unhealthy",
        description="Component requires attention",
        evidence=("component_id=test",),
        observed_at=NOW,
        source="test",
        urgency=0.8,
    )


def _candidate(identifier: str, action: str) -> ActionCandidate:
    return ActionCandidate(
        action=action,
        description=action,
        rationale=("test",),
        reversible=Reversibility.FULL,
        estimated_cost=0.1,
        candidate_id=identifier,
    )


def _assessment(identifier: str, confidence: float = 0.9) -> RiskAssessment:
    return RiskAssessment(
        candidate_id=identifier,
        risk=RiskLevel.LOW,
        confidence=confidence,
        impact=0.2,
        reversibility=Reversibility.FULL,
        reasons=("test",),
    )


def _pattern(action: str, *, succeeded: int, failed: int) -> ExperiencePattern:
    occurrences = succeeded + failed
    return ExperiencePattern(
        situation_kind="runtime_component_unhealthy",
        action=action,
        occurrences=occurrences,
        succeeded=succeeded,
        degraded=0,
        failed=failed,
        unknown=0,
        last_observed_at=NOW,
        last_summary="test outcome",
    )


def test_m327_8_successful_history_breaks_equal_score_tie() -> None:
    candidates = (_candidate("c1", "action_a"), _candidate("c2", "action_b"))
    assessments = (_assessment("c1"), _assessment("c2"))
    provider = ExperienceAwareDynamicPriorityProvider(
        StaticMemory(
            (
                _pattern("action_a", succeeded=0, failed=5),
                _pattern("action_b", succeeded=5, failed=0),
            )
        )
    )
    result = DeterministicDecisionPolicyEngine(priority_provider=provider).decide(
        _situation(), candidates, assessments, DecisionPolicy()
    )

    assert result.decision.candidate_id == "c2"
    assert "historical_outcome_priority" in result.scores[1].reasons


def test_m327_8_insufficient_history_does_not_change_order() -> None:
    candidates = (_candidate("c1", "action_a"), _candidate("c2", "action_b"))
    provider = ExperienceAwareDynamicPriorityProvider(
        StaticMemory((_pattern("action_b", succeeded=1, failed=0),))
    )
    result = DeterministicDecisionPolicyEngine(priority_provider=provider).decide(
        _situation(),
        candidates,
        (_assessment("c1"), _assessment("c2")),
        DecisionPolicy(),
    )

    assert result.decision.candidate_id == "c1"
    assert "insufficient_experience" in result.scores[1].reasons


def test_m327_8_priority_never_overrides_policy_eligibility() -> None:
    candidate = _candidate("c1", "successful_but_prohibited")
    provider = ExperienceAwareDynamicPriorityProvider(
        StaticMemory((_pattern(candidate.action, succeeded=5, failed=0),))
    )
    result = DeterministicDecisionPolicyEngine(priority_provider=provider).decide(
        _situation(),
        (candidate,),
        (_assessment("c1"),),
        DecisionPolicy(prohibited_actions=(candidate.action,)),
    )

    assert result.scores[0].eligible is False
    assert result.decision.disposition.value == "block"


def test_m327_8_adjustment_contract_is_bounded() -> None:
    try:
        DynamicPriorityAdjustment("c1", 0.13, ("test",))
    except ValueError as error:
        assert "between" in str(error)
    else:
        raise AssertionError("out-of-range adjustment must be rejected")
