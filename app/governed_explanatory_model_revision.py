from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from app.governed_explanatory_model_productive_consumption import (
    GovernedExplanatoryModelProductiveConsumption,
    GovernedExplanatoryModelProductiveConsumptionV1,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from core.governed_reasoning.explanatory_model_composition import (
    ExplanatoryModelCompositionStatus,
    GovernedExplanatoryModelCandidate,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
)


class GovernedExplanatoryModelRevisionStatus(StrEnum):
    REVISED = "revised"
    REENTRY_REQUIRED = "reentry_required"
    LINEAGE_MISMATCH = "lineage_mismatch"
    EVIDENCE_NOT_APPLIED = "evidence_not_applied"
    HYPOTHESIS_SET_MISMATCH = "hypothesis_set_mismatch"
    NO_MATERIAL_CHANGE = "no_material_change"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedExplanatoryModelRevision:
    revision_id: str
    status: GovernedExplanatoryModelRevisionStatus
    previous_model_id: str
    revised_model_id: str | None
    reentry_id: str
    evidence_id: str | None
    requirement_id: str
    source_reference: str
    world_snapshot_id: str
    changed_hypothesis_ids: tuple[str, ...]
    removed_requirement_ids: tuple[str, ...]
    added_requirement_ids: tuple[str, ...]
    revised_consumption: GovernedExplanatoryModelProductiveConsumption | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-cap-05-evidence-driven-model-revision-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_facts: bool = False
    establishes_truth: bool = False
    establishes_causality: bool = False
    creates_questions: bool = False
    creates_learning: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    executes_transfer: bool = False
    registers_rule: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.revision_id.startswith("explanatory-model-revision-"):
            raise ValueError("explanatory model revision identifier is invalid")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("explanatory model revision must preserve authority")
        if not self.read_only or not self.consultative or any(
            (
                self.persists_results,
                self.creates_facts,
                self.establishes_truth,
                self.establishes_causality,
                self.creates_questions,
                self.creates_learning,
                self.modifies_memory,
                self.modifies_world_model,
                self.executes_transfer,
                self.registers_rule,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("explanatory model revision violates governed limits")
        if self.status is GovernedExplanatoryModelRevisionStatus.REVISED:
            if self.revised_consumption is None or self.revised_model_id is None:
                raise ValueError("successful revision requires revised model")
            if self.evidence_id is None:
                raise ValueError("successful revision requires acquired evidence")
            if self.previous_model_id == self.revised_model_id:
                raise ValueError("revision must produce a materially distinct model")
        elif self.revised_consumption is not None or self.revised_model_id is not None:
            raise ValueError("non-revised result cannot expose a revised model")

    def context_lines(self) -> tuple[str, ...]:
        if self.status is not GovernedExplanatoryModelRevisionStatus.REVISED:
            return ()
        changed = ", ".join(self.changed_hypothesis_ids) or "estructura discriminativa"
        return (
            (
                "Modelo explicativo revisado por evidencia gobernada disponible: "
                f"{self.previous_model_id} → {self.revised_model_id}; "
                f"cambio en {changed}."
            ),
            (
                "La revisión preserva lineage hacia la evidencia adquirida y sigue "
                "siendo consultiva: no establece verdad, causalidad, aprendizaje, "
                "memoria, transferencia ni acción."
            ),
        )


class GovernedEvidenceDrivenExplanatoryModelRevisionV1:
    """Compose V1 + governed acquired evidence reassessment into bounded V2."""

    def __init__(self) -> None:
        self._consumer = GovernedExplanatoryModelProductiveConsumptionV1()

    def consume(
        self,
        previous: GovernedExplanatoryModelProductiveConsumption,
        reentry: GovernedLevel2ReasoningReentryResult,
        revised_report: GovernedHypothesisDeepeningReport,
    ) -> GovernedExplanatoryModelRevision:
        model_v1 = previous.model
        if (
            reentry.status is not GovernedReasoningReentryStatus.REEVALUATED
            or reentry.evidence_id is None
        ):
            return self._result(
                model_v1,
                reentry,
                GovernedExplanatoryModelRevisionStatus.REENTRY_REQUIRED,
                None,
                (),
                (),
                (),
                ("revision:successful_governed_reentry_required",),
            )

        if (
            reentry.requirement_id not in model_v1.unresolved_requirement_ids
            or reentry.source_reference != model_v1.source_reference
            or reentry.world_snapshot_id != model_v1.world_snapshot_id
            or revised_report.source_reference != model_v1.source_reference
            or revised_report.world_snapshot_id != model_v1.world_snapshot_id
        ):
            return self._result(
                model_v1,
                reentry,
                GovernedExplanatoryModelRevisionStatus.LINEAGE_MISMATCH,
                None,
                (),
                (),
                (),
                ("revision:exact_model_evidence_lineage_required",),
            )

        previous_ids = tuple(sorted(item.hypothesis_id for item in model_v1.components))
        revised_ids = tuple(
            sorted(item.hypothesis_id for item in revised_report.assessments)
        )
        if previous_ids != revised_ids:
            return self._result(
                model_v1,
                reentry,
                GovernedExplanatoryModelRevisionStatus.HYPOTHESIS_SET_MISMATCH,
                None,
                (),
                (),
                (),
                ("revision:same_hypothesis_set_required",),
            )

        evidence_applied_to = tuple(
            sorted(
                item.hypothesis_id
                for item in revised_report.assessments
                if reentry.evidence_id in item.evidence_references
            )
        )
        if not evidence_applied_to:
            return self._result(
                model_v1,
                reentry,
                GovernedExplanatoryModelRevisionStatus.EVIDENCE_NOT_APPLIED,
                None,
                (),
                (),
                (),
                ("revision:acquired_evidence_must_reach_reassessment",),
            )

        revised = self._consumer.consume(revised_report)
        model_v2 = revised.model
        if model_v2.status is not ExplanatoryModelCompositionStatus.MODEL_CANDIDATE:
            return self._result(
                model_v1,
                reentry,
                GovernedExplanatoryModelRevisionStatus.REVIEW_REQUIRED,
                None,
                (),
                (),
                (),
                ("revision:revised_model_candidate_required",),
            )

        changed_ids = self._changed_hypothesis_ids(model_v1, model_v2)
        previous_requirements = set(model_v1.unresolved_requirement_ids)
        revised_requirements = set(model_v2.unresolved_requirement_ids)
        removed = tuple(sorted(previous_requirements - revised_requirements))
        added = tuple(sorted(revised_requirements - previous_requirements))
        material_change = bool(
            changed_ids
            or removed
            or added
            or self._relation_signature(model_v1)
            != self._relation_signature(model_v2)
        )
        if not material_change:
            return self._result(
                model_v1,
                reentry,
                GovernedExplanatoryModelRevisionStatus.NO_MATERIAL_CHANGE,
                None,
                (),
                (),
                (),
                ("revision:new_evidence_did_not_change_model_assessment",),
            )

        return self._result(
            model_v1,
            reentry,
            GovernedExplanatoryModelRevisionStatus.REVISED,
            revised,
            changed_ids,
            removed,
            added,
            (
                "revision:governed_evidence_reassessment_applied",
                "revision:same_hypothesis_set_preserved",
                "revision:material_model_change_confirmed",
            ),
        )

    @staticmethod
    def _component_signature(component) -> tuple[object, ...]:
        return (
            component.evidence_relation.value,
            component.evidence_references,
            component.unresolved_gap_ids,
        )

    @classmethod
    def _changed_hypothesis_ids(
        cls,
        previous: GovernedExplanatoryModelCandidate,
        revised: GovernedExplanatoryModelCandidate,
    ) -> tuple[str, ...]:
        left = {item.hypothesis_id: item for item in previous.components}
        right = {item.hypothesis_id: item for item in revised.components}
        return tuple(
            sorted(
                hypothesis_id
                for hypothesis_id in left
                if cls._component_signature(left[hypothesis_id])
                != cls._component_signature(right[hypothesis_id])
            )
        )

    @staticmethod
    def _relation_signature(
        model: GovernedExplanatoryModelCandidate,
    ) -> tuple[tuple[str, str, str], ...]:
        return tuple(
            sorted(
                (
                    item.left_hypothesis_id,
                    item.right_hypothesis_id,
                    item.relation.value,
                )
                for item in model.relations
            )
        )

    @staticmethod
    def _result(
        model_v1: GovernedExplanatoryModelCandidate,
        reentry: GovernedLevel2ReasoningReentryResult,
        status: GovernedExplanatoryModelRevisionStatus,
        revised: GovernedExplanatoryModelProductiveConsumption | None,
        changed_hypothesis_ids: tuple[str, ...],
        removed_requirement_ids: tuple[str, ...],
        added_requirement_ids: tuple[str, ...],
        rationale_codes: tuple[str, ...],
    ) -> GovernedExplanatoryModelRevision:
        model_v2 = revised.model if revised is not None else None
        fingerprint = sha256(
            repr(
                (
                    model_v1.model_id,
                    reentry.reentry_id,
                    reentry.evidence_id,
                    reentry.requirement_id,
                    None if model_v2 is None else model_v2.model_id,
                    status.value,
                    changed_hypothesis_ids,
                    removed_requirement_ids,
                    added_requirement_ids,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedExplanatoryModelRevision(
            revision_id=f"explanatory-model-revision-{fingerprint[:24]}",
            status=status,
            previous_model_id=model_v1.model_id,
            revised_model_id=None if model_v2 is None else model_v2.model_id,
            reentry_id=reentry.reentry_id,
            evidence_id=reentry.evidence_id,
            requirement_id=reentry.requirement_id,
            source_reference=model_v1.source_reference,
            world_snapshot_id=model_v1.world_snapshot_id,
            changed_hypothesis_ids=changed_hypothesis_ids,
            removed_requirement_ids=removed_requirement_ids,
            added_requirement_ids=added_requirement_ids,
            revised_consumption=revised,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
