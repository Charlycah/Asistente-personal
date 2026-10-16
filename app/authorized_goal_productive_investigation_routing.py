from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from hashlib import sha256
from typing import Protocol

from app.governed_intellectual_goal_investigation_admission import (
    GovernedAuthorizedIntellectualGoal,
    GovernedAuthorizedIntellectualGoalRequirementAdmissionResult,
    GovernedAuthorizedIntellectualGoalRequirementAdmissionV1,
)
from app.governed_multi_hypothesis_productive_consumption import (
    GovernedMultiHypothesisProductiveConsumption,
    GovernedMultiHypothesisProductiveConsumptionV1,
)
from core.governed_reasoning.causal_prediction import GovernedCausalPredictiveReasoner
from core.governed_reasoning.explicit_hypothesis_source import (
    ExplicitHypothesisSourceKind,
    GovernedExplicitHypothesisSource,
    GovernedExplicitHypothesisSourceResult,
    GovernedExplicitHypothesisSourceStatus,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepener,
    GovernedHypothesisDeepeningReport,
)
from core.governed_reasoning.scenario_simulation import GovernedScenarioSimulator
from core.persistent_world_model import PersistentWorldSnapshot


class _ExplicitHypothesisEvaluationGateway(Protocol):
    def evaluate_explicit_hypothesis_source(
        self,
        source: GovernedExplicitHypothesisSource,
        *,
        world: PersistentWorldSnapshot,
    ) -> GovernedExplicitHypothesisSourceResult: ...


class AuthorizedGoalInvestigationRoutingStatus(StrEnum):
    ADMITTED = "admitted"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class AuthorizedGoalProductiveInvestigationRoutingResult:
    status: AuthorizedGoalInvestigationRoutingStatus
    source_evaluations: tuple[GovernedExplicitHypothesisSourceResult, ...]
    deepening: GovernedHypothesisDeepeningReport
    discrimination: GovernedMultiHypothesisProductiveConsumption
    admission: GovernedAuthorizedIntellectualGoalRequirementAdmissionResult | None
    source_reference: str
    world_snapshot_id: str
    cap11_admission_invocation_count: int
    read_only: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("routing result requires exact source lineage")
        if self.cap11_admission_invocation_count not in {0, 1}:
            raise ValueError("routing result permits at most one CAP-11 admission")
        if self.status is AuthorizedGoalInvestigationRoutingStatus.ADMITTED:
            if self.admission is None or self.cap11_admission_invocation_count != 1:
                raise ValueError("admitted routing requires one G4 admission")
        elif self.admission is not None or self.cap11_admission_invocation_count:
            raise ValueError("review routing cannot expose CAP-11 admission")
        if not self.read_only or any(
            (
                self.persists_results,
                self.creates_memory,
                self.creates_learning,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("routing result violates governed limits")


class AuthorizedGoalProductiveInvestigationRoutingV1:
    """Compose existing reasoning authorities into the existing G4 CAP-11 gate."""

    def __init__(
        self,
        reasoning_gateway: _ExplicitHypothesisEvaluationGateway,
        *,
        discrimination: GovernedMultiHypothesisProductiveConsumptionV1 | None = None,
        g4_admission: GovernedAuthorizedIntellectualGoalRequirementAdmissionV1
        | None = None,
    ) -> None:
        self._reasoning_gateway = reasoning_gateway
        self._discrimination = (
            discrimination or GovernedMultiHypothesisProductiveConsumptionV1()
        )
        self._g4_admission = (
            g4_admission or GovernedAuthorizedIntellectualGoalRequirementAdmissionV1()
        )

    def route(
        self,
        goal: GovernedAuthorizedIntellectualGoal,
        sources: tuple[GovernedExplicitHypothesisSource, ...],
        *,
        world: PersistentWorldSnapshot,
        originating_reasoning_id: str,
    ) -> AuthorizedGoalProductiveInvestigationRoutingResult:
        reasoning_id = originating_reasoning_id.strip()
        if not goal.authorized or not goal.read_only or not goal.non_executive:
            raise ValueError("routing requires authorized intellectual goal")
        if not reasoning_id:
            raise ValueError("routing requires originating reasoning lineage")
        if len(sources) != 2:
            raise ValueError("routing requires exactly two structured hypotheses")
        if any(source.source_reference != goal.source_reference for source in sources):
            raise ValueError("structured hypothesis lineage does not match goal")
        kinds = {source.kind for source in sources}
        if len(kinds) != 1 or ExplicitHypothesisSourceKind.NONE in kinds:
            raise ValueError("routing requires two hypotheses of one structured kind")

        evaluated = tuple(
            self._reasoning_gateway.evaluate_explicit_hypothesis_source(
                source,
                world=world,
            )
            for source in sources
        )
        deepening = self._deepen(evaluated, world=world)
        qualified = self._qualify_goal_lineage(
            deepening,
            goal_source_reference=goal.source_reference,
        )
        discrimination = self._discrimination.consume(qualified)
        requirements = discrimination.discrimination_requirements
        if len(requirements) != 1:
            return AuthorizedGoalProductiveInvestigationRoutingResult(
                status=AuthorizedGoalInvestigationRoutingStatus.REVIEW_REQUIRED,
                source_evaluations=evaluated,
                deepening=qualified,
                discrimination=discrimination,
                admission=None,
                source_reference=goal.source_reference,
                world_snapshot_id=world.snapshot_id,
                cap11_admission_invocation_count=0,
            )

        admission = self._g4_admission.admit(
            goal,
            requirements[0],
            originating_reasoning_id=reasoning_id,
        )
        return AuthorizedGoalProductiveInvestigationRoutingResult(
            status=AuthorizedGoalInvestigationRoutingStatus.ADMITTED,
            source_evaluations=evaluated,
            deepening=qualified,
            discrimination=discrimination,
            admission=admission,
            source_reference=goal.source_reference,
            world_snapshot_id=world.snapshot_id,
            cap11_admission_invocation_count=1,
        )

    @staticmethod
    def _deepen(
        evaluated: tuple[GovernedExplicitHypothesisSourceResult, ...],
        *,
        world: PersistentWorldSnapshot,
    ) -> GovernedHypothesisDeepeningReport:
        statuses = {item.status for item in evaluated}
        deepener = GovernedHypothesisDeepener()
        if statuses == {GovernedExplicitHypothesisSourceStatus.SCENARIO_ELIGIBLE}:
            hypotheses = tuple(item.scenario_hypotheses[0] for item in evaluated)
            report = GovernedScenarioSimulator().simulate(world, hypotheses)
            return deepener.deepen_scenarios_safely(report)
        if statuses == {GovernedExplicitHypothesisSourceStatus.CAUSAL_ELIGIBLE}:
            hypotheses = tuple(item.causal_hypotheses[0] for item in evaluated)
            report = GovernedCausalPredictiveReasoner().analyze(world, hypotheses)
            return deepener.deepen_causal_predictions_safely(report)
        raise ValueError("structured hypotheses are not jointly eligible")

    @staticmethod
    def _qualify_goal_lineage(
        report: GovernedHypothesisDeepeningReport,
        *,
        goal_source_reference: str,
    ) -> GovernedHypothesisDeepeningReport:
        reference = goal_source_reference.strip()
        if not reference:
            raise ValueError("goal source reference must not be blank")
        gaps = tuple(
            replace(gap, source_reference=reference)
            for gap in report.epistemic_gaps
        )
        fingerprint = sha256(
            repr(
                (
                    report.report_id,
                    report.source_reference,
                    reference,
                    report.world_snapshot_id,
                    tuple(item.hypothesis_id for item in report.assessments),
                    tuple(item.gap_id for item in gaps),
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedHypothesisDeepeningReport(
            report_id=f"hypothesis-deepening-{fingerprint[:16]}",
            status=report.status,
            source_kind=report.source_kind,
            source_reference=reference,
            world_snapshot_id=report.world_snapshot_id,
            assessments=report.assessments,
            epistemic_gaps=gaps,
            evidence_codes=tuple(
                dict.fromkeys(
                    (*report.evidence_codes, f"authorized_goal_source:{reference}")
                )
            ),
            risk_codes=report.risk_codes,
            source_fingerprint=fingerprint,
        )
