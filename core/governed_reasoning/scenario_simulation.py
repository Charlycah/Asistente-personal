from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.persistent_world_model import PersistentWorldSnapshot


class ScenarioSimulationStatus(StrEnum):
    COMPLETE = "complete"
    WORLD_CONFLICT_REVIEW_REQUIRED = "world_conflict_review_required"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


class ScenarioOutcomeKind(StrEnum):
    CONSISTENT = "consistent"
    CONTRADICTED = "contradicted"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class ScenarioHypothesis:
    hypothesis_id: str
    proposition: str
    world_domain: str
    fact_key: str
    assumed_value: str
    evidence_codes: tuple[str, ...] = ()
    epistemic_level: EpistemicLevel = EpistemicLevel.HYPOTHESIS
    temporal_scope: str = "current"

    def __post_init__(self) -> None:
        for value, label in (
            (self.hypothesis_id, "hypothesis id"),
            (self.proposition, "proposition"),
            (self.world_domain, "world domain"),
            (self.fact_key, "fact key"),
            (self.assumed_value, "assumed value"),
        ):
            if not value.strip():
                raise ValueError(f"scenario {label} must not be blank")
        if self.epistemic_level is not EpistemicLevel.HYPOTHESIS:
            raise ValueError("scenario inputs must remain hypotheses")
        if self.temporal_scope not in {"current", "future"}:
            raise ValueError("scenario temporal scope must be current or future")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("scenario evidence codes must not be blank")


@dataclass(frozen=True)
class ScenarioOutcome:
    hypothesis_id: str
    kind: ScenarioOutcomeKind
    matched_fact_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    epistemic_level: EpistemicLevel = EpistemicLevel.HYPOTHESIS

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip():
            raise ValueError("scenario outcome hypothesis id must not be blank")
        if any(not item.strip() for item in self.matched_fact_ids):
            raise ValueError("scenario fact references must not be blank")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("scenario outcome requires rationale codes")
        if self.epistemic_level is not EpistemicLevel.HYPOTHESIS:
            raise ValueError("scenario outcomes must remain hypotheses")


@dataclass(frozen=True)
class GovernedScenarioSimulationReport:
    simulation_id: str
    status: ScenarioSimulationStatus
    world_snapshot_id: str
    hypotheses: tuple[ScenarioHypothesis, ...]
    outcomes: tuple[ScenarioOutcome, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m391.3"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    creates_facts: bool = False
    persists_hypotheses: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    executes_actions: bool = False
    resolves_world_conflicts: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.simulation_id.startswith("scenario-simulation-"):
            raise ValueError("scenario simulation identifier is invalid")
        if not self.world_snapshot_id.strip():
            raise ValueError("scenario simulation world snapshot is required")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("scenario simulation must preserve reasoning authority")
        ids = tuple(item.hypothesis_id for item in self.hypotheses)
        if len(ids) != len(set(ids)):
            raise ValueError("scenario hypothesis identifiers must be unique")
        if tuple(item.hypothesis_id for item in self.outcomes) != ids:
            raise ValueError("scenario outcomes must preserve hypothesis ordering")
        if any(
            (
                not self.read_only,
                self.creates_facts,
                self.persists_hypotheses,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_planning,
                self.executes_actions,
                self.resolves_world_conflicts,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("scenario simulation violates governed limits")


class GovernedScenarioSimulator:
    """Pure consultative simulation under the governed reasoning authority."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def simulate(
        self,
        world: PersistentWorldSnapshot,
        hypotheses: tuple[ScenarioHypothesis, ...],
    ) -> GovernedScenarioSimulationReport:
        ordered = tuple(sorted(hypotheses, key=lambda item: item.hypothesis_id))
        outcomes = tuple(self._evaluate(world, item) for item in ordered)
        status = self._status(world, outcomes)
        evidence_codes = tuple(
            dict.fromkeys(
                (
                    f"world_snapshot:{world.snapshot_id}",
                    *world.evidence_codes,
                    *(
                        code
                        for hypothesis in ordered
                        for code in hypothesis.evidence_codes
                    ),
                    *(
                        code
                        for outcome in outcomes
                        for code in outcome.rationale_codes
                    ),
                )
            )
        )
        risk_codes = tuple(
            dict.fromkeys(
                (
                    *world.risk_codes,
                    *(
                        "scenario_unresolved"
                        for outcome in outcomes
                        if outcome.kind is ScenarioOutcomeKind.UNRESOLVED
                    ),
                    *(
                        "scenario_contradicted"
                        for outcome in outcomes
                        if outcome.kind is ScenarioOutcomeKind.CONTRADICTED
                    ),
                )
            )
        )
        fingerprint = self._fingerprint(world, ordered, outcomes)
        return GovernedScenarioSimulationReport(
            simulation_id=f"scenario-simulation-{fingerprint[:16]}",
            status=status,
            world_snapshot_id=world.snapshot_id,
            hypotheses=ordered,
            outcomes=outcomes,
            evidence_codes=evidence_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    def simulate_safely(
        self,
        world: PersistentWorldSnapshot,
        hypotheses: tuple[ScenarioHypothesis, ...],
    ) -> GovernedScenarioSimulationReport:
        try:
            return self.simulate(world, hypotheses)
        except Exception:
            fingerprint = sha256(world.snapshot_id.encode("utf-8")).hexdigest()
            return GovernedScenarioSimulationReport(
                simulation_id=f"scenario-simulation-{fingerprint[:16]}",
                status=ScenarioSimulationStatus.DEGRADED,
                world_snapshot_id=world.snapshot_id,
                hypotheses=(),
                outcomes=(),
                evidence_codes=(f"world_snapshot:{world.snapshot_id}",),
                risk_codes=("scenario_simulation_failure",),
                source_fingerprint=fingerprint,
            )

    @staticmethod
    def _evaluate(
        world: PersistentWorldSnapshot,
        hypothesis: ScenarioHypothesis,
    ) -> ScenarioOutcome:
        relevant = tuple(
            fact
            for fact in world.facts
            if fact.active
            and fact.domain.value == hypothesis.world_domain
            and fact.fact_key.casefold() == hypothesis.fact_key.casefold()
            and fact.epistemic_level is EpistemicLevel.FACT
        )
        matched = tuple(fact.fact_id for fact in relevant)
        if not relevant:
            return ScenarioOutcome(
                hypothesis_id=hypothesis.hypothesis_id,
                kind=ScenarioOutcomeKind.UNRESOLVED,
                matched_fact_ids=(),
                rationale_codes=("scenario:no_persistent_fact",),
            )
        values = {fact.value.strip().casefold() for fact in relevant}
        assumed = hypothesis.assumed_value.strip().casefold()
        if assumed in values and len(values) == 1:
            kind = ScenarioOutcomeKind.CONSISTENT
            rationale = ("scenario:consistent_with_persistent_fact",)
        elif assumed not in values and hypothesis.temporal_scope == "future":
            kind = ScenarioOutcomeKind.UNRESOLVED
            rationale = (
                "scenario:future_alternative_not_current_contradiction",
                "scenario:future_hypothesis_not_established_as_fact",
            )
        elif assumed not in values:
            kind = ScenarioOutcomeKind.CONTRADICTED
            rationale = ("scenario:contradicted_by_persistent_fact",)
        else:
            kind = ScenarioOutcomeKind.UNRESOLVED
            rationale = ("scenario:world_conflict_prevents_resolution",)
        return ScenarioOutcome(
            hypothesis_id=hypothesis.hypothesis_id,
            kind=kind,
            matched_fact_ids=matched,
            rationale_codes=rationale,
        )

    @staticmethod
    def _status(
        world: PersistentWorldSnapshot,
        outcomes: tuple[ScenarioOutcome, ...],
    ) -> ScenarioSimulationStatus:
        if world.conflict_keys:
            return ScenarioSimulationStatus.WORLD_CONFLICT_REVIEW_REQUIRED
        if not outcomes or all(
            item.kind is ScenarioOutcomeKind.UNRESOLVED for item in outcomes
        ):
            return ScenarioSimulationStatus.INSUFFICIENT_EVIDENCE
        return ScenarioSimulationStatus.COMPLETE

    @staticmethod
    def _fingerprint(
        world: PersistentWorldSnapshot,
        hypotheses: tuple[ScenarioHypothesis, ...],
        outcomes: tuple[ScenarioOutcome, ...],
    ) -> str:
        payload = "\n".join(
            (
                world.source_fingerprint,
                *(
                    "|".join(
                        (
                            item.hypothesis_id,
                            item.proposition,
                            item.world_domain,
                            item.fact_key,
                            item.assumed_value,
                            item.temporal_scope,
                            ",".join(item.evidence_codes),
                        )
                    )
                    for item in hypotheses
                ),
                *(
                    "|".join(
                        (
                            item.hypothesis_id,
                            item.kind.value,
                            ",".join(item.matched_fact_ids),
                            ",".join(item.rationale_codes),
                        )
                    )
                    for item in outcomes
                ),
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()
