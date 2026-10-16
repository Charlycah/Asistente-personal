from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.criterion_importance_compatibility import (
    CriterionImportanceCompatibilityFoundationV1,
)
from core.explicit_complex_decision_intake_envelope import (
    ExplicitComplexDecisionIntakeEnvelopeResult,
    ExplicitComplexDecisionIntakeEnvelopeStatus,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.gcdr_assessment_adapter import CertifiedGCDRAssessmentAdapterV1
from core.gcdr_complete_input_assembly import (
    GCDRCompleteInputAssemblyFoundationV1,
    GCDRCompleteInputAssemblyResult,
)
from core.option_criteria_certified_linkage import (
    CertifiedOptionCriterionEvidenceLinkageV1,
    CertifiedOptionCriterionLinkageStatus,
)
from core.productive_gcdr_advisory_wiring import (
    ProductiveGCDRAdvisoryResult,
    ProductiveGCDRAdvisoryWiringV1,
)

_SCHEMA_VERSION = "post-m409.1-productive-gcdr-intake-integration-v1"


class ProductiveGCDRIntakeIntegrationStatus(StrEnum):
    ADVISORY_READY = "advisory_ready"
    NOT_APPLICABLE = "not_applicable"
    CERTIFICATION_FAILED = "certification_failed"


@dataclass(frozen=True)
class ProductiveGCDRIntakeIntegrationResult:
    status: ProductiveGCDRIntakeIntegrationStatus
    intake_fingerprint: str
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    assembly: GCDRCompleteInputAssemblyResult | None = None
    advisory: ProductiveGCDRAdvisoryResult | None = None
    schema_version: str = _SCHEMA_VERSION
    read_only: bool = True
    advisory_only: bool = True
    infers_options: bool = False
    infers_criteria: bool = False
    infers_evidence: bool = False
    repairs_references: bool = False
    resolves_context: bool = False
    uses_memory: bool = False
    uses_retrieval: bool = False
    uses_llm: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    creates_plan: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if len(self.intake_fingerprint) != 64:
            raise ValueError("productive GCDR intake requires SHA-256 intake lineage")
        if len(self.source_fingerprint) != 64:
            raise ValueError("productive GCDR intake requires SHA-256 fingerprint")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("productive GCDR intake requires rationale codes")
        if self.status is ProductiveGCDRIntakeIntegrationStatus.ADVISORY_READY:
            if self.assembly is None or self.advisory is None:
                raise ValueError("ready GCDR intake requires assembly and advisory")
            if self.advisory.assembly_fingerprint != self.assembly.source_fingerprint:
                raise ValueError("productive GCDR intake assembly lineage mismatch")
        elif self.assembly is not None or self.advisory is not None:
            raise ValueError("non-ready GCDR intake cannot expose partial artifacts")
        if any(
            (
                not self.read_only,
                not self.advisory_only,
                self.infers_options,
                self.infers_criteria,
                self.infers_evidence,
                self.repairs_references,
                self.resolves_context,
                self.uses_memory,
                self.uses_retrieval,
                self.uses_llm,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.creates_plan,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("productive GCDR intake violates governed limits")


class ProductiveGCDRIntakeIntegrationV1:
    """Compose certified complex-decision artifacts behind one intake boundary."""

    def integrate(
        self,
        intake: ExplicitComplexDecisionIntakeEnvelopeResult,
    ) -> ProductiveGCDRIntakeIntegrationResult:
        if intake.status is not ExplicitComplexDecisionIntakeEnvelopeStatus.COMPLETE:
            return self._result(
                status=ProductiveGCDRIntakeIntegrationStatus.NOT_APPLICABLE,
                intake=intake,
                rationale_codes=("gcdr_intake:complete_envelope_required",),
            )
        if (
            intake.deliberation_evidence is None
            or intake.criteria_evidence is None
            or intake.option_criterion_evidence is None
        ):
            return self._result(
                status=ProductiveGCDRIntakeIntegrationStatus.CERTIFICATION_FAILED,
                intake=intake,
                rationale_codes=("gcdr_intake:certified_children_required",),
            )

        option_adaptation = ExplicitDeliberationDecisionOptionAdapter().adapt(
            intake.deliberation_evidence
        )
        linkage = CertifiedOptionCriterionEvidenceLinkageV1().link(
            deliberation=intake.deliberation_evidence,
            option_adaptation=option_adaptation,
            criteria_evidence=intake.criteria_evidence,
            relation_evidence=intake.option_criterion_evidence,
        )
        if linkage.status is not CertifiedOptionCriterionLinkageStatus.LINKED:
            return self._result(
                status=ProductiveGCDRIntakeIntegrationStatus.CERTIFICATION_FAILED,
                intake=intake,
                rationale_codes=(
                    "gcdr_intake:certified_linkage_required",
                    f"gcdr_intake:linkage_status:{linkage.status.value}",
                ),
            )

        try:
            assessment_adaptation = CertifiedGCDRAssessmentAdapterV1().adapt(
                option_adaptation=option_adaptation,
                criteria_evidence=intake.criteria_evidence,
                linkage=linkage,
            )
            importance = CriterionImportanceCompatibilityFoundationV1().assess(
                intake.criteria_evidence
            )
            assembly = GCDRCompleteInputAssemblyFoundationV1().assemble(
                option_adaptation=option_adaptation,
                criteria_evidence=intake.criteria_evidence,
                assessment_adaptation=assessment_adaptation,
                importance_compatibility=importance,
            )
            advisory = ProductiveGCDRAdvisoryWiringV1().advise(assembly)
        except ValueError:
            return self._result(
                status=ProductiveGCDRIntakeIntegrationStatus.CERTIFICATION_FAILED,
                intake=intake,
                rationale_codes=("gcdr_intake:downstream_certification_failed",),
            )

        return self._result(
            status=ProductiveGCDRIntakeIntegrationStatus.ADVISORY_READY,
            intake=intake,
            assembly=assembly,
            advisory=advisory,
            rationale_codes=(
                "gcdr_intake:complete_envelope_consumed",
                "gcdr_intake:certified_chain_reused",
                "gcdr_intake:productive_gcdr_advisory_ready",
                "gcdr_intake:human_decision_preserved",
            ),
        )

    @staticmethod
    def _result(
        *,
        status: ProductiveGCDRIntakeIntegrationStatus,
        intake: ExplicitComplexDecisionIntakeEnvelopeResult,
        rationale_codes: tuple[str, ...],
        assembly: GCDRCompleteInputAssemblyResult | None = None,
        advisory: ProductiveGCDRAdvisoryResult | None = None,
    ) -> ProductiveGCDRIntakeIntegrationResult:
        payload = repr(
            (
                _SCHEMA_VERSION,
                status.value,
                intake.source_fingerprint,
                assembly.source_fingerprint if assembly is not None else None,
                advisory.source_fingerprint if advisory is not None else None,
                rationale_codes,
            )
        )
        return ProductiveGCDRIntakeIntegrationResult(
            status=status,
            intake_fingerprint=intake.source_fingerprint,
            assembly=assembly,
            advisory=advisory,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
            rationale_codes=rationale_codes,
        )
