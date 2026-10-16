from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.criterion_importance_compatibility import (
    CertifiedOrdinalCriterionImportanceRelation,
    CriterionImportanceCompatibilityResult,
    CriterionImportanceCompatibilityStatus,
)
from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaEvidence,
    ExplicitComplexDecisionCriteriaStatus,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdaptation,
)
from core.gcdr_assessment_adapter import GovernedComplexDecisionAssessmentAdaptation
from core.governed_complex_decision_reasoning import (
    GovernedDecisionCriterion,
    GovernedOptionCriterionAssessment,
)
from core.governed_decision_advisory import GovernedDecisionOption

_SCHEMA_VERSION = "post-m409.1-gcdr-complete-input-assembly-v1"


class GCDRCompleteInputAssemblyStatus(StrEnum):
    ASSEMBLED = "assembled"


@dataclass(frozen=True)
class GCDRCompleteInputAssemblyResult:
    status: GCDRCompleteInputAssemblyStatus
    options: tuple[GovernedDecisionOption, ...]
    criteria: tuple[GovernedDecisionCriterion, ...]
    assessments: tuple[GovernedOptionCriterionAssessment, ...]
    ordinal_importance_relations: tuple[
        CertifiedOrdinalCriterionImportanceRelation, ...
    ]
    source_fingerprint: str
    option_adaptation_fingerprint: str
    criteria_evidence_fingerprint: str
    assessment_adaptation_fingerprint: str
    importance_compatibility_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    read_only: bool = True
    derivational: bool = True
    generates_options: bool = False
    generates_criteria: bool = False
    infers_importance: bool = False
    assigns_importance: bool = False
    infers_assessments: bool = False
    evaluates_decision: bool = False
    ranks_options: bool = False
    recommends_option: bool = False
    calls_gcdr: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.status is not GCDRCompleteInputAssemblyStatus.ASSEMBLED:
            raise ValueError("GCDR complete input assembly status is invalid")
        if len(self.options) < 2:
            raise ValueError(
                "GCDR complete input assembly requires at least two options"
            )
        if not self.criteria:
            raise ValueError("GCDR complete input assembly requires criteria")
        if not self.assessments:
            raise ValueError("GCDR complete input assembly requires assessments")
        fingerprints = (
            self.source_fingerprint,
            self.option_adaptation_fingerprint,
            self.criteria_evidence_fingerprint,
            self.assessment_adaptation_fingerprint,
            self.importance_compatibility_fingerprint,
        )
        if any(len(value) != 64 for value in fingerprints):
            raise ValueError("GCDR complete input assembly requires SHA-256 lineage")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("GCDR complete input assembly requires rationale")
        if any(item.explicit_importance is not None for item in self.criteria):
            raise ValueError("GCDR assembly cannot synthesize cardinal importance")
        if any(
            (
                not self.read_only,
                not self.derivational,
                self.generates_options,
                self.generates_criteria,
                self.infers_importance,
                self.assigns_importance,
                self.infers_assessments,
                self.evaluates_decision,
                self.ranks_options,
                self.recommends_option,
                self.calls_gcdr,
                self.uses_llm,
                self.uses_retrieval,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("GCDR complete input assembly violates governed limits")


class GCDRCompleteInputAssemblyFoundationV1:
    """Assemble already-certified GCDR inputs without evaluating the decision."""

    def assemble(
        self,
        *,
        option_adaptation: ExplicitDeliberationDecisionOptionAdaptation,
        criteria_evidence: ExplicitComplexDecisionCriteriaEvidence,
        assessment_adaptation: GovernedComplexDecisionAssessmentAdaptation,
        importance_compatibility: CriterionImportanceCompatibilityResult,
    ) -> GCDRCompleteInputAssemblyResult:
        if (
            criteria_evidence.status
            is not ExplicitComplexDecisionCriteriaStatus.EXPLICIT
        ):
            raise ValueError("GCDR assembly requires explicit criteria evidence")
        if (
            importance_compatibility.status
            is CriterionImportanceCompatibilityStatus.INCOMPATIBLE_PROVENANCE
        ):
            raise ValueError("GCDR assembly requires compatible importance provenance")
        self._validate_lineage(
            option_adaptation=option_adaptation,
            criteria_evidence=criteria_evidence,
            assessment_adaptation=assessment_adaptation,
            importance_compatibility=importance_compatibility,
        )

        options = option_adaptation.options
        criteria = self._criteria(criteria_evidence, importance_compatibility)
        assessments = assessment_adaptation.assessments
        self._validate_matrix(options, criteria, assessments)
        self._validate_ordinal_relations(
            criteria=criteria,
            importance_compatibility=importance_compatibility,
        )

        source_fingerprint = self._fingerprint(
            option_adaptation.source_fingerprint,
            criteria_evidence.source_fingerprint,
            assessment_adaptation.source_fingerprint,
            importance_compatibility.source_fingerprint,
            repr(options),
            repr(criteria),
            repr(assessments),
            repr(importance_compatibility.ordinal_relations),
        )
        return GCDRCompleteInputAssemblyResult(
            status=GCDRCompleteInputAssemblyStatus.ASSEMBLED,
            options=options,
            criteria=criteria,
            assessments=assessments,
            ordinal_importance_relations=importance_compatibility.ordinal_relations,
            source_fingerprint=source_fingerprint,
            option_adaptation_fingerprint=option_adaptation.source_fingerprint,
            criteria_evidence_fingerprint=criteria_evidence.source_fingerprint,
            assessment_adaptation_fingerprint=assessment_adaptation.source_fingerprint,
            importance_compatibility_fingerprint=(
                importance_compatibility.source_fingerprint
            ),
            rationale_codes=(
                "gcdr_assembly:certified_options_preserved",
                "gcdr_assembly:explicit_criteria_adapted_without_cardinal_synthesis",
                "gcdr_assembly:complete_assessment_matrix_preserved",
                "gcdr_assembly:ordinal_importance_provenance_preserved",
            ),
        )

    @staticmethod
    def _validate_lineage(
        *,
        option_adaptation: ExplicitDeliberationDecisionOptionAdaptation,
        criteria_evidence: ExplicitComplexDecisionCriteriaEvidence,
        assessment_adaptation: GovernedComplexDecisionAssessmentAdaptation,
        importance_compatibility: CriterionImportanceCompatibilityResult,
    ) -> None:
        if (
            assessment_adaptation.option_adaptation_fingerprint
            != option_adaptation.source_fingerprint
        ):
            raise ValueError("GCDR assembly option lineage is incompatible")
        if (
            assessment_adaptation.criteria_evidence_fingerprint
            != criteria_evidence.source_fingerprint
        ):
            raise ValueError("GCDR assembly criterion lineage is incompatible")
        binding_ids = tuple(
            item.criterion_id for item in importance_compatibility.bindings
        )
        criterion_ids = tuple(item.criterion_id for item in criteria_evidence.criteria)
        if binding_ids != criterion_ids:
            raise ValueError(
                "GCDR assembly importance criterion identity is incompatible"
            )
        if any(
            item.criterion_source_fingerprint != criteria_evidence.source_fingerprint
            for item in importance_compatibility.bindings
        ):
            raise ValueError("GCDR assembly importance lineage is incompatible")
        if any(
            item.source_fingerprint != criteria_evidence.source_fingerprint
            for item in importance_compatibility.ordinal_relations
        ):
            raise ValueError("GCDR assembly ordinal importance lineage is incompatible")

    @staticmethod
    def _criteria(
        evidence: ExplicitComplexDecisionCriteriaEvidence,
        compatibility: CriterionImportanceCompatibilityResult,
    ) -> tuple[GovernedDecisionCriterion, ...]:
        compatibility_by_id = {
            item.criterion_id: item for item in compatibility.bindings
        }
        if len(compatibility_by_id) != len(compatibility.bindings):
            raise ValueError("GCDR assembly importance bindings must be unique")

        result: list[GovernedDecisionCriterion] = []
        for criterion in evidence.criteria:
            binding = compatibility_by_id.get(criterion.criterion_id)
            if binding is None:
                raise ValueError("GCDR assembly criterion lacks importance binding")
            if binding.explicit_importance is not None:
                raise ValueError("GCDR assembly cannot accept synthetic importance")
            provenance_codes = [
                f"criterion_evidence:{evidence.source_fingerprint}",
                f"criterion_span:{criterion.start_offset}:{criterion.end_offset}",
                f"importance_compatibility:{compatibility.source_fingerprint}",
            ]
            if criterion.required_source_span is not None:
                start, end = criterion.required_source_span
                provenance_codes.append(f"criterion_required_span:{start}:{end}")
            result.append(
                GovernedDecisionCriterion(
                    criterion_id=criterion.criterion_id,
                    title=criterion.normalized_text,
                    required=criterion.required,
                    explicit_importance=None,
                    provenance_codes=tuple(provenance_codes),
                )
            )
        return tuple(result)

    @staticmethod
    def _validate_matrix(
        options: tuple[GovernedDecisionOption, ...],
        criteria: tuple[GovernedDecisionCriterion, ...],
        assessments: tuple[GovernedOptionCriterionAssessment, ...],
    ) -> None:
        option_ids = tuple(item.option_id for item in options)
        criterion_ids = tuple(item.criterion_id for item in criteria)
        if len(option_ids) != len(set(option_ids)):
            raise ValueError("GCDR assembly option ids must be unique")
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("GCDR assembly criterion ids must be unique")
        actual_pairs = tuple(
            (item.option_id, item.criterion_id) for item in assessments
        )
        if len(actual_pairs) != len(set(actual_pairs)):
            raise ValueError("GCDR assembly assessment pairs must be unique")
        expected_pairs = {
            (option_id, criterion_id)
            for option_id in option_ids
            for criterion_id in criterion_ids
        }
        if set(actual_pairs) != expected_pairs:
            raise ValueError("GCDR assembly requires complete assessment matrix")

    @staticmethod
    def _validate_ordinal_relations(
        *,
        criteria: tuple[GovernedDecisionCriterion, ...],
        importance_compatibility: CriterionImportanceCompatibilityResult,
    ) -> None:
        known_ids = {item.criterion_id for item in criteria}
        for relation in importance_compatibility.ordinal_relations:
            if relation.more_important_criterion_id not in known_ids:
                raise ValueError("GCDR assembly ordinal relation has unknown criterion")
            if relation.less_important_criterion_id not in known_ids:
                raise ValueError("GCDR assembly ordinal relation has unknown criterion")

    @staticmethod
    def _fingerprint(*parts: str) -> str:
        payload = "|".join(parts)
        return sha256(payload.encode("utf-8")).hexdigest()
