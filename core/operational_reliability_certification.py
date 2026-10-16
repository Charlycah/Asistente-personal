from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.end_to_end_stress_validation import (
    EndToEndStressReport,
    EndToEndStressValidator,
    StressValidationStatus,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class ReliabilityCertificationStatus(str, Enum):
    CERTIFIED = "certified"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ReliabilityCriterion:
    name: str
    passed: bool
    observed: str
    requirement: str

    def __post_init__(self) -> None:
        name = self.name.strip()
        observed = self.observed.strip()
        requirement = self.requirement.strip()
        if not name or not observed or not requirement:
            raise ValueError("reliability criterion fields must not be blank")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "observed", observed)
        object.__setattr__(self, "requirement", requirement)


@dataclass(frozen=True)
class OperationalReliabilityCertificate:
    owner: str
    session_id: str
    status: ReliabilityCertificationStatus | str
    criteria: tuple[ReliabilityCriterion, ...]
    stress_report_id: str
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    certificate_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        report_id = self.stress_report_id.strip()
        status = ReliabilityCertificationStatus(self.status)
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id or not report_id or not self.criteria:
            raise ValueError(
                "reliability certificate identity and evidence are required"
            )
        if self.created_at.tzinfo is None:
            raise ValueError("reliability certificate time must be timezone-aware")
        if len({item.name for item in self.criteria}) != len(self.criteria):
            raise ValueError("reliability criterion names must be unique")
        if len(set(references)) != len(references):
            raise ValueError("reliability certificate references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    report_id,
                    *(
                        f"{item.name}:{item.passed}:{item.observed}:{item.requirement}"
                        for item in self.criteria
                    ),
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode()
        ).hexdigest()
        if self.certificate_id and self.certificate_id != expected:
            raise ValueError("reliability certificate id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "stress_report_id", report_id)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "certificate_id", expected)


class OperationalReliabilityCertifier:
    """Certify bounded operational evidence produced by M217."""

    def __init__(
        self,
        validator: EndToEndStressValidator,
        *,
        minimum_cycles: int = 3,
        maximum_failure_rate: float = 0.05,
    ) -> None:
        if minimum_cycles < 1:
            raise ValueError("minimum reliability cycles must be positive")
        if not 0.0 <= maximum_failure_rate <= 1.0:
            raise ValueError("maximum failure rate must be between zero and one")
        self.validator = validator
        self.minimum_cycles = minimum_cycles
        self.maximum_failure_rate = maximum_failure_rate
        self.last_certificate: OperationalReliabilityCertificate | None = None

    def certify(
        self,
        *,
        owner: str,
        session_id: str,
        report: EndToEndStressReport | None = None,
        now: datetime | None = None,
    ) -> OperationalReliabilityCertificate:
        evidence = report or self.validator.last_report
        if evidence is None:
            raise ValueError(
                "operational reliability certification requires M217 evidence"
            )
        if evidence.owner != owner.strip() or evidence.session_id != session_id.strip():
            raise ValueError(
                "stress evidence identity does not match certification request"
            )
        failure_rate = evidence.total_task_failures / max(evidence.total_cycles, 1)
        blocked = sum(item.blocked for item in evidence.scenarios)
        lineage_complete = bool(evidence.source_reference_ids) and all(
            item.source_reference_ids for item in evidence.scenarios
        )
        criteria = (
            ReliabilityCriterion(
                "bounded_coverage",
                evidence.total_cycles >= self.minimum_cycles,
                str(evidence.total_cycles),
                f">={self.minimum_cycles} cycles",
            ),
            ReliabilityCriterion(
                "stress_outcome",
                evidence.status is not StressValidationStatus.FAILED,
                evidence.status.value,
                "passed or degraded",
            ),
            ReliabilityCriterion(
                "task_failure_rate",
                failure_rate <= self.maximum_failure_rate,
                f"{failure_rate:.6f}",
                f"<={self.maximum_failure_rate:.6f}",
            ),
            ReliabilityCriterion(
                "execution_availability",
                blocked < evidence.total_cycles,
                f"{blocked}/{evidence.total_cycles} blocked",
                "not all cycles blocked",
            ),
            ReliabilityCriterion(
                "trace_lineage",
                lineage_complete,
                "complete" if lineage_complete else "incomplete",
                "complete M211-M217 lineage",
            ),
        )
        failed = sum(not item.passed for item in criteria)
        status = (
            ReliabilityCertificationStatus.CERTIFIED
            if failed == 0 and evidence.status is StressValidationStatus.PASSED
            else ReliabilityCertificationStatus.CONDITIONAL
            if failed <= 1 and evidence.status is not StressValidationStatus.FAILED
            else ReliabilityCertificationStatus.REJECTED
        )
        timestamp = now or datetime.now(timezone.utc)
        certificate = OperationalReliabilityCertificate(
            owner=owner,
            session_id=session_id,
            status=status,
            criteria=criteria,
            stress_report_id=evidence.report_id,
            source_reference_ids=(evidence.report_id, *evidence.source_reference_ids),
            created_at=timestamp,
        )
        self.last_certificate = certificate
        return certificate


@dataclass
class OperationalReliabilityCertificationRuntimeContributor:
    certifier: OperationalReliabilityCertifier
    blackboard: UnifiedCognitiveBlackboard
    name: str = "operational_reliability_certification"

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
            owner=owner,
            session_id=session_id,
            now=now,
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
            prompt_lines=(
                "Certificación de confiabilidad operacional: "
                f"{certificate.status.value}.",
            ),
            reference_ids=(
                entry.entry_id,
                certificate.certificate_id,
                *certificate.source_reference_ids,
            ),
            rationale=(
                "m217_evidence_certified",
                "explicit_reliability_criteria_evaluated",
                "production_readiness_not_assessed",
            ),
        )
