from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable
from uuid import uuid4


class AutonomyLevel(str, Enum):
    """Maximum authority granted to a decision before execution."""

    OBSERVE_ONLY = "observe_only"
    RECOMMEND = "recommend"
    CONFIRM_BEFORE_ACTION = "confirm_before_action"
    AUTONOMOUS_LOW_RISK = "autonomous_low_risk"
    PROHIBITED = "prohibited"


class DecisionDisposition(str, Enum):
    """Governed result produced by an autonomy decision."""

    OBSERVE = "observe"
    RECOMMEND = "recommend"
    REQUEST_CONFIRMATION = "request_confirmation"
    AUTHORIZE = "authorize"
    BLOCK = "block"
    SIMULATE = "simulate"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROHIBITED = "prohibited"


class Reversibility(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


class OutcomeStatus(str, Enum):
    NOT_EXECUTED = "not_executed"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REVERTED = "reverted"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DecisionSituation:
    """Normalized situation that can be evaluated without executing actions."""

    kind: str
    description: str
    evidence: tuple[str, ...]
    observed_at: datetime
    source: str
    urgency: float = 0.0
    situation_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.kind, "situation kind")
        _require_text(self.description, "situation description")
        _require_text(self.source, "situation source")
        _require_text(self.situation_id, "situation id")
        _require_items(self.evidence, "situation evidence")
        _require_aware(self.observed_at, "situation timestamp")
        _require_unit_interval(self.urgency, "situation urgency")


@dataclass(frozen=True)
class ActionCandidate:
    """Possible response to a situation; this contract never executes it."""

    action: str
    description: str
    rationale: tuple[str, ...]
    reversible: Reversibility | str
    estimated_cost: float = 0.0
    candidate_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.action, "candidate action")
        _require_text(self.description, "candidate description")
        _require_text(self.candidate_id, "candidate id")
        _require_items(self.rationale, "candidate rationale")
        object.__setattr__(self, "reversible", Reversibility(self.reversible))
        if self.estimated_cost < 0.0:
            raise ValueError("candidate estimated cost must not be negative")


@dataclass(frozen=True)
class RiskAssessment:
    """Deterministic evaluation of one candidate for one situation."""

    candidate_id: str
    risk: RiskLevel | str
    confidence: float
    impact: float
    reversibility: Reversibility | str
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.candidate_id, "assessment candidate id")
        _require_unit_interval(self.confidence, "assessment confidence")
        _require_unit_interval(self.impact, "assessment impact")
        _require_items(self.reasons, "assessment reasons")
        object.__setattr__(self, "risk", RiskLevel(self.risk))
        object.__setattr__(
            self,
            "reversibility",
            Reversibility(self.reversibility),
        )


@dataclass(frozen=True)
class DecisionPolicy:
    """Explicit limits used by a later policy engine and autonomy gate."""

    autonomy_level: AutonomyLevel | str = AutonomyLevel.RECOMMEND
    minimum_confidence: float = 0.8
    maximum_automatic_risk: RiskLevel | str = RiskLevel.LOW
    require_reversible_automatic_actions: bool = True
    simulation_mode: bool = True
    maximum_attempts: int = 1
    prohibited_actions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "autonomy_level",
            AutonomyLevel(self.autonomy_level),
        )
        object.__setattr__(
            self,
            "maximum_automatic_risk",
            RiskLevel(self.maximum_automatic_risk),
        )
        _require_unit_interval(self.minimum_confidence, "minimum confidence")
        if self.maximum_attempts <= 0:
            raise ValueError("maximum decision attempts must be positive")
        if any(not item.strip() for item in self.prohibited_actions):
            raise ValueError("prohibited action names must not be blank")
        if len(set(self.prohibited_actions)) != len(self.prohibited_actions):
            raise ValueError("prohibited action names must be unique")


@dataclass(frozen=True)
class AutonomyDecision:
    """Auditable choice; authorization is represented but not executed."""

    situation_id: str
    candidate_id: str | None
    disposition: DecisionDisposition | str
    confidence: float
    risk: RiskLevel | str
    rationale: tuple[str, ...]
    decided_at: datetime
    policy_level: AutonomyLevel | str
    decision_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.situation_id, "decision situation id")
        _require_text(self.decision_id, "decision id")
        _require_unit_interval(self.confidence, "decision confidence")
        _require_items(self.rationale, "decision rationale")
        _require_aware(self.decided_at, "decision timestamp")
        disposition = DecisionDisposition(self.disposition)
        risk = RiskLevel(self.risk)
        policy_level = AutonomyLevel(self.policy_level)
        object.__setattr__(self, "disposition", disposition)
        object.__setattr__(self, "risk", risk)
        object.__setattr__(self, "policy_level", policy_level)
        if disposition in _CANDIDATE_REQUIRED and not _has_text(self.candidate_id):
            raise ValueError("decision disposition requires a candidate id")
        if disposition is DecisionDisposition.AUTHORIZE:
            if policy_level is not AutonomyLevel.AUTONOMOUS_LOW_RISK:
                raise ValueError(
                "authorization requires autonomous low-risk policy"
            )
            if risk is not RiskLevel.LOW:
                raise ValueError("only low-risk decisions can be authorized")
        if (
            risk is RiskLevel.PROHIBITED
            and disposition is not DecisionDisposition.BLOCK
        ):
            raise ValueError("prohibited risk must produce a blocked decision")


@dataclass(frozen=True)
class DecisionOutcome:
    """Observed result linked to a prior decision."""

    decision_id: str
    status: OutcomeStatus | str
    observed_at: datetime
    summary: str
    evidence: tuple[str, ...]
    reversible_action_used: bool = False
    outcome_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.decision_id, "outcome decision id")
        _require_text(self.summary, "outcome summary")
        _require_text(self.outcome_id, "outcome id")
        _require_items(self.evidence, "outcome evidence")
        _require_aware(self.observed_at, "outcome timestamp")
        object.__setattr__(self, "status", OutcomeStatus(self.status))


@dataclass(frozen=True)
class DecisionJournalEntry:
    """Immutable audit record connecting evaluation, decision and outcome."""

    situation: DecisionSituation
    candidates: tuple[ActionCandidate, ...]
    assessments: tuple[RiskAssessment, ...]
    decision: AutonomyDecision
    outcome: DecisionOutcome | None = None
    journal_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.journal_id, "journal id")
        if self.decision.situation_id != self.situation.situation_id:
            raise ValueError("journal decision must reference its situation")
        candidate_ids = {candidate.candidate_id for candidate in self.candidates}
        if len(candidate_ids) != len(self.candidates):
            raise ValueError("journal candidate ids must be unique")
        if self.decision.candidate_id is not None:
            if self.decision.candidate_id not in candidate_ids:
                raise ValueError("journal decision candidate is not present")
        assessment_ids = {assessment.candidate_id for assessment in self.assessments}
        if not assessment_ids.issubset(candidate_ids):
            raise ValueError("journal assessment references an unknown candidate")
        if len(assessment_ids) != len(self.assessments):
            raise ValueError("journal assessments must be unique per candidate")
        if self.outcome is not None:
            if self.outcome.decision_id != self.decision.decision_id:
                raise ValueError("journal outcome must reference its decision")


@runtime_checkable
class DecisionEngine(Protocol):
    """Future decision engine contract; implementations remain out of M326.1."""

    def decide(
        self,
        situation: DecisionSituation,
        candidates: tuple[ActionCandidate, ...],
        assessments: tuple[RiskAssessment, ...],
        policy: DecisionPolicy,
    ) -> AutonomyDecision: ...


@runtime_checkable
class DecisionJournal(Protocol):
    """Append-only journal port for later infrastructure adapters."""

    def append(self, entry: DecisionJournalEntry) -> None: ...

    def entries(self) -> tuple[DecisionJournalEntry, ...]: ...


_CANDIDATE_REQUIRED = frozenset(
    {
        DecisionDisposition.RECOMMEND,
        DecisionDisposition.REQUEST_CONFIRMATION,
        DecisionDisposition.AUTHORIZE,
        DecisionDisposition.SIMULATE,
    }
)


def _has_text(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be blank")


def _require_items(values: tuple[str, ...], label: str) -> None:
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must contain non-blank items")


def _require_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")


def _require_unit_interval(value: float, label: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{label} must be between zero and one")
