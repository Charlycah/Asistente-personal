from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaEvidence,
    ExplicitComplexDecisionCriteriaStatus,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdaptation,
)
from core.explicit_human_decision_deliberation import (
    ExplicitDecisionDeliberationEvidence,
    ExplicitDecisionDeliberationStatus,
)
from core.explicit_option_criterion_evidence import (
    ExplicitOptionCriterionEvidence,
    ExplicitOptionCriterionEvidenceStatus,
    ExplicitOptionCriterionOutcome,
)


class CertifiedOptionCriterionLinkageStatus(StrEnum):
    LINKED = "linked"
    NO_EVIDENCE = "no_evidence"
    UNRESOLVED_OPTION = "unresolved_option"
    UNRESOLVED_CRITERION = "unresolved_criterion"
    AMBIGUOUS_REFERENCE = "ambiguous_reference"
    INCOMPATIBLE_PROVENANCE = "incompatible_provenance"


@dataclass(frozen=True)
class CertifiedOptionCriterionEvidenceBinding:
    option_id: str
    criterion_id: str
    outcome: ExplicitOptionCriterionOutcome
    evidence_id: str
    option_source_fingerprint: str
    option_source_span: tuple[int, int]
    criterion_source_fingerprint: str
    criterion_source_span: tuple[int, int]
    relation_source_fingerprint: str
    relation_source_span: tuple[int, int]

    def __post_init__(self) -> None:
        if not self.option_id.strip() or not self.criterion_id.strip():
            raise ValueError("certified linkage binding requires ids")
        if not isinstance(self.outcome, ExplicitOptionCriterionOutcome):
            raise ValueError("certified linkage binding outcome is invalid")
        if not self.evidence_id.startswith("explicit-option-criterion-evidence-"):
            raise ValueError("certified linkage evidence id is invalid")
        fingerprints = (
            self.option_source_fingerprint,
            self.criterion_source_fingerprint,
            self.relation_source_fingerprint,
        )
        if any(len(value) != 64 for value in fingerprints):
            raise ValueError("certified linkage requires SHA-256 provenance")
        spans = (
            self.option_source_span,
            self.criterion_source_span,
            self.relation_source_span,
        )
        if any(start < 0 or end <= start for start, end in spans):
            raise ValueError("certified linkage source span is invalid")


@dataclass(frozen=True)
class CertifiedOptionCriterionEvidenceLinkageResult:
    status: CertifiedOptionCriterionLinkageStatus
    bindings: tuple[CertifiedOptionCriterionEvidenceBinding, ...]
    option_adaptation_fingerprint: str
    criteria_evidence_fingerprint: str
    relation_evidence_fingerprint: str
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = "post-m409.1-option-criteria-certified-linkage-v1"
    read_only: bool = True
    parses_text: bool = False
    generates_options: bool = False
    generates_criteria: bool = False
    infers_outcome: bool = False
    uses_fuzzy_matching: bool = False
    uses_semantic_matching: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    resolves_context: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    evaluates_decision: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.source_fingerprint.strip():
            raise ValueError("certified linkage fingerprint must not be blank")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("certified linkage requires rationale codes")
        lineage = (
            self.option_adaptation_fingerprint,
            self.criteria_evidence_fingerprint,
            self.relation_evidence_fingerprint,
        )
        if any(len(value) != 64 for value in lineage):
            raise ValueError("certified linkage requires SHA-256 lineage")
        if self.status is CertifiedOptionCriterionLinkageStatus.LINKED:
            if not self.bindings:
                raise ValueError("linked result requires bindings")
        elif self.bindings:
            raise ValueError("failed linkage cannot expose partial bindings")
        if any(
            (
                not self.read_only,
                self.parses_text,
                self.generates_options,
                self.generates_criteria,
                self.infers_outcome,
                self.uses_fuzzy_matching,
                self.uses_semantic_matching,
                self.uses_llm,
                self.uses_retrieval,
                self.resolves_context,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.evaluates_decision,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("certified linkage violates governed limits")


class CertifiedOptionCriterionEvidenceLinkageV1:
    """Resolve references only against already-certified exact identities."""

    def link(
        self,
        *,
        deliberation: ExplicitDecisionDeliberationEvidence,
        option_adaptation: ExplicitDeliberationDecisionOptionAdaptation,
        criteria_evidence: ExplicitComplexDecisionCriteriaEvidence,
        relation_evidence: ExplicitOptionCriterionEvidence,
    ) -> CertifiedOptionCriterionEvidenceLinkageResult:
        if (
            relation_evidence.status
            is not ExplicitOptionCriterionEvidenceStatus.EXPLICIT
        ):
            return self._result(
                CertifiedOptionCriterionLinkageStatus.NO_EVIDENCE,
                option_adaptation,
                criteria_evidence,
                relation_evidence,
                ("linkage:no_explicit_relation_evidence",),
            )
        if (
            deliberation.status is not ExplicitDecisionDeliberationStatus.EXPLICIT
            or criteria_evidence.status
            is not ExplicitComplexDecisionCriteriaStatus.EXPLICIT
        ):
            return self._result(
                CertifiedOptionCriterionLinkageStatus.INCOMPATIBLE_PROVENANCE,
                option_adaptation,
                criteria_evidence,
                relation_evidence,
                ("linkage:certified_sources_not_explicit",),
            )
        if not self._adaptation_matches(deliberation, option_adaptation):
            return self._result(
                CertifiedOptionCriterionLinkageStatus.INCOMPATIBLE_PROVENANCE,
                option_adaptation,
                criteria_evidence,
                relation_evidence,
                ("linkage:option_adaptation_lineage_mismatch",),
            )

        option_index = self._option_index(deliberation, option_adaptation)
        criterion_index = self._criterion_index(criteria_evidence)
        if option_index is None or criterion_index is None:
            return self._result(
                CertifiedOptionCriterionLinkageStatus.AMBIGUOUS_REFERENCE,
                option_adaptation,
                criteria_evidence,
                relation_evidence,
                ("linkage:certified_identity_not_unique",),
            )

        bindings: list[CertifiedOptionCriterionEvidenceBinding] = []
        for relation in relation_evidence.relations:
            option = option_index.get(self._normalize(relation.option_reference))
            if option is None:
                return self._result(
                    CertifiedOptionCriterionLinkageStatus.UNRESOLVED_OPTION,
                    option_adaptation,
                    criteria_evidence,
                    relation_evidence,
                    ("linkage:exact_option_reference_required",),
                )
            criterion = criterion_index.get(
                self._normalize(relation.criterion_reference)
            )
            if criterion is None:
                return self._result(
                    CertifiedOptionCriterionLinkageStatus.UNRESOLVED_CRITERION,
                    option_adaptation,
                    criteria_evidence,
                    relation_evidence,
                    ("linkage:exact_criterion_reference_required",),
                )
            bindings.append(
                CertifiedOptionCriterionEvidenceBinding(
                    option_id=option[0],
                    criterion_id=criterion[0],
                    outcome=relation.outcome,
                    evidence_id=relation.evidence_id,
                    option_source_fingerprint=deliberation.source_fingerprint,
                    option_source_span=option[1],
                    criterion_source_fingerprint=criteria_evidence.source_fingerprint,
                    criterion_source_span=criterion[1],
                    relation_source_fingerprint=relation_evidence.source_fingerprint,
                    relation_source_span=(relation.start_offset, relation.end_offset),
                )
            )

        return self._result(
            CertifiedOptionCriterionLinkageStatus.LINKED,
            option_adaptation,
            criteria_evidence,
            relation_evidence,
            (
                "linkage:exact_certified_option_identity",
                "linkage:exact_certified_criterion_identity",
                "linkage:relation_provenance_preserved",
            ),
            tuple(bindings),
        )

    @classmethod
    def _adaptation_matches(
        cls,
        deliberation: ExplicitDecisionDeliberationEvidence,
        adaptation: ExplicitDeliberationDecisionOptionAdaptation,
    ) -> bool:
        if adaptation.source_fingerprint != deliberation.source_fingerprint:
            return False
        if len(adaptation.bindings) != len(deliberation.alternatives):
            return False
        if len(adaptation.options) != len(deliberation.alternatives):
            return False
        for alternative, binding, option in zip(
            deliberation.alternatives,
            adaptation.bindings,
            adaptation.options,
            strict=True,
        ):
            if binding.option_id != option.option_id:
                return False
            if binding.alternative_ordinal != alternative.ordinal:
                return False
            if (
                binding.source_start_offset,
                binding.source_end_offset,
            ) != (alternative.start_offset, alternative.end_offset):
                return False
            if cls._normalize(option.title) != cls._normalize(
                alternative.normalized_text
            ):
                return False
        return True

    @classmethod
    def _option_index(
        cls,
        deliberation: ExplicitDecisionDeliberationEvidence,
        adaptation: ExplicitDeliberationDecisionOptionAdaptation,
    ) -> dict[str, tuple[str, tuple[int, int]]] | None:
        result: dict[str, tuple[str, tuple[int, int]]] = {}
        for alternative, binding in zip(
            deliberation.alternatives,
            adaptation.bindings,
            strict=True,
        ):
            key = cls._normalize(alternative.normalized_text)
            if key in result:
                return None
            result[key] = (
                binding.option_id,
                (alternative.start_offset, alternative.end_offset),
            )
        return result

    @classmethod
    def _criterion_index(
        cls,
        evidence: ExplicitComplexDecisionCriteriaEvidence,
    ) -> dict[str, tuple[str, tuple[int, int]]] | None:
        result: dict[str, tuple[str, tuple[int, int]]] = {}
        for criterion in evidence.criteria:
            key = cls._normalize(criterion.normalized_text)
            if key in result:
                return None
            result[key] = (
                criterion.criterion_id,
                (criterion.start_offset, criterion.end_offset),
            )
        return result

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.strip().split()).casefold()

    @staticmethod
    def _result(
        status: CertifiedOptionCriterionLinkageStatus,
        adaptation: ExplicitDeliberationDecisionOptionAdaptation,
        criteria: ExplicitComplexDecisionCriteriaEvidence,
        relations: ExplicitOptionCriterionEvidence,
        rationale_codes: tuple[str, ...],
        bindings: tuple[CertifiedOptionCriterionEvidenceBinding, ...] = (),
    ) -> CertifiedOptionCriterionEvidenceLinkageResult:
        payload = repr(
            (
                "post-m409.1-option-criteria-certified-linkage-v1",
                status.value,
                adaptation.source_fingerprint,
                criteria.source_fingerprint,
                relations.source_fingerprint,
                bindings,
                rationale_codes,
            )
        )
        return CertifiedOptionCriterionEvidenceLinkageResult(
            status=status,
            bindings=bindings,
            option_adaptation_fingerprint=adaptation.source_fingerprint,
            criteria_evidence_fingerprint=criteria.source_fingerprint,
            relation_evidence_fingerprint=relations.source_fingerprint,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
            rationale_codes=rationale_codes,
        )
