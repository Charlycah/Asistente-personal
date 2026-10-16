from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import PurePosixPath


class DiagnosticObservationLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class DiagnosticTrendDirection(str, Enum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    STABLE = "stable"
    INCREASING = "increasing"
    DECREASING = "decreasing"


class DiagnosticAnomalyStatus(str, Enum):
    CLEAR = "clear"
    OBSERVED = "observed"


class DiagnosticThresholdDirection(str, Enum):
    ABOVE = "above"
    BELOW = "below"


class DiagnosticConfidenceLevel(str, Enum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DiagnosticProofStatus(str, Enum):
    REPRODUCED = "reproduced"
    NOT_REPRODUCED = "not_reproduced"
    INCONCLUSIVE = "inconclusive"


class DiagnosticProposalStatus(str, Enum):
    DRAFT = "draft"


@dataclass(frozen=True)
class DiagnosticObservation:
    observation_id: str
    source_authority: str
    metric: str
    value: float
    observed_at: datetime
    level: DiagnosticObservationLevel | str = DiagnosticObservationLevel.INFO
    evidence_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        observation_id = self.observation_id.strip()
        source_authority = self.source_authority.strip()
        metric = self.metric.strip()
        if not observation_id:
            raise ValueError("diagnostic observation requires observation_id")
        if not source_authority:
            raise ValueError("diagnostic observation requires source_authority")
        if not metric:
            raise ValueError("diagnostic observation requires metric")
        if self.observed_at.tzinfo is None:
            raise ValueError("diagnostic observation timestamp must be timezone-aware")
        codes = tuple(code.strip() for code in self.evidence_codes)
        if any(not code for code in codes):
            raise ValueError("diagnostic evidence codes must not be empty")
        object.__setattr__(self, "observation_id", observation_id)
        object.__setattr__(self, "source_authority", source_authority)
        object.__setattr__(self, "metric", metric)
        object.__setattr__(self, "level", DiagnosticObservationLevel(self.level))
        object.__setattr__(self, "evidence_codes", codes)


@dataclass(frozen=True)
class DiagnosticTrend:
    source_authority: str
    metric: str
    direction: DiagnosticTrendDirection | str
    sample_count: int
    first_value: float | None
    last_value: float | None
    observation_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.sample_count < 0:
            raise ValueError("diagnostic trend sample_count cannot be negative")
        if self.sample_count != len(self.observation_ids):
            raise ValueError("diagnostic trend sample_count must match evidence")
        object.__setattr__(self, "direction", DiagnosticTrendDirection(self.direction))


@dataclass(frozen=True)
class DiagnosticThreshold:
    metric: str
    limit: float
    direction: DiagnosticThresholdDirection | str
    minimum_consecutive_samples: int = 1

    def __post_init__(self) -> None:
        metric = self.metric.strip()
        if not metric:
            raise ValueError("diagnostic threshold requires metric")
        if self.minimum_consecutive_samples < 1:
            raise ValueError("minimum consecutive samples must be positive")
        object.__setattr__(self, "metric", metric)
        object.__setattr__(
            self,
            "direction",
            DiagnosticThresholdDirection(self.direction),
        )


@dataclass(frozen=True)
class DiagnosticAnomaly:
    source_authority: str
    metric: str
    status: DiagnosticAnomalyStatus | str
    threshold: DiagnosticThreshold
    consecutive_violations: int
    observation_ids: tuple[str, ...]
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.consecutive_violations < 0:
            raise ValueError("consecutive violations cannot be negative")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("diagnostic anomaly rationale must not be empty")
        object.__setattr__(self, "status", DiagnosticAnomalyStatus(self.status))


@dataclass(frozen=True)
class SelfDiagnosticReport:
    source_authority: str
    metric: str
    observations: tuple[DiagnosticObservation, ...]
    trend: DiagnosticTrend
    anomaly: DiagnosticAnomaly | None

    @property
    def anomaly_observed(self) -> bool:
        return (
            self.anomaly is not None
            and self.anomaly.status is DiagnosticAnomalyStatus.OBSERVED
        )


@dataclass(frozen=True)
class DiagnosticHypothesis:
    hypothesis_id: str
    statement: str
    supporting_observation_ids: tuple[str, ...]
    contradicting_observation_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        hypothesis_id = self.hypothesis_id.strip()
        statement = self.statement.strip()
        supporting = tuple(item.strip() for item in self.supporting_observation_ids)
        contradicting = tuple(
            item.strip() for item in self.contradicting_observation_ids
        )
        if not hypothesis_id:
            raise ValueError("diagnostic hypothesis requires hypothesis_id")
        if not statement:
            raise ValueError("diagnostic hypothesis requires statement")
        if any(not item for item in supporting + contradicting):
            raise ValueError("diagnostic hypothesis evidence ids must not be empty")
        if len(set(supporting)) != len(supporting):
            raise ValueError("supporting diagnostic evidence ids must be unique")
        if len(set(contradicting)) != len(contradicting):
            raise ValueError("contradicting diagnostic evidence ids must be unique")
        if set(supporting).intersection(contradicting):
            raise ValueError("diagnostic evidence cannot both support and contradict")
        object.__setattr__(self, "hypothesis_id", hypothesis_id)
        object.__setattr__(self, "statement", statement)
        object.__setattr__(self, "supporting_observation_ids", supporting)
        object.__setattr__(self, "contradicting_observation_ids", contradicting)


@dataclass(frozen=True)
class DiagnosticConfidencePolicy:
    minimum_supporting_evidence: int = 2
    minimum_supported_ratio: float = 0.6
    high_confidence_ratio: float = 0.85

    def __post_init__(self) -> None:
        if self.minimum_supporting_evidence < 1:
            raise ValueError("minimum supporting evidence must be positive")
        if not 0.0 <= self.minimum_supported_ratio <= 1.0:
            raise ValueError("minimum supported ratio must be between 0 and 1")
        if not 0.0 <= self.high_confidence_ratio <= 1.0:
            raise ValueError("high confidence ratio must be between 0 and 1")
        if self.high_confidence_ratio < self.minimum_supported_ratio:
            raise ValueError("high confidence ratio cannot be below supported ratio")


@dataclass(frozen=True)
class DiagnosticHypothesisAssessment:
    hypothesis: DiagnosticHypothesis
    confidence_level: DiagnosticConfidenceLevel | str
    confidence_score: float
    supporting_evidence_count: int
    contradicting_evidence_count: int
    evidence_codes: tuple[str, ...]
    policy: DiagnosticConfidencePolicy
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("diagnostic confidence score must be between 0 and 1")
        if self.supporting_evidence_count < 0 or self.contradicting_evidence_count < 0:
            raise ValueError("diagnostic evidence counts cannot be negative")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("diagnostic hypothesis rationale must not be empty")
        object.__setattr__(
            self,
            "confidence_level",
            DiagnosticConfidenceLevel(self.confidence_level),
        )


@dataclass(frozen=True)
class DiagnosticProofSpecification:
    proof_id: str
    hypothesis: DiagnosticHypothesis
    policy: DiagnosticConfidencePolicy
    source_authority: str
    metric: str
    expected_confidence_level: DiagnosticConfidenceLevel | str
    expected_confidence_score: float
    evidence_digest: str
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        proof_id = self.proof_id.strip()
        source_authority = self.source_authority.strip()
        metric = self.metric.strip()
        evidence_digest = self.evidence_digest.strip()
        if not proof_id:
            raise ValueError("diagnostic proof requires proof_id")
        if not source_authority or not metric:
            raise ValueError("diagnostic proof requires source authority and metric")
        if len(evidence_digest) != 64:
            raise ValueError("diagnostic proof requires sha256 evidence digest")
        if not 0.0 <= self.expected_confidence_score <= 1.0:
            raise ValueError("expected diagnostic confidence must be between 0 and 1")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("diagnostic proof rationale must not be empty")
        object.__setattr__(self, "proof_id", proof_id)
        object.__setattr__(self, "source_authority", source_authority)
        object.__setattr__(self, "metric", metric)
        object.__setattr__(self, "evidence_digest", evidence_digest)
        object.__setattr__(
            self,
            "expected_confidence_level",
            DiagnosticConfidenceLevel(self.expected_confidence_level),
        )


@dataclass(frozen=True)
class DiagnosticProofResult:
    proof_id: str
    hypothesis_id: str
    status: DiagnosticProofStatus | str
    reproduced_confidence_level: DiagnosticConfidenceLevel | str | None
    reproduced_confidence_score: float | None
    evidence_digest: str
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.reproduced_confidence_score is not None and not (
            0.0 <= self.reproduced_confidence_score <= 1.0
        ):
            raise ValueError("reproduced diagnostic confidence must be between 0 and 1")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("diagnostic proof result rationale must not be empty")
        object.__setattr__(self, "status", DiagnosticProofStatus(self.status))
        if self.reproduced_confidence_level is not None:
            object.__setattr__(
                self,
                "reproduced_confidence_level",
                DiagnosticConfidenceLevel(self.reproduced_confidence_level),
            )


@dataclass(frozen=True)
class DiagnosticProposalRequest:
    proposal_id: str
    title: str
    change_intent: str
    affected_files: tuple[str, ...]
    validation_tests: tuple[str, ...]
    risk_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        proposal_id = self.proposal_id.strip()
        title = self.title.strip()
        change_intent = self.change_intent.strip()
        affected_files = tuple(item.strip() for item in self.affected_files)
        validation_tests = tuple(item.strip() for item in self.validation_tests)
        risk_notes = tuple(item.strip() for item in self.risk_notes)
        if not proposal_id or "/" in proposal_id or "\\" in proposal_id:
            raise ValueError("diagnostic proposal requires safe proposal_id")
        if proposal_id in {".", ".."}:
            raise ValueError("diagnostic proposal requires safe proposal_id")
        if not title:
            raise ValueError("diagnostic proposal requires title")
        if not change_intent:
            raise ValueError("diagnostic proposal requires explicit change intent")
        if not affected_files or any(not item for item in affected_files):
            raise ValueError("diagnostic proposal requires affected files")
        if len(set(affected_files)) != len(affected_files):
            raise ValueError("diagnostic proposal affected files must be unique")
        if not validation_tests or any(not item for item in validation_tests):
            raise ValueError("diagnostic proposal requires validation tests")
        if any(not item for item in risk_notes):
            raise ValueError("diagnostic proposal risk notes must not be empty")
        object.__setattr__(self, "proposal_id", proposal_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "change_intent", change_intent)
        object.__setattr__(self, "affected_files", affected_files)
        object.__setattr__(self, "validation_tests", validation_tests)
        object.__setattr__(self, "risk_notes", risk_notes)


@dataclass(frozen=True)
class DiagnosticProposal:
    proposal_id: str
    status: DiagnosticProposalStatus | str
    proof_id: str
    hypothesis_id: str
    source_authority: str
    metric: str
    evidence_digest: str
    title: str
    change_intent: str
    affected_files: tuple[str, ...]
    validation_tests: tuple[str, ...]
    risk_notes: tuple[str, ...]
    review_path: str
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.review_path.startswith(".roby/review/proposals/"):
            raise ValueError("diagnostic proposal must use governed review path")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("diagnostic proposal rationale must not be empty")
        object.__setattr__(self, "status", DiagnosticProposalStatus(self.status))


class DiagnosticSandboxStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class DiagnosticSandboxFile:
    relative_path: str
    content: str

    def __post_init__(self) -> None:
        path = self.relative_path.strip().replace("\\", "/")
        if not path or path.startswith("/") or path.startswith("../"):
            raise ValueError("diagnostic sandbox file requires safe relative path")
        if "/../" in f"/{path}/" or path in {".", ".."}:
            raise ValueError("diagnostic sandbox file requires safe relative path")
        object.__setattr__(self, "relative_path", path)


@dataclass(frozen=True)
class DiagnosticSandboxRequest:
    sandbox_id: str
    candidate_files: tuple[DiagnosticSandboxFile, ...]

    def __post_init__(self) -> None:
        sandbox_id = self.sandbox_id.strip()
        if not sandbox_id or "/" in sandbox_id or "\\" in sandbox_id:
            raise ValueError("diagnostic sandbox requires safe sandbox_id")
        if sandbox_id in {".", ".."}:
            raise ValueError("diagnostic sandbox requires safe sandbox_id")
        if not self.candidate_files:
            raise ValueError("diagnostic sandbox requires explicit candidate files")
        paths = tuple(item.relative_path for item in self.candidate_files)
        if len(set(paths)) != len(paths):
            raise ValueError("diagnostic sandbox candidate files must be unique")
        object.__setattr__(self, "sandbox_id", sandbox_id)


@dataclass(frozen=True)
class DiagnosticSandboxResult:
    sandbox_id: str
    proposal_id: str
    status: DiagnosticSandboxStatus | str
    sandbox_path: str
    candidate_files: tuple[str, ...]
    validation_tests: tuple[str, ...]
    return_code: int | None
    stdout: str
    stderr: str
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.sandbox_path.startswith(".roby/review/proposals/"):
            raise ValueError("diagnostic sandbox must use governed review path")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("diagnostic sandbox rationale must not be empty")
        object.__setattr__(self, "status", DiagnosticSandboxStatus(self.status))

class DiagnosticReviewDecision(str, Enum):
    APPROVED_FOR_MANUAL_APPLICATION = "approved_for_manual_application"
    REJECTED = "rejected"


@dataclass(frozen=True)
class DiagnosticDiffFile:
    relative_path: str
    unified_diff: str

    def __post_init__(self) -> None:
        path = self.relative_path.strip().replace("\\", "/")
        diff = self.unified_diff.rstrip()
        if not path or path.startswith("/") or ".." in PurePosixPath(path).parts:
            raise ValueError("diagnostic diff requires safe relative path")
        if not diff:
            raise ValueError("diagnostic diff requires explicit unified diff")
        object.__setattr__(self, "relative_path", path)
        object.__setattr__(self, "unified_diff", diff)


@dataclass(frozen=True)
class DiagnosticReviewPackage:
    review_id: str
    proposal_id: str
    sandbox_id: str
    diff_files: tuple[DiagnosticDiffFile, ...]
    explanation: tuple[str, ...]
    review_path: str
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.review_id.strip():
            raise ValueError("diagnostic review requires review_id")
        if not self.diff_files:
            raise ValueError("diagnostic review requires explicit diff")
        if not self.explanation or any(not item.strip() for item in self.explanation):
            raise ValueError("diagnostic review requires explanation")
        if not self.review_path.startswith(".roby/review/proposals/"):
            raise ValueError("diagnostic review must use governed review path")


@dataclass(frozen=True)
class DiagnosticHumanDecision:
    review_id: str
    reviewer: str
    decision: DiagnosticReviewDecision | str
    explanation: str

    def __post_init__(self) -> None:
        reviewer = self.reviewer.strip()
        explanation = self.explanation.strip()
        if not reviewer:
            raise ValueError("diagnostic human decision requires reviewer")
        if not explanation:
            raise ValueError("diagnostic human decision requires explanation")
        object.__setattr__(self, "reviewer", reviewer)
        object.__setattr__(self, "explanation", explanation)
        object.__setattr__(self, "decision", DiagnosticReviewDecision(self.decision))

