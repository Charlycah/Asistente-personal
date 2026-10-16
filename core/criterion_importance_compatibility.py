from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaEvidence,
    ExplicitComplexDecisionCriteriaStatus,
)

_SCHEMA_VERSION = "post-m409.1-criterion-importance-compatibility-v1"


class CriterionImportanceCompatibilityStatus(StrEnum):
    COMPATIBLE_NO_CARDINAL_IMPORTANCE = "compatible_no_cardinal_importance"
    ORDINAL_IMPORTANCE_PRESERVED = "ordinal_importance_preserved"
    INCOMPATIBLE_PROVENANCE = "incompatible_provenance"


@dataclass(frozen=True)
class CriterionImportanceCompatibilityBinding:
    criterion_id: str
    explicit_importance: None
    has_explicit_ordinal_importance: bool
    criterion_source_fingerprint: str
    criterion_source_span: tuple[int, int]

    def __post_init__(self) -> None:
        if not self.criterion_id.strip():
            raise ValueError("criterion importance compatibility requires criterion id")
        if self.explicit_importance is not None:
            raise ValueError("ordinal importance cannot synthesize cardinal importance")
        if len(self.criterion_source_fingerprint) != 64:
            raise ValueError(
                "criterion importance compatibility requires SHA-256 source"
            )
        start, end = self.criterion_source_span
        if start < 0 or end <= start:
            raise ValueError(
                "criterion importance compatibility source span is invalid"
            )


@dataclass(frozen=True)
class CertifiedOrdinalCriterionImportanceRelation:
    more_important_criterion_id: str
    less_important_criterion_id: str
    raw_text: str
    source_fingerprint: str
    source_span: tuple[int, int]

    def __post_init__(self) -> None:
        if not self.more_important_criterion_id.strip():
            raise ValueError("ordinal importance requires more-important criterion id")
        if not self.less_important_criterion_id.strip():
            raise ValueError("ordinal importance requires less-important criterion id")
        if self.more_important_criterion_id == self.less_important_criterion_id:
            raise ValueError("ordinal importance requires distinct criteria")
        if not self.raw_text:
            raise ValueError("ordinal importance requires explicit source text")
        if len(self.source_fingerprint) != 64:
            raise ValueError("ordinal importance requires SHA-256 source")
        start, end = self.source_span
        if start < 0 or end <= start:
            raise ValueError("ordinal importance source span is invalid")


@dataclass(frozen=True)
class CriterionImportanceCompatibilityResult:
    status: CriterionImportanceCompatibilityStatus
    bindings: tuple[CriterionImportanceCompatibilityBinding, ...]
    ordinal_relations: tuple[CertifiedOrdinalCriterionImportanceRelation, ...]
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    read_only: bool = True
    derivational: bool = True
    infers_importance: bool = False
    assigns_importance: bool = False
    ranks_criteria: bool = False
    normalizes_weights: bool = False
    infers_transitivity: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    evaluates_options: bool = False
    evaluates_decision: bool = False
    calls_gcdr: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if len(self.source_fingerprint) != 64:
            raise ValueError("criterion importance compatibility requires fingerprint")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("criterion importance compatibility requires rationale")
        if (
            self.status
            is CriterionImportanceCompatibilityStatus.INCOMPATIBLE_PROVENANCE
        ):
            if self.bindings or self.ordinal_relations:
                raise ValueError(
                    "incompatible importance evidence cannot expose bindings"
                )
        elif not self.bindings:
            raise ValueError(
                "compatible importance evidence requires criterion bindings"
            )
        if any(
            (
                not self.read_only,
                not self.derivational,
                self.infers_importance,
                self.assigns_importance,
                self.ranks_criteria,
                self.normalizes_weights,
                self.infers_transitivity,
                self.uses_llm,
                self.uses_retrieval,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.evaluates_options,
                self.evaluates_decision,
                self.calls_gcdr,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError(
                "criterion importance compatibility violates governed limits"
            )


class CriterionImportanceCompatibilityFoundationV1:
    """Preserve explicit ordinal importance without synthesizing cardinal weights."""

    def assess(
        self,
        evidence: ExplicitComplexDecisionCriteriaEvidence,
    ) -> CriterionImportanceCompatibilityResult:
        if evidence.status is not ExplicitComplexDecisionCriteriaStatus.EXPLICIT:
            return self._result(
                status=CriterionImportanceCompatibilityStatus.INCOMPATIBLE_PROVENANCE,
                evidence=evidence,
                rationale_codes=("importance:explicit_criteria_required",),
            )

        criterion_ids = tuple(item.criterion_id for item in evidence.criteria)
        if len(criterion_ids) != len(set(criterion_ids)):
            return self._result(
                status=CriterionImportanceCompatibilityStatus.INCOMPATIBLE_PROVENANCE,
                evidence=evidence,
                rationale_codes=("importance:criterion_identity_not_unique",),
            )
        known_ids = set(criterion_ids)
        relation_pairs: set[tuple[str, str]] = set()
        related_ids: set[str] = set()
        relations: list[CertifiedOrdinalCriterionImportanceRelation] = []
        for relation in evidence.importance_relations:
            pair = (
                relation.more_important_criterion_id,
                relation.less_important_criterion_id,
            )
            if pair[0] not in known_ids or pair[1] not in known_ids:
                return self._result(
                    status=(
                        CriterionImportanceCompatibilityStatus.INCOMPATIBLE_PROVENANCE
                    ),
                    evidence=evidence,
                    rationale_codes=(
                        "importance:relation_references_unknown_criterion",
                    ),
                )
            if pair in relation_pairs or (pair[1], pair[0]) in relation_pairs:
                return self._result(
                    status=(
                        CriterionImportanceCompatibilityStatus.INCOMPATIBLE_PROVENANCE
                    ),
                    evidence=evidence,
                    rationale_codes=("importance:relation_not_unique",),
                )
            relation_pairs.add(pair)
            related_ids.update(pair)
            relations.append(
                CertifiedOrdinalCriterionImportanceRelation(
                    more_important_criterion_id=pair[0],
                    less_important_criterion_id=pair[1],
                    raw_text=relation.raw_text,
                    source_fingerprint=evidence.source_fingerprint,
                    source_span=(relation.start_offset, relation.end_offset),
                )
            )

        bindings = tuple(
            CriterionImportanceCompatibilityBinding(
                criterion_id=criterion.criterion_id,
                explicit_importance=None,
                has_explicit_ordinal_importance=criterion.criterion_id in related_ids,
                criterion_source_fingerprint=evidence.source_fingerprint,
                criterion_source_span=(criterion.start_offset, criterion.end_offset),
            )
            for criterion in evidence.criteria
        )
        status = (
            CriterionImportanceCompatibilityStatus.ORDINAL_IMPORTANCE_PRESERVED
            if relations
            else (
                CriterionImportanceCompatibilityStatus.COMPATIBLE_NO_CARDINAL_IMPORTANCE
            )
        )
        rationale_codes = (
            "importance:ordinal_relation_preserved_without_cardinal_synthesis",
            "importance:explicit_importance_remains_none",
        ) if relations else (
            "importance:no_explicit_cardinal_importance",
            "importance:explicit_importance_remains_none",
        )
        return self._result(
            status=status,
            evidence=evidence,
            bindings=bindings,
            ordinal_relations=tuple(relations),
            rationale_codes=rationale_codes,
        )

    @staticmethod
    def _result(
        *,
        status: CriterionImportanceCompatibilityStatus,
        evidence: ExplicitComplexDecisionCriteriaEvidence,
        rationale_codes: tuple[str, ...],
        bindings: tuple[CriterionImportanceCompatibilityBinding, ...] = (),
        ordinal_relations: tuple[CertifiedOrdinalCriterionImportanceRelation, ...] = (),
    ) -> CriterionImportanceCompatibilityResult:
        payload = repr(
            (
                _SCHEMA_VERSION,
                status.value,
                evidence.source_fingerprint,
                bindings,
                ordinal_relations,
                rationale_codes,
            )
        )
        return CriterionImportanceCompatibilityResult(
            status=status,
            bindings=bindings,
            ordinal_relations=ordinal_relations,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
            rationale_codes=rationale_codes,
        )
