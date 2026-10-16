from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.epistemic_sufficiency import (
    GovernedEpistemicSufficiencyAssessment,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
)
from core.governed_reasoning.hypothesis_epistemic_delta import (
    GovernedHypothesisEpistemicDeltaReport,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsReport,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    GovernedMultiHypothesisDiscriminationReport,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
)


class GovernedReasoningMethodOperationKind(StrEnum):
    HYPOTHESIS_DEEPENING = "hypothesis_deepening"
    MULTI_HYPOTHESIS_DISCRIMINATION = "multi_hypothesis_discrimination"
    EPISTEMIC_DELTA = "epistemic_delta"
    HYPOTHESIS_UPDATE_SEMANTICS = "hypothesis_update_semantics"


@dataclass(frozen=True)
class GovernedReasoningMethodProvenance:
    provenance_id: str
    source_kind: HypothesisDeepeningSourceKind
    source_reference: str
    world_snapshot_id: str
    operation_kinds: tuple[GovernedReasoningMethodOperationKind, ...]
    source_hypothesis_deepening_report_id: str
    source_multi_hypothesis_discrimination_report_id: str | None
    source_hypothesis_epistemic_delta_report_id: str | None
    source_hypothesis_update_semantics_report_id: str | None
    source_epistemic_sufficiency_assessment_id: str | None
    source_reasoning_quality_assessment_id: str | None
    method_fingerprint: str
    source_fingerprint: str
    schema_version: str = "post-m409.1-reasoning-method-provenance-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    derivational: bool = True
    consultative: bool = True
    evaluates_effectiveness: bool = False
    ranks_methods: bool = False
    selects_method: bool = False
    recommends_method: bool = False
    establishes_causality: bool = False
    establishes_truth: bool = False
    assigns_probability: bool = False
    modifies_reasoning: bool = False
    reruns_reasoning: bool = False
    invokes_curiosity: bool = False
    invokes_reflection: bool = False
    creates_learning_candidate: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.provenance_id.startswith("reasoning-method-provenance-"):
            raise ValueError("reasoning method provenance identifier is invalid")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("reasoning method provenance requires source lineage")
        if not self.source_hypothesis_deepening_report_id.strip():
            raise ValueError("reasoning method provenance requires deepening lineage")
        if not self.operation_kinds:
            raise ValueError("reasoning method provenance requires operations")
        if self.operation_kinds[0] is not (
            GovernedReasoningMethodOperationKind.HYPOTHESIS_DEEPENING
        ):
            raise ValueError("reasoning method provenance must begin with deepening")
        if len(set(self.operation_kinds)) != len(self.operation_kinds):
            raise ValueError("reasoning method provenance operations must be unique")
        if not self.method_fingerprint.strip() or not self.source_fingerprint.strip():
            raise ValueError("reasoning method provenance requires fingerprints")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("reasoning method provenance must preserve authority")
        if not self.read_only or not self.derivational or not self.consultative:
            raise ValueError("reasoning method provenance must remain read-only")
        if any(
            (
                self.evaluates_effectiveness,
                self.ranks_methods,
                self.selects_method,
                self.recommends_method,
                self.establishes_causality,
                self.establishes_truth,
                self.assigns_probability,
                self.modifies_reasoning,
                self.reruns_reasoning,
                self.invokes_curiosity,
                self.invokes_reflection,
                self.creates_learning_candidate,
                self.persists_results,
                self.creates_memory,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("reasoning method provenance violates governed limits")


class GovernedReasoningMethodProvenanceFoundationV1:
    """Derive method provenance only from explicit governed reasoning artifacts."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def derive(
        self,
        deepening: GovernedHypothesisDeepeningReport,
        *,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None = None,
        epistemic_delta: GovernedHypothesisEpistemicDeltaReport | None = None,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None = None,
        sufficiency: GovernedEpistemicSufficiencyAssessment | None = None,
        quality: GovernedReasoningQualityAssessment | None = None,
    ) -> GovernedReasoningMethodProvenance:
        self._validate_deepening(deepening)
        self._validate_discrimination(deepening, discrimination)
        self._validate_delta(deepening, epistemic_delta)
        self._validate_update(deepening, epistemic_delta, update_semantics)
        self._validate_sufficiency(
            deepening,
            discrimination=discrimination,
            update_semantics=update_semantics,
            sufficiency=sufficiency,
        )
        self._validate_quality(
            deepening,
            discrimination=discrimination,
            update_semantics=update_semantics,
            sufficiency=sufficiency,
            quality=quality,
        )

        operation_kinds = self._operation_kinds(
            discrimination=discrimination,
            epistemic_delta=epistemic_delta,
            update_semantics=update_semantics,
        )
        method_fingerprint = self._method_fingerprint(
            deepening.source_kind,
            operation_kinds,
        )
        source_fingerprint = self._source_fingerprint(
            deepening,
            discrimination=discrimination,
            epistemic_delta=epistemic_delta,
            update_semantics=update_semantics,
            sufficiency=sufficiency,
            quality=quality,
            method_fingerprint=method_fingerprint,
        )
        return GovernedReasoningMethodProvenance(
            provenance_id=f"reasoning-method-provenance-{source_fingerprint[:24]}",
            source_kind=deepening.source_kind,
            source_reference=deepening.source_reference,
            world_snapshot_id=deepening.world_snapshot_id,
            operation_kinds=operation_kinds,
            source_hypothesis_deepening_report_id=deepening.report_id,
            source_multi_hypothesis_discrimination_report_id=(
                discrimination.report_id if discrimination is not None else None
            ),
            source_hypothesis_epistemic_delta_report_id=(
                epistemic_delta.report_id if epistemic_delta is not None else None
            ),
            source_hypothesis_update_semantics_report_id=(
                update_semantics.report_id if update_semantics is not None else None
            ),
            source_epistemic_sufficiency_assessment_id=(
                sufficiency.assessment_id if sufficiency is not None else None
            ),
            source_reasoning_quality_assessment_id=(
                quality.assessment_id if quality is not None else None
            ),
            method_fingerprint=method_fingerprint,
            source_fingerprint=source_fingerprint,
        )

    @staticmethod
    def _operation_kinds(
        *,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
        epistemic_delta: GovernedHypothesisEpistemicDeltaReport | None,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None,
    ) -> tuple[GovernedReasoningMethodOperationKind, ...]:
        operations = [GovernedReasoningMethodOperationKind.HYPOTHESIS_DEEPENING]
        if discrimination is not None:
            operations.append(
                GovernedReasoningMethodOperationKind.MULTI_HYPOTHESIS_DISCRIMINATION
            )
        if epistemic_delta is not None:
            operations.append(GovernedReasoningMethodOperationKind.EPISTEMIC_DELTA)
        if update_semantics is not None:
            operations.append(
                GovernedReasoningMethodOperationKind.HYPOTHESIS_UPDATE_SEMANTICS
            )
        return tuple(operations)

    @classmethod
    def _validate_deepening(cls, deepening: GovernedHypothesisDeepeningReport) -> None:
        if deepening.canonical_authority != cls.CANONICAL_AUTHORITY:
            raise ValueError("method provenance requires governed reasoning authority")
        if not deepening.read_only or not deepening.consultative:
            raise ValueError("method provenance requires read-only deepening")
        if (
            not deepening.source_reference.strip()
            or not deepening.world_snapshot_id.strip()
        ):
            raise ValueError("method provenance requires deepening source lineage")

    @classmethod
    def _validate_discrimination(
        cls,
        deepening: GovernedHypothesisDeepeningReport,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
    ) -> None:
        if discrimination is None:
            return
        if discrimination.canonical_authority != cls.CANONICAL_AUTHORITY:
            raise ValueError("method discrimination must preserve reasoning authority")
        if not discrimination.read_only or not discrimination.consultative:
            raise ValueError("method provenance requires read-only discrimination")
        if discrimination.source_reference != deepening.source_reference:
            raise ValueError("method discrimination source lineage mismatch")
        if discrimination.world_snapshot_id != deepening.world_snapshot_id:
            raise ValueError("method discrimination snapshot lineage mismatch")

    @classmethod
    def _validate_delta(
        cls,
        deepening: GovernedHypothesisDeepeningReport,
        delta: GovernedHypothesisEpistemicDeltaReport | None,
    ) -> None:
        if delta is None:
            return
        if delta.canonical_authority != cls.CANONICAL_AUTHORITY:
            raise ValueError("method delta must preserve reasoning authority")
        if not delta.read_only or not delta.consultative:
            raise ValueError("method provenance requires read-only delta")
        if delta.source_reference != deepening.source_reference:
            raise ValueError("method delta source lineage mismatch")
        if delta.after_report_id != deepening.report_id:
            raise ValueError("method delta after-report lineage mismatch")
        if delta.after_world_snapshot_id != deepening.world_snapshot_id:
            raise ValueError("method delta after-snapshot lineage mismatch")

    @classmethod
    def _validate_update(
        cls,
        deepening: GovernedHypothesisDeepeningReport,
        delta: GovernedHypothesisEpistemicDeltaReport | None,
        update: GovernedHypothesisUpdateSemanticsReport | None,
    ) -> None:
        if update is None:
            return
        if update.canonical_authority != cls.CANONICAL_AUTHORITY:
            raise ValueError("method update must preserve reasoning authority")
        if not update.read_only or not update.consultative:
            raise ValueError("method provenance requires read-only update semantics")
        if update.source_reference != deepening.source_reference:
            raise ValueError("method update source lineage mismatch")
        if update.after_world_snapshot_id != deepening.world_snapshot_id:
            raise ValueError("method update snapshot lineage mismatch")
        if delta is not None and update.source_delta_report_id != delta.report_id:
            raise ValueError("method update delta lineage mismatch")

    @classmethod
    def _validate_sufficiency(
        cls,
        deepening: GovernedHypothesisDeepeningReport,
        *,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None,
        sufficiency: GovernedEpistemicSufficiencyAssessment | None,
    ) -> None:
        if sufficiency is None:
            return
        if sufficiency.canonical_authority != cls.CANONICAL_AUTHORITY:
            raise ValueError("method sufficiency must preserve reasoning authority")
        if not sufficiency.read_only or not sufficiency.consultative:
            raise ValueError("method provenance requires read-only sufficiency")
        if sufficiency.source_hypothesis_deepening_report_id != deepening.report_id:
            raise ValueError("method sufficiency deepening lineage mismatch")
        if sufficiency.source_reference != deepening.source_reference:
            raise ValueError("method sufficiency source lineage mismatch")
        if sufficiency.world_snapshot_id != deepening.world_snapshot_id:
            raise ValueError("method sufficiency snapshot lineage mismatch")
        expected_discrimination = discrimination.report_id if discrimination else None
        if (
            sufficiency.source_multi_hypothesis_discrimination_report_id
            != expected_discrimination
        ):
            raise ValueError("method sufficiency discrimination lineage mismatch")
        expected_update = update_semantics.report_id if update_semantics else None
        if sufficiency.source_hypothesis_update_semantics_report_id != expected_update:
            raise ValueError("method sufficiency update lineage mismatch")

    @classmethod
    def _validate_quality(
        cls,
        deepening: GovernedHypothesisDeepeningReport,
        *,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None,
        sufficiency: GovernedEpistemicSufficiencyAssessment | None,
        quality: GovernedReasoningQualityAssessment | None,
    ) -> None:
        if quality is None:
            return
        if sufficiency is None:
            raise ValueError("method quality lineage requires supplied sufficiency")
        if quality.canonical_authority != cls.CANONICAL_AUTHORITY:
            raise ValueError("method quality must preserve reasoning authority")
        if not quality.read_only or not quality.consultative:
            raise ValueError("method provenance requires read-only quality")
        if quality.source_hypothesis_deepening_report_id != deepening.report_id:
            raise ValueError("method quality deepening lineage mismatch")
        if (
            quality.source_epistemic_sufficiency_assessment_id
            != sufficiency.assessment_id
        ):
            raise ValueError("method quality sufficiency lineage mismatch")
        if quality.source_reference != deepening.source_reference:
            raise ValueError("method quality source lineage mismatch")
        if quality.world_snapshot_id != deepening.world_snapshot_id:
            raise ValueError("method quality snapshot lineage mismatch")
        expected_discrimination = discrimination.report_id if discrimination else None
        if (
            quality.source_multi_hypothesis_discrimination_report_id
            != expected_discrimination
        ):
            raise ValueError("method quality discrimination lineage mismatch")
        expected_update = update_semantics.report_id if update_semantics else None
        if quality.source_hypothesis_update_semantics_report_id != expected_update:
            raise ValueError("method quality update lineage mismatch")

    @staticmethod
    def _method_fingerprint(
        source_kind: HypothesisDeepeningSourceKind,
        operation_kinds: tuple[GovernedReasoningMethodOperationKind, ...],
    ) -> str:
        return sha256(
            repr(
                (source_kind.value, tuple(item.value for item in operation_kinds))
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _source_fingerprint(
        deepening: GovernedHypothesisDeepeningReport,
        *,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
        epistemic_delta: GovernedHypothesisEpistemicDeltaReport | None,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None,
        sufficiency: GovernedEpistemicSufficiencyAssessment | None,
        quality: GovernedReasoningQualityAssessment | None,
        method_fingerprint: str,
    ) -> str:
        return sha256(
            repr(
                (
                    deepening.source_reference,
                    deepening.world_snapshot_id,
                    deepening.report_id,
                    discrimination.report_id if discrimination else None,
                    epistemic_delta.report_id if epistemic_delta else None,
                    update_semantics.report_id if update_semantics else None,
                    sufficiency.assessment_id if sufficiency else None,
                    quality.assessment_id if quality else None,
                    method_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
