from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.adaptive_cognition.mental_models import MentalModel
from core.governed_reasoning import GovernedReasoningResult, GovernedReasoningStatus


class MetaReasoningDimension(str, Enum):
    EVIDENCE_SUFFICIENCY = "evidence_sufficiency"
    INFERENCE_QUALITY = "inference_quality"
    CONFLICT_HANDLING = "conflict_handling"
    UNCERTAINTY_CALIBRATION = "uncertainty_calibration"
    EXPLANATION_ADEQUACY = "explanation_adequacy"
    SCOPE_COMPLIANCE = "scope_compliance"


class MetaReasoningJudgement(str, Enum):
    SOUND = "sound"
    ACCEPTABLE = "acceptable"
    UNCERTAIN = "uncertain"
    DEFICIENT = "deficient"
    BLOCKED = "blocked"


class MetaReasoningFindingSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ReasoningReference:
    reference_type: str
    reference_id: str

    def __post_init__(self) -> None:
        if not self.reference_type.strip() or not self.reference_id.strip():
            raise ValueError("reasoning reference fields must not be empty")

    def to_dict(self) -> dict[str, str]:
        return {"type": self.reference_type, "id": self.reference_id}


@dataclass(frozen=True)
class MetaReasoningFinding:
    dimension: MetaReasoningDimension | str
    description: str
    severity: MetaReasoningFindingSeverity | str
    confidence: float
    references: tuple[ReasoningReference, ...] = ()
    finding_id: str = ""

    def __post_init__(self) -> None:
        dimension = MetaReasoningDimension(self.dimension)
        severity = MetaReasoningFindingSeverity(self.severity)
        if not self.description.strip():
            raise ValueError("meta-reasoning finding description must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("meta-reasoning finding confidence must be valid")
        keys = {(item.reference_type, item.reference_id) for item in self.references}
        if len(keys) != len(self.references):
            raise ValueError("meta-reasoning finding references must be unique")
        expected = sha256(
            "|".join(
                (
                    dimension.value,
                    severity.value,
                    self.description.strip(),
                    f"{self.confidence:.6f}",
                    ";".join(
                        f"{item.reference_type}:{item.reference_id}"
                        for item in self.references
                    ),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.finding_id and self.finding_id != expected:
            raise ValueError("meta-reasoning finding id is inconsistent")
        object.__setattr__(self, "finding_id", expected)

    @property
    def normalized_dimension(self) -> MetaReasoningDimension:
        return MetaReasoningDimension(self.dimension)

    @property
    def normalized_severity(self) -> MetaReasoningFindingSeverity:
        return MetaReasoningFindingSeverity(self.severity)

    def to_dict(self) -> dict[str, object]:
        return {
            "finding_id": self.finding_id,
            "dimension": self.normalized_dimension.value,
            "description": self.description,
            "severity": self.normalized_severity.value,
            "confidence": self.confidence,
            "references": [item.to_dict() for item in self.references],
        }


@dataclass(frozen=True)
class MetaReasoningAssessment:
    reasoning_result_id: str
    judgement: MetaReasoningJudgement | str
    score: float
    summary: str
    findings: tuple[MetaReasoningFinding, ...]
    recommendations: tuple[str, ...] = ()
    mental_model_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        judgement = MetaReasoningJudgement(self.judgement)
        if not self.reasoning_result_id.strip() or not self.summary.strip():
            raise ValueError("meta-reasoning assessment fields must not be empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("meta-reasoning score must be between zero and one")
        if not self.findings:
            raise ValueError("meta-reasoning assessment requires findings")
        if self.created_at.tzinfo is None:
            raise ValueError("meta-reasoning timestamp must be timezone-aware")
        if len(set(self.recommendations)) != len(self.recommendations):
            raise ValueError("meta-reasoning recommendations must be unique")
        if len(set(self.mental_model_ids)) != len(self.mental_model_ids):
            raise ValueError("mental model references must be unique")
        if any(not item.strip() for item in self.recommendations):
            raise ValueError("meta-reasoning recommendations must not be blank")
        expected = sha256(
            "|".join(
                (
                    self.reasoning_result_id,
                    judgement.value,
                    f"{self.score:.6f}",
                    self.summary,
                    ";".join(item.finding_id for item in self.findings),
                    ";".join(self.recommendations),
                    ";".join(self.mental_model_ids),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("meta-reasoning assessment id is inconsistent")
        object.__setattr__(self, "assessment_id", expected)

    @property
    def normalized_judgement(self) -> MetaReasoningJudgement:
        return MetaReasoningJudgement(self.judgement)

    @property
    def requires_review(self) -> bool:
        return self.normalized_judgement in {
            MetaReasoningJudgement.UNCERTAIN,
            MetaReasoningJudgement.DEFICIENT,
            MetaReasoningJudgement.BLOCKED,
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "assessment_id": self.assessment_id,
            "reasoning_result_id": self.reasoning_result_id,
            "judgement": self.normalized_judgement.value,
            "score": self.score,
            "summary": self.summary,
            "requires_review": self.requires_review,
            "findings": [item.to_dict() for item in self.findings],
            "recommendations": list(self.recommendations),
            "mental_model_ids": list(self.mental_model_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class MetaReasoningPolicy:
    sound_threshold: float = 0.85
    acceptable_threshold: float = 0.65
    uncertain_threshold: float = 0.4
    low_confidence_threshold: float = 0.6

    def __post_init__(self) -> None:
        values = (
            self.sound_threshold,
            self.acceptable_threshold,
            self.uncertain_threshold,
            self.low_confidence_threshold,
        )
        if any(not 0.0 <= item <= 1.0 for item in values):
            raise ValueError("meta-reasoning thresholds must be valid")
        if not (
            self.sound_threshold
            >= self.acceptable_threshold
            >= self.uncertain_threshold
        ):
            raise ValueError("meta-reasoning thresholds must be descending")


@runtime_checkable
class MetaReasoningRepository(Protocol):
    def add(self, assessment: MetaReasoningAssessment) -> None: ...
    def get(self, assessment_id: str) -> MetaReasoningAssessment | None: ...
    def list_all(self) -> tuple[MetaReasoningAssessment, ...]: ...
    def for_result(self, result_id: str) -> tuple[MetaReasoningAssessment, ...]: ...


class InMemoryMetaReasoningRepository:
    def __init__(self) -> None:
        self._items: dict[str, MetaReasoningAssessment] = {}

    def add(self, assessment: MetaReasoningAssessment) -> None:
        if assessment.assessment_id in self._items:
            raise ValueError("meta-reasoning assessment already exists")
        self._items[assessment.assessment_id] = assessment

    def get(self, assessment_id: str) -> MetaReasoningAssessment | None:
        return self._items.get(assessment_id)

    def list_all(self) -> tuple[MetaReasoningAssessment, ...]:
        return tuple(sorted(self._items.values(), key=lambda item: item.created_at))

    def for_result(self, result_id: str) -> tuple[MetaReasoningAssessment, ...]:
        return tuple(
            item for item in self.list_all() if item.reasoning_result_id == result_id
        )


class MetaReasoningEngine:
    def __init__(self, policy: MetaReasoningPolicy | None = None) -> None:
        self.policy = policy or MetaReasoningPolicy()

    def assess(
        self,
        result: GovernedReasoningResult,
        *,
        mental_models: tuple[MentalModel, ...] = (),
        now: datetime | None = None,
    ) -> MetaReasoningAssessment:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("meta-reasoning timestamp must be timezone-aware")
        findings = self._findings(result)
        score = self._score(result, findings)
        judgement = self._judgement(result, score)
        recommendations = self._recommendations(findings, judgement)
        return MetaReasoningAssessment(
            reasoning_result_id=result.result_id,
            judgement=judgement,
            score=score,
            summary=self._summary(judgement, score),
            findings=findings,
            recommendations=recommendations,
            mental_model_ids=tuple(sorted(model.model_id for model in mental_models)),
            created_at=timestamp,
        )

    def _findings(
        self, result: GovernedReasoningResult
    ) -> tuple[MetaReasoningFinding, ...]:
        refs = (
            ReasoningReference("reasoning_result", result.result_id),
            ReasoningReference("decision", result.decision.decision_id),
        )
        findings: list[MetaReasoningFinding] = []
        evidence_count = len(result.decision.evidence_links)
        findings.append(
            MetaReasoningFinding(
                MetaReasoningDimension.EVIDENCE_SUFFICIENCY,
                f"The decision references {evidence_count} evidence item(s).",
                MetaReasoningFindingSeverity.INFO
                if evidence_count
                else MetaReasoningFindingSeverity.HIGH,
                1.0,
                refs,
            )
        )
        conflict_count = len(result.conflict_analysis.conflicts)
        findings.append(
            MetaReasoningFinding(
                MetaReasoningDimension.CONFLICT_HANDLING,
                f"The reasoning run detected {conflict_count} conflict(s).",
                MetaReasoningFindingSeverity.MEDIUM
                if conflict_count
                else MetaReasoningFindingSeverity.INFO,
                result.conflict_analysis.confidence.score,
                refs,
            )
        )
        confidence = result.decision.confidence_score
        findings.append(
            MetaReasoningFinding(
                MetaReasoningDimension.UNCERTAINTY_CALIBRATION,
                f"The recorded decision confidence is {confidence:.2f}.",
                MetaReasoningFindingSeverity.HIGH
                if confidence < self.policy.low_confidence_threshold
                else MetaReasoningFindingSeverity.INFO,
                confidence,
                refs,
            )
        )
        findings.append(
            MetaReasoningFinding(
                MetaReasoningDimension.SCOPE_COMPLIANCE,
                f"The governed reasoning status is {result.status.value}.",
                MetaReasoningFindingSeverity.CRITICAL
                if result.status is GovernedReasoningStatus.BLOCKED
                else MetaReasoningFindingSeverity.INFO,
                1.0,
                refs,
            )
        )
        explanation_ok = bool(result.explanation.summary.strip())
        findings.append(
            MetaReasoningFinding(
                MetaReasoningDimension.EXPLANATION_ADEQUACY,
                "A traceable explanation was produced."
                if explanation_ok
                else "No usable explanation was produced.",
                MetaReasoningFindingSeverity.INFO
                if explanation_ok
                else MetaReasoningFindingSeverity.HIGH,
                1.0,
                refs,
            )
        )
        return tuple(findings)

    @staticmethod
    def _score(
        result: GovernedReasoningResult,
        findings: tuple[MetaReasoningFinding, ...],
    ) -> float:
        score = result.decision.confidence_score
        if not result.decision.evidence_links:
            score -= 0.2
        if result.conflict_analysis.conflicts:
            score -= 0.15
        if result.status is GovernedReasoningStatus.REVIEW_REQUIRED:
            score -= 0.1
        if result.status is GovernedReasoningStatus.ABSTAINED:
            score -= 0.25
        if result.status is GovernedReasoningStatus.BLOCKED:
            score = 0.0
        if any(
            item.normalized_severity is MetaReasoningFindingSeverity.CRITICAL
            for item in findings
        ):
            score = min(score, 0.2)
        return round(max(0.0, min(1.0, score)), 6)

    def _judgement(
        self, result: GovernedReasoningResult, score: float
    ) -> MetaReasoningJudgement:
        if result.status is GovernedReasoningStatus.BLOCKED:
            return MetaReasoningJudgement.BLOCKED
        if score >= self.policy.sound_threshold:
            return MetaReasoningJudgement.SOUND
        if score >= self.policy.acceptable_threshold:
            return MetaReasoningJudgement.ACCEPTABLE
        if score >= self.policy.uncertain_threshold:
            return MetaReasoningJudgement.UNCERTAIN
        return MetaReasoningJudgement.DEFICIENT

    @staticmethod
    def _recommendations(
        findings: tuple[MetaReasoningFinding, ...],
        judgement: MetaReasoningJudgement,
    ) -> tuple[str, ...]:
        recommendations: list[str] = []
        dimensions = {
            item.normalized_dimension
            for item in findings
            if item.normalized_severity
            in {
                MetaReasoningFindingSeverity.HIGH,
                MetaReasoningFindingSeverity.CRITICAL,
            }
        }
        if MetaReasoningDimension.EVIDENCE_SUFFICIENCY in dimensions:
            recommendations.append("Acquire additional governed evidence.")
        if MetaReasoningDimension.UNCERTAINTY_CALIBRATION in dimensions:
            recommendations.append("Request review before relying on the conclusion.")
        if MetaReasoningDimension.SCOPE_COMPLIANCE in dimensions:
            recommendations.append("Do not bypass the governing scope decision.")
        if judgement is MetaReasoningJudgement.DEFICIENT:
            recommendations.append("Re-run reasoning only after inputs are improved.")
        return tuple(recommendations)

    @staticmethod
    def _summary(judgement: MetaReasoningJudgement, score: float) -> str:
        return f"Meta-reasoning judged the process {judgement.value} ({score:.2f})."


class MetaReasoningManager:
    def __init__(
        self,
        repository: MetaReasoningRepository | None = None,
        *,
        engine: MetaReasoningEngine | None = None,
    ) -> None:
        self.repository = repository or InMemoryMetaReasoningRepository()
        self.engine = engine or MetaReasoningEngine()
        self.last_assessment: MetaReasoningAssessment | None = None

    def assess(
        self,
        result: GovernedReasoningResult,
        *,
        mental_models: tuple[MentalModel, ...] = (),
        now: datetime | None = None,
    ) -> MetaReasoningAssessment:
        assessment = self.engine.assess(result, mental_models=mental_models, now=now)
        self.repository.add(assessment)
        self.last_assessment = assessment
        return assessment

    def system_prompt_lines(self) -> tuple[str, ...]:
        return (
            "Meta-razonamiento: evalúa el proceso, no reemplaza su conclusión.",
            "No repitas razonamiento ni ejecutes recomendaciones automáticamente.",
            "Conserva incertidumbre, conflictos, alcance y trazabilidad.",
        )
