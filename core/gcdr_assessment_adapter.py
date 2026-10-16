from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaEvidence,
    ExplicitComplexDecisionCriteriaStatus,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdaptation,
)
from core.governed_complex_decision_reasoning import (
    ComplexDecisionCriterionOutcome,
    GovernedOptionCriterionAssessment,
)
from core.option_criteria_certified_linkage import (
    CertifiedOptionCriterionEvidenceBinding,
    CertifiedOptionCriterionEvidenceLinkageResult,
    CertifiedOptionCriterionLinkageStatus,
)

_SCHEMA_VERSION = "post-m409.1-gcdr-assessment-adapter-v1"
_MISSING_EVIDENCE_CODE = "gcdr_adapter:no_certified_evidence_for_pair"


@dataclass(frozen=True)
class GovernedComplexDecisionAssessmentAdaptation:
    assessments: tuple[GovernedOptionCriterionAssessment, ...]
    source_fingerprint: str
    option_adaptation_fingerprint: str
    criteria_evidence_fingerprint: str
    linkage_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    read_only: bool = True
    derivational: bool = True
    parses_text: bool = False
    infers_outcome: bool = False
    assigns_value: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    evaluates_decision: bool = False
    calls_gcdr: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.assessments:
            raise ValueError("GCDR assessment adaptation requires assessments")
        if len(self.source_fingerprint) != 64:
            raise ValueError("GCDR assessment adaptation requires SHA-256 fingerprint")
        lineage = (
            self.option_adaptation_fingerprint,
            self.criteria_evidence_fingerprint,
            self.linkage_fingerprint,
        )
        if any(len(value) != 64 for value in lineage):
            raise ValueError("GCDR assessment adaptation requires SHA-256 lineage")
        if any(
            (
                not self.read_only,
                not self.derivational,
                self.parses_text,
                self.infers_outcome,
                self.assigns_value,
                self.uses_llm,
                self.uses_retrieval,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.evaluates_decision,
                self.calls_gcdr,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("GCDR assessment adaptation violates governed limits")
        pairs = tuple((item.option_id, item.criterion_id) for item in self.assessments)
        if len(pairs) != len(set(pairs)):
            raise ValueError("GCDR assessment adaptation pairs must be unique")


class CertifiedGCDRAssessmentAdapterV1:
    """Adapt certified explicit option×criterion evidence into GCDR inputs."""

    def adapt(
        self,
        *,
        option_adaptation: ExplicitDeliberationDecisionOptionAdaptation,
        criteria_evidence: ExplicitComplexDecisionCriteriaEvidence,
        linkage: CertifiedOptionCriterionEvidenceLinkageResult,
    ) -> GovernedComplexDecisionAssessmentAdaptation:
        if linkage.status is not CertifiedOptionCriterionLinkageStatus.LINKED:
            raise ValueError(
                "GCDR assessment adapter requires linked certified evidence"
            )
        if (
            criteria_evidence.status
            is not ExplicitComplexDecisionCriteriaStatus.EXPLICIT
        ):
            raise ValueError(
                "GCDR assessment adapter requires explicit criteria evidence"
            )
        if (
            linkage.option_adaptation_fingerprint
            != option_adaptation.source_fingerprint
        ):
            raise ValueError(
                "GCDR assessment adapter option provenance is incompatible"
            )
        if (
            linkage.criteria_evidence_fingerprint
            != criteria_evidence.source_fingerprint
        ):
            raise ValueError(
                "GCDR assessment adapter criterion provenance is incompatible"
            )

        option_ids = tuple(option.option_id for option in option_adaptation.options)
        criterion_ids = tuple(
            criterion.criterion_id for criterion in criteria_evidence.criteria
        )
        if len(option_ids) != len(set(option_ids)):
            raise ValueError("GCDR assessment adapter option ids must be unique")
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("GCDR assessment adapter criterion ids must be unique")

        binding_by_pair: dict[
            tuple[str, str], CertifiedOptionCriterionEvidenceBinding
        ] = {}
        for binding in linkage.bindings:
            pair = (binding.option_id, binding.criterion_id)
            if binding.option_id not in option_ids:
                raise ValueError("GCDR assessment binding references unknown option")
            if binding.criterion_id not in criterion_ids:
                raise ValueError("GCDR assessment binding references unknown criterion")
            if pair in binding_by_pair:
                raise ValueError("GCDR assessment binding pairs must be unique")
            binding_by_pair[pair] = binding

        assessments = tuple(
            self._assessment(
                option_id=option_id,
                criterion_id=criterion_id,
                binding=binding_by_pair.get((option_id, criterion_id)),
                linkage=linkage,
                option_adaptation=option_adaptation,
                criteria_evidence=criteria_evidence,
            )
            for option_id in option_ids
            for criterion_id in criterion_ids
        )
        source_fingerprint = self._fingerprint(
            "adaptation",
            option_adaptation.source_fingerprint,
            criteria_evidence.source_fingerprint,
            linkage.source_fingerprint,
            *(item.source_fingerprint or "" for item in assessments),
        )
        return GovernedComplexDecisionAssessmentAdaptation(
            assessments=assessments,
            source_fingerprint=source_fingerprint,
            option_adaptation_fingerprint=option_adaptation.source_fingerprint,
            criteria_evidence_fingerprint=criteria_evidence.source_fingerprint,
            linkage_fingerprint=linkage.source_fingerprint,
        )

    @classmethod
    def _assessment(
        cls,
        *,
        option_id: str,
        criterion_id: str,
        binding: CertifiedOptionCriterionEvidenceBinding | None,
        linkage: CertifiedOptionCriterionEvidenceLinkageResult,
        option_adaptation: ExplicitDeliberationDecisionOptionAdaptation,
        criteria_evidence: ExplicitComplexDecisionCriteriaEvidence,
    ) -> GovernedOptionCriterionAssessment:
        if binding is not None:
            outcome = ComplexDecisionCriterionOutcome(binding.outcome.value)
            evidence_codes = (
                f"gcdr_adapter:certified_evidence:{binding.evidence_id}",
                "gcdr_adapter:certified_linkage",
            )
            source_fingerprint = cls._fingerprint(
                "explicit",
                option_id,
                criterion_id,
                binding.evidence_id,
                binding.option_source_fingerprint,
                cls._span(binding.option_source_span),
                binding.criterion_source_fingerprint,
                cls._span(binding.criterion_source_span),
                binding.relation_source_fingerprint,
                cls._span(binding.relation_source_span),
                linkage.source_fingerprint,
            )
        else:
            outcome = ComplexDecisionCriterionOutcome.INSUFFICIENT
            evidence_codes = (_MISSING_EVIDENCE_CODE,)
            source_fingerprint = cls._fingerprint(
                "missing",
                option_id,
                criterion_id,
                option_adaptation.source_fingerprint,
                criteria_evidence.source_fingerprint,
                linkage.source_fingerprint,
            )
        return GovernedOptionCriterionAssessment(
            option_id=option_id,
            criterion_id=criterion_id,
            outcome=outcome,
            evidence_codes=evidence_codes,
            explicit_value=None,
            source_fingerprint=source_fingerprint,
        )

    @staticmethod
    def _span(value: tuple[int, int]) -> str:
        return f"{value[0]}:{value[1]}"

    @staticmethod
    def _fingerprint(*parts: str) -> str:
        payload = "|".join(parts)
        return sha256(payload.encode("utf-8")).hexdigest()
