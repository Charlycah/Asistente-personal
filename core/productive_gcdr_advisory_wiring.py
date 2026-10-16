from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.gcdr_complete_input_assembly import (
    GCDRCompleteInputAssemblyResult,
    GCDRCompleteInputAssemblyStatus,
)
from core.governed_complex_decision_reasoning import (
    GovernedComplexDecisionReasoningFoundationV1,
    GovernedComplexDecisionReport,
)

_SCHEMA_VERSION = "post-m409.1-productive-gcdr-advisory-wiring-v1"


@dataclass(frozen=True)
class ProductiveGCDRAdvisoryResult:
    report: GovernedComplexDecisionReport
    assembly_fingerprint: str
    report_fingerprint: str
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "unified_cognitive_coordination"
    canonical_facade: str = "CanonicalDecisionFacade"
    read_only: bool = True
    advisory_only: bool = True
    human_decision_preserved: bool = True
    consumes_certified_assembly_only: bool = True
    infers_missing_evidence: bool = False
    synthesizes_importance: bool = False
    creates_plans: bool = False
    modifies_organization: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.report.schema_version != (
            "post-m409.1-governed-complex-decision-reasoning-v1"
        ):
            raise ValueError("productive GCDR wiring requires GCDR v1 report")
        if self.report.canonical_authority != self.canonical_authority:
            raise ValueError("productive GCDR wiring must preserve decision authority")
        if self.report.canonical_facade != self.canonical_facade:
            raise ValueError("productive GCDR wiring must preserve canonical facade")
        if self.report.source_fingerprint != self.report_fingerprint:
            raise ValueError("productive GCDR report fingerprint is inconsistent")
        fingerprints = (
            self.assembly_fingerprint,
            self.report_fingerprint,
            self.source_fingerprint,
        )
        if any(len(value) != 64 for value in fingerprints):
            raise ValueError("productive GCDR wiring requires SHA-256 lineage")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("productive GCDR wiring requires rationale codes")
        if any(
            (
                not self.read_only,
                not self.advisory_only,
                not self.human_decision_preserved,
                not self.consumes_certified_assembly_only,
                self.infers_missing_evidence,
                self.synthesizes_importance,
                self.creates_plans,
                self.modifies_organization,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("productive GCDR wiring violates governed limits")


class ProductiveGCDRAdvisoryWiringV1:
    """Delegate one certified complete assembly to existing GCDR only."""

    def advise(
        self,
        assembly: GCDRCompleteInputAssemblyResult,
    ) -> ProductiveGCDRAdvisoryResult:
        self._validate_assembly(assembly)
        report = GovernedComplexDecisionReasoningFoundationV1().assess(
            assembly.options,
            assembly.criteria,
            assembly.assessments,
        )
        self._validate_report(assembly, report)
        source_fingerprint = sha256(
            repr(
                (
                    _SCHEMA_VERSION,
                    assembly.source_fingerprint,
                    report.source_fingerprint,
                    report.report_id,
                )
            ).encode("utf-8")
        ).hexdigest()
        return ProductiveGCDRAdvisoryResult(
            report=report,
            assembly_fingerprint=assembly.source_fingerprint,
            report_fingerprint=report.source_fingerprint,
            source_fingerprint=source_fingerprint,
            rationale_codes=(
                "productive_gcdr:certified_complete_assembly_consumed",
                "productive_gcdr:existing_gcdr_reused",
                "productive_gcdr:advisory_only",
                "productive_gcdr:human_decision_preserved",
            ),
        )

    @staticmethod
    def _validate_assembly(assembly: GCDRCompleteInputAssemblyResult) -> None:
        if assembly.status is not GCDRCompleteInputAssemblyStatus.ASSEMBLED:
            raise ValueError("productive GCDR wiring requires assembled input")
        if not assembly.read_only or not assembly.derivational:
            raise ValueError("productive GCDR wiring requires governed assembly")
        if any(
            (
                assembly.evaluates_decision,
                assembly.recommends_option,
                assembly.calls_gcdr,
                assembly.persists_results,
                assembly.creates_memory,
                assembly.creates_learning_candidate,
                assembly.modifies_world_model,
                assembly.executes_actions,
                assembly.grants_authority,
                assembly.starts_background_process,
            )
        ):
            raise ValueError("productive GCDR wiring rejects empowered assembly")

    @staticmethod
    def _validate_report(
        assembly: GCDRCompleteInputAssemblyResult,
        report: GovernedComplexDecisionReport,
    ) -> None:
        option_ids = tuple(option.option_id for option in assembly.options)
        criterion_ids = tuple(item.criterion_id for item in assembly.criteria)
        report_criterion_ids = tuple(item.criterion_id for item in report.criteria)
        if set(report.source_option_ids) != set(option_ids):
            raise ValueError("productive GCDR report option lineage mismatch")
        if report_criterion_ids != tuple(
            sorted(criterion_ids)
        ):
            raise ValueError("productive GCDR report criterion lineage mismatch")
        if any(
            (
                not report.read_only,
                not report.advisory_only,
                not report.human_decision_preserved,
                report.creates_plans,
                report.persists_results,
                report.modifies_memory,
                report.modifies_learning,
                report.modifies_world_model,
                report.modifies_planning,
                report.modifies_organization,
                report.executes_actions,
                report.grants_authority,
                report.starts_background_process,
            )
        ):
            raise ValueError("productive GCDR report violates governed limits")
