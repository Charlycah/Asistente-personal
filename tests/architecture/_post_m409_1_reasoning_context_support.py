from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from app.governed_reasoning_runtime import build_default_governed_reasoning_orchestrator
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.context import ReasoningContextBundle, ReasoningQuery
from core.governed_reasoning.derived_epistemic_assessment import (
    GovernedDerivedEpistemicAssessment,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.hypothesis_epistemic_delta import (
    GovernedHypothesisDeltaTrigger,
    GovernedHypothesisEpistemicDeltaFoundationV1,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsFoundationV1,
)

NOW = datetime(2026, 8, 14, 14, 55, tzinfo=timezone.utc)


def context() -> ReasoningContextBundle:
    orchestrator = build_default_governed_reasoning_orchestrator()
    return orchestrator.context_assembler.assemble(
        ReasoningQuery(
            text="evaluate hypotheses h1 and h2",
            topics=("h1", "h2"),
            as_of=NOW,
        ),
        now=NOW,
    )


def _assessment(
    relation: HypothesisEvidenceRelation,
    *,
    hypothesis_id: str = "h1",
    evidence: tuple[str, ...] = ("fact-a",),
) -> HypothesisEvidenceAssessment:
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=f"proposition {hypothesis_id}",
        relation=relation,
        evidence_references=evidence,
        rationale_codes=(f"assessment:{hypothesis_id}",),
        epistemic_level=EpistemicLevel.HYPOTHESIS,
    )


def _report(
    suffix: str,
    assessments: tuple[HypothesisEvidenceAssessment, ...],
    snapshot: str,
) -> GovernedHypothesisDeepeningReport:
    return GovernedHypothesisDeepeningReport(
        report_id=f"hypothesis-deepening-{suffix:0<16}"[:37],
        status=HypothesisDeepeningStatus.COMPLETE,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-123",
        world_snapshot_id=snapshot,
        assessments=assessments,
        epistemic_gaps=(),
        evidence_codes=(f"world_snapshot:{snapshot}",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint=f"fingerprint-{suffix}",
    )


def semantics():
    before = _report(
        "before",
        (
            _assessment(HypothesisEvidenceRelation.UNRESOLVED, hypothesis_id="h1"),
            _assessment(HypothesisEvidenceRelation.COMPATIBLE, hypothesis_id="h2"),
        ),
        "world-1",
    )
    after = _report(
        "after",
        (
            _assessment(
                HypothesisEvidenceRelation.COMPATIBLE,
                hypothesis_id="h1",
                evidence=("fact-a", "evidence-e1"),
            ),
            _assessment(
                HypothesisEvidenceRelation.CONTRADICTED,
                hypothesis_id="h2",
                evidence=("fact-a", "evidence-e1"),
            ),
        ),
        "world-2",
    )
    trigger = GovernedHypothesisDeltaTrigger(
        trigger_id="hypothesis-delta-trigger-evidence-1234567890",
        evidence_references=("evidence-e1",),
        source_reference="scenario-123",
        world_snapshot_id="world-2",
        rationale_codes=("trigger:level2_acquired_evidence",),
    )
    delta = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before,
        trigger,
        after,
    )
    return GovernedHypothesisUpdateSemanticsFoundationV1().classify(delta)


def augment_with_semantics(
    base: ReasoningContextBundle | None = None,
) -> ReasoningContextBundle:
    report = semantics()
    items = tuple(
        GovernedDerivedEpistemicAssessment.build(
            semantic_report_id=report.report_id,
            hypothesis_id=update.hypothesis_id,
            delta_kind=update.delta_kind,
            semantic=update.semantic,
            before_relation=update.before_relation,
            after_relation=update.after_relation,
            triggering_evidence_references=update.triggering_evidence_references,
            added_evidence_references=update.added_evidence_references,
            source_reference=report.source_reference,
            before_world_snapshot_id=report.before_world_snapshot_id,
            after_world_snapshot_id=report.after_world_snapshot_id,
            rationale_codes=update.rationale_codes,
        )
        for update in report.updates
    )
    current = context() if base is None else base
    return replace(
        current,
        derived_assessments=(*current.derived_assessments, *items),
        context_id="",
    )
