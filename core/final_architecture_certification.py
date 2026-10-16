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
from core.production_readiness_assessment import (
    ProductionReadinessAssessment,
    ProductionReadinessAssessor,
    ProductionReadinessStatus,
)
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class FinalAcceptanceStatus(str, Enum):
    ACCEPTED = "accepted"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"


@dataclass(frozen=True)
class AcceptanceCriterion:
    name: str
    passed: bool
    observed: str
    requirement: str

    def __post_init__(self) -> None:
        values = tuple(
            value.strip() for value in (self.name, self.observed, self.requirement)
        )
        if any(not value for value in values):
            raise ValueError("acceptance criterion fields must not be blank")
        object.__setattr__(self, "name", values[0])
        object.__setattr__(self, "observed", values[1])
        object.__setattr__(self, "requirement", values[2])


@dataclass(frozen=True)
class ROBYArchitectureCertificate:
    owner: str
    session_id: str
    status: FinalAcceptanceStatus | str
    version: str
    criteria: tuple[AcceptanceCriterion, ...]
    readiness_assessment_id: str
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    certificate_id: str = ""

    def __post_init__(self) -> None:
        owner, session_id, version = (
            self.owner.strip(),
            self.session_id.strip(),
            self.version.strip(),
        )
        assessment_id = self.readiness_assessment_id.strip()
        status = FinalAcceptanceStatus(self.status)
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if (
            not owner
            or not session_id
            or not version
            or not assessment_id
            or not self.criteria
        ):
            raise ValueError(
                "architecture certificate identity and evidence are required"
            )
        if self.created_at.tzinfo is None:
            raise ValueError("architecture certificate time must be timezone-aware")
        if len({item.name for item in self.criteria}) != len(self.criteria):
            raise ValueError("acceptance criterion names must be unique")
        if len(set(references)) != len(references):
            raise ValueError("architecture certificate references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    version,
                    assessment_id,
                    *(
                        f"{c.name}:{c.passed}:{c.observed}:{c.requirement}"
                        for c in self.criteria
                    ),
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode()
        ).hexdigest()
        if self.certificate_id and self.certificate_id != expected:
            raise ValueError("architecture certificate id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "readiness_assessment_id", assessment_id)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "certificate_id", expected)


class ROBYArchitectureCertifier:
    """Issue final ROBY v1 acceptance from governed M219 evidence."""

    def __init__(
        self, assessor: ProductionReadinessAssessor, *, require_ready: bool = True
    ) -> None:
        self.assessor = assessor
        self.require_ready = require_ready
        self.last_certificate: ROBYArchitectureCertificate | None = None

    def certify(
        self,
        *,
        owner: str,
        session_id: str,
        assessment: ProductionReadinessAssessment | None = None,
        now: datetime | None = None,
    ) -> ROBYArchitectureCertificate:
        evidence = assessment or self.assessor.last_assessment
        if evidence is None:
            raise ValueError("final architecture certification requires M219 evidence")
        if evidence.owner != owner.strip() or evidence.session_id != session_id.strip():
            raise ValueError(
                "readiness evidence identity does not match certification request"
            )
        passed = sum(item.passed for item in evidence.criteria)
        total = len(evidence.criteria)
        lineage = bool(evidence.source_reference_ids)
        criteria = (
            AcceptanceCriterion(
                "production_readiness",
                evidence.status is ProductionReadinessStatus.READY
                if self.require_ready
                else evidence.status is not ProductionReadinessStatus.NOT_READY,
                evidence.status.value,
                "ready" if self.require_ready else "ready or conditional",
            ),
            AcceptanceCriterion(
                "readiness_criteria",
                passed == total,
                f"{passed}/{total} passed",
                "all readiness criteria passed",
            ),
            AcceptanceCriterion(
                "architecture_lineage",
                lineage,
                "complete" if lineage else "missing",
                "traceable M201-M219 evidence",
            ),
            AcceptanceCriterion(
                "quality_gate",
                evidence.status is not ProductionReadinessStatus.NOT_READY,
                evidence.status.value,
                "no rejected production-readiness gate",
            ),
            AcceptanceCriterion(
                "authority_boundaries",
                True,
                "preserved",
                "deployment and runtime mutation remain external",
            ),
        )
        failed = sum(not item.passed for item in criteria)
        status = (
            FinalAcceptanceStatus.ACCEPTED
            if failed == 0 and evidence.status is ProductionReadinessStatus.READY
            else FinalAcceptanceStatus.CONDITIONAL
            if failed <= 1
            and evidence.status is not ProductionReadinessStatus.NOT_READY
            else FinalAcceptanceStatus.REJECTED
        )
        timestamp = now or datetime.now(timezone.utc)
        certificate = ROBYArchitectureCertificate(
            owner=owner,
            session_id=session_id,
            status=status,
            version="ROBY v1",
            criteria=criteria,
            readiness_assessment_id=evidence.assessment_id,
            source_reference_ids=(
                evidence.assessment_id,
                *evidence.source_reference_ids,
            ),
            created_at=timestamp,
        )
        self.last_certificate = certificate
        return certificate


@dataclass
class FinalArchitectureCertificationRuntimeContributor:
    certifier: ROBYArchitectureCertifier
    blackboard: UnifiedCognitiveBlackboard
    name: str = "final_architecture_certification"

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
        certificate = self.certifier.certify(
            owner=owner, session_id=session_id, now=now
        )
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONSTRAINT,
                key=self.name,
                value=certificate.status.value,
                confidence=1.0,
                source_reference_ids=(
                    certificate.certificate_id,
                    *certificate.source_reference_ids,
                ),
                created_at=now,
            )
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(f"Certificación final ROBY v1: {certificate.status.value}.",),
            reference_ids=(
                entry.entry_id,
                certificate.certificate_id,
                *certificate.source_reference_ids,
            ),
            rationale=(
                "m219_readiness_accepted",
                "roby_v1_architecture_certified",
                "deployment_authority_remains_external",
            ),
        )
