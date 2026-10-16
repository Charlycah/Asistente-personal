from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable
from uuid import uuid4

from .contracts import (
    ActionCandidate,
    DecisionSituation,
    Reversibility,
    RiskAssessment,
    RiskLevel,
)


class RiskEvaluationStatus(str, Enum):
    ASSESSMENTS_GENERATED = "assessments_generated"
    NO_CANDIDATES = "no_candidates"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class RiskProfile:
    """Declarative scoring profile for one action name."""

    action: str
    base_risk: RiskLevel | str
    base_confidence: float
    base_impact: float
    reasons: tuple[str, ...]
    profile_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.action, "risk profile action")
        _require_text(self.profile_id, "risk profile id")
        _require_items(self.reasons, "risk profile reasons")
        _require_unit_interval(self.base_confidence, "base confidence")
        _require_unit_interval(self.base_impact, "base impact")
        object.__setattr__(self, "base_risk", RiskLevel(self.base_risk))


@dataclass(frozen=True)
class RiskEvaluationResult:
    status: RiskEvaluationStatus | str
    situation: DecisionSituation
    candidates: tuple[ActionCandidate, ...]
    assessments: tuple[RiskAssessment, ...]
    rationale: tuple[str, ...]
    evaluation_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.evaluation_id, "risk evaluation id")
        _require_items(self.rationale, "risk evaluation rationale")
        status = RiskEvaluationStatus(self.status)
        object.__setattr__(self, "status", status)
        candidate_ids = tuple(item.candidate_id for item in self.candidates)
        assessment_ids = tuple(item.candidate_id for item in self.assessments)
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("risk evaluation candidate ids must be unique")
        if len(set(assessment_ids)) != len(assessment_ids):
            raise ValueError("risk assessments must be unique per candidate")
        if status is RiskEvaluationStatus.ASSESSMENTS_GENERATED:
            if not self.candidates or len(self.assessments) != len(self.candidates):
                raise ValueError(
                    "generated evaluation requires one assessment per candidate"
                )
            if set(candidate_ids) != set(assessment_ids):
                raise ValueError("risk assessments must reference all candidates")
        elif self.assessments:
            raise ValueError("non-generated evaluation must not contain assessments")


@runtime_checkable
class RiskConfidenceEvaluator(Protocol):
    def evaluate(
        self,
        situation: DecisionSituation,
        candidates: tuple[ActionCandidate, ...],
    ) -> RiskEvaluationResult: ...


class DeterministicRiskConfidenceEvaluator:
    """Pure evaluator using explicit profiles and bounded deterministic modifiers."""

    def __init__(self, profiles: tuple[RiskProfile, ...]) -> None:
        identifiers = tuple(item.profile_id for item in profiles)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("risk profile ids must be unique")
        actions = tuple(item.action for item in profiles)
        if len(set(actions)) != len(actions):
            raise ValueError("risk profile actions must be unique")
        self._profiles = profiles
        self._by_action = {item.action: item for item in profiles}

    @property
    def profiles(self) -> tuple[RiskProfile, ...]:
        return self._profiles

    def evaluate(
        self,
        situation: DecisionSituation,
        candidates: tuple[ActionCandidate, ...],
    ) -> RiskEvaluationResult:
        if not candidates:
            return RiskEvaluationResult(
                status=RiskEvaluationStatus.NO_CANDIDATES,
                situation=situation,
                candidates=(),
                assessments=(),
                rationale=("no_candidates_to_evaluate",),
            )
        unsupported = tuple(
            candidate.action
            for candidate in candidates
            if candidate.action not in self._by_action
        )
        if unsupported:
            return RiskEvaluationResult(
                status=RiskEvaluationStatus.UNSUPPORTED,
                situation=situation,
                candidates=candidates,
                assessments=(),
                rationale=(
                    "missing_risk_profile",
                    *(f"unsupported_action={action}" for action in unsupported),
                ),
            )
        assessments = tuple(
            self._assess(situation, candidate, self._by_action[candidate.action])
            for candidate in candidates
        )
        return RiskEvaluationResult(
            status=RiskEvaluationStatus.ASSESSMENTS_GENERATED,
            situation=situation,
            candidates=candidates,
            assessments=assessments,
            rationale=(
                "all_candidates_matched_explicit_profiles",
                "bounded_modifiers_applied",
            ),
        )

    def _assess(
        self,
        situation: DecisionSituation,
        candidate: ActionCandidate,
        profile: RiskProfile,
    ) -> RiskAssessment:
        confidence = _clamp(
            profile.base_confidence
            + (0.08 * situation.urgency)
            - min(candidate.estimated_cost, 1.0) * 0.08
        )
        impact = _clamp(
            profile.base_impact
            + (0.12 * situation.urgency)
            + min(candidate.estimated_cost, 1.0) * 0.08
        )
        risk = _effective_risk(profile.base_risk, candidate.reversible, impact)
        reasons = (
            *profile.reasons,
            f"profile_id={profile.profile_id}",
            f"situation_id={situation.situation_id}",
            f"urgency={situation.urgency:.3f}",
            f"estimated_cost={candidate.estimated_cost:.3f}",
            f"reversibility={candidate.reversible.value}",
        )
        return RiskAssessment(
            candidate_id=candidate.candidate_id,
            risk=risk,
            confidence=round(confidence, 6),
            impact=round(impact, 6),
            reversibility=candidate.reversible,
            reasons=reasons,
        )


def default_risk_profiles() -> tuple[RiskProfile, ...]:
    return (
        _profile("verify_component_health", "low", 0.95, 0.1, "read_only_check"),
        _profile("notify_user", "low", 0.98, 0.15, "user_visibility"),
        _profile("do_nothing", "low", 0.99, 0.05, "observation_only"),
        _profile("restart_component", "medium", 0.82, 0.48, "runtime_mutation"),
        _profile("enter_degraded_mode", "medium", 0.88, 0.38, "service_reduction"),
        _profile("enable_power_saving", "medium", 0.86, 0.32, "runtime_profile_change"),
        _profile("deliver_reminder", "low", 0.96, 0.2, "expected_user_delivery"),
        _profile("postpone_reminder", "low", 0.9, 0.18, "temporary_deferral"),
    )


def _profile(
    action: str,
    risk: RiskLevel | str,
    confidence: float,
    impact: float,
    reason: str,
) -> RiskProfile:
    return RiskProfile(
        action=action,
        base_risk=risk,
        base_confidence=confidence,
        base_impact=impact,
        reasons=(reason,),
        profile_id=f"risk-profile-{action}",
    )


def _effective_risk(
    base: RiskLevel,
    reversibility: Reversibility,
    impact: float,
) -> RiskLevel:
    if base is RiskLevel.PROHIBITED:
        return base
    rank = {
        RiskLevel.LOW: 0,
        RiskLevel.MEDIUM: 1,
        RiskLevel.HIGH: 2,
    }
    reverse_penalty = {
        Reversibility.FULL: 0,
        Reversibility.PARTIAL: 0,
        Reversibility.NONE: 1,
    }[reversibility]
    impact_penalty = 1 if impact >= 0.75 else 0
    value = min(rank[base] + reverse_penalty + impact_penalty, 2)
    return (RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH)[value]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _has_text(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def _require_text(value: str | None, label: str) -> None:
    if not _has_text(value):
        raise ValueError(f"{label} must not be blank")


def _require_items(values: tuple[str, ...], label: str) -> None:
    if not values or any(not item.strip() for item in values):
        raise ValueError(f"{label} must contain non-blank items")


def _require_unit_interval(value: float, label: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{label} must be between 0.0 and 1.0")
