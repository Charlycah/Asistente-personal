
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.causal_prediction import (
    CausalHypothesis,
    GovernedCausalPredictionReport,
    GovernedCausalPredictiveReasoner,
)
from core.governed_reasoning.scenario_simulation import (
    GovernedScenarioSimulationReport,
    GovernedScenarioSimulator,
    ScenarioHypothesis,
)
from core.persistent_world_model import PersistentWorldSnapshot


class ExplicitHypothesisSourceKind(StrEnum):
    NONE = "none"
    SCENARIO = "scenario"
    CAUSAL = "causal"


class GovernedExplicitHypothesisSourceStatus(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    SCENARIO_ELIGIBLE = "scenario_eligible"
    CAUSAL_ELIGIBLE = "causal_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedExplicitHypothesisSource:
    """Explicit structured semantics eligible for governed hypothesis projection."""

    source_id: str
    kind: ExplicitHypothesisSourceKind | str
    proposition: str | None
    source_reference: str
    source_fingerprint: str
    world_domain: str | None = None
    fact_key: str | None = None
    assumed_value: str | None = None
    cause_domain: str | None = None
    cause_key: str | None = None
    cause_value: str | None = None
    effect_domain: str | None = None
    effect_key: str | None = None
    effect_value: str | None = None
    temporal_scope: str = "current"
    evidence_codes: tuple[str, ...] = ()
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    derivational: bool = True
    uses_llm: bool = False
    uses_retrieval: bool = False
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        kind = ExplicitHypothesisSourceKind(self.kind)
        if not self.source_id.startswith("explicit-hypothesis-source-"):
            raise ValueError("explicit hypothesis source identifier is invalid")
        if not self.source_reference.strip():
            raise ValueError("explicit hypothesis source reference is required")
        if (
            len(self.source_fingerprint) != 64
            or any(
                char not in "0123456789abcdef"
                for char in self.source_fingerprint.casefold()
            )
        ):
            raise ValueError(
                "explicit hypothesis source fingerprint must be SHA-256"
            )
        if not self.temporal_scope.strip():
            raise ValueError("explicit hypothesis temporal scope is required")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("explicit hypothesis source must preserve authority")
        if any(
            (
                not self.read_only,
                not self.derivational,
                self.uses_llm,
                self.uses_retrieval,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.modifies_world_model,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("explicit hypothesis source violates governed limits")
        object.__setattr__(self, "kind", kind)


@dataclass(frozen=True)
class GovernedExplicitHypothesisSourceResult:
    status: GovernedExplicitHypothesisSourceStatus | str
    source_id: str
    source_reference: str
    source_fingerprint_input: str
    world_snapshot_id: str
    scenario_hypotheses: tuple[ScenarioHypothesis, ...]
    causal_hypotheses: tuple[CausalHypothesis, ...]
    scenario_report: GovernedScenarioSimulationReport | None
    causal_report: GovernedCausalPredictionReport | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    derivational: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        status = GovernedExplicitHypothesisSourceStatus(self.status)
        if not self.world_snapshot_id.strip():
            raise ValueError("explicit hypothesis result requires world snapshot")
        if not self.rationale_codes:
            raise ValueError("explicit hypothesis result requires rationale")
        if len(self.source_fingerprint) != 64:
            raise ValueError("explicit hypothesis result requires SHA-256 lineage")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("explicit hypothesis result must preserve authority")
        if any(
            (
                not self.read_only,
                not self.derivational,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.modifies_world_model,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("explicit hypothesis result violates governed limits")
        if (
            status
            is GovernedExplicitHypothesisSourceStatus.SCENARIO_ELIGIBLE
        ):
            if not self.scenario_hypotheses or self.scenario_report is None:
                raise ValueError("scenario-eligible result requires scenario report")
            if self.causal_hypotheses or self.causal_report is not None:
                raise ValueError("scenario result cannot contain causal projection")
        if status is GovernedExplicitHypothesisSourceStatus.CAUSAL_ELIGIBLE:
            if not self.causal_hypotheses or self.causal_report is None:
                raise ValueError("causal-eligible result requires causal report")
            if self.scenario_hypotheses or self.scenario_report is not None:
                raise ValueError("causal result cannot contain scenario projection")
        if status in {
            GovernedExplicitHypothesisSourceStatus.NOT_APPLICABLE,
            GovernedExplicitHypothesisSourceStatus.REVIEW_REQUIRED,
        } and any(
            (
                self.scenario_hypotheses,
                self.causal_hypotheses,
                self.scenario_report is not None,
                self.causal_report is not None,
            )
        ):
            raise ValueError("non-eligible result cannot contain hypothesis output")
        object.__setattr__(self, "status", status)


class GovernedExplicitHypothesisSourceAdapterV1:
    """Project explicit structured semantics into existing reasoning foundations."""

    def evaluate(
        self,
        source: GovernedExplicitHypothesisSource,
        world: PersistentWorldSnapshot,
    ) -> GovernedExplicitHypothesisSourceResult:
        if source.kind is ExplicitHypothesisSourceKind.NONE:
            return self._empty(
                source,
                world,
                GovernedExplicitHypothesisSourceStatus.NOT_APPLICABLE,
                ("explicit_hypothesis:not_applicable",),
            )
        if source.kind is ExplicitHypothesisSourceKind.SCENARIO:
            return self._scenario(source, world)
        if source.kind is ExplicitHypothesisSourceKind.CAUSAL:
            return self._causal(source, world)
        raise ValueError("unsupported explicit hypothesis source kind")

    def from_decision_options(
        self,
        options: tuple[object, ...],
        *,
        world: PersistentWorldSnapshot,
        source_fingerprint: str,
    ) -> GovernedExplicitHypothesisSourceResult:
        del options
        source = GovernedExplicitHypothesisSource(
            source_id=(
                "explicit-hypothesis-source-decision-options-"
                f"{source_fingerprint[:16]}"
            ),
            kind=ExplicitHypothesisSourceKind.NONE,
            proposition=None,
            source_reference="governed_decision_options",
            source_fingerprint=source_fingerprint,
        )
        return self._empty(
            source,
            world,
            GovernedExplicitHypothesisSourceStatus.NOT_APPLICABLE,
            (
                "explicit_hypothesis:decision_option_identity_insufficient",
                "explicit_hypothesis:no_semantic_inference",
            ),
        )

    def _scenario(
        self,
        source: GovernedExplicitHypothesisSource,
        world: PersistentWorldSnapshot,
    ) -> GovernedExplicitHypothesisSourceResult:
        required = (
            source.proposition,
            source.world_domain,
            source.fact_key,
            source.assumed_value,
            source.temporal_scope,
        )
        if any(item is None or not str(item).strip() for item in required):
            return self._empty(
                source,
                world,
                GovernedExplicitHypothesisSourceStatus.REVIEW_REQUIRED,
                ("explicit_hypothesis:scenario_semantics_incomplete",),
            )
        hypothesis_id = self._hypothesis_id(source, "scenario")
        hypothesis = ScenarioHypothesis(
            hypothesis_id=hypothesis_id,
            proposition=str(source.proposition),
            world_domain=str(source.world_domain),
            fact_key=str(source.fact_key),
            assumed_value=str(source.assumed_value),
            temporal_scope=source.temporal_scope,
            evidence_codes=tuple(
                dict.fromkeys(
                    (
                        *source.evidence_codes,
                        f"source:{source.source_reference}",
                        f"source_fingerprint:{source.source_fingerprint}",
                    )
                )
            ),
        )
        report = GovernedScenarioSimulator().simulate_safely(
            world,
            (hypothesis,),
        )
        return self._result(
            source,
            world,
            GovernedExplicitHypothesisSourceStatus.SCENARIO_ELIGIBLE,
            scenario_hypotheses=(hypothesis,),
            scenario_report=report,
            rationale_codes=(
                "explicit_hypothesis:scenario_semantics_complete",
                "explicit_hypothesis:existing_scenario_simulator_reused",
            ),
        )

    def _causal(
        self,
        source: GovernedExplicitHypothesisSource,
        world: PersistentWorldSnapshot,
    ) -> GovernedExplicitHypothesisSourceResult:
        required = (
            source.proposition,
            source.cause_domain,
            source.cause_key,
            source.cause_value,
            source.effect_domain,
            source.effect_key,
            source.effect_value,
            source.temporal_scope,
        )
        if any(item is None or not str(item).strip() for item in required):
            return self._empty(
                source,
                world,
                GovernedExplicitHypothesisSourceStatus.REVIEW_REQUIRED,
                ("explicit_hypothesis:causal_semantics_incomplete",),
            )
        relation_id = self._hypothesis_id(source, "causal")
        hypothesis = CausalHypothesis(
            relation_id=relation_id,
            proposition=str(source.proposition),
            cause_domain=str(source.cause_domain),
            cause_key=str(source.cause_key),
            cause_value=str(source.cause_value),
            effect_domain=str(source.effect_domain),
            effect_key=str(source.effect_key),
            effect_value=str(source.effect_value),
            temporal_scope=source.temporal_scope,
            evidence_codes=tuple(
                dict.fromkeys(
                    (
                        *source.evidence_codes,
                        f"source:{source.source_reference}",
                        f"source_fingerprint:{source.source_fingerprint}",
                    )
                )
            ),
        )
        report = GovernedCausalPredictiveReasoner().analyze_safely(
            world,
            (hypothesis,),
        )
        return self._result(
            source,
            world,
            GovernedExplicitHypothesisSourceStatus.CAUSAL_ELIGIBLE,
            causal_hypotheses=(hypothesis,),
            causal_report=report,
            rationale_codes=(
                "explicit_hypothesis:causal_semantics_complete",
                "explicit_hypothesis:existing_causal_reasoner_reused",
                "explicit_hypothesis:causality_not_established",
            ),
        )

    @classmethod
    def _empty(
        cls,
        source: GovernedExplicitHypothesisSource,
        world: PersistentWorldSnapshot,
        status: GovernedExplicitHypothesisSourceStatus,
        rationale_codes: tuple[str, ...],
    ) -> GovernedExplicitHypothesisSourceResult:
        return cls._result(
            source,
            world,
            status,
            rationale_codes=rationale_codes,
        )

    @staticmethod
    def _result(
        source: GovernedExplicitHypothesisSource,
        world: PersistentWorldSnapshot,
        status: GovernedExplicitHypothesisSourceStatus,
        *,
        scenario_hypotheses: tuple[ScenarioHypothesis, ...] = (),
        causal_hypotheses: tuple[CausalHypothesis, ...] = (),
        scenario_report: GovernedScenarioSimulationReport | None = None,
        causal_report: GovernedCausalPredictionReport | None = None,
        rationale_codes: tuple[str, ...],
    ) -> GovernedExplicitHypothesisSourceResult:
        payload = repr(
            (
                source.source_fingerprint,
                source.source_reference,
                world.snapshot_id,
                world.source_fingerprint,
                status.value,
                tuple(item.hypothesis_id for item in scenario_hypotheses),
                tuple(item.relation_id for item in causal_hypotheses),
                (
                    scenario_report.source_fingerprint
                    if scenario_report is not None
                    else None
                ),
                (
                    causal_report.source_fingerprint
                    if causal_report is not None
                    else None
                ),
                rationale_codes,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return GovernedExplicitHypothesisSourceResult(
            status=status,
            source_id=source.source_id,
            source_reference=source.source_reference,
            source_fingerprint_input=source.source_fingerprint,
            world_snapshot_id=world.snapshot_id,
            scenario_hypotheses=scenario_hypotheses,
            causal_hypotheses=causal_hypotheses,
            scenario_report=scenario_report,
            causal_report=causal_report,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _hypothesis_id(
        source: GovernedExplicitHypothesisSource,
        kind: str,
    ) -> str:
        digest = sha256(
            repr(
                (
                    kind,
                    source.source_fingerprint,
                    source.source_reference,
                    source.proposition,
                    source.temporal_scope,
                )
            ).encode("utf-8")
        ).hexdigest()
        prefix = "scenario-hypothesis" if kind == "scenario" else "causal-relation"
        return f"{prefix}-{digest[:24]}"
