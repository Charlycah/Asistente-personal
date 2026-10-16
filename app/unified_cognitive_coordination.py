from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from core.capability_registry import CapabilityRisk
from core.cognitive_maturity import PlanningDecisionEvidenceAdapter
from core.cognitive_planning import CognitivePlanner, ToolRequirement
from core.cognitive_planning.models import CognitiveNeed
from core.cognitive_runtime_orchestration import (
    CognitiveStrategyApplicationEvidence,
    CognitiveStrategyApplicationOutcomeStatus,
    CognitiveStrategyApplicationStatus,
    GovernedCognitiveStrategyApplication,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.governed_reasoning.epistemic_sufficiency import EpistemicSufficiencyStatus
from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeObservation,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityStatus,
)


@dataclass(frozen=True)
class CognitiveCompositionAdvice:
    """Read-only composition evidence owned by the Decision authority."""

    owner: str
    scope: str
    needs: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    provenance: tuple[str, ...]
    execution_authorized: bool = False

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        scope = self.scope.strip()
        provenance = tuple(item.strip() for item in self.provenance if item.strip())
        if not owner:
            raise ValueError("composition advice owner must not be blank")
        if not scope:
            raise ValueError("composition advice scope must not be blank")
        if not provenance:
            raise ValueError("composition advice provenance must not be empty")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "provenance", provenance)




class CognitiveStrategyStatus(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class CognitiveStrategyStep:
    """One advisory cognitive step; never an execution directive."""

    sequence: int
    capability: str
    depends_on: tuple[str, ...]
    rationale_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise ValueError("strategy step sequence must be positive")
        if not self.capability.strip():
            raise ValueError("strategy step capability must not be blank")
        if not self.rationale_codes:
            raise ValueError("strategy step requires rationale")
        if self.capability in self.depends_on:
            raise ValueError("strategy step cannot depend on itself")


@dataclass(frozen=True)
class CognitiveStrategyCandidate:
    """Read-only strategy proposed by the existing Decision authority."""

    owner: str
    scope: str
    status: CognitiveStrategyStatus | str
    capabilities: tuple[str, ...]
    steps: tuple[CognitiveStrategyStep, ...]
    missing_capabilities: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    provenance: tuple[str, ...]
    source_fingerprint: str
    structural_fingerprint: str = ""
    advisory_only: bool = True
    execution_authorized: bool = False
    persists: bool = False
    learns: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        status = CognitiveStrategyStatus(self.status)
        if not self.owner.strip() or not self.scope.strip():
            raise ValueError("strategy owner and scope must not be blank")
        if len(self.capabilities) != len(set(self.capabilities)):
            raise ValueError("strategy capabilities must be unique")
        if len(self.missing_capabilities) != len(set(self.missing_capabilities)):
            raise ValueError("strategy missing capabilities must be unique")
        if not self.rationale_codes or not self.provenance:
            raise ValueError("strategy requires rationale and provenance")
        if not self.source_fingerprint.strip():
            raise ValueError("strategy requires source fingerprint")
        structural = self._expected_structural_fingerprint()
        if self.structural_fingerprint and self.structural_fingerprint != structural:
            raise ValueError("strategy structural fingerprint is inconsistent")
        object.__setattr__(self, "structural_fingerprint", structural)
        if any(
            (
                not self.advisory_only,
                self.execution_authorized,
                self.persists,
                self.learns,
                self.grants_authority,
            )
        ):
            raise ValueError("strategy candidate violates advisory-only boundary")
        if status is CognitiveStrategyStatus.READY:
            if len(self.capabilities) < 2 or not self.steps:
                raise ValueError("ready strategy requires multiple cognitive steps")
            if self.missing_capabilities:
                raise ValueError("ready strategy cannot have missing capabilities")
        elif self.steps:
            raise ValueError("blocked strategy cannot expose executable-like steps")


    def _expected_structural_fingerprint(self) -> str:
        payload = repr(
            (
                "hce-cognitive-strategy-structure-v1",
                tuple(self.capabilities),
                tuple(
                    (
                        step.sequence,
                        step.capability,
                        tuple(step.depends_on),
                    )
                    for step in self.steps
                ),
                "decision" in self.capabilities,
                tuple(
                    capability
                    for capability in self.capabilities
                    if capability
                    in {"memory", "weather", "calendar", "current_affairs"}
                ),
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()



def project_strategy_application(
    strategy: CognitiveStrategyCandidate,
) -> GovernedCognitiveStrategyApplication:
    """Project one advisory strategy onto the bounded cognitive runtime surface."""
    capability_to_stage = {
        "reasoning": "reasoning",
        "planning": "planning",
        "reflection": "reflection",
        "coordination": "executive",
    }
    evidence_capabilities = {"memory", "weather", "calendar", "current_affairs"}
    if CognitiveStrategyStatus(strategy.status) is CognitiveStrategyStatus.BLOCKED:
        requested_stages: tuple[str, ...] = ()
        status = CognitiveStrategyApplicationStatus.BLOCKED
    else:
        requested_stages = tuple(
            capability_to_stage[step.capability]
            for step in strategy.steps
            if step.capability in capability_to_stage
        )
        status = CognitiveStrategyApplicationStatus.READY
    evidence_requirements = tuple(
        step.capability
        for step in strategy.steps
        if step.capability in evidence_capabilities
    )
    payload = repr(
        (
            strategy.source_fingerprint,
            strategy.owner,
            strategy.scope,
            status.value,
            requested_stages,
            evidence_requirements,
            "decision" in strategy.capabilities,
            strategy.capabilities,
            strategy.provenance,
        )
    )
    return GovernedCognitiveStrategyApplication(
        strategy_fingerprint=strategy.source_fingerprint,
        owner=strategy.owner,
        scope=strategy.scope,
        status=status,
        requested_stage_sequence=requested_stages,
        evidence_requirements=evidence_requirements,
        decision_required="decision" in strategy.capabilities,
        requested_capabilities=strategy.capabilities,
        provenance=strategy.provenance,
        source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
    )


@dataclass(frozen=True)
class CognitiveCoordinationSnapshot:
    evaluations: int
    coordinated_turns: int
    executed_capabilities: tuple[str, ...]
    deduplicated_requests: int
    conflicts_resolved: int


class UnifiedCognitiveCoordinator:
    """Coordinates safe capabilities and fuses their results."""

    _SCENARIOS = {
        "outing": (
            "clima para manana",
            "dame el resumen del dia",
            "que recordatorios tengo",
        ),
        "travel": (
            "pronostico extendido",
            "que objetivos ejecutivos tengo",
            "que proyectos tenemos",
            "que recordatorios tengo",
        ),
        "day": (
            "dame el resumen del dia",
            "como esta el clima",
            "que recordatorios tengo",
        ),
    }

    def __init__(self, registry) -> None:
        self.registry = registry
        self._evaluations = 0
        self._coordinated_turns = 0
        self._executed_capabilities: tuple[str, ...] = ()
        self._deduplicated_requests = 0
        self._conflicts_resolved = 0
        self._productive_strategy_instances: dict[
            str, CognitiveStrategyCandidate
        ] = {}
        self._productive_strategy_outcomes: list[
            GovernedStrategyOutcomeObservation
        ] = []

    @property
    def snapshot(self) -> CognitiveCoordinationSnapshot:
        return CognitiveCoordinationSnapshot(
            evaluations=self._evaluations,
            coordinated_turns=self._coordinated_turns,
            executed_capabilities=self._executed_capabilities,
            deduplicated_requests=self._deduplicated_requests,
            conflicts_resolved=self._conflicts_resolved,
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        self._evaluations += 1
        scenario = self._detect_scenario(request.text)
        self._executed_capabilities = ()
        if scenario is None:
            return None

        executions: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for text in self._SCENARIOS[scenario]:
            execution = self._execute(request, text, now)
            if execution is None:
                continue
            key = (execution[0], text.casefold())
            if key in seen:
                self._deduplicated_requests += 1
                continue
            seen.add(key)
            executions.append(execution)

        if not executions:
            PlanningDecisionEvidenceAdapter().observe_unified_decision(
                scenario_detected=True,
                safe_result_selected=False,
            )
            return None

        executions = self._resolve_conflicts(executions)
        self._coordinated_turns += 1
        self._executed_capabilities = tuple(name for name, _ in executions)
        PlanningDecisionEvidenceAdapter().observe_unified_decision(
            scenario_detected=True,
            safe_result_selected=True,
        )
        return GovernedOperationalInterception(
            response_text=self._fuse(scenario, executions),
            rationale="unified_cognitive_coordination_completed",
        )

    def compose_advisory(
        self,
        request: GovernedConversationPipelineRequest,
    ) -> CognitiveCompositionAdvice | None:
        """Describe a novel composition without executing registered capabilities."""
        planner = CognitivePlanner()
        plan = planner.plan(request.text)
        cognitive_needs = planner.assess_cognitive_needs(request.text)

        mapped_tools = {
            ToolRequirement.MEMORY: "memory",
            ToolRequirement.WEATHER: "weather",
            ToolRequirement.CALENDAR: "calendar",
            ToolRequirement.CURRENT_AFFAIRS: "current_affairs",
        }
        needs = [
            mapped_tools[item] for item in plan.required_tools if item in mapped_tools
        ]
        if CognitiveNeed.DECISION in cognitive_needs:
            needs.append("decision")
        elif CognitiveNeed.REASONING in cognitive_needs:
            needs.append("reasoning")
        if CognitiveNeed.PLANNING in cognitive_needs:
            needs.append("planning")
        if CognitiveNeed.REFLECTION in cognitive_needs:
            needs.append("reflection")
        if CognitiveNeed.COORDINATION in cognitive_needs:
            needs.append("coordination")

        unique_needs = tuple(dict.fromkeys(needs))
        if len(unique_needs) < 2:
            return None
        return CognitiveCompositionAdvice(
            owner=request.owner,
            scope=request.session_id,
            needs=unique_needs,
            rationale_codes=(
                "existing_planning_needs_composed",
                "advisory_only_no_execution",
            ),
            provenance=(
                "cognitive_planning:required_tools",
                "cognitive_planning:cognitive_needs",
                "decision:unified_cognitive_coordination",
            ),
        )

    def prepare_productive_strategy_application(
        self,
        request: GovernedConversationPipelineRequest,
    ) -> GovernedCognitiveStrategyApplication | None:
        """Project one ordinary-turn strategy using only certified transient history."""
        historical = tuple(
            item
            for item in self._productive_strategy_instances.values()
            if item.scope == request.session_id
            and item.owner.casefold() == request.owner.casefold()
        )
        observations = tuple(
            item
            for item in self._productive_strategy_outcomes
            if item.evaluation_scope == request.session_id
            and item.owner.casefold() == request.owner.casefold()
        )
        advisory = None
        candidate_ids = tuple(item.source_fingerprint for item in historical)
        if observations and candidate_ids:
            derived = GovernedStrategyMetacognitiveAdaptationV1().advise(
                observations,
                evaluation_scope=request.session_id,
                candidate_strategy_fingerprints=candidate_ids,
            )
            if (
                derived.status
                is StrategyMetacognitiveAdaptationStatus.ADAPTATION_SUGGESTED
            ):
                advisory = derived
        baseline = self.synthesize_strategy_advisory(request)
        if baseline is None:
            return None
        strategy = baseline
        if advisory is not None:
            result = self.synthesize_strategy_with_metacognitive_influence(
                request,
                advisory=advisory,
                historical_strategies=historical,
            )
            strategy = result.strategy
        self._productive_strategy_instances[strategy.source_fingerprint] = strategy
        return project_strategy_application(strategy)

    def close_productive_strategy_outcome(
        self,
        application: CognitiveStrategyApplicationEvidence,
        outcome: GovernedReasoningMethodOutcomeObservation,
        *,
        evaluation_scope: str,
    ) -> GovernedStrategyOutcomeObservation:
        """Construct and admit one exact certified productive strategy outcome."""
        observation = GovernedStrategyOutcomeObservation.from_artifacts(
            application,
            outcome,
            evaluation_scope=evaluation_scope,
        )
        self.observe_productive_strategy_outcome(observation)
        return observation

    def observe_productive_strategy_outcome(
        self,
        observation: GovernedStrategyOutcomeObservation,
    ) -> None:
        """Accept only already-certified outcome evidence for transient future use."""
        if observation.strategy_fingerprint not in self._productive_strategy_instances:
            raise ValueError(
                "productive strategy outcome requires a known strategy instance"
            )
        if any(
            item.observation_id == observation.observation_id
            for item in self._productive_strategy_outcomes
        ):
            return
        self._productive_strategy_outcomes.append(observation)

    def synthesize_strategy_advisory(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        available_capabilities: tuple[str, ...] | None = None,
    ) -> CognitiveStrategyCandidate | None:
        """Synthesize an ordered advisory strategy from existing planner evidence."""
        planner = CognitivePlanner()
        plan = planner.plan(request.text)
        cognitive_needs = planner.assess_cognitive_needs(request.text)

        mapped_tools = {
            ToolRequirement.MEMORY: "memory",
            ToolRequirement.WEATHER: "weather",
            ToolRequirement.CALENDAR: "calendar",
            ToolRequirement.CURRENT_AFFAIRS: "current_affairs",
        }
        selected: list[str] = [
            mapped_tools[item] for item in plan.required_tools if item in mapped_tools
        ]
        need_mapping = (
            (CognitiveNeed.REASONING, "reasoning"),
            (CognitiveNeed.PLANNING, "planning"),
            (CognitiveNeed.DECISION, "decision"),
            (CognitiveNeed.REFLECTION, "reflection"),
            (CognitiveNeed.COORDINATION, "coordination"),
        )
        selected.extend(
            capability for need, capability in need_mapping if need in cognitive_needs
        )
        capabilities = tuple(dict.fromkeys(selected))
        if len(capabilities) < 2:
            return None

        available = (
            frozenset(capabilities)
            if available_capabilities is None
            else frozenset(available_capabilities)
        )
        missing = tuple(
            capability for capability in capabilities if capability not in available
        )
        provenance = (
            "cognitive_planning:required_tools",
            "cognitive_planning:cognitive_needs",
            "decision:unified_cognitive_coordination",
        )
        if missing:
            rationale = (
                "strategy:existing_capability_missing",
                "strategy:fail_closed_no_partial_execution_plan",
                "strategy:advisory_only",
            )
            return self._strategy_candidate(
                request=request,
                status=CognitiveStrategyStatus.BLOCKED,
                capabilities=capabilities,
                steps=(),
                missing_capabilities=missing,
                rationale_codes=rationale,
                provenance=provenance,
            )

        evidence_capabilities = tuple(
            capability
            for capability in capabilities
            if capability in {"memory", "weather", "calendar", "current_affairs"}
        )
        steps: list[CognitiveStrategyStep] = []
        completed: list[str] = []
        for sequence, capability in enumerate(capabilities, start=1):
            if capability in evidence_capabilities:
                dependencies: tuple[str, ...] = ()
                rationale = ("strategy:acquire_relevant_evidence",)
            elif capability == "reasoning":
                dependencies = evidence_capabilities
                rationale = ("strategy:reason_over_available_evidence",)
            elif capability == "planning":
                dependencies = tuple(
                    item
                    for item in (*evidence_capabilities, "reasoning")
                    if item in completed
                )
                rationale = ("strategy:structure_course_after_prerequisites",)
            elif capability == "decision":
                dependencies = tuple(
                    item
                    for item in (*evidence_capabilities, "reasoning")
                    if item in completed
                )
                rationale = ("strategy:decide_after_relevant_analysis",)
            elif capability == "reflection":
                dependencies = tuple(
                    item
                    for item in completed
                    if item in {"reasoning", "planning", "decision"}
                )
                rationale = ("strategy:review_prior_cognitive_output",)
            else:
                dependencies = tuple(completed)
                rationale = ("strategy:coordinate_prior_cognitive_steps",)
            steps.append(
                CognitiveStrategyStep(
                    sequence=sequence,
                    capability=capability,
                    depends_on=dependencies,
                    rationale_codes=rationale,
                )
            )
            completed.append(capability)

        return self._strategy_candidate(
            request=request,
            status=CognitiveStrategyStatus.READY,
            capabilities=capabilities,
            steps=tuple(steps),
            missing_capabilities=(),
            rationale_codes=(
                "strategy:derived_from_existing_planning_evidence",
                "strategy:ordered_by_cognitive_dependencies",
                "strategy:advisory_only",
            ),
            provenance=provenance,
        )


    def synthesize_eligible_strategy_advisories(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        available_capabilities: tuple[str, ...] | None = None,
    ) -> tuple[CognitiveStrategyCandidate, ...]:
        """Return bounded topological variants of current planner-derived needs."""
        base = self.synthesize_strategy_advisory(
            request,
            available_capabilities=available_capabilities,
        )
        if (
            base is None
            or CognitiveStrategyStatus(base.status) is CognitiveStrategyStatus.BLOCKED
        ):
            return (() if base is None else (base,))
        orderings = self._bounded_topological_orders(base.steps)
        variants = tuple(
            self._strategy_candidate_from_order(
                request=request,
                template=base,
                capability_order=order,
            )
            for order in orderings
        )
        return variants

    def synthesize_strategy_with_metacognitive_influence(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        advisory: GovernedStrategyMetacognitiveAdaptation | None,
        historical_strategies: tuple[CognitiveStrategyCandidate, ...],
        available_capabilities: tuple[str, ...] | None = None,
    ) -> GovernedFutureStrategySynthesisResult:
        """Prefer one currently eligible structure from compatible observed history."""
        eligible = self.synthesize_eligible_strategy_advisories(
            request,
            available_capabilities=available_capabilities,
        )
        if not eligible:
            raise ValueError("future strategy influence requires an eligible strategy")
        baseline = eligible[0]
        influence = self._derive_future_strategy_influence(
            request=request,
            advisory=advisory,
            historical_strategies=historical_strategies,
            eligible=eligible,
        )
        if influence.status is not GovernedFutureStrategyInfluenceStatus.PREFER:
            return GovernedFutureStrategySynthesisResult(
                strategy=baseline,
                influence=influence,
            )
        selected = next(
            item
            for item in eligible
            if item.structural_fingerprint
            == influence.selected_structural_fingerprint
        )
        influenced = self._strategy_candidate_from_order(
            request=request,
            template=selected,
            capability_order=tuple(step.capability for step in selected.steps),
            extra_rationale=(
                "metacognitive_influence:bounded_preference_applied",
            ),
            extra_provenance=(
                f"metacognitive_advisory:{influence.advisory_fingerprint}",
                f"metacognitive_influence:{influence.source_fingerprint}",
            ),
        )
        return GovernedFutureStrategySynthesisResult(
            strategy=influenced,
            influence=influence,
        )

    @staticmethod
    def _bounded_topological_orders(
        steps: tuple[CognitiveStrategyStep, ...],
        *,
        limit: int = 16,
    ) -> tuple[tuple[str, ...], ...]:
        dependencies = {
            step.capability: frozenset(step.depends_on)
            for step in steps
        }
        original = tuple(step.capability for step in steps)
        results: list[tuple[str, ...]] = []

        def visit(prefix: tuple[str, ...], remaining: frozenset[str]) -> None:
            if len(results) >= limit:
                return
            if not remaining:
                results.append(prefix)
                return
            ready = tuple(
                capability
                for capability in original
                if capability in remaining
                and dependencies[capability].issubset(prefix)
            )
            for capability in ready:
                visit(prefix + (capability,), remaining - {capability})

        visit((), frozenset(original))
        return tuple(results) or (original,)

    @classmethod
    def _strategy_candidate_from_order(
        cls,
        *,
        request: GovernedConversationPipelineRequest,
        template: CognitiveStrategyCandidate,
        capability_order: tuple[str, ...],
        extra_rationale: tuple[str, ...] = (),
        extra_provenance: tuple[str, ...] = (),
    ) -> CognitiveStrategyCandidate:
        if set(capability_order) != set(template.capabilities):
            raise ValueError(
                "strategy order must preserve planner-derived capabilities"
            )
        by_capability = {step.capability: step for step in template.steps}
        completed: list[str] = []
        rebuilt: list[CognitiveStrategyStep] = []
        for sequence, capability in enumerate(capability_order, start=1):
            original = by_capability[capability]
            if not set(original.depends_on).issubset(completed):
                raise ValueError("strategy order violates cognitive dependencies")
            rebuilt.append(
                CognitiveStrategyStep(
                    sequence=sequence,
                    capability=capability,
                    depends_on=original.depends_on,
                    rationale_codes=original.rationale_codes,
                )
            )
            completed.append(capability)
        return cls._strategy_candidate(
            request=request,
            status=CognitiveStrategyStatus(template.status),
            capabilities=capability_order,
            steps=tuple(rebuilt),
            missing_capabilities=template.missing_capabilities,
            rationale_codes=tuple(
                dict.fromkeys((*template.rationale_codes, *extra_rationale))
            ),
            provenance=tuple(
                dict.fromkeys((*template.provenance, *extra_provenance))
            ),
        )

    @staticmethod
    def _derive_future_strategy_influence(
        *,
        request: GovernedConversationPipelineRequest,
        advisory: GovernedStrategyMetacognitiveAdaptation | None,
        historical_strategies: tuple[CognitiveStrategyCandidate, ...],
        eligible: tuple[CognitiveStrategyCandidate, ...],
    ) -> GovernedFutureStrategyInfluence:
        eligible_ids = tuple(item.structural_fingerprint for item in eligible)
        status = GovernedFutureStrategyInfluenceStatus.NO_INFLUENCE
        recommended_structural: str | None = None
        selected_structural: str | None = None
        rationale = ["future_strategy_influence:no_applicable_preference"]
        advisory_id: str | None = None
        advisory_fingerprint: str | None = None

        if advisory is not None:
            advisory_id = advisory.advisory_id
            advisory_fingerprint = advisory.source_fingerprint
            if advisory.evaluation_scope != request.session_id:
                rationale = ["future_strategy_influence:scope_mismatch"]
            elif (
                advisory.status
                is StrategyMetacognitiveAdaptationStatus.ADAPTATION_SUGGESTED
                and advisory.recommended_strategy_fingerprint is not None
            ):
                historical = next(
                    (
                        item
                        for item in historical_strategies
                        if item.source_fingerprint
                        == advisory.recommended_strategy_fingerprint
                    ),
                    None,
                )
                if historical is None:
                    rationale = [
                        "future_strategy_influence:historical_instance_unavailable"
                    ]
                else:
                    recommended_structural = historical.structural_fingerprint
                    if recommended_structural in eligible_ids:
                        status = GovernedFutureStrategyInfluenceStatus.PREFER
                        selected_structural = recommended_structural
                        rationale = [
                            "future_strategy_influence:compatible_structure_preferred"
                        ]
                    else:
                        rationale = [
                            "future_strategy_influence:"
                            "recommended_structure_not_eligible"
                        ]
            elif (
                advisory.status
                is StrategyMetacognitiveAdaptationStatus.REVIEW_REQUIRED
            ):
                status = GovernedFutureStrategyInfluenceStatus.REVIEW_REQUIRED
                rationale = ["future_strategy_influence:review_required"]
            elif advisory.status is StrategyMetacognitiveAdaptationStatus.AMBIGUOUS:
                status = GovernedFutureStrategyInfluenceStatus.AMBIGUOUS
                rationale = ["future_strategy_influence:ambiguous_history"]

        source = sha256(
            repr(
                (
                    request.owner,
                    request.session_id,
                    eligible_ids,
                    advisory_id,
                    advisory_fingerprint,
                    recommended_structural,
                    selected_structural,
                    status.value,
                    tuple(rationale),
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedFutureStrategyInfluence(
            status=status,
            evaluation_scope=request.session_id,
            advisory_id=advisory_id,
            advisory_fingerprint=advisory_fingerprint,
            eligible_structural_fingerprints=eligible_ids,
            recommended_structural_fingerprint=recommended_structural,
            selected_structural_fingerprint=selected_structural,
            rationale_codes=tuple(rationale),
            source_fingerprint=source,
        )

    @staticmethod
    def _strategy_candidate(
        *,
        request: GovernedConversationPipelineRequest,
        status: CognitiveStrategyStatus,
        capabilities: tuple[str, ...],
        steps: tuple[CognitiveStrategyStep, ...],
        missing_capabilities: tuple[str, ...],
        rationale_codes: tuple[str, ...],
        provenance: tuple[str, ...],
    ) -> CognitiveStrategyCandidate:
        payload = repr(
            (
                request.owner,
                request.session_id,
                request.text.strip(),
                status.value,
                capabilities,
                tuple(
                    (
                        step.sequence,
                        step.capability,
                        step.depends_on,
                        step.rationale_codes,
                    )
                    for step in steps
                ),
                missing_capabilities,
                rationale_codes,
                provenance,
            )
        )
        return CognitiveStrategyCandidate(
            owner=request.owner,
            scope=request.session_id,
            status=status,
            capabilities=capabilities,
            steps=steps,
            missing_capabilities=missing_capabilities,
            rationale_codes=rationale_codes,
            provenance=provenance,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )

    @staticmethod
    def _detect_scenario(text: str) -> str | None:
        normalized = text.strip().casefold()
        outing_triggers = ("organiza la salida", "organizame la salida")
        if any(item in normalized for item in outing_triggers):
            return "outing"
        travel_triggers = ("prepara el viaje", "organizame el viaje")
        if any(item in normalized for item in travel_triggers):
            return "travel"
        if any(item in normalized for item in ("organiza mi dia", "organizame el dia")):
            return "day"
        return None

    def _execute(self, original, text: str, now: datetime):
        request = GovernedConversationPipelineRequest(
            owner=original.owner,
            session_id=original.session_id,
            text=text,
        )
        for registration in self.registry.registrations:
            descriptor = registration.descriptor
            if not descriptor.enabled or not self._safe(descriptor):
                continue
            result = self.registry.execute_registration(
                registration, request, now=now, origin="coordinator"
            )
            if result is not None:
                return descriptor.name, result.response_text
        return None

    @staticmethod
    def _safe(descriptor) -> bool:
        if descriptor.requires_confirmation:
            return False
        return descriptor.normalized_risk in {
            CapabilityRisk.LOW,
            CapabilityRisk.MEDIUM,
        }

    def _resolve_conflicts(
        self,
        executions: list[tuple[str, str]],
    ) -> list[tuple[str, str]]:
        resolved: list[tuple[str, str]] = []
        seen_names: set[str] = set()
        for item in executions:
            if item[0] in seen_names:
                self._conflicts_resolved += 1
                continue
            seen_names.add(item[0])
            resolved.append(item)
        return resolved

    @staticmethod
    def _fuse(scenario: str, executions: list[tuple[str, str]]) -> str:
        titles = {
            "outing": "Plan coordinado para la salida:",
            "travel": "Preparacion coordinada del viaje:",
            "day": "Coordinacion del dia:",
        }
        sections = [titles[scenario]]
        sections.extend(response for _, response in executions)
        return "\n\n".join(sections)


class StrategyOutcomePatternStatus(StrEnum):
    SUPPORTIVE = "supportive"
    LIMITING = "limiting"
    REVIEW_REQUIRED = "review_required"


class StrategyMetacognitiveAdaptationStatus(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    ADAPTATION_SUGGESTED = "adaptation_suggested"
    AMBIGUOUS = "ambiguous"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedStrategyOutcomeObservation:
    observation_id: str
    strategy_fingerprint: str
    application_fingerprint: str
    owner: str
    evaluation_scope: str
    reasoning_method_fingerprint: str
    reasoning_outcome_observation_id: str
    quality_status: GovernedReasoningQualityStatus
    sufficiency_status: EpistemicSufficiencyStatus
    source_reference: str
    world_snapshot_id: str
    pattern_status: StrategyOutcomePatternStatus
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    canonical_authority: str = "unified_cognitive_coordination"
    read_only: bool = True
    consultative: bool = True
    establishes_causality: bool = False
    establishes_strategy_superiority: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    modifies_planner: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.observation_id.startswith("strategy-outcome-observation-"):
            raise ValueError("strategy outcome observation identifier is invalid")
        if not all(
            item.strip()
            for item in (
                self.strategy_fingerprint,
                self.application_fingerprint,
                self.owner,
                self.evaluation_scope,
                self.reasoning_method_fingerprint,
                self.reasoning_outcome_observation_id,
                self.source_reference,
                self.world_snapshot_id,
                self.source_fingerprint,
            )
        ):
            raise ValueError("strategy outcome observation requires complete lineage")
        if not self.rationale_codes:
            raise ValueError("strategy outcome observation requires rationale")
        if self.canonical_authority != "unified_cognitive_coordination":
            raise ValueError("strategy outcome observation must preserve authority")
        if not self.read_only or not self.consultative:
            raise ValueError("strategy outcome observation must remain consultative")
        if any(
            (
                self.establishes_causality,
                self.establishes_strategy_superiority,
                self.persists_results,
                self.creates_memory,
                self.creates_learning,
                self.modifies_planner,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("strategy outcome observation violates governed limits")

    @classmethod
    def from_artifacts(
        cls,
        application: CognitiveStrategyApplicationEvidence,
        outcome: GovernedReasoningMethodOutcomeObservation,
        *,
        evaluation_scope: str,
    ) -> GovernedStrategyOutcomeObservation:
        scope = evaluation_scope.strip()
        if application.status is not CognitiveStrategyApplicationOutcomeStatus.APPLIED:
            raise ValueError("strategy outcome requires a fully applied strategy")
        if application.scope != scope:
            raise ValueError("strategy outcome evaluation scope mismatch")
        if "reasoning" not in application.applied_stage_sequence:
            raise ValueError("strategy outcome requires applied reasoning")
        if outcome.source_reference not in application.contribution_reference_ids:
            raise ValueError("strategy outcome reasoning reference lineage mismatch")
        pattern, rationale = cls._derive_pattern(
            outcome.quality_status,
            outcome.sufficiency_status,
        )
        source = sha256(
            repr(
                (
                    application.strategy_fingerprint,
                    application.source_fingerprint,
                    application.owner,
                    scope,
                    outcome.source_fingerprint,
                    outcome.method_fingerprint,
                    outcome.quality_status.value,
                    outcome.sufficiency_status.value,
                    outcome.source_reference,
                    outcome.world_snapshot_id,
                    pattern.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        return cls(
            observation_id=f"strategy-outcome-observation-{source[:24]}",
            strategy_fingerprint=application.strategy_fingerprint,
            application_fingerprint=application.source_fingerprint,
            owner=application.owner,
            evaluation_scope=scope,
            reasoning_method_fingerprint=outcome.method_fingerprint,
            reasoning_outcome_observation_id=outcome.observation_id,
            quality_status=outcome.quality_status,
            sufficiency_status=outcome.sufficiency_status,
            source_reference=outcome.source_reference,
            world_snapshot_id=outcome.world_snapshot_id,
            pattern_status=pattern,
            rationale_codes=rationale,
            source_fingerprint=source,
        )

    @staticmethod
    def _derive_pattern(
        quality: GovernedReasoningQualityStatus,
        sufficiency: EpistemicSufficiencyStatus,
    ) -> tuple[StrategyOutcomePatternStatus, tuple[str, ...]]:
        if (
            quality is GovernedReasoningQualityStatus.REVIEW_REQUIRED
            or sufficiency is EpistemicSufficiencyStatus.INDETERMINATE
        ):
            return (
                StrategyOutcomePatternStatus.REVIEW_REQUIRED,
                ("strategy_outcome:review_required_evidence",),
            )
        if (
            quality is GovernedReasoningQualityStatus.ADEQUATE
            and sufficiency is EpistemicSufficiencyStatus.SUFFICIENT
        ):
            return (
                StrategyOutcomePatternStatus.SUPPORTIVE,
                ("strategy_outcome:supportive_observed_pattern",),
            )
        return (
            StrategyOutcomePatternStatus.LIMITING,
            ("strategy_outcome:limiting_observed_pattern",),
        )


class GovernedFutureStrategyInfluenceStatus(StrEnum):
    PREFER = "prefer"
    NO_INFLUENCE = "no_influence"
    AMBIGUOUS = "ambiguous"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedFutureStrategyInfluence:
    status: GovernedFutureStrategyInfluenceStatus
    evaluation_scope: str
    advisory_id: str | None
    advisory_fingerprint: str | None
    eligible_structural_fingerprints: tuple[str, ...]
    recommended_structural_fingerprint: str | None
    selected_structural_fingerprint: str | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    canonical_authority: str = "unified_cognitive_coordination"
    read_only: bool = True
    persists: bool = False
    creates_learning: bool = False
    creates_memory: bool = False
    modifies_planner: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.evaluation_scope.strip() or not self.rationale_codes:
            raise ValueError("future strategy influence requires scope and rationale")
        if not self.source_fingerprint.strip():
            raise ValueError("future strategy influence requires provenance")
        if self.canonical_authority != "unified_cognitive_coordination":
            raise ValueError("future strategy influence must preserve authority")
        if any(
            (
                not self.read_only,
                self.persists,
                self.creates_learning,
                self.creates_memory,
                self.modifies_planner,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("future strategy influence violates governed limits")
        if (
            self.status is GovernedFutureStrategyInfluenceStatus.PREFER
            and self.selected_structural_fingerprint is None
        ):
            raise ValueError("preferred future strategy influence requires selection")


@dataclass(frozen=True)
class GovernedFutureStrategySynthesisResult:
    strategy: CognitiveStrategyCandidate
    influence: GovernedFutureStrategyInfluence



@dataclass(frozen=True)
class GovernedStrategyMetacognitiveAdaptation:
    advisory_id: str
    status: StrategyMetacognitiveAdaptationStatus
    evaluation_scope: str
    candidate_strategy_fingerprints: tuple[str, ...]
    recommended_strategy_fingerprint: str | None
    source_observation_ids: tuple[str, ...]
    world_snapshot_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    canonical_authority: str = "unified_cognitive_coordination"
    read_only: bool = True
    consultative: bool = True
    recommends_strategy: bool = True
    application_authorized: bool = False
    modifies_planner: bool = False
    persists_preference: bool = False
    creates_learning: bool = False
    creates_memory: bool = False
    establishes_causality: bool = False
    establishes_strategy_superiority: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.advisory_id.startswith("strategy-metacognitive-adaptation-"):
            raise ValueError("strategy adaptation identifier is invalid")
        expected_id = (
            f"strategy-metacognitive-adaptation-{self.source_fingerprint[:24]}"
        )
        if self.advisory_id != expected_id:
            raise ValueError("strategy adaptation identifier is inconsistent")
        if not self.evaluation_scope.strip() or not self.rationale_codes:
            raise ValueError("strategy adaptation requires scope and rationale")
        if not self.source_fingerprint.strip():
            raise ValueError("strategy adaptation requires provenance")
        if self.canonical_authority != "unified_cognitive_coordination":
            raise ValueError("strategy adaptation must preserve authority")
        if not self.read_only or not self.consultative or not self.recommends_strategy:
            raise ValueError("strategy adaptation must remain consultative")
        if any(
            (
                self.application_authorized,
                self.modifies_planner,
                self.persists_preference,
                self.creates_learning,
                self.creates_memory,
                self.establishes_causality,
                self.establishes_strategy_superiority,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("strategy adaptation violates governed limits")
        if (
            self.status is StrategyMetacognitiveAdaptationStatus.ADAPTATION_SUGGESTED
            and self.recommended_strategy_fingerprint is None
        ):
            raise ValueError("suggested adaptation requires a recommendation")


class GovernedStrategyMetacognitiveAdaptationV1:
    """Recommend a bounded strategy from compatible observed strategy outcomes."""

    MIN_OBSERVATIONS = 2

    def advise(
        self,
        observations: tuple[GovernedStrategyOutcomeObservation, ...],
        *,
        evaluation_scope: str,
        candidate_strategy_fingerprints: tuple[str, ...],
    ) -> GovernedStrategyMetacognitiveAdaptation:
        scope = evaluation_scope.strip()
        candidates = tuple(sorted(set(candidate_strategy_fingerprints)))
        if not scope or not candidates or any(not item.strip() for item in candidates):
            raise ValueError("strategy adaptation requires scope and candidates")
        applicable = tuple(
            sorted(
                (
                    item
                    for item in observations
                    if item.evaluation_scope == scope
                    and item.strategy_fingerprint in candidates
                ),
                key=lambda item: (
                    item.strategy_fingerprint,
                    item.world_snapshot_id,
                    item.observation_id,
                ),
            )
        )
        status, recommendation, rationale = self._derive(applicable, candidates)
        source_ids = tuple(item.observation_id for item in applicable)
        snapshots = tuple(sorted({item.world_snapshot_id for item in applicable}))
        source = sha256(
            repr(
                (
                    scope,
                    candidates,
                    tuple(item.source_fingerprint for item in applicable),
                    status.value,
                    recommendation,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedStrategyMetacognitiveAdaptation(
            advisory_id=f"strategy-metacognitive-adaptation-{source[:24]}",
            status=status,
            evaluation_scope=scope,
            candidate_strategy_fingerprints=candidates,
            recommended_strategy_fingerprint=recommendation,
            source_observation_ids=source_ids,
            world_snapshot_ids=snapshots,
            rationale_codes=rationale,
            source_fingerprint=source,
        )

    def _derive(
        self,
        observations: tuple[GovernedStrategyOutcomeObservation, ...],
        candidates: tuple[str, ...],
    ) -> tuple[
        StrategyMetacognitiveAdaptationStatus,
        str | None,
        tuple[str, ...],
    ]:
        if any(
            item.pattern_status is StrategyOutcomePatternStatus.REVIEW_REQUIRED
            for item in observations
        ):
            return (
                StrategyMetacognitiveAdaptationStatus.REVIEW_REQUIRED,
                None,
                ("strategy_adaptation:review_required_history_present",),
            )
        grouped = {
            candidate: tuple(
                item for item in observations if item.strategy_fingerprint == candidate
            )
            for candidate in candidates
        }
        sufficient = {
            candidate: items
            for candidate, items in grouped.items()
            if len(items) >= self.MIN_OBSERVATIONS
        }
        if not sufficient:
            return (
                StrategyMetacognitiveAdaptationStatus.INSUFFICIENT_EVIDENCE,
                None,
                ("strategy_adaptation:insufficient_compatible_history",),
            )
        supportive = tuple(
            candidate
            for candidate, items in sufficient.items()
            if all(
                item.pattern_status is StrategyOutcomePatternStatus.SUPPORTIVE
                for item in items
            )
        )
        limiting = tuple(
            candidate
            for candidate, items in sufficient.items()
            if all(
                item.pattern_status is StrategyOutcomePatternStatus.LIMITING
                for item in items
            )
        )
        if len(supportive) == 1 and (
            len(candidates) == 1 or any(item in limiting for item in candidates)
        ):
            return (
                StrategyMetacognitiveAdaptationStatus.ADAPTATION_SUGGESTED,
                supportive[0],
                ("strategy_adaptation:bounded_supportive_pattern_observed",),
            )
        if len(supportive) > 1:
            return (
                StrategyMetacognitiveAdaptationStatus.AMBIGUOUS,
                None,
                ("strategy_adaptation:multiple_supportive_patterns",),
            )
        return (
            StrategyMetacognitiveAdaptationStatus.AMBIGUOUS,
            None,
            ("strategy_adaptation:no_unique_supportive_pattern",),
        )
