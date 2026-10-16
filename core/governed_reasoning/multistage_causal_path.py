from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.causal_prediction import (
    CausalHypothesis,
    GovernedCausalPredictiveReasoner,
    PredictiveOutcomeKind,
)
from core.persistent_world_model import PersistentWorldSnapshot


class MultiStageCausalPathStatus(StrEnum):
    PATH_CANDIDATE = "path_candidate"
    INSUFFICIENT_STAGES = "insufficient_stages"
    BROKEN_CHAIN = "broken_chain"
    BASELINE_REVIEW_REQUIRED = "baseline_review_required"
    UPSTREAM_UNRESOLVED = "upstream_unresolved"


class MultiStageCausalStageStatus(StrEnum):
    BASELINE_SUPPORTED = "baseline_supported"
    CONDITIONALLY_PROPAGATED = "conditionally_propagated"
    UNRESOLVED = "unresolved"
    BLOCKED_BY_UPSTREAM = "blocked_by_upstream"
    CONTRADICTED = "contradicted"


@dataclass(frozen=True)
class GovernedMultiStageCausalStage:
    stage_index: int
    relation_id: str
    proposition: str
    cause_domain: str
    cause_key: str
    cause_value: str
    effect_domain: str
    effect_key: str
    effect_value: str
    status: MultiStageCausalStageStatus
    conditional_on_relation_id: str | None
    evidence_references: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    establishes_fact: bool = False
    establishes_causality: bool = False
    is_future_fact: bool = False

    def __post_init__(self) -> None:
        if self.stage_index < 1:
            raise ValueError("causal path stage index must be positive")
        if self.establishes_fact or self.establishes_causality or self.is_future_fact:
            raise ValueError("causal path stages cannot establish facts or causality")


@dataclass(frozen=True)
class GovernedMultiStageCausalPath:
    path_id: str
    owner: str
    session_id: str
    baseline_snapshot_id: str
    relation_ids: tuple[str, ...]
    stages: tuple[GovernedMultiStageCausalStage, ...]
    status: MultiStageCausalPathStatus
    initial_assumption: tuple[str, str, str]
    terminal_projection: tuple[str, str, str] | None
    rationale_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "cap-06-multistage-causal-path-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    creates_facts: bool = False
    proves_causality: bool = False
    calibrates_probability: bool = False
    persists_results: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    registers_rule: bool = False
    executes_transfer: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.path_id.startswith("multistage-causal-path-"):
            raise ValueError("multi-stage causal path identifier is invalid")
        if not self.owner.strip() or not self.session_id.strip():
            raise ValueError("multi-stage causal path requires owner/session lineage")
        if not self.baseline_snapshot_id.strip():
            raise ValueError("multi-stage causal path requires explicit baseline")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("multi-stage causal path must preserve authority")
        if (
            not self.read_only
            or not self.consultative
            or any(
                (
                    self.creates_facts,
                    self.proves_causality,
                    self.calibrates_probability,
                    self.persists_results,
                    self.modifies_world_model,
                    self.modifies_memory,
                    self.modifies_learning,
                    self.modifies_planning,
                    self.registers_rule,
                    self.executes_transfer,
                    self.executes_actions,
                    self.grants_authority,
                )
            )
        ):
            raise ValueError("multi-stage causal path violates governed limits")


class GovernedMultiStageCausalPathComposer:
    """Compose explicit causal hypotheses into one bounded conditional path."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def __init__(self) -> None:
        self._reasoner = GovernedCausalPredictiveReasoner()

    def compose(
        self,
        *,
        owner: str,
        session_id: str,
        baseline: PersistentWorldSnapshot,
        hypotheses: tuple[CausalHypothesis, ...],
    ) -> GovernedMultiStageCausalPath:
        ordered = tuple(hypotheses)
        if len(ordered) < 2:
            return self._result(
                owner,
                session_id,
                baseline,
                ordered,
                (),
                MultiStageCausalPathStatus.INSUFFICIENT_STAGES,
                ("causal_path:at_least_two_explicit_stages_required",),
            )
        if len({item.relation_id for item in ordered}) != len(ordered):
            raise ValueError("causal path relation identifiers must be unique")

        for left, right in zip(ordered, ordered[1:], strict=False):
            if self._effect_key(left) != self._cause_key(right):
                return self._result(
                    owner,
                    session_id,
                    baseline,
                    ordered,
                    (),
                    MultiStageCausalPathStatus.BROKEN_CHAIN,
                    (
                        "causal_path:stage_continuity_required",
                        f"causal_path:broken_after:{left.relation_id}",
                    ),
                )

        report = self._reasoner.analyze(baseline, (ordered[0],))
        first_assessment = report.assessments[0]
        first_prediction = report.predictions[0]
        if first_prediction.kind is PredictiveOutcomeKind.CURRENTLY_CONTRADICTED:
            first_status = MultiStageCausalStageStatus.CONTRADICTED
        elif first_prediction.kind is PredictiveOutcomeKind.CONDITIONALLY_EXPECTED:
            first_status = MultiStageCausalStageStatus.BASELINE_SUPPORTED
        else:
            first_status = MultiStageCausalStageStatus.UNRESOLVED

        stages = [
            self._stage(
                1,
                ordered[0],
                first_status,
                None,
                tuple(
                    dict.fromkeys(
                        (
                            *first_assessment.cause_fact_ids,
                            *first_assessment.effect_fact_ids,
                        )
                    )
                ),
                tuple(
                    dict.fromkeys(
                        (
                            *first_assessment.rationale_codes,
                            *first_prediction.rationale_codes,
                        )
                    )
                ),
            )
        ]

        can_propagate = first_status is MultiStageCausalStageStatus.BASELINE_SUPPORTED
        for index, hypothesis in enumerate(ordered[1:], start=2):
            previous = ordered[index - 2]
            status = (
                MultiStageCausalStageStatus.CONDITIONALLY_PROPAGATED
                if can_propagate
                else MultiStageCausalStageStatus.BLOCKED_BY_UPSTREAM
            )
            rationale = (
                (
                    "causal_path:conditional_on_prior_projection",
                    "causal_path:not_reasserted_as_world_fact",
                    "causal_path:causality_not_established",
                )
                if can_propagate
                else (
                    "causal_path:upstream_support_insufficient",
                    "causal_path:downstream_not_promoted",
                )
            )
            stages.append(
                self._stage(
                    index,
                    hypothesis,
                    status,
                    previous.relation_id,
                    (),
                    rationale,
                )
            )

        if first_status is MultiStageCausalStageStatus.CONTRADICTED:
            path_status = MultiStageCausalPathStatus.BASELINE_REVIEW_REQUIRED
        elif not can_propagate:
            path_status = MultiStageCausalPathStatus.UPSTREAM_UNRESOLVED
        else:
            path_status = MultiStageCausalPathStatus.PATH_CANDIDATE

        return self._result(
            owner,
            session_id,
            baseline,
            ordered,
            tuple(stages),
            path_status,
            (
                "causal_path:explicit_stage_composition",
                "causal_path:conditional_projection_only",
                "causal_path:world_baseline_unchanged",
            ),
        )

    @staticmethod
    def _effect_key(hypothesis: CausalHypothesis) -> tuple[str, str, str]:
        return (
            hypothesis.effect_domain.strip().casefold(),
            hypothesis.effect_key.strip().casefold(),
            hypothesis.effect_value.strip().casefold(),
        )

    @staticmethod
    def _cause_key(hypothesis: CausalHypothesis) -> tuple[str, str, str]:
        return (
            hypothesis.cause_domain.strip().casefold(),
            hypothesis.cause_key.strip().casefold(),
            hypothesis.cause_value.strip().casefold(),
        )

    @staticmethod
    def _stage(
        index: int,
        hypothesis: CausalHypothesis,
        status: MultiStageCausalStageStatus,
        conditional_on: str | None,
        evidence_references: tuple[str, ...],
        rationale_codes: tuple[str, ...],
    ) -> GovernedMultiStageCausalStage:
        return GovernedMultiStageCausalStage(
            stage_index=index,
            relation_id=hypothesis.relation_id,
            proposition=hypothesis.proposition,
            cause_domain=hypothesis.cause_domain,
            cause_key=hypothesis.cause_key,
            cause_value=hypothesis.cause_value,
            effect_domain=hypothesis.effect_domain,
            effect_key=hypothesis.effect_key,
            effect_value=hypothesis.effect_value,
            status=status,
            conditional_on_relation_id=conditional_on,
            evidence_references=evidence_references,
            rationale_codes=rationale_codes,
        )

    @classmethod
    def _result(
        cls,
        owner: str,
        session_id: str,
        baseline: PersistentWorldSnapshot,
        hypotheses: tuple[CausalHypothesis, ...],
        stages: tuple[GovernedMultiStageCausalStage, ...],
        status: MultiStageCausalPathStatus,
        rationale_codes: tuple[str, ...],
    ) -> GovernedMultiStageCausalPath:
        relation_ids = tuple(item.relation_id for item in hypotheses)
        initial = (
            (
                hypotheses[0].cause_domain,
                hypotheses[0].cause_key,
                hypotheses[0].cause_value,
            )
            if hypotheses
            else ("unknown", "unknown", "unknown")
        )
        terminal = (
            (
                hypotheses[-1].effect_domain,
                hypotheses[-1].effect_key,
                hypotheses[-1].effect_value,
            )
            if stages and status is MultiStageCausalPathStatus.PATH_CANDIDATE
            else None
        )
        fingerprint = sha256(
            repr(
                (
                    owner.casefold(),
                    session_id,
                    baseline.snapshot_id,
                    relation_ids,
                    tuple(
                        (
                            item.status.value,
                            item.conditional_on_relation_id,
                            item.evidence_references,
                        )
                        for item in stages
                    ),
                    status.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedMultiStageCausalPath(
            path_id=f"multistage-causal-path-{fingerprint[:24]}",
            owner=owner,
            session_id=session_id,
            baseline_snapshot_id=baseline.snapshot_id,
            relation_ids=relation_ids,
            stages=stages,
            status=status,
            initial_assumption=initial,
            terminal_projection=terminal,
            rationale_codes=rationale_codes,
            risk_codes=(
                "causal_path_does_not_prove_causality",
                "conditional_projection_not_world_fact",
                "no_probability_calibration",
            ),
            source_fingerprint=fingerprint,
        )
