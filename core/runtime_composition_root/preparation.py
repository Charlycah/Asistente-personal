from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from core.adaptive_personality import (
    AdaptivePersonalityProfile,
    AdaptivePersonalityRequest,
)
from core.cognitive_maturity import (
    IdentityContextAccessGate,
    MemoryKnowledgeEvidenceAdapter,
    PlanningDecisionEvidenceAdapter,
    ResponseActionEvidenceAdapter,
)
from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedConversationPreparation,
    build_governed_conversation_turn_identity,
)
from core.governed_provider_routing import (
    GovernedProviderRouter,
    GovernedProviderRoutingRequest,
)
from core.governed_reasoning.longitudinal_intellectual_reconstruction import (
    GovernedLongitudinalIntellectualReconstruction,
)
from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedLongitudinalReasoningAssessment,
    GovernedLongitudinalReasoningAssessmentFoundationV1,
    GovernedReasoningAssessmentObservation,
)
from core.governed_reasoning.longitudinal_reasoning_conversational_projection import (
    GovernedLongitudinalReasoningConversationalProjection,
    GovernedLongitudinalReasoningConversationalProjectorV1,
)
from core.knowledge_retrieval_orchestrator import (
    KnowledgeRetrievalOrchestrator,
    KnowledgeRetrievalRequest,
    KnowledgeRetrievalStatus,
)
from core.knowledge_source_policy import (
    KnowledgeSourcePolicy,
    KnowledgeSourcePolicyRequest,
)
from core.llm_provider import LLMRequest
from core.local_first_provider_policy import (
    LocalFirstProviderPolicy,
    LocalFirstProviderRequest,
)
from core.provider_health_evaluation import (
    ProviderHealthEvaluator,
    ProviderHealthRequest,
)
from core.stable_personality import StablePersonalitySnapshot

from .models import RuntimeCompositionDependencies


class GovernedRuntimePreparation:
    """Builds exact M166-M170 lineage for one M177 operational turn."""

    def __init__(
        self,
        *,
        dependencies: RuntimeCompositionDependencies,
        health_evaluator: ProviderHealthEvaluator,
        provider_policy: LocalFirstProviderPolicy,
        provider_router: GovernedProviderRouter,
        knowledge_policy: KnowledgeSourcePolicy,
        retrieval_orchestrator: KnowledgeRetrievalOrchestrator,
    ) -> None:
        self.dependencies = dependencies
        self.health_evaluator = health_evaluator
        self.provider_policy = provider_policy
        self.provider_router = provider_router
        self.knowledge_policy = knowledge_policy
        self.retrieval_orchestrator = retrieval_orchestrator

    @staticmethod
    def _enrich_with_canonical_personality_expression(
        request: LLMRequest,
        *,
        stable: StablePersonalitySnapshot,
        profile: AdaptivePersonalityProfile,
    ) -> LLMRequest:
        """Project already-decided M55/M377 expression into ordinary inference."""
        context = "\n".join(
            (
                "[CANONICAL STABLE PERSONALITY EXPRESSION]",
                *stable.system_prompt_lines(),
                f"- Delivery tone: {profile.normalized_tone.value}",
                f"- Response detail: {profile.normalized_detail.value}",
                f"- Response structure: {profile.normalized_structure.value}",
                "This context governs expression only; it does not establish facts, ",
                "memory, reasoning, authorization, action, or subjective emotion.",
            )
        )
        system_prompt = (
            context
            if not request.system_prompt
            else f"{request.system_prompt.rstrip()}\n\n{context}"
        )
        return replace(request, system_prompt=system_prompt)

    @staticmethod
    def _enrich_with_productive_longitudinal_intellectual_reconstruction(
        request: LLMRequest,
        *,
        reconstruction: GovernedLongitudinalIntellectualReconstruction,
    ) -> LLMRequest:
        """Transport one certified reconstruction into ordinary inference."""
        context = "\n".join(
            (
                "[GOVERNED LONGITUDINAL INTELLECTUAL RECONSTRUCTION]",
                f"assessment_id: {reconstruction.assessment_id}",
                "prior_antecedent_status: "
                f"{reconstruction.prior_antecedent_status.value}",
                "previously_established_status: "
                f"{reconstruction.previously_established_status.value}",
                f"uncertainty_status: {reconstruction.uncertainty_status.value}",
                f"change_status: {reconstruction.change_status.value}",
                f"open_status: {reconstruction.open_status.value}",
                "evidence_references: " + ", ".join(reconstruction.evidence_references),
                "source_references: " + ", ".join(reconstruction.source_references),
                f"source_fingerprint: {reconstruction.source_fingerprint}",
                "This reconstruction is derived, read-only, and does not establish "
                "truth, longitudinal identity, authorization, or autonomous "
                "continuation.",
            )
        )
        system_prompt = (
            context
            if not request.system_prompt
            else f"{request.system_prompt.rstrip()}\n\n{context}"
        )
        return replace(request, system_prompt=system_prompt)

    @classmethod
    def _compose_and_enrich_productive_longitudinal_intellectual_reconstruction(
        cls,
        request: LLMRequest,
        *,
        reasoning_runtime: object | None,
        recalled_antecedent_reference: str | None,
        recalled_antecedent_fingerprint: str | None,
        recalled_evidence_references: tuple[str, ...],
        current_epistemic_assessment: object | None,
        epistemic_delta: object | None,
        open_state_references: tuple[str, ...],
    ) -> LLMRequest:
        """Compose and transport only explicitly admitted longitudinal inputs."""
        if (
            reasoning_runtime is None
            or not recalled_antecedent_reference
            or not recalled_antecedent_fingerprint
        ):
            return request
        compose = getattr(
            reasoning_runtime,
            "compose_productive_longitudinal_intellectual_reconstruction",
            None,
        )
        if not callable(compose):
            return request
        reconstruction = compose(
            recalled_antecedent_reference=recalled_antecedent_reference,
            recalled_antecedent_fingerprint=recalled_antecedent_fingerprint,
            recalled_evidence_references=recalled_evidence_references,
            current_epistemic_assessment=current_epistemic_assessment,
            epistemic_delta=epistemic_delta,
            open_state_references=open_state_references,
        )
        return cls._enrich_with_productive_longitudinal_intellectual_reconstruction(
            request,
            reconstruction=reconstruction,
        )

    @staticmethod
    def _bind_productive_epistemic_episode(
        *,
        request: GovernedConversationPipelineRequest,
        reasoning_runtime: object | None,
        now: datetime,
    ) -> object | None:
        if (
            reasoning_runtime is None
            or request.explicit_hypothesis_source is None
            or request.hypothesis_world_snapshot is None
        ):
            return None
        identity = build_governed_conversation_turn_identity(request, now)
        reasoning_episode = reasoning_runtime.evaluate_productive_episode(
            owner=request.owner,
            session_id=request.session_id,
            text=request.text,
            now=now,
            turn_id=identity.turn_id,
            scope_reference=request.session_id,
            observe_productive_intake=False,
        )
        return reasoning_runtime.bind_productive_epistemic_assessment(
            reasoning_episode,
            request.explicit_hypothesis_source,
            world=request.hypothesis_world_snapshot,
        )

    @staticmethod
    def _retain_productive_epistemic_observation(
        *,
        epistemic_episode: object | None,
        retention: object | None,
    ) -> GovernedReasoningAssessmentObservation | None:
        """Retain and expose only the exactly admitted epistemic observation."""
        if epistemic_episode is None or retention is None:
            return None
        status = getattr(epistemic_episode, "status", None)
        status_value = getattr(status, "value", status)
        if str(status_value).lower() != "assessed":
            return None
        quality = getattr(epistemic_episode, "quality", None)
        sufficiency = getattr(epistemic_episode, "sufficiency", None)
        if quality is None or sufficiency is None:
            return None
        try:
            observation = GovernedReasoningAssessmentObservation.from_assessments(
                quality, sufficiency
            )
        except (TypeError, ValueError):
            return None
        retain = getattr(retention, "retain", None)
        if not callable(retain):
            return None
        retention.retain(observation)
        return observation

    @staticmethod
    def _compose_productive_longitudinal_reasoning_assessment(
        *,
        observation: GovernedReasoningAssessmentObservation | None,
        retention: object | None,
    ) -> GovernedLongitudinalReasoningAssessment | None:
        """Derive one bounded assessment from exact retained source lineage."""
        if observation is None or retention is None:
            return None
        retrieve = getattr(retention, "retrieve", None)
        if not callable(retrieve):
            return None
        try:
            observations = retention.retrieve(
                source_reference=observation.source_reference
            )
            return GovernedLongitudinalReasoningAssessmentFoundationV1().assess(
                observations
            )
        except (TypeError, ValueError, OSError):
            return None

    @staticmethod
    def _project_productive_longitudinal_reasoning_assessment(
        assessment: GovernedLongitudinalReasoningAssessment | None,
    ) -> GovernedLongitudinalReasoningConversationalProjection | None:
        """Project only one already-derived canonical longitudinal assessment."""
        if assessment is None:
            return None
        try:
            return GovernedLongitudinalReasoningConversationalProjectorV1().project(
                assessment
            )
        except (TypeError, ValueError, KeyError):
            return None

    @staticmethod
    def _enrich_with_productive_longitudinal_reasoning_projection(
        request: LLMRequest,
        *,
        projection: GovernedLongitudinalReasoningConversationalProjection,
    ) -> LLMRequest:
        """Transport one certified descriptive projection into ordinary inference."""
        context = "\n".join(
            (
                "[GOVERNED LONGITUDINAL REASONING ASSESSMENT]",
                projection.conversation_context,
                "This context is derived, read-only, consultative, and descriptive "
                "only; it grants no review or action authority.",
            )
        )
        system_prompt = (
            context
            if not request.system_prompt
            else f"{request.system_prompt.rstrip()}\n\n{context}"
        )
        return replace(request, system_prompt=system_prompt)

    @staticmethod
    def _close_productive_epistemic_strategy_outcome(
        *,
        request: GovernedConversationPipelineRequest,
        epistemic_episode: object | None,
        strategy_application_evidence: object | None,
        strategy_coordinator: object | None,
    ) -> object | None:
        if (
            epistemic_episode is None
            or strategy_application_evidence is None
            or strategy_coordinator is None
        ):
            return None
        method_outcome = getattr(epistemic_episode, "method_outcome", None)
        if method_outcome is None:
            return None
        close_outcome = getattr(
            strategy_coordinator,
            "close_productive_strategy_outcome",
            None,
        )
        if not callable(close_outcome):
            return None
        return close_outcome(
            strategy_application_evidence,
            method_outcome,
            evaluation_scope=request.session_id,
        )

    def prepare_at(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedConversationPreparation:
        return self.prepare(request, reasoning_now=now)

    def prepare(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime | None = None,
        reasoning_now: datetime | None = None,
    ) -> GovernedConversationPreparation:
        timestamp = now or datetime.now(timezone.utc)
        reasoning_timestamp = reasoning_now or timestamp
        if timestamp.tzinfo is None:
            raise ValueError("runtime preparation time must be timezone-aware")

        readiness = self.dependencies.readiness_port.resolve(request)
        health = self.health_evaluator.evaluate(
            ProviderHealthRequest(
                owner=request.owner,
                readiness_result=readiness,
                observations=self.dependencies.observations_port.observe(request),
            ),
            now=timestamp,
        )
        policy = self.provider_policy.decide(
            LocalFirstProviderRequest(
                owner=request.owner,
                health_result=health,
                workload=self.dependencies.workload_port.describe(request),
            ),
            now=timestamp,
        )
        route = self.provider_router.route(
            GovernedProviderRoutingRequest(
                owner=request.owner,
                policy_decision=policy,
            ),
            now=timestamp,
        )
        source = self.knowledge_policy.decide(
            KnowledgeSourcePolicyRequest(
                owner=request.owner,
                provider_route=route,
                need=self.dependencies.knowledge_need_port.describe(request),
            ),
            now=timestamp,
        )
        plan = self.retrieval_orchestrator.orchestrate(
            KnowledgeRetrievalRequest(owner=request.owner, source_decision=source),
            now=timestamp,
        )
        MemoryKnowledgeEvidenceAdapter.observe_knowledge_plan(plan.status)
        retrieval_plan = (
            None
            if plan.status
            in {
                KnowledgeRetrievalStatus.WITHHELD,
                KnowledgeRetrievalStatus.NOT_APPLICABLE,
            }
            else plan
        )
        inference_request = self.dependencies.inference_request_port.build(request)
        stable_personality = self.dependencies.stable_personality
        adaptive_personality = self.dependencies.adaptive_personality
        if stable_personality is not None and adaptive_personality is not None:
            stable = stable_personality.evaluate_turn(request.text, now=timestamp)
            profile = adaptive_personality.adapt(
                stable,
                AdaptivePersonalityRequest(),
            )
            inference_request = self._enrich_with_canonical_personality_expression(
                inference_request,
                stable=stable,
                profile=profile,
            )
        context_runtime = self.dependencies.context_continuity_runtime
        if context_runtime is None:
            inference_request = enrich_with_recent_conversation_context(
                conversation=request,
                inference_request=inference_request,
            )
        else:
            inference_request = context_runtime.enrich(
                conversation=request,
                inference_request=inference_request,
            )
        declaration = request.explicit_longitudinal_topic_declaration
        living_conversation_source = self.dependencies.living_conversation_source
        if (
            declaration is not None
            and living_conversation_source is not None
            and context_runtime is not None
        ):
            read_prior = getattr(
                living_conversation_source,
                "read_prior_longitudinal_episodes",
                None,
            )
            enrich_longitudinal = getattr(
                context_runtime,
                "enrich_with_longitudinal_history",
                None,
            )
            if callable(read_prior) and callable(enrich_longitudinal):
                prior_episodes = read_prior(
                    owner=request.owner,
                    topic_key=declaration.topic_key,
                )
                inference_request = enrich_longitudinal(
                    inference_request=inference_request,
                    episodes=prior_episodes,
                )
        memory_runtime = self.dependencies.memory_runtime
        recalled_antecedent_candidates: tuple[object, ...] = ()
        memory_access = IdentityContextAccessGate.current().private_context_allowed
        if memory_runtime is None:
            MemoryKnowledgeEvidenceAdapter().observe_memory(
                runtime_available=False,
                access_allowed=memory_access,
                recall_completed=False,
            )
        elif not memory_access:
            MemoryKnowledgeEvidenceAdapter().observe_memory(
                runtime_available=True,
                access_allowed=False,
                recall_completed=False,
            )
        else:
            memory_context = memory_runtime.enrich(
                owner=request.owner,
                text=request.text,
                request=inference_request,
            )
            inference_request = memory_context.request
            recalled_antecedent_candidates = tuple(
                memory_context.recalled_antecedent_candidates
            )
            MemoryKnowledgeEvidenceAdapter().observe_memory(
                runtime_available=True,
                access_allowed=True,
                recall_completed=True,
                context_included=bool(memory_context.context_included),
            )
        cognitive_runtime = self.dependencies.cognitive_runtime
        reasoning_runtime = self.dependencies.governed_reasoning_runtime
        reconstruction_adapter = (
            self.dependencies.longitudinal_reconstruction_productive_adapter
        )
        antecedent_admission = None
        if reconstruction_adapter is not None:
            admit_antecedent = getattr(
                reconstruction_adapter,
                "admit_recalled_antecedent",
                None,
            )
            if callable(admit_antecedent):
                antecedent_admission = admit_antecedent(
                    candidates=recalled_antecedent_candidates
                )
        epistemic_episode = self._bind_productive_epistemic_episode(
            request=request,
            reasoning_runtime=reasoning_runtime,
            now=reasoning_timestamp,
        )
        current_epistemic_view = None
        if reconstruction_adapter is not None:
            project_current_epistemic_view = getattr(
                reconstruction_adapter,
                "project_current_epistemic_view",
                None,
            )
            if callable(project_current_epistemic_view):
                current_epistemic_view = project_current_epistemic_view(
                    epistemic_episode
                )
        compose_reconstruction = (
            self._compose_and_enrich_productive_longitudinal_intellectual_reconstruction
        )
        if antecedent_admission is not None:
            inference_request = compose_reconstruction(
                    inference_request,
                    reasoning_runtime=reasoning_runtime,
                    recalled_antecedent_reference=(
                        antecedent_admission.antecedent_reference
                    ),
                    recalled_antecedent_fingerprint=(
                        antecedent_admission.antecedent_fingerprint
                    ),
                    recalled_evidence_references=(),
                    current_epistemic_assessment=current_epistemic_view,
                    epistemic_delta=None,
                    open_state_references=(),
                )
        epistemic_observation_retention = (
            self.dependencies.epistemic_observation_retention
        )
        epistemic_observation = self._retain_productive_epistemic_observation(
            epistemic_episode=epistemic_episode,
            retention=epistemic_observation_retention,
        )
        longitudinal_reasoning_assessment = (
            self._compose_productive_longitudinal_reasoning_assessment(
                observation=epistemic_observation,
                retention=epistemic_observation_retention,
            )
        )
        longitudinal_reasoning_projection = (
            self._project_productive_longitudinal_reasoning_assessment(
                longitudinal_reasoning_assessment
            )
        )
        if longitudinal_reasoning_projection is not None:
            inference_request = (
                self._enrich_with_productive_longitudinal_reasoning_projection(
                    inference_request,
                    projection=longitudinal_reasoning_projection,
                )
            )
        if declaration is not None and living_conversation_source is not None:
            identity = build_governed_conversation_turn_identity(
                request, reasoning_timestamp
            )
            supply_declaration = getattr(
                living_conversation_source,
                "supply_explicit_longitudinal_topic_declaration",
                None,
            )
            observe_turn = getattr(
                living_conversation_source,
                "observe_longitudinal_productive_turn",
                None,
            )
            if callable(supply_declaration) and callable(observe_turn):
                evidence = supply_declaration(
                    owner=request.owner,
                    session_id=request.session_id,
                    turn_id=identity.turn_id,
                    topic_key=declaration.topic_key,
                )
                observe_turn(
                    owner=request.owner,
                    session_id=request.session_id,
                    turn_id=identity.turn_id,
                    summary=request.text,
                    occurred_at=reasoning_timestamp,
                    evidence=evidence,
                    topic_key=declaration.topic_key,
                )
        strategy_application = None
        strategy_coordinator = self.dependencies.cognitive_strategy_coordinator
        if cognitive_runtime is not None and strategy_coordinator is not None:
            prepare_strategy = getattr(
                strategy_coordinator,
                "prepare_productive_strategy_application",
                None,
            )
            if callable(prepare_strategy):
                strategy_application = prepare_strategy(request)
        continuity_selection = None
        continuity_context_surface = self.dependencies.continuity_context_surface
        continuity_adapter = self.dependencies.longitudinal_identity_productive_adapter
        if continuity_adapter is not None and reasoning_runtime is not None:
            identity = build_governed_conversation_turn_identity(
                request, reasoning_timestamp
            )
            assess_and_select = getattr(
                continuity_adapter,
                "assess_and_select",
                None,
            )
            if callable(assess_and_select):
                continuity_result = assess_and_select(
                    owner=request.owner,
                    session_id=request.session_id,
                    candidate_turn_id=identity.turn_id,
                    current_artifact_reference=identity.turn_id,
                )
                if continuity_result is not None:
                    continuity_selection = continuity_result.selection

        strategy_application_evidence = None
        if cognitive_runtime is not None:
            if (
                continuity_selection is not None
                and continuity_context_surface is not None
            ):
                cognitive_context = cognitive_runtime.enrich(
                    owner=request.owner,
                    session_id=request.session_id,
                    text=request.text,
                    request=inference_request,
                    now=reasoning_timestamp,
                    external_evidence=request.external_evidence,
                    integrated_visual_context=request.integrated_visual_context,
                    strategy_application=strategy_application,
                    explicit_document_ids=request.explicit_document_ids,
                    explicit_sources=request.explicit_sources,
                    explicit_evidence_references=request.explicit_evidence_references,
                    continuity_selection=continuity_selection,
                    continuity_context_surface=continuity_context_surface,
                )
            else:
                cognitive_context = cognitive_runtime.enrich(
                    owner=request.owner,
                    session_id=request.session_id,
                    text=request.text,
                    request=inference_request,
                    now=reasoning_timestamp,
                    external_evidence=request.external_evidence,
                    integrated_visual_context=request.integrated_visual_context,
                    strategy_application=strategy_application,
                    explicit_document_ids=request.explicit_document_ids,
                    explicit_sources=request.explicit_sources,
                    explicit_evidence_references=request.explicit_evidence_references,
                )
            inference_request = cognitive_context.request
            strategy_application_evidence = getattr(
                cognitive_context,
                "strategy_application_evidence",
                None,
            )
            PlanningDecisionEvidenceAdapter().observe_cognitive_runtime(
                cognitive_context
            )
            self._close_productive_epistemic_strategy_outcome(
                request=request,
                epistemic_episode=epistemic_episode,
                strategy_application_evidence=strategy_application_evidence,
                strategy_coordinator=strategy_coordinator,
            )
            adaptive_cognition_runtime = self.dependencies.adaptive_cognition_runtime
            if reasoning_runtime is not None and adaptive_cognition_runtime is not None:
                identity = build_governed_conversation_turn_identity(
                    request, reasoning_timestamp
                )
                reasoning_episode = reasoning_runtime.productive_episode(
                    owner=request.owner,
                    session_id=request.session_id,
                    turn_id=identity.turn_id,
                )
                if (
                    reasoning_episode is not None
                    and reasoning_episode.result.status.value == "derived"
                ):
                    adaptive_cognition_runtime.observe_productive_episode(
                        owner=request.owner,
                        text=request.text,
                        episode=reasoning_episode,
                        now=reasoning_timestamp,
                    )
        else:
            PlanningDecisionEvidenceAdapter().observe_cognitive_runtime(None)
        tool_runtime = self.dependencies.tool_runtime
        if tool_runtime is not None:
            tool_context = tool_runtime.enrich(
                owner=request.owner,
                session_id=request.session_id,
                text=request.text,
                request=inference_request,
            )
            inference_request = tool_context.request
            ResponseActionEvidenceAdapter().observe_tool_context(tool_context)
        else:
            ResponseActionEvidenceAdapter().observe_tool_context(None)
        return GovernedConversationPreparation(
            owner=request.owner,
            session_id=request.session_id,
            text=request.text,
            provider_route=route,
            inference_request=inference_request,
            retrieval_plan=retrieval_plan,
            strategy_application_evidence=strategy_application_evidence,
        )
