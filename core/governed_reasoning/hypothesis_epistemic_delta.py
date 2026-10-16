from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningStatus,
    HypothesisEvidenceRelation,
)


class HypothesisEpistemicDeltaKind(StrEnum):
    UNCHANGED = "unchanged"
    EVIDENCE_CHANGED = "evidence_changed"
    RELATION_CHANGED = "relation_changed"
    RELATION_AND_EVIDENCE_CHANGED = "relation_and_evidence_changed"
    NEW_HYPOTHESIS = "new_hypothesis"
    MISSING_FROM_AFTER = "missing_from_after"
    PROPOSITION_CONFLICT = "proposition_conflict"


class GovernedHypothesisEpistemicDeltaStatus(StrEnum):
    COMPLETE = "complete"
    REVIEW_REQUIRED = "review_required"
    SOURCE_REVIEW_REQUIRED = "source_review_required"


@dataclass(frozen=True)
class GovernedHypothesisDeltaTrigger:
    trigger_id: str
    evidence_references: tuple[str, ...]
    source_reference: str
    world_snapshot_id: str
    rationale_codes: tuple[str, ...]
    read_only: bool = True
    establishes_truth: bool = False
    establishes_falsity: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_hypotheses: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.trigger_id.startswith("hypothesis-delta-trigger-"):
            raise ValueError("hypothesis delta trigger identifier is invalid")
        if not self.evidence_references or any(
            not item.strip() for item in self.evidence_references
        ):
            raise ValueError("hypothesis delta trigger requires evidence references")
        if len(self.evidence_references) != len(set(self.evidence_references)):
            raise ValueError("hypothesis delta trigger evidence must be unique")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("hypothesis delta trigger requires source lineage")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("hypothesis delta trigger requires rationale codes")
        if not self.read_only or any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_hypotheses,
                self.grants_authority,
            )
        ):
            raise ValueError("hypothesis delta trigger violates governed limits")


@dataclass(frozen=True)
class GovernedHypothesisEpistemicDelta:
    hypothesis_id: str
    kind: HypothesisEpistemicDeltaKind
    proposition_before: str | None
    proposition_after: str | None
    before_relation: HypothesisEvidenceRelation | None
    after_relation: HypothesisEvidenceRelation | None
    before_evidence_references: tuple[str, ...]
    after_evidence_references: tuple[str, ...]
    added_evidence_references: tuple[str, ...]
    removed_evidence_references: tuple[str, ...]
    triggering_evidence_references: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    establishes_truth: bool = False
    establishes_falsity: bool = False
    deletes_hypothesis: bool = False
    revokes_evidence: bool = False

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip():
            raise ValueError("hypothesis delta requires hypothesis identity")
        if self.proposition_before is None and self.proposition_after is None:
            raise ValueError("hypothesis delta requires at least one proposition")
        if not self.triggering_evidence_references:
            raise ValueError("hypothesis delta requires triggering evidence")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("hypothesis delta requires rationale codes")
        if self.establishes_truth or self.establishes_falsity:
            raise ValueError("hypothesis delta cannot establish truth or falsity")
        if self.deletes_hypothesis or self.revokes_evidence:
            raise ValueError("hypothesis delta cannot delete hypotheses or evidence")


@dataclass(frozen=True)
class GovernedHypothesisEpistemicDeltaReport:
    report_id: str
    status: GovernedHypothesisEpistemicDeltaStatus
    before_report_id: str
    after_report_id: str
    trigger_id: str
    source_reference: str
    before_world_snapshot_id: str
    after_world_snapshot_id: str
    triggering_evidence_references: tuple[str, ...]
    deltas: tuple[GovernedHypothesisEpistemicDelta, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-hypothesis-epistemic-delta-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    establishes_truth: bool = False
    establishes_falsity: bool = False
    modifies_hypotheses: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    invokes_reasoning: bool = False
    invokes_curiosity: bool = False
    invokes_planning: bool = False
    invokes_capabilities: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("hypothesis-epistemic-delta-"):
            raise ValueError("hypothesis epistemic delta report identifier is invalid")
        if not self.before_report_id.strip() or not self.after_report_id.strip():
            raise ValueError("hypothesis delta report requires report lineage")
        if not self.source_reference.strip():
            raise ValueError("hypothesis delta report requires source lineage")
        if (
            not self.before_world_snapshot_id.strip()
            or not self.after_world_snapshot_id.strip()
        ):
            raise ValueError("hypothesis delta report requires snapshot lineage")
        if not self.triggering_evidence_references:
            raise ValueError("hypothesis delta report requires triggering evidence")
        if not self.rationale_codes:
            raise ValueError("hypothesis delta report requires rationale codes")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("hypothesis delta must preserve reasoning authority")
        if not self.read_only or not self.consultative or any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.modifies_hypotheses,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.invokes_reasoning,
                self.invokes_curiosity,
                self.invokes_planning,
                self.invokes_capabilities,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("hypothesis epistemic delta violates governed limits")


class GovernedHypothesisEpistemicDeltaFoundationV1:
    """Describe structural epistemic change without becoming a reasoning authority."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def compare(
        self,
        before: GovernedHypothesisDeepeningReport,
        trigger: GovernedHypothesisDeltaTrigger,
        after: GovernedHypothesisDeepeningReport,
    ) -> GovernedHypothesisEpistemicDeltaReport:
        self._validate_lineage(before, trigger, after)
        if self._source_requires_review(before) or self._source_requires_review(after):
            return self._report(
                before,
                trigger,
                after,
                GovernedHypothesisEpistemicDeltaStatus.SOURCE_REVIEW_REQUIRED,
                (),
                ("hypothesis_delta:source_review_required",),
            )

        before_by_id = {item.hypothesis_id: item for item in before.assessments}
        after_by_id = {item.hypothesis_id: item for item in after.assessments}
        hypothesis_ids = tuple(sorted(set(before_by_id) | set(after_by_id)))
        deltas = tuple(
            self._delta_for(
                hypothesis_id,
                before_by_id.get(hypothesis_id),
                after_by_id.get(hypothesis_id),
                trigger,
            )
            for hypothesis_id in hypothesis_ids
        )
        review_required = any(
            item.kind
            in {
                HypothesisEpistemicDeltaKind.MISSING_FROM_AFTER,
                HypothesisEpistemicDeltaKind.PROPOSITION_CONFLICT,
            }
            for item in deltas
        )
        status = (
            GovernedHypothesisEpistemicDeltaStatus.REVIEW_REQUIRED
            if review_required
            else GovernedHypothesisEpistemicDeltaStatus.COMPLETE
        )
        rationale = (
            "hypothesis_delta:structural_delta_derived",
            "hypothesis_delta:no_truth_or_falsity_promotion",
        )
        if review_required:
            rationale = (*rationale, "hypothesis_delta:structural_review_required")
        return self._report(before, trigger, after, status, deltas, rationale)

    @staticmethod
    def _source_requires_review(report: GovernedHypothesisDeepeningReport) -> bool:
        return report.status in {
            HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED,
            HypothesisDeepeningStatus.DEGRADED,
        }

    @staticmethod
    def _validate_lineage(
        before: GovernedHypothesisDeepeningReport,
        trigger: GovernedHypothesisDeltaTrigger,
        after: GovernedHypothesisDeepeningReport,
    ) -> None:
        if before.canonical_authority != "governed_reasoning":
            raise ValueError("before report must preserve governed reasoning authority")
        if after.canonical_authority != "governed_reasoning":
            raise ValueError("after report must preserve governed reasoning authority")
        if before.source_kind is not after.source_kind:
            raise ValueError("hypothesis delta requires one source kind")
        if before.source_reference != after.source_reference:
            raise ValueError("hypothesis delta requires one source reference")
        if trigger.source_reference != after.source_reference:
            raise ValueError("trigger must preserve hypothesis source lineage")
        if trigger.world_snapshot_id != after.world_snapshot_id:
            raise ValueError("trigger must identify the after snapshot")
        if before.report_id == after.report_id:
            raise ValueError("before and after reports must be distinct")

    @classmethod
    def _delta_for(cls, hypothesis_id, before, after, trigger):
        if before is None:
            return GovernedHypothesisEpistemicDelta(
                hypothesis_id=hypothesis_id,
                kind=HypothesisEpistemicDeltaKind.NEW_HYPOTHESIS,
                proposition_before=None,
                proposition_after=after.proposition,
                before_relation=None,
                after_relation=after.relation,
                before_evidence_references=(),
                after_evidence_references=after.evidence_references,
                added_evidence_references=after.evidence_references,
                removed_evidence_references=(),
                triggering_evidence_references=trigger.evidence_references,
                rationale_codes=("hypothesis_delta:new_hypothesis_observed",),
            )
        if after is None:
            return GovernedHypothesisEpistemicDelta(
                hypothesis_id=hypothesis_id,
                kind=HypothesisEpistemicDeltaKind.MISSING_FROM_AFTER,
                proposition_before=before.proposition,
                proposition_after=None,
                before_relation=before.relation,
                after_relation=None,
                before_evidence_references=before.evidence_references,
                after_evidence_references=(),
                added_evidence_references=(),
                removed_evidence_references=before.evidence_references,
                triggering_evidence_references=trigger.evidence_references,
                rationale_codes=(
                    "hypothesis_delta:missing_from_after_requires_review",
                ),
            )
        if before.proposition != after.proposition:
            kind = HypothesisEpistemicDeltaKind.PROPOSITION_CONFLICT
        else:
            relation_changed = before.relation is not after.relation
            evidence_changed = before.evidence_references != after.evidence_references
            if relation_changed and evidence_changed:
                kind = HypothesisEpistemicDeltaKind.RELATION_AND_EVIDENCE_CHANGED
            elif relation_changed:
                kind = HypothesisEpistemicDeltaKind.RELATION_CHANGED
            elif evidence_changed:
                kind = HypothesisEpistemicDeltaKind.EVIDENCE_CHANGED
            else:
                kind = HypothesisEpistemicDeltaKind.UNCHANGED
        before_refs = set(before.evidence_references)
        after_refs = set(after.evidence_references)
        return GovernedHypothesisEpistemicDelta(
            hypothesis_id=hypothesis_id,
            kind=kind,
            proposition_before=before.proposition,
            proposition_after=after.proposition,
            before_relation=before.relation,
            after_relation=after.relation,
            before_evidence_references=before.evidence_references,
            after_evidence_references=after.evidence_references,
            added_evidence_references=tuple(sorted(after_refs - before_refs)),
            removed_evidence_references=tuple(sorted(before_refs - after_refs)),
            triggering_evidence_references=trigger.evidence_references,
            rationale_codes=(f"hypothesis_delta:{kind.value}",),
        )

    @staticmethod
    def _report(before, trigger, after, status, deltas, rationale_codes):
        fingerprint = sha256(
            repr(
                (
                    before.report_id,
                    after.report_id,
                    trigger.trigger_id,
                    trigger.evidence_references,
                    tuple(
                        (
                            item.hypothesis_id,
                            item.kind.value,
                            item.before_relation.value
                            if item.before_relation is not None
                            else None,
                            item.after_relation.value
                            if item.after_relation is not None
                            else None,
                            item.added_evidence_references,
                            item.removed_evidence_references,
                        )
                        for item in deltas
                    ),
                    status.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedHypothesisEpistemicDeltaReport(
            report_id=f"hypothesis-epistemic-delta-{fingerprint[:24]}",
            status=status,
            before_report_id=before.report_id,
            after_report_id=after.report_id,
            trigger_id=trigger.trigger_id,
            source_reference=before.source_reference,
            before_world_snapshot_id=before.world_snapshot_id,
            after_world_snapshot_id=after.world_snapshot_id,
            triggering_evidence_references=trigger.evidence_references,
            deltas=deltas,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
