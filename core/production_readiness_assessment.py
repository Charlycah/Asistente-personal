from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest
from core.operational_reliability_certification import (
    OperationalReliabilityCertificate,
    OperationalReliabilityCertifier,
    ReliabilityCertificationStatus,
)
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class ProductionReadinessStatus(str, Enum):
    READY = "ready"
    CONDITIONAL = "conditional"
    NOT_READY = "not_ready"


@dataclass(frozen=True)
class ReadinessCriterion:
    name: str
    passed: bool
    observed: str
    requirement: str

    def __post_init__(self) -> None:
        values = tuple(
            value.strip() for value in (self.name, self.observed, self.requirement)
        )
        if any(not value for value in values):
            raise ValueError("readiness criterion fields must not be blank")
        object.__setattr__(self, "name", values[0])
        object.__setattr__(self, "observed", values[1])
        object.__setattr__(self, "requirement", values[2])


@dataclass(frozen=True)
class ProductionReadinessAssessment:
    owner: str
    session_id: str
    status: ProductionReadinessStatus | str
    criteria: tuple[ReadinessCriterion, ...]
    reliability_certificate_id: str
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        certificate_id = self.reliability_certificate_id.strip()
        status = ProductionReadinessStatus(self.status)
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id or not certificate_id or not self.criteria:
            raise ValueError("readiness assessment identity and evidence are required")
        if self.created_at.tzinfo is None:
            raise ValueError("readiness assessment time must be timezone-aware")
        if len({item.name for item in self.criteria}) != len(self.criteria):
            raise ValueError("readiness criterion names must be unique")
        if len(set(references)) != len(references):
            raise ValueError("readiness assessment references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    certificate_id,
                    *(
                        f"{item.name}:{item.passed}:{item.observed}:{item.requirement}"
                        for item in self.criteria
                    ),
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode()
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("readiness assessment id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "reliability_certificate_id", certificate_id)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "assessment_id", expected)


class ProductionReadinessAssessor:
    """Assess production readiness from governed M218 certification evidence."""

    def __init__(
        self,
        certifier: OperationalReliabilityCertifier,
        *,
        require_full_certification: bool = True,
    ) -> None:
        self.certifier = certifier
        self.require_full_certification = require_full_certification
        self.last_assessment: ProductionReadinessAssessment | None = None

    def assess(
        self,
        *,
        owner: str,
        session_id: str,
        certificate: OperationalReliabilityCertificate | None = None,
        now: datetime | None = None,
    ) -> ProductionReadinessAssessment:
        evidence = certificate or self.certifier.last_certificate
        if evidence is None:
            raise ValueError(
                "production readiness requires M218 certification evidence"
            )
        if evidence.owner != owner.strip() or evidence.session_id != session_id.strip():
            raise ValueError(
                "certification evidence identity does not match readiness request"
            )
        passed_criteria = sum(item.passed for item in evidence.criteria)
        total_criteria = len(evidence.criteria)
        lineage_complete = bool(evidence.source_reference_ids)
        criteria = (
            ReadinessCriterion(
                "reliability_certification",
                evidence.status is ReliabilityCertificationStatus.CERTIFIED
                if self.require_full_certification
                else evidence.status is not ReliabilityCertificationStatus.REJECTED,
                evidence.status.value,
                "certified"
                if self.require_full_certification
                else "certified or conditional",
            ),
            ReadinessCriterion(
                "reliability_criteria",
                passed_criteria == total_criteria,
                f"{passed_criteria}/{total_criteria} passed",
                "all reliability criteria passed",
            ),
            ReadinessCriterion(
                "operational_lineage",
                lineage_complete,
                "complete" if lineage_complete else "missing",
                "traceable M211-M218 evidence",
            ),
            ReadinessCriterion(
                "bounded_execution_controls",
                any(
                    item.name == "bounded_coverage" and item.passed
                    for item in evidence.criteria
                ),
                "present"
                if any(
                    item.name == "bounded_coverage" and item.passed
                    for item in evidence.criteria
                )
                else "absent",
                "bounded validation coverage confirmed",
            ),
            ReadinessCriterion(
                "failure_controls",
                any(
                    item.name == "task_failure_rate" and item.passed
                    for item in evidence.criteria
                ),
                "within threshold"
                if any(
                    item.name == "task_failure_rate" and item.passed
                    for item in evidence.criteria
                )
                else "outside threshold",
                "task failure rate within certified threshold",
            ),
        )
        failed = sum(not item.passed for item in criteria)
        conditional_limit = 1 if self.require_full_certification else 2
        status = (
            ProductionReadinessStatus.READY
            if failed == 0
            and evidence.status is ReliabilityCertificationStatus.CERTIFIED
            else ProductionReadinessStatus.CONDITIONAL
            if failed <= conditional_limit
            and evidence.status is not ReliabilityCertificationStatus.REJECTED
            else ProductionReadinessStatus.NOT_READY
        )
        timestamp = now or datetime.now(timezone.utc)
        assessment = ProductionReadinessAssessment(
            owner=owner,
            session_id=session_id,
            status=status,
            criteria=criteria,
            reliability_certificate_id=evidence.certificate_id,
            source_reference_ids=(
                evidence.certificate_id,
                *evidence.source_reference_ids,
            ),
            created_at=timestamp,
        )
        self.last_assessment = assessment
        return assessment


@dataclass
class ProductionReadinessAssessmentRuntimeContributor:
    assessor: ProductionReadinessAssessor
    blackboard: UnifiedCognitiveBlackboard
    name: str = "production_readiness_assessment"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del text, request
        assessment = self.assessor.assess(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONSTRAINT,
                key=self.name,
                value=assessment.status.value,
                confidence=1.0,
                source_reference_ids=(
                    assessment.assessment_id,
                    *assessment.source_reference_ids,
                ),
                created_at=now,
            )
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(f"Preparación para producción: {assessment.status.value}.",),
            reference_ids=(
                entry.entry_id,
                assessment.assessment_id,
                *assessment.source_reference_ids,
            ),
            rationale=(
                "m218_certification_assessed",
                "production_controls_evaluated",
                "final_architecture_acceptance_reserved_for_m220",
            ),
        )
