from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum

from core.cognitive_runtime_orchestration import CognitiveExternalEvidenceAdmission
from core.end_to_end_local_conversation import LocalConversationTurn

from .canonical_cognitive_core import CanonicalCognitiveCore
from .canonical_cognitive_cycle import CanonicalCognitiveCycle
from .canonical_cognitive_state_facade import CanonicalCognitiveStateFacade
from .canonical_decision_facade import CanonicalDecisionFacade
from .canonical_memory_facade import CanonicalMemoryFacade
from .canonical_planning_facade import CanonicalPlanningFacade
from .canonical_reflection_facade import CanonicalReflectionFacade
from .cognitive_authority_map import CognitiveAuthorityMap
from .cognitive_integration_adapters import CognitiveIntegrationAdapters
from .cognitive_operational_inventory import CognitiveOperationalObserver
from .governed_local_music_runtime_wiring import local_music_command
from .current_affairs_router import CurrentAffairsRouter


class ConversationOrigin(StrEnum):
    CONSOLE = "console"
    DESKTOP_TEXT = "desktop_text"
    DESKTOP_VOICE = "desktop_voice"
    INTERNAL = "internal"


@dataclass(frozen=True)
class OfficialConversationGatewaySnapshot:
    submitted_turns: int
    last_origin: ConversationOrigin | None
    last_session_id: str | None
    analysis_mode: "OfficialConversationGateway.AnalysisModeStatus"


class OfficialConversationGateway:
    """Single governed entry boundary for every interactive ROBY turn."""

    def __init__(self, runtime, *, governed_learning_memory_gateway=None) -> None:
        self._runtime = runtime
        self._submitted_turns = 0
        self._last_origin: ConversationOrigin | None = None
        self._last_session_id: str | None = None
        self._analysis_mode_by_session = {}
        self._cognitive_observer = CognitiveOperationalObserver()
        self._canonical_cognitive_state = CanonicalCognitiveStateFacade()
        self._canonical_decision = CanonicalDecisionFacade()
        self._canonical_memory = CanonicalMemoryFacade()
        self._canonical_planning = CanonicalPlanningFacade()
        self._canonical_reflection = CanonicalReflectionFacade()
        self._canonical_cognitive_core = CanonicalCognitiveCore(
            memory=self._canonical_memory,
            planning=self._canonical_planning,
            decision=self._canonical_decision,
            state=self._canonical_cognitive_state,
            reflection=self._canonical_reflection,
        )
        self._last_applied_owner_turn_result = None
        cognitive_state_authority = getattr(runtime, "cognitive_state_authority", None)
        if cognitive_state_authority is not None:
            self._canonical_cognitive_state.bind(cognitive_state_authority)
        self._governed_learning_memory_gateway = governed_learning_memory_gateway
        from core.cognitive_maturity import EpistemicEvidenceAdapter

        self._epistemic_evidence = EpistemicEvidenceAdapter()
        self._initialize_cognitive_evidence()
        self._initialize_governed_conversation_services()

    def _initialize_cognitive_evidence(self) -> None:
        from core.cognitive_maturity import (
            CognitiveStateEvidenceAdapter,
            ControlledConversationalIdentificationFlow,
            ConversationEntryEvidenceAdapter,
            IdentityContextAccessGate,
            IdentityContextEvidenceAdapter,
            IntentReasoningEvidenceAdapter,
            MemoryKnowledgeEvidenceAdapter,
            PlanningDecisionEvidenceAdapter,
            ReflectionLearningEvidenceAdapter,
            RelationalAffectiveEvidenceAdapter,
            ResponseActionEvidenceAdapter,
            TextPerceptionEvidenceAdapter,
            UnifiedCoordinationEvidenceAdapter,
        )

        self._conversational_identification = (
            ControlledConversationalIdentificationFlow()
        )
        self._conversation_entry_evidence = ConversationEntryEvidenceAdapter()
        self._cognitive_state_evidence = CognitiveStateEvidenceAdapter()
        self._identity_context_access = IdentityContextAccessGate()
        self._identity_context_evidence = IdentityContextEvidenceAdapter()
        self._intent_reasoning_evidence = IntentReasoningEvidenceAdapter()
        self._memory_knowledge_evidence = MemoryKnowledgeEvidenceAdapter()
        self._planning_decision_evidence = PlanningDecisionEvidenceAdapter()
        self._reflection_learning_evidence = ReflectionLearningEvidenceAdapter()
        self._relational_affective_evidence = RelationalAffectiveEvidenceAdapter()
        self._response_action_evidence = ResponseActionEvidenceAdapter()
        self._text_perception_evidence = TextPerceptionEvidenceAdapter()
        self._unified_coordination_evidence = UnifiedCoordinationEvidenceAdapter()

    def _initialize_governed_conversation_services(self) -> None:
        from core.decision_advisory_conversational_realization import (
            DecisionAdvisoryConversationalRealizer,
        )
        from core.explicit_complex_decision_intake_envelope import (
            ExplicitComplexDecisionIntakeEnvelopeFoundationV1,
            ExplicitComplexDecisionIntakeEnvelopeStatus,
        )
        from core.explicit_deliberation_decision_option_adapter import (
            ExplicitDeliberationDecisionOptionAdapter,
        )
        from core.explicit_human_decision_deliberation import (
            ExplicitDecisionDeliberationStatus,
            ExplicitHumanDecisionDeliberationEvidenceProducer,
        )
        from core.gcdr_intake_conversational_realization import (
            GCDRIntakeConversationalRealizerV1,
        )
        from core.productive_gcdr_intake_integration import (
            ProductiveGCDRIntakeIntegrationV1,
        )
        from domain.governed_action_preparation import GovernedActionPreparation
        from domain.governed_cognitive_judgment import (
            GovernedCognitiveJudgmentAuthority,
        )
        from domain.governed_objective_memory import GovernedObjectiveMemory
        from domain.governed_permanent_knowledge import GovernedPermanentKnowledge
        from domain.governed_plan import GovernedPlanModel
        from domain.governed_plan_continuity import GovernedPlanContinuity
        from domain.governed_proactive_care import GovernedProactiveCare
        from domain.governed_proposal import GovernedProposalModel
        from domain.governed_proposal_inbox import GovernedProposalInbox

        from .apple_audiovisual_governed_source import (
            AppleAudiovisualGovernedSourceAdapter,
        )
        from .applied_conversational_intelligence import (
            AppliedConversationalIntelligence,
        )
        from .argentina_healthy_eating_governed_source import (
            ArgentinaHealthyEatingGovernedSourceAdapter,
        )
        from .cultura_caba_governed_source import CulturaCabaGovernedSourceAdapter
        from .governed_conversational_source_selection import (
            GovernedConversationalSourceSelector,
        )
        from .governed_information_normalizer import GovernedInformationNormalizer
        from .governed_information_sources import GovernedInformationSources
        from .governed_initiative_engine import GovernedInitiativeEngine
        from .governed_proposal_inbox_query import GovernedProposalInboxQuery
        from .governed_proposal_lifecycle import GovernedProposalLifecycle
        from .governed_proposal_presentation_policy import (
            GovernedProposalPresentationPolicy,
        )
        from .governed_source_query import GovernedSourceQueryContract
        from .governed_source_query_executor import GovernedSourceQueryExecutor
        from .nasa_governed_source import NasaGovernedSourceAdapter
        from .natural_governed_conversational_response import (
            NaturalGovernedConversationalResponse,
        )
        from .personal_initiative_engine import PersonalInitiativeEngine
        from .personal_interest_center import PersonalInterestCenter
        from .personal_on_demand_bulletin import PersonalOnDemandBulletin
        from .productive_conversational_curiosity_wiring import (
            ProductiveConversationalCuriosityWiring,
        )
        from .productive_governed_learning_wiring import (
            ProductiveGovernedLearningWiring,
        )
        from .productive_organization_advisory_wiring import (
            ProductiveOrganizationAdvisoryWiring,
        )
        from .relevance_evaluator import RelevanceEvaluator

        self._explicit_deliberation_producer = (
            ExplicitHumanDecisionDeliberationEvidenceProducer()
        )
        self._explicit_deliberation_adapter = (
            ExplicitDeliberationDecisionOptionAdapter()
        )
        self._decision_advisory_realizer = DecisionAdvisoryConversationalRealizer()
        self._complex_decision_intake = (
            ExplicitComplexDecisionIntakeEnvelopeFoundationV1()
        )
        self._gcdr_intake_integration = ProductiveGCDRIntakeIntegrationV1()
        self._gcdr_intake_realizer = GCDRIntakeConversationalRealizerV1()
        self._complex_decision_complete_status = (
            ExplicitComplexDecisionIntakeEnvelopeStatus.COMPLETE
        )
        self._organization_advisory_wiring = ProductiveOrganizationAdvisoryWiring(
            self._runtime
        )
        self._explicit_deliberation_status = ExplicitDecisionDeliberationStatus.EXPLICIT
        self._applied_conversational_intelligence = AppliedConversationalIntelligence()
        self._natural_governed_conversational_response = (
            NaturalGovernedConversationalResponse()
        )
        self._governed_action_preparation = GovernedActionPreparation()
        self._governed_cognitive_judgment = GovernedCognitiveJudgmentAuthority()
        self._governed_objective_memory = GovernedObjectiveMemory()
        self._governed_permanent_knowledge = GovernedPermanentKnowledge()
        self._governed_proactive_care = GovernedProactiveCare()
        self._governed_plan_model = GovernedPlanModel()
        self._governed_plan_continuity = GovernedPlanContinuity()
        self._governed_proposal_model = GovernedProposalModel()
        self._governed_proposal_inbox = GovernedProposalInbox()
        self._governed_proposal_inbox_query = GovernedProposalInboxQuery(
            self._governed_proposal_inbox
        )
        self._governed_proposal_lifecycle = GovernedProposalLifecycle(
            self._governed_proposal_inbox
        )
        self._governed_proposal_presentation_policy = (
            GovernedProposalPresentationPolicy()
        )
        self._governed_information_sources = GovernedInformationSources()
        self._governed_conversational_source_selector = (
            GovernedConversationalSourceSelector(self._governed_information_sources)
        )
        self._governed_information_normalizer = GovernedInformationNormalizer(
            self._governed_information_sources
        )
        self._governed_source_query_contract = GovernedSourceQueryContract(
            self._governed_information_sources
        )
        self._governed_source_query_executor = GovernedSourceQueryExecutor(
            self._governed_source_query_contract
        )
        self._nasa_governed_source_adapter = NasaGovernedSourceAdapter()
        self._apple_audiovisual_governed_source_adapter = (
            AppleAudiovisualGovernedSourceAdapter()
        )
        self._argentina_healthy_eating_governed_source_adapter = (
            ArgentinaHealthyEatingGovernedSourceAdapter()
        )
        self._cultura_caba_governed_source_adapter = CulturaCabaGovernedSourceAdapter()
        self._personal_on_demand_bulletin = PersonalOnDemandBulletin()
        self._personal_interest_center = PersonalInterestCenter()
        self._relevance_evaluator = RelevanceEvaluator(self._personal_interest_center)
        self._initiative_engine = PersonalInitiativeEngine(self._relevance_evaluator)
        self._productive_curiosity_wiring = ProductiveConversationalCuriosityWiring(
            self._relevance_evaluator,
            self._initiative_engine,
        )
        self._productive_governed_learning_wiring = ProductiveGovernedLearningWiring(
            self._governed_learning_memory_gateway
        )
        self._governed_initiative_engine = GovernedInitiativeEngine(
            self._relevance_evaluator,
            self._governed_proposal_model,
            self._governed_proposal_inbox,
        )
        self._cognitive_authority_map = CognitiveAuthorityMap()
        self._canonical_cognitive_cycle = CanonicalCognitiveCycle(
            authority_map=self._cognitive_authority_map
        )
        self._cognitive_integration_adapters = CognitiveIntegrationAdapters(
            authority_map=self._cognitive_authority_map,
            cycle=self._canonical_cognitive_cycle,
        )

    @property
    def bootstrap(self):
        return self._runtime.bootstrap

    @property
    def history(self):
        return self._runtime.history

    @property
    def traces(self):
        return self._runtime.traces

    @property
    def canonical_cognitive_core(self):
        return self._canonical_cognitive_core.snapshot

    @property
    def canonical_cognitive_state(self):
        return self._canonical_cognitive_state.snapshot

    @property
    def canonical_decision(self):
        return self._canonical_decision.snapshot

    @property
    def canonical_memory(self):
        return self._canonical_memory.snapshot

    @property
    def canonical_planning(self):
        return self._canonical_planning.snapshot

    @property
    def canonical_reflection(self):
        return self._canonical_reflection.snapshot

    @property
    def governed_cognitive_judgment(self):
        return self._governed_cognitive_judgment.snapshot

    def assess_governed_cognitive_judgment(
        self,
        *,
        objective_ids,
        knowledge_fact_ids=(),
        **judgment_fields,
    ):
        objectives = tuple(
            self._governed_objective_memory._require(objective_id)
            for objective_id in objective_ids
        )
        knowledge_facts = tuple(
            self._governed_permanent_knowledge._require(fact_id)
            for fact_id in knowledge_fact_ids
        )
        return self._governed_cognitive_judgment.assess(
            objectives,
            knowledge_facts,
            **judgment_fields,
        )

    def find_governed_cognitive_judgment(self, judgment_id: str):
        return self._governed_cognitive_judgment.find(judgment_id)

    def governed_judgments_for_objective(self, objective_id: str):
        return self._governed_cognitive_judgment.for_objective(objective_id)

    @property
    def governed_proactive_care(self):
        return self._governed_proactive_care.snapshot

    def propose_governed_proactive_care(self, *, judgment_id, **proposal_fields):
        judgment = self._governed_cognitive_judgment.find(judgment_id)
        if judgment is None:
            from domain.exceptions import DomainError

            raise DomainError(f"unknown governed judgment: {judgment_id}")
        return self._governed_proactive_care.propose(
            judgment,
            **proposal_fields,
        )

    def find_governed_care_proposal(self, proposal_id: str):
        return self._governed_proactive_care.find(proposal_id)

    def governed_care_proposals_for_objective(self, objective_id: str):
        return self._governed_proactive_care.for_objective(objective_id)

    def governed_care_proposals_for_beneficiary(self, beneficiary: str):
        return self._governed_proactive_care.for_beneficiary(beneficiary)

    @property
    def governed_permanent_knowledge(self):
        return self._governed_permanent_knowledge.snapshot

    def remember_governed_knowledge(self, **fact_fields):
        return self._governed_permanent_knowledge.remember(**fact_fields)

    def find_governed_knowledge(self, fact_id: str):
        return self._governed_permanent_knowledge.find(fact_id)

    def active_governed_knowledge(self, *, owner=None, kind=None):
        return self._governed_permanent_knowledge.active(owner=owner, kind=kind)

    def governed_knowledge_history(self, fact_id: str):
        return self._governed_permanent_knowledge.history(fact_id)

    def revise_governed_knowledge(self, fact_id: str, **revision_fields):
        return self._governed_permanent_knowledge.revise(fact_id, **revision_fields)

    def retract_governed_knowledge(
        self, fact_id: str, *, accepted_by, observed_at=None
    ):
        return self._governed_permanent_knowledge.retract(
            fact_id,
            accepted_by=accepted_by,
            observed_at=observed_at,
        )

    @property
    def governed_objective_memory(self):
        return self._governed_objective_memory.snapshot

    def remember_governed_objective(self, **objective_fields):
        return self._governed_objective_memory.remember(**objective_fields)

    def find_governed_objective(self, objective_id: str):
        return self._governed_objective_memory.find(objective_id)

    def active_governed_objectives(self, *, owner: str | None = None):
        return self._governed_objective_memory.active(owner=owner)

    def set_governed_objective_state(
        self, objective_id: str, state, *, observed_at=None
    ):
        return self._governed_objective_memory.set_state(
            objective_id, state, observed_at=observed_at
        )

    def link_governed_objective_plan(
        self, objective_id: str, plan_id: str, *, observed_at=None
    ):
        return self._governed_objective_memory.link_plan(
            objective_id, plan_id, observed_at=observed_at
        )

    @property
    def governed_plan_model(self):
        return self._governed_plan_model.snapshot

    def create_governed_plan(self, **plan_fields):
        return self._governed_plan_model.create(**plan_fields)

    @property
    def governed_plan_continuity(self):
        return self._governed_plan_continuity.snapshot

    def track_governed_plan_continuity(self, objective_id: str, plan):
        objective = self._governed_objective_memory._require(objective_id)
        return self._governed_plan_continuity.track(objective, plan)

    def current_governed_plan(self, objective_id: str, plan_id: str):
        return self._governed_plan_continuity.current(objective_id, plan_id)

    def governed_plan_history(self, objective_id: str, plan_id: str):
        return self._governed_plan_continuity.history(objective_id, plan_id)

    def governed_plan_reviews(self, objective_id: str, plan_id: str):
        return self._governed_plan_continuity.reviews(objective_id, plan_id)

    def review_governed_plan(self, objective_id: str, plan_id: str, **review_fields):
        objective = self._governed_objective_memory._require(objective_id)
        return self._governed_plan_continuity.review(
            objective,
            plan_id,
            **review_fields,
        )

    @property
    def governed_action_preparation(self):
        return self._governed_action_preparation.snapshot

    def prepare_governed_action(self, objective_id: str, plan_id: str, **action_fields):
        objective = self._governed_objective_memory._require(objective_id)
        plan = self._governed_plan_continuity.current(objective_id, plan_id)
        if plan is None:
            from domain.exceptions import DomainError

            raise DomainError("unknown tracked plan for objective")
        return self._governed_action_preparation.prepare(
            objective,
            plan,
            **action_fields,
        )

    def find_governed_action_candidate(self, action_id: str):
        return self._governed_action_preparation.find(action_id)

    def governed_action_candidates(self, objective_id: str, plan_id: str):
        return self._governed_action_preparation.for_plan(objective_id, plan_id)

    @property
    def governed_proposal_model(self):
        return self._governed_proposal_model.snapshot

    def create_governed_proposal(self, **proposal_fields):
        return self._governed_proposal_model.create(**proposal_fields)

    @property
    def governed_proposal_inbox(self):
        return self._governed_proposal_inbox.snapshot

    def enqueue_governed_proposal(self, proposal, *, observed_at=None):
        return self._governed_proposal_inbox.enqueue(proposal, observed_at=observed_at)

    def pending_governed_proposals(self, *, observed_at=None):
        return self._governed_proposal_inbox.pending(observed_at=observed_at)

    def find_governed_proposal(self, proposal_id: str):
        return self._governed_proposal_inbox.find(proposal_id)

    @property
    def governed_proposal_inbox_query(self):
        return self._governed_proposal_inbox_query.snapshot

    def query_governed_proposal_inbox(self, request=None, *, observed_at=None):
        return self._governed_proposal_inbox_query.query(
            request,
            observed_at=observed_at,
        )

    @property
    def governed_proposal_lifecycle(self):
        return self._governed_proposal_lifecycle.snapshot

    def offer_governed_proposal(self, proposal_id: str, *, observed_at=None):
        return self._governed_proposal_lifecycle.offer(
            proposal_id,
            observed_at=observed_at,
        )

    def accept_governed_proposal(self, proposal_id: str, *, observed_at=None):
        return self._governed_proposal_lifecycle.accept(
            proposal_id,
            observed_at=observed_at,
        )

    def dismiss_governed_proposal(self, proposal_id: str, *, observed_at=None):
        return self._governed_proposal_lifecycle.dismiss(
            proposal_id,
            observed_at=observed_at,
        )

    def expire_governed_proposals(self, *, observed_at=None):
        return self._governed_proposal_lifecycle.expire_due(observed_at=observed_at)

    @property
    def governed_proposal_presentation_policy(self):
        return self._governed_proposal_presentation_policy.snapshot

    def evaluate_governed_proposal_presentation(
        self,
        proposal_id: str,
        context=None,
        *,
        observed_at=None,
    ):
        proposal = self._governed_proposal_inbox.find(proposal_id)
        if proposal is None:
            from domain.exceptions import DomainError

            raise DomainError(f"unknown proposal_id: {proposal_id}")
        return self._governed_proposal_presentation_policy.evaluate(
            proposal,
            context,
            observed_at=observed_at,
        )

    def next_presentable_governed_proposal(
        self,
        context=None,
        *,
        observed_at=None,
    ):
        pending = self._governed_proposal_inbox.pending(observed_at=observed_at)
        decisions = (
            self._governed_proposal_presentation_policy.evaluate(
                proposal,
                context,
                observed_at=observed_at,
            )
            for proposal in pending
        )
        return next((item for item in decisions if item.presentable), None)

    @property
    def governed_initiative_engine(self):
        return self._governed_initiative_engine.snapshot

    def generate_governed_initiative(self, candidate, *, observed_at=None):
        return self._governed_initiative_engine.generate(
            candidate,
            observed_at=observed_at,
        )

    @property
    def governed_information_sources(self):
        return self._governed_information_sources.snapshot

    def classify_information_source(self, source_id: str):
        return self._governed_information_sources.classify(source_id)

    def accept_information_item(self, item):
        return self._governed_information_sources.accept(item)

    @property
    def governed_information_normalizer(self):
        return self._governed_information_normalizer.snapshot

    def normalize_information(self, raw):
        return self._governed_information_normalizer.normalize(raw)

    def normalize_information_candidate(self, raw):
        return self._governed_information_normalizer.normalize_to_candidate(raw)

    @property
    def last_applied_owner_turn_result(self):
        return self._last_applied_owner_turn_result

    @property
    def applied_conversational_intelligence(self):
        return self._applied_conversational_intelligence.snapshot

    def interpret_applied_conversational_intelligence(self, text: str):
        return self._applied_conversational_intelligence.interpret(text)

    @property
    def natural_governed_conversational_response(self):
        return self._natural_governed_conversational_response.snapshot

    def execute_applied_conversational_intelligence(self, text: str):
        from .applied_conversational_intelligence import (
            AppliedConversationalIntelligence,
            AppliedConversationalIntelligenceResult,
        )

        interpretation = self.interpret_applied_conversational_intelligence(text)
        request = interpretation.request
        if request is None:
            return AppliedConversationalIntelligenceResult(
                interpretation=interpretation,
                selection=None,
                conversational_result=None,
            )
        if AppliedConversationalIntelligence.requires_original_images(text):
            return self._unverified_original_images(interpretation)
        selection, result = self.execute_selected_governed_conversational_query(request)
        natural_answer = self._natural_governed_conversational_response.compose(
            query_text=request.query_text,
            selection=selection,
            result=result,
        )
        return AppliedConversationalIntelligenceResult(
            interpretation=interpretation,
            selection=selection,
            conversational_result=result,
            natural_answer_text=natural_answer,
        )

    @staticmethod
    def _unverified_original_images(interpretation):
        from .applied_conversational_intelligence import (
            AppliedConversationalIntelligenceResult,
        )

        return AppliedConversationalIntelligenceResult(
            interpretation=interpretation,
            selection=None,
            conversational_result=None,
            natural_answer_text=(
                "No tengo una fuente que confirme cuáles son esas imágenes inéditas. "
                "Si querés imágenes generales del tema, pedímelas sin esa condición."
            ),
        )

    @property
    def personal_on_demand_bulletin(self):
        return self._personal_on_demand_bulletin.snapshot

    def execute_personal_on_demand_bulletin(self, text: str):
        return self._personal_on_demand_bulletin.execute(
            text,
            execute_request=self.execute_selected_governed_conversational_query,
        )

    @property
    def governed_conversational_source_selection(self):
        return self._governed_conversational_source_selector.snapshot

    def select_governed_conversational_source(self, request):
        return self._governed_conversational_source_selector.select(
            request,
            registered_sources=(
                self._governed_source_query_executor.snapshot.registered_sources
            ),
        )

    def execute_selected_governed_conversational_query(self, request):
        from .governed_conversational_query import GovernedConversationalQuery

        selection = self.select_governed_conversational_source(request)
        if selection.query is None:
            return selection, None
        conversational_request = GovernedConversationalQuery(
            text=request.text,
            query=selection.query,
        )
        return (
            selection,
            self.execute_governed_conversational_query(conversational_request),
        )

    @property
    def governed_conversational_query(self):
        from .governed_conversational_query import snapshot

        return snapshot()

    def execute_governed_conversational_query(self, request):
        from .governed_conversational_query import (
            GovernedConversationalInformation,
            GovernedConversationalQueryResult,
            GovernedConversationalQueryStatus,
            immutable_item,
            raw_information_from_item,
        )
        from .governed_source_query import GovernedSourceQueryStatus

        source_result = self._governed_source_query_executor.execute(request.query)
        response = source_result.response
        if response is None or response.status is GovernedSourceQueryStatus.FAILED:
            error = response.error if response is not None else None
            return GovernedConversationalQueryResult(
                request=request,
                status=GovernedConversationalQueryStatus.FAILED,
                source_result=source_result,
                items=(),
                answer_text=self._governed_conversational_answer(
                    request.query.source_id, 0, failed=True
                ),
                error=error,
            )

        items = []
        discarded_items = 0
        for raw_item in response.raw_items:
            try:
                raw = raw_information_from_item(raw_item, request.query)
                normalized = self._governed_information_normalizer.normalize(raw)
            except (TypeError, ValueError):
                discarded_items += 1
                continue
            candidate = normalized.as_relevance_candidate()
            relevance = self._relevance_evaluator.evaluate(candidate)
            items.append(
                GovernedConversationalInformation(
                    raw=immutable_item(raw_item),
                    normalized=normalized,
                    relevance=relevance,
                )
            )

        status = (
            GovernedConversationalQueryStatus.SUCCEEDED
            if items
            else GovernedConversationalQueryStatus.EMPTY
        )
        return GovernedConversationalQueryResult(
            request=request,
            status=status,
            source_result=source_result,
            items=tuple(items),
            answer_text=self._governed_conversational_answer(
                request.query.source_id, len(items), failed=False
            ),
            discarded_items=discarded_items,
        )

    @staticmethod
    def _governed_conversational_answer(
        source_id: str, item_count: int, *, failed: bool
    ) -> str:
        if failed:
            return f"No pude consultar la fuente gobernada {source_id}."
        if item_count == 0:
            return f"La fuente gobernada {source_id} no devolvió resultados válidos."
        suffix = "resultado" if item_count == 1 else "resultados"
        return f"Encontré {item_count} {suffix} en la fuente gobernada {source_id}."

    @property
    def governed_source_query_contract(self):
        return self._governed_source_query_contract.snapshot

    def prepare_governed_source_query(self, query):
        return self._governed_source_query_contract.prepare(query)

    def governed_source_query_unavailable_response(self, query):
        return self._governed_source_query_contract.unavailable_response(query)

    @property
    def governed_source_query_executor(self):
        return self._governed_source_query_executor.snapshot

    @property
    def governed_source_query_observability(self):
        return self._governed_source_query_executor.observability

    @property
    def governed_source_query_observations(self):
        return self._governed_source_query_executor.observations

    def register_governed_source_query_adapter(self, source_id, adapter):
        self._governed_source_query_executor.register(source_id, adapter)

    def execute_governed_source_query(self, query):
        return self._governed_source_query_executor.execute(query)

    @property
    def nasa_governed_source(self):
        return self._nasa_governed_source_adapter.snapshot

    def enable_nasa_governed_source(self):
        self._governed_source_query_executor.register(
            self._nasa_governed_source_adapter.SOURCE_ID,
            self._nasa_governed_source_adapter,
        )
        return self._nasa_governed_source_adapter.snapshot

    @property
    def apple_audiovisual_governed_source(self):
        return self._apple_audiovisual_governed_source_adapter.snapshot

    def enable_apple_audiovisual_governed_source(self):
        self._governed_source_query_executor.register(
            self._apple_audiovisual_governed_source_adapter.SOURCE_ID,
            self._apple_audiovisual_governed_source_adapter,
        )
        return self._apple_audiovisual_governed_source_adapter.snapshot

    @property
    def argentina_healthy_eating_governed_source(self):
        return self._argentina_healthy_eating_governed_source_adapter.snapshot

    def enable_argentina_healthy_eating_governed_source(self):
        self._governed_source_query_executor.register(
            self._argentina_healthy_eating_governed_source_adapter.SOURCE_ID,
            self._argentina_healthy_eating_governed_source_adapter,
        )
        return self._argentina_healthy_eating_governed_source_adapter.snapshot

    @property
    def cultura_caba_governed_source(self):
        return self._cultura_caba_governed_source_adapter.snapshot

    def enable_cultura_caba_governed_source(self):
        self._governed_source_query_executor.register(
            self._cultura_caba_governed_source_adapter.SOURCE_ID,
            self._cultura_caba_governed_source_adapter,
        )
        return self._cultura_caba_governed_source_adapter.snapshot

    @property
    def personal_interest_center(self):
        return self._personal_interest_center.snapshot

    @property
    def relevance_evaluator(self):
        return self._relevance_evaluator.snapshot

    def evaluate_relevance(self, candidate):
        return self._relevance_evaluator.evaluate(candidate)

    @property
    def initiative_engine(self):
        return self._initiative_engine.snapshot

    def propose_initiative(self, candidate, *, context=None):
        return self._initiative_engine.propose(candidate, context=context)

    @property
    def cognitive_inventory(self):
        return self._cognitive_observer.snapshot

    @property
    def cognitive_authority_map(self):
        return self._cognitive_authority_map.snapshot

    @property
    def canonical_cognitive_cycle(self):
        return self._canonical_cognitive_cycle.snapshot

    @property
    def cognitive_integration_adapters(self):
        return self._cognitive_integration_adapters.snapshot

    @property
    def target_cognitive_cycle_evidence(self):
        return self._conversation_entry_evidence.snapshot

    @property
    def operational_cycle_diagnostic(self):
        from core.cognitive_maturity import diagnose_operational_cycles

        return diagnose_operational_cycles(
            self._conversation_entry_evidence.snapshot.cycles
        )

    @property
    def post_m387_operational_baseline(self):
        from core.cognitive_maturity import diagnose_post_m387_baseline

        return diagnose_post_m387_baseline(self.operational_cycle_diagnostic)

    @property
    def m388_gap_closure_diagnostic(self):
        from core.cognitive_maturity import diagnose_m388_gap_closure

        return diagnose_m388_gap_closure(self.operational_cycle_diagnostic)

    @property
    def cognitive_turn_dossiers(self):
        from core.cognitive_maturity import (
            create_cognitive_turn_dossier_snapshot,
        )

        return create_cognitive_turn_dossier_snapshot(
            self._conversation_entry_evidence.snapshot.cycles
        )

    @property
    def interlocutor_sessions(self):
        return self._conversational_identification.state.snapshot

    @property
    def snapshot(self) -> OfficialConversationGatewaySnapshot:
        session_id = self._effective_session_id(self._last_session_id)
        return OfficialConversationGatewaySnapshot(
            submitted_turns=self._submitted_turns,
            last_origin=self._last_origin,
            last_session_id=self._last_session_id,
            analysis_mode=self.analysis_mode_status(session_id),
        )

    def analysis_mode_status(
        self, session_id: str | None = None
    ) -> "OfficialConversationGateway.AnalysisModeStatus":
        """Return the ephemeral analysis-mode state for one conversation session."""
        effective_session_id = self._effective_session_id(session_id)
        return self._analysis_mode_by_session.get(
            effective_session_id,
            self.AnalysisModeStatus(active=False, level=None),
        )

    def analysis_mode_command(
        self, text: str
    ) -> "OfficialConversationGateway.AnalysisModeCommand | None":
        """Recognize only explicit analysis-mode interaction commands."""
        normalized = " ".join(text.casefold().strip().split())
        if normalized in {
            "¿está activo el modo análisis?",
            "está activo el modo análisis?",
            "estado del modo análisis",
        }:
            return self.AnalysisModeCommand("status")
        if normalized in {
            "salir del modo análisis",
            "desactivar modo análisis",
            "volver al modo normal",
        }:
            return self.AnalysisModeCommand("exit")
        explicit_prefixes = (
            "entrar en modo análisis",
            "activar modo análisis",
            "modo análisis",
        )
        if not normalized.startswith(explicit_prefixes):
            return None
        level = self.AnalysisModeLevel.PERSONAL
        if "arquitect" in normalized:
            level = self.AnalysisModeLevel.ARCHITECTURAL
        elif "técnic" in normalized or "tecnic" in normalized:
            level = self.AnalysisModeLevel.TECHNICAL
        elif "personal" in normalized:
            level = self.AnalysisModeLevel.PERSONAL
        return self.AnalysisModeCommand("enter", level)

    def apply_analysis_mode_command(
        self,
        text: str,
        *,
        session_id: str | None = None,
    ) -> "OfficialConversationGateway.AnalysisModeStatus | None":
        """Apply an explicit mode command without invoking cognitive authorities."""
        command = self.analysis_mode_command(text)
        if command is None:
            return None
        effective_session_id = self._effective_session_id(session_id)
        if command.action == "enter":
            status = self.AnalysisModeStatus(active=True, level=command.level)
            self._analysis_mode_by_session[effective_session_id] = status
            return status
        if command.action == "exit":
            self._analysis_mode_by_session.pop(effective_session_id, None)
        return self.analysis_mode_status(effective_session_id)

    from typing import TYPE_CHECKING as _TYPE_CHECKING

    if _TYPE_CHECKING:
        from .unified_runtime_observability import (
            InvestigationEpisodeBudgetObservabilityScope,
        )

    def analysis_mode_projection(
        self,
        runtime,
        *,
        session_id: str | None = None,
        investigation_scope: (
            "InvestigationEpisodeBudgetObservabilityScope | None"
        ) = None,
    ):
        """Select a governed read-only observability view for the active level."""
        status = self.analysis_mode_status(session_id)
        if not status.active or status.level is None:
            return None
        from .unified_runtime_observability import UnifiedRuntimeObservability

        snapshot = UnifiedRuntimeObservability().snapshot(
            runtime, investigation_scope=investigation_scope
        )
        sections: list[tuple[str, object]] = []
        unavailable: list[str] = []

        if status.level is self.AnalysisModeLevel.PERSONAL:
            sections.extend(
                (
                    ("cognitive_core", snapshot.cognitive_core),
                    ("conversation", snapshot.conversation),
                )
            )
            if snapshot.self_model is None:
                unavailable.append("self_model: unavailable")
            else:
                sections.append(("self_model", snapshot.self_model))

        elif status.level is self.AnalysisModeLevel.TECHNICAL:
            sections.extend(
                (
                    ("operational", snapshot.operational),
                    ("readiness", snapshot.readiness),
                    ("conversation", snapshot.conversation),
                    ("registered_capabilities", snapshot.registered_capabilities),
                    ("capability_registry", snapshot.capability_registry),
                    ("cognitive_core", snapshot.cognitive_core),
                    ("self_diagnostics", snapshot.self_diagnostics),
                )
            )
            if snapshot.capabilities is None:
                unavailable.append("capabilities: unavailable")
            else:
                sections.append(("capabilities", snapshot.capabilities))
            if snapshot.capability_dependencies is None:
                unavailable.append("capability_dependencies: not provisioned")
            else:
                sections.append(
                    ("capability_dependencies", snapshot.capability_dependencies)
                )
            if snapshot.investigation_episode_budget is None:
                unavailable.append("investigation_episode_budget: not provisioned")
            else:
                sections.append(
                    (
                        "investigation_episode_budget",
                        snapshot.investigation_episode_budget,
                    )
                )
            if snapshot.recovery is None:
                unavailable.append("recovery: not provisioned")
            else:
                sections.append(("recovery", snapshot.recovery))

        elif status.level is self.AnalysisModeLevel.ARCHITECTURAL:
            sections.extend(
                (
                    ("reflection_architecture", snapshot.reflection.architecture),
                    ("capability_registry", snapshot.capability_registry),
                    ("self_diagnostics", snapshot.self_diagnostics),
                )
            )
            if snapshot.reflection.published_state is None:
                unavailable.append("reflection_published_state: unavailable")
            else:
                sections.append(
                    ("reflection_published_state", snapshot.reflection.published_state)
                )
            unavailable.append("architectural_evidence: not provisioned")

        return self.AnalysisModeProjection(
            level=status.level,
            sections=tuple(sections),
            unavailable=tuple(unavailable),
        )

    def analysis_mode_conversational_projection(
        self, runtime, *, session_id: str | None = None
    ):
        """Return a stable conversational shape without exposing the raw snapshot."""
        projection = self.analysis_mode_projection(runtime, session_id=session_id)
        if projection is None:
            return None
        return projection.as_dict()


    @staticmethod
    def _is_anaphoric_visual_request(interpretation):
        """Identify visual requests with an unresolved subject reference."""
        import re

        request = getattr(interpretation, 'request', None)
        if request is None:
            return False

        mode = getattr(request, 'mode', None)
        if getattr(mode, 'value', mode) != 'open_visual_subject':
            return False

        query = getattr(request, 'query_text', None)
        if not isinstance(query, str):
            return False

        return bool(re.match(
            r'^\s*(?:(?:el|la|los|las)\s+)?'
            r'(?:mismo|misma|mismos|mismas|ese|esa|esos|esas)\b',
            query.casefold(),
        ))

    def _resolve_applied_contextual_follow_up(self, text, session_id):
        """Resolve an explicit follow-up within the authorized runtime session."""
        from core.cognitive_maturity import IdentityContextAccessGate

        from .applied_conversational_intelligence import (
            AppliedConversationalIntelligence,
            AppliedConversationalIntelligenceInterpretation,
            AppliedConversationalIntelligenceResult,
            AppliedConversationalIntelligenceStatus,
        )
        from .contextual_follow_up_interpreter import (
            FollowUpIntent,
            interpret_contextual_follow_up,
        )
        from .governed_source_query import GovernedSourceQueryOrder

        if not IdentityContextAccessGate.current().shared_conversation_context_allowed:
            return None

        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = getattr(config, "owner", None)
        configured_session = getattr(config, "session_id", None)

        if (
            not isinstance(owner, str)
            or not isinstance(configured_session, str)
            or configured_session != session_id
        ):
            return None

        follow_up = interpret_contextual_follow_up(text)
        bare_visual = AppliedConversationalIntelligence.is_bare_visual_request(text)
        if not bare_visual and follow_up.intent not in (
            FollowUpIntent.CONTINUE,
            FollowUpIntent.REORDER,
        ):
            return None

        reader = getattr(
            self._runtime, "authorized_recent_turns", None
        )
        if not callable(reader):
            return None

        history = reader()
        if not history:
            return None

        previous = history[-1]

        latest_matches = getattr(
            self._runtime, "authorized_latest_turn_matches", None
        )
        if not callable(latest_matches) or not latest_matches(previous):
            return None

        if (
            previous.owner.casefold() != owner.casefold()
            or previous.session_id != session_id
            or str(previous.response_path) not in (
                "interceptor",
                "ConversationResponsePath.INTERCEPTOR",
            )
        ):
            return None

        if bare_visual and (
            "current_affairs_headline_expanded" in getattr(previous, "rationale", ())
        ):
            import re

            headline = re.match(r"Sobre «([^»\n]+)»", previous.response_text)
            if headline is not None:
                subject = headline[1]
                if len(subject) <= 300:
                    visual = self.interpret_applied_conversational_intelligence(
                        f"Mostrame imágenes de {subject}"
                    )
                    if visual.request is not None:
                        request = replace(visual.request, text=text)
                        if AppliedConversationalIntelligence.requires_original_images(subject):
                            return self._unverified_original_images(
                                replace(visual, text=text, request=request)
                            )
                        selection, result = self.execute_selected_governed_conversational_query(
                            request
                        )
                        answer = self._natural_governed_conversational_response.compose(
                            query_text=subject, selection=selection, result=result
                        )
                        return AppliedConversationalIntelligenceResult(
                            interpretation=replace(visual, text=text, request=request),
                            selection=selection,
                            conversational_result=result,
                            natural_answer_text=answer,
                        )

        expected_sequence = getattr(previous, "sequence", None)

        if not isinstance(expected_sequence, int):
            return None

        for candidate in reversed(history):
            if (
                candidate.owner.casefold() != owner.casefold()
                or candidate.session_id != session_id
                or str(candidate.response_path)
                not in (
                    "interceptor",
                    "ConversationResponsePath.INTERCEPTOR",
                )
                or getattr(candidate, "sequence", None)
                != expected_sequence
                or "applied_conversational_intelligence"
                not in getattr(candidate, "rationale", ())
            ):
                return None

            earlier = self.interpret_applied_conversational_intelligence(
                candidate.user_text
            )

            if (
                earlier.request is not None
                and not self._is_anaphoric_visual_request(earlier)
            ):
                break

            intermediate = interpret_contextual_follow_up(
                candidate.user_text
            )

            if intermediate.intent not in (
                FollowUpIntent.CONTINUE,
                FollowUpIntent.REORDER,
            ):
                return None

            expected_sequence -= 1
        else:
            return None

        request = earlier.request
        if request is None:
            return None

        updated_query = request.query_text or previous.user_text
        order = (
            GovernedSourceQueryOrder.NEWEST_FIRST
            if follow_up.newest_first
            else request.order
        )

        updated_request = replace(
            request,
            text=text,
            query_text=updated_query,
            order=order,
        )

        interpretation = AppliedConversationalIntelligenceInterpretation(
            text=text,
            status=AppliedConversationalIntelligenceStatus.RECOGNIZED,
            request=updated_request,
            matched_topics=earlier.matched_topics,
        )

        selection, result = self.execute_selected_governed_conversational_query(
            updated_request
        )
        natural_answer = self._natural_governed_conversational_response.compose(
            query_text=updated_request.query_text,
            selection=selection,
            result=result,
        )
        return AppliedConversationalIntelligenceResult(
            interpretation=interpretation,
            selection=selection,
            conversational_result=result,
            natural_answer_text=natural_answer,
        )

    def submit(
        self,
        text: str,
        *,
        origin: ConversationOrigin = ConversationOrigin.INTERNAL,
        session_id: str | None = None,
        now: datetime | None = None,
        external_evidence: tuple[CognitiveExternalEvidenceAdmission, ...] = (),
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
        organization_references=(),
        curiosity_report=None,
        curiosity_relevance_candidate=None,
        curiosity_initiative_context=None,
        learning_approval_evaluation=None,
        learning_approval_response=None,
        knowledge_revision_approval_response=None,
        governed_memory_write_request=None,
        governed_knowledge_revision_request=None,
        knowledge_revision_execution_authorization=None,
        _causal_result_receiver=None,
        _post_turn_observer=None,
    ) -> LocalConversationTurn:
        self._last_applied_owner_turn_result = None
        causal_applied_result = None
        observation_id = self._cognitive_observer.begin_turn(
            origin=origin.value,
            session_id=session_id,
            now=now,
        )
        self._conversation_entry_evidence.begin(observation_id)
        coordination_record = self._unified_coordination_evidence.current_record()
        if coordination_record is not None:
            self._conversation_entry_evidence.observe(
                observation_id,
                coordination_record,
            )

        def observe_identity_context(record):
            self._conversation_entry_evidence.observe(observation_id, record)

        observe_identity_context(
            self._text_perception_evidence.observe_input(
                text=text,
                origin=origin,
            )
        )

        runtime_converse_called = False

        def converse_runtime(text_value: str, **kwargs):
            nonlocal runtime_converse_called
            runtime_converse_called = True
            if (
                explicit_document_ids
                or explicit_sources
                or explicit_evidence_references
                or integrated_visual_context is not None
            ):
                return self._runtime.converse(
                    text_value,
                    explicit_document_ids=explicit_document_ids,
                    explicit_sources=explicit_sources,
                    explicit_evidence_references=explicit_evidence_references,
                    integrated_visual_context=integrated_visual_context,
                    **kwargs,
                )
            return self._runtime.converse(text_value, **kwargs)

        effective_session_id = self._effective_session_id(session_id)
        self.apply_analysis_mode_command(text, session_id=effective_session_id)
        current_resolution = self._conversational_identification.state.current(
            effective_session_id
        )
        runtime_session_id = self._runtime_session_id(effective_session_id)
        has_explicit_context = bool(
            explicit_document_ids
            or explicit_sources
            or explicit_evidence_references
            or integrated_visual_context is not None
        )

        def applied_or_runtime(external_evidence_value=()):
            nonlocal causal_applied_result
            if (
                not external_evidence_value
                and not has_explicit_context
                and local_music_command(text) is None
                and not CurrentAffairsRouter.is_headline_followup_phrase(text)
                and not CurrentAffairsRouter.is_headline_feed_request(text)
                and not CurrentAffairsRouter.is_recent_nasa_mission_information_request(
                    text
                )
            ):
                preliminary = self.interpret_applied_conversational_intelligence(text)
                anaphoric_visual = self._is_anaphoric_visual_request(preliminary)
                if anaphoric_visual:
                    applied_result = self._resolve_applied_contextual_follow_up(
                        text,
                        effective_session_id,
                    )
                else:
                    applied_result = self.execute_applied_conversational_intelligence(text)
                    if getattr(applied_result.interpretation, "request", None) is None:
                        contextual = self._resolve_applied_contextual_follow_up(
                            text,
                            effective_session_id,
                        )
                        if contextual is not None:
                            applied_result = contextual
                interpretation = getattr(applied_result, "interpretation", None)
                if getattr(interpretation, "request", None) is not None:
                    causal_applied_result = applied_result
                    self._last_applied_owner_turn_result = applied_result
                    return self._applied_owner_turn(
                        text,
                        applied_result,
                        session_id=effective_session_id,
                        now=now,
                    )
            with self._epistemic_evidence.capture(observe_identity_context):
                if external_evidence_value:
                    if now is None:
                        return converse_runtime(
                            text,
                            external_evidence=(external_evidence_value),
                        )
                    return converse_runtime(
                        text,
                        now=now,
                        external_evidence=(external_evidence_value),
                    )
                if now is None:
                    return converse_runtime(text)
                return converse_runtime(text, now=now)

        identification_flow = self._conversational_identification
        identity_evidence = self._identity_context_evidence
        reflection_evidence = self._reflection_learning_evidence
        observe_learning = reflection_evidence.observe_learning_candidate
        observe_diagnostics = reflection_evidence.observe_diagnostics
        governed_learning_wiring = self._productive_governed_learning_wiring
        revision_approval_response = knowledge_revision_approval_response
        revision_request = governed_knowledge_revision_request
        revision_authorization = knowledge_revision_execution_authorization
        revision_not_applied_turn = self._governed_revision_not_applied_turn
        with self._cognitive_state_evidence.capture(observe_identity_context):
            self._cognitive_state_evidence.observe_facade(
                self._canonical_cognitive_state
            )
        try:
            with self._identity_context_access.activate(
                current_resolution,
                session_id=effective_session_id,
                context_session_id=runtime_session_id,
            ):
                with self._memory_knowledge_evidence.capture(observe_identity_context):
                    with self._intent_reasoning_evidence.capture(
                        observe_identity_context
                    ):
                        with self._planning_decision_evidence.capture(
                            observe_identity_context
                        ):
                            with self._reflection_learning_evidence.capture(
                                observe_identity_context
                            ):
                                with self._response_action_evidence.capture(
                                    observe_identity_context
                                ):
                                    with self._identity_context_evidence.capture(
                                        observe_identity_context,
                                        interlocutor_resolved=(
                                            current_resolution.interlocutor_resolved
                                        ),
                                    ):
                                        identification = identification_flow.process(
                                            text,
                                            session_id=effective_session_id,
                                        )
                                        if identification.handled:
                                            resolution = identification.resolution
                                            if resolution is None:
                                                raise ValueError(
                                                    "handled identification requires"
                                                    " resolution"
                                                )
                                            interlocutor_resolved = (
                                                resolution.interlocutor_resolved
                                            )
                                            identity_evidence.observe_resolution(
                                                coownership_scoped=True,
                                                session_scoped=True,
                                                context_bounded=True,
                                                interlocutor_resolved=(
                                                    interlocutor_resolved
                                                ),
                                            )
                                            turn = self._identification_turn(
                                                text,
                                                identification,
                                                session_id=effective_session_id,
                                                now=now,
                                            )
                                        elif (
                                            revision_approval_response
                                            is not None
                                            and not external_evidence
                                        ):
                                            revision_approval = (
                                                governed_learning_wiring
                                                .evaluate_pending_knowledge_revision(
                                                    effective_session_id,
                                                    (
                                                        revision_approval_response
                                                    ),
                                                )
                                            )
                                            revision_turn = (
                                                self._governed_revision_approval_turn
                                            )
                                            turn = revision_turn(
                                                text,
                                                revision_approval,
                                                session_id=effective_session_id,
                                                now=now,
                                            )
                                        elif (
                                            governed_knowledge_revision_request
                                            is not None
                                            and not external_evidence
                                        ):
                                            revision_result = (
                                                governed_learning_wiring
                                                .execute_certified_revision_request(
                                                    revision_request,
                                                    revision_authorization,
                                                )
                                            )
                                            if revision_result is None:
                                                turn = (
                                                    revision_not_applied_turn(
                                                        text,
                                                        revision_request,
                                                        session_id=(
                                                            effective_session_id
                                                        ),
                                                        now=now,
                                                    )
                                                )
                                            else:
                                                turn = self._governed_revision_turn(
                                                    text,
                                                    revision_request,
                                                    session_id=effective_session_id,
                                                    now=now,
                                                )
                                        elif (
                                            governed_memory_write_request is not None
                                            and not external_evidence
                                        ):
                                            learning_result = (
                                                governed_learning_wiring
                                                .execute_certified_write_request(
                                                    governed_memory_write_request
                                                )
                                            )
                                            turn = self._governed_learning_turn(
                                                text,
                                                learning_result,
                                                session_id=effective_session_id,
                                                now=now,
                                            )
                                        elif (
                                            learning_approval_evaluation is not None
                                            and learning_approval_response is not None
                                            and not external_evidence
                                        ):
                                            learning_result = (
                                                governed_learning_wiring.execute(
                                                    learning_approval_evaluation,
                                                    learning_approval_response,
                                                    current_turn_text=text,
                                                )
                                            )
                                            turn = self._governed_learning_turn(
                                                text,
                                                learning_result,
                                                session_id=effective_session_id,
                                                now=now,
                                            )
                                        elif (
                                            curiosity_report is not None
                                            and (
                                                curiosity_relevance_candidate
                                                is not None
                                            )
                                            and not external_evidence
                                        ):
                                            wiring = self._productive_curiosity_wiring
                                            assembly = wiring.assemble(
                                                curiosity_report,
                                                curiosity_relevance_candidate,
                                                context=curiosity_initiative_context,
                                            )
                                            if assembly is not None:
                                                turn = self._curiosity_question_turn(
                                                    text,
                                                    assembly,
                                                    session_id=effective_session_id,
                                                    now=now,
                                                )
                                            elif now is None:
                                                with self._epistemic_evidence.capture(
                                                    observe_identity_context
                                                ):
                                                    turn = converse_runtime(text)
                                            else:
                                                with self._epistemic_evidence.capture(
                                                    observe_identity_context
                                                ):
                                                    turn = converse_runtime(
                                                        text,
                                                        now=now,
                                                    )
                                        elif not external_evidence:
                                            complex_intake = (
                                                self._complex_decision_intake
                                            )
                                            complex_status = (
                                                self._complex_decision_complete_status
                                            )
                                            gcdr_integration = (
                                                self._gcdr_intake_integration
                                            )
                                            gcdr_realizer = self._gcdr_intake_realizer
                                            intake = complex_intake.analyze(text)
                                            if intake.status is complex_status:
                                                integrate = gcdr_integration.integrate
                                                integration = integrate(intake)
                                                realization = gcdr_realizer.realize(
                                                    integration
                                                )
                                                turn = self._gcdr_advisory_turn(
                                                    text,
                                                    realization,
                                                    integration,
                                                    session_id=effective_session_id,
                                                    now=now,
                                                )
                                            else:
                                                producer = (
                                                    self._explicit_deliberation_producer
                                                )
                                                decision_status = (
                                                    self._explicit_deliberation_status
                                                )
                                                decision_adapter = (
                                                    self._explicit_deliberation_adapter
                                                )
                                                organization_wiring = (
                                                    self._organization_advisory_wiring
                                                )
                                                decision_realizer = (
                                                    self._decision_advisory_realizer
                                                )
                                                deliberation = producer.analyze(text)
                                                if (
                                                    deliberation.status
                                                    is decision_status
                                                ):
                                                    adaptation = decision_adapter.adapt(
                                                        deliberation
                                                    )
                                                    organization_assembly = (
                                                        organization_wiring.assemble(
                                                            adaptation,
                                                            tuple(
                                                                organization_references
                                                            ),
                                                        )
                                                    )
                                                    if organization_assembly is None:
                                                        decision = (
                                                            self._canonical_decision
                                                        )
                                                        report = decision.advise(
                                                            adaptation.options,
                                                            organization=None,
                                                            scenarios=None,
                                                            causal=None,
                                                        )
                                                    else:
                                                        report = getattr(
                                                            organization_assembly,
                                                            "advisory",
                                                        )
                                                    realization = (
                                                        decision_realizer.realize(
                                                            report,
                                                            deliberation,
                                                            adaptation,
                                                        )
                                                    )
                                                    turn = self._decision_advisory_turn(
                                                        text,
                                                        realization,
                                                        session_id=(
                                                            effective_session_id
                                                        ),
                                                        now=now,
                                                    )
                                                else:
                                                    turn = applied_or_runtime()
                                        else:
                                            turn = applied_or_runtime(
                                                external_evidence
                                            )
                                        relationship_authority = getattr(
                                            self._runtime,
                                            "relationship_memory",
                                            None,
                                        )
                                        relationship_snapshot = getattr(
                                            relationship_authority,
                                            "last_snapshot",
                                            None,
                                        )
                                        personality_profile = getattr(
                                            self._runtime,
                                            "adaptive_personality_profile",
                                            None,
                                        )
                                        active_resolution = (
                                            identification.resolution
                                            or current_resolution
                                        )
                                        interlocutor_is_resolved = (
                                            active_resolution.interlocutor_resolved
                                        )
                                        relational_evidence = (
                                            self._relational_affective_evidence
                                        )
                                        with relational_evidence.capture(
                                            observe_identity_context
                                        ):
                                            relational_evidence.observe_context(
                                                interlocutor_resolved=(
                                                    interlocutor_is_resolved
                                                ),
                                                relationship_snapshot=(
                                                    relationship_snapshot
                                                ),
                                                personality_profile=(
                                                    personality_profile
                                                ),
                                            )
                                        response_status = getattr(turn, "status", None)
                                        if response_status is not None:
                                            response_evidence = (
                                                self._response_action_evidence
                                            )
                                            response_evidence.observe_response_status(
                                                response_status
                                            )
                                        if _post_turn_observer is not None:
                                            reflection = _post_turn_observer(turn)
                                            reflection_evidence.observe_reflection(
                                                reflection
                                            )
                                            observe_learning(
                                                getattr(
                                                    reflection,
                                                    "learning_candidate",
                                                    None,
                                                )
                                            )
                                            observe_diagnostics(
                                                reflection_observed=(
                                                    reflection is not None
                                                ),
                                                learning_assessed=True,
                                            )
        except BaseException as exc:
            self._cognitive_observer.fail_turn(observation_id, exc)
            self._conversation_entry_evidence.seal(observation_id)
            raise
        if not runtime_converse_called:
            try:
                turn = self._persist_non_runtime_turn(turn)
            except BaseException as exc:
                self._cognitive_observer.fail_turn(observation_id, exc)
                self._conversation_entry_evidence.seal(observation_id)
                raise
        self._submitted_turns += 1
        self._last_origin = origin
        self._last_session_id = session_id or turn.session_id
        self._cognitive_observer.complete_turn(
            observation_id, session_id=self._last_session_id
        )
        self._conversation_entry_evidence.seal(observation_id)
        if _causal_result_receiver is not None:
            _causal_result_receiver(turn, causal_applied_result)
        return turn

    def submit_observed(self, text: str, *, post_turn_observer, **kwargs):
        if not callable(post_turn_observer):
            raise TypeError("post-turn observer must be callable")
        return self.submit(
            text,
            _post_turn_observer=post_turn_observer,
            **kwargs,
        )

    def _persist_non_runtime_turn(
        self, turn: LocalConversationTurn
    ) -> LocalConversationTurn:
        """Share successful gateway-only turns with the runtime's recent context.

        Runtime-produced turns already persist inside converse(); do not duplicate them.
        Never persist into a different session or when persistence is disabled.
        """
        runtime = self._runtime
        journal = getattr(runtime, "journal", None)
        config = getattr(runtime, "config", None)
        bootstrap = getattr(runtime, "bootstrap", None)
        runtime_config = getattr(bootstrap, "config", None)
        if (
            journal is None
            or config is None
            or not getattr(config, "persist_turns", False)
            or runtime_config is None
        ):
            return turn
        owner = getattr(runtime_config, "owner", None)
        session_id = getattr(runtime_config, "session_id", None)
        if (
            not isinstance(owner, str)
            or not isinstance(session_id, str)
            or owner.strip().casefold() != turn.owner.casefold()
            or session_id.strip() != turn.session_id
        ):
            return turn
        history = journal.list_for_session(owner, session_id)
        if any(previous.turn_id == turn.turn_id for previous in history):
            return turn
        # Use the journal sequence, not the gateway's global turn counter.
        next_sequence = max((item.sequence for item in history), default=0) + 1
        if turn.sequence != next_sequence:
            turn = replace(turn, sequence=next_sequence, turn_id="")
        journal.append(turn)
        return turn

    def _effective_session_id(self, requested: str | None) -> str:
        if requested and requested.strip():
            return requested.strip()
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        configured = getattr(config, "session_id", None)
        return str(configured or "coowners-main").strip()

    def _runtime_session_id(self, fallback: str) -> str:
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        configured = getattr(config, "session_id", None)
        return str(configured or fallback).strip()

    def _applied_owner_turn(
        self,
        text,
        applied_result,
        *,
        session_id,
        now,
    ) -> LocalConversationTurn:
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = str(getattr(config, "owner", "Carlos y Cristina")).strip()
        response_text = str(
            getattr(applied_result, "natural_answer_text", None)
            or getattr(applied_result, "answer_text", "")
        ).strip()
        if not response_text:
            raise ValueError("recognized applied result must provide answer text")
        conversational_result = getattr(
            applied_result,
            "conversational_result",
            None,
        )
        source_result = getattr(conversational_result, "source_result", None)
        retrieval_performed = bool(
            getattr(
                source_result,
                "retrieval_performed",
                source_result is not None,
            )
        )
        network_access_performed = bool(
            getattr(
                source_result,
                "network_access_performed",
                retrieval_performed,
            )
        )
        lineage = getattr(conversational_result, "result_id", None)
        if not lineage:
            lineage = f"{session_id}-{self._submitted_turns + 1}"
        return LocalConversationTurn(
            owner=owner or "Carlos y Cristina",
            session_id=session_id,
            sequence=self._submitted_turns + 1,
            user_text=text,
            response_text=response_text,
            status="completed",
            pipeline_result_id=f"applied-conversational-{lineage}",
            operational_response_id=f"applied-response-{lineage}",
            provider_call_performed=False,
            retrieval_performed=retrieval_performed,
            network_access_performed=network_access_performed,
            rationale=("applied_conversational_intelligence",),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def _identification_turn(
        self,
        text,
        identification,
        *,
        session_id,
        now,
    ) -> LocalConversationTurn:
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = str(getattr(config, "owner", "Carlos y Cristina")).strip()
        resolution = identification.resolution
        lineage = resolution.resolution_id
        return LocalConversationTurn(
            owner=owner or "Carlos y Cristina",
            session_id=session_id,
            sequence=self._submitted_turns + 1,
            user_text=text,
            response_text=identification.response_text,
            status="completed",
            pipeline_result_id=f"identity-{lineage}",
            operational_response_id=f"identity-response-{lineage}",
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=(
                "controlled_interlocutor_identification_completed",
                identification.interpretation.response_code,
            ),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def realize_governed_intellectual_goal_proposal(
        self,
        proposal: GovernedIntellectualGoalProposal,  # noqa: F821
        *,
        user_text: str | None = None,
        session_id: str | None = None,
        now: datetime | None = None,
    ) -> LocalConversationTurn:
        """Realize an existing governed study proposal without advancing it."""
        if not proposal.read_only or not proposal.non_executive:
            raise ValueError(
                "investigative goal realization requires a governed proposal"
            )
        if not proposal.authorization_required or proposal.authorized:
            raise ValueError(
                "investigative goal realization must stop before authorization"
            )
        if any(
            (
                proposal.planning_invoked,
                proposal.investigation_started,
                proposal.executes_capabilities,
                proposal.persists_results,
                proposal.creates_memory,
                proposal.creates_learning_candidate,
                proposal.modifies_knowledge,
                proposal.starts_background_process,
            )
        ):
            raise ValueError(
                "investigative goal realization crossed its governed stop"
            )

        effective_session_id = self._effective_session_id(session_id)
        prompt = (user_text or proposal.question).strip()
        response = (
            f'Propongo investigar "{proposal.subject}" para resolver: '
            f"{proposal.unknown_element}. Pregunta de estudio: {proposal.question} "
            "La investigación requiere autorización explícita antes de avanzar."
        )
        return LocalConversationTurn(
            owner=proposal.owner,
            session_id=effective_session_id,
            sequence=self._submitted_turns + 1,
            user_text=prompt,
            response_text=response,
            status="completed",
            pipeline_result_id=proposal.proposal_id,
            operational_response_id=(
                f"investigative-goal-proposal-response-{proposal.proposal_id}"
            ),
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=(
                "governed_investigative_goal_proposal",
                "existing_curiosity_lineage_preserved",
                "existing_relevance_consumed",
                "existing_initiative_consumed",
                "explicit_authorization_required_before_investigation",
            ),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def _curiosity_question_turn(
        self,
        text,
        assembly,
        *,
        session_id,
        now,
    ) -> LocalConversationTurn:
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = str(getattr(config, "owner", "Carlos y Cristina")).strip()
        lineage = assembly.source_fingerprint[:16]
        return LocalConversationTurn(
            owner=owner or "Carlos y Cristina",
            session_id=session_id,
            sequence=self._submitted_turns + 1,
            user_text=text,
            response_text=assembly.question,
            status="completed",
            pipeline_result_id=assembly.curiosity_report_id,
            operational_response_id=f"curiosity-question-response-{lineage}",
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=(
                "governed_epistemic_curiosity",
                "existing_relevance_consumed",
                "existing_initiative_consumed",
                "question_candidate_productively_realized",
            ),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def _governed_revision_approval_turn(
        self,
        text,
        approval_evidence,
        *,
        session_id,
        now,
    ) -> LocalConversationTurn:
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = str(getattr(config, "owner", "Carlos y Cristina")).strip()
        approved = approval_evidence is not None
        lineage = getattr(approval_evidence, "approval_id", "not-approved")
        return LocalConversationTurn(
            owner=owner or "Carlos y Cristina",
            session_id=session_id,
            sequence=self._submitted_turns + 1,
            user_text=text,
            response_text=(
                "La revisión quedó aprobada para revisión posterior; "
                "no fue aplicada."
                if approved
                else (
                    "La respuesta no produjo una aprobación "
                    "de la revisión pendiente."
                )
            ),
            status="completed",
            pipeline_result_id=f"governed-revision-approval-{lineage}",
            operational_response_id=(
                f"governed-revision-approval-response-{str(lineage)[-16:]}"
            ),
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=(
                "governed_learning_productive_wiring",
                (
                    "approved_knowledge_revision_evidence_produced"
                    if approved
                    else "knowledge_revision_approval_not_granted"
                ),
                "revision_not_applied",
            ),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def _governed_revision_not_applied_turn(
        self,
        text,
        request,
        *,
        session_id,
        now,
    ) -> LocalConversationTurn:
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = str(getattr(config, "owner", "Carlos y Cristina")).strip()
        lineage = request.request_id
        return LocalConversationTurn(
            owner=owner or "Carlos y Cristina",
            session_id=session_id,
            sequence=self._submitted_turns + 1,
            user_text=text,
            response_text=(
                "La revisión certificada no fue aplicada: falta una autorización "
                "explícita y exacta de ejecución."
            ),
            status="completed",
            pipeline_result_id=f"governed-revision-not-applied-{lineage}",
            operational_response_id=(
                f"governed-revision-not-applied-response-{str(lineage)[-16:]}"
            ),
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=(
                "governed_learning_productive_wiring",
                "certified_revision_requires_exact_execution_authorization",
            ),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def _governed_revision_turn(
        self,
        text,
        request,
        *,
        session_id,
        now,
    ) -> LocalConversationTurn:
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = str(getattr(config, "owner", "Carlos y Cristina")).strip()
        lineage = request.request_id
        return LocalConversationTurn(
            owner=owner or "Carlos y Cristina",
            session_id=session_id,
            sequence=self._submitted_turns + 1,
            user_text=text,
            response_text="Bien, apliqué la revisión en la memoria oficial.",
            status="completed",
            pipeline_result_id=f"governed-revision-{lineage}",
            operational_response_id=(
                f"governed-revision-response-{str(lineage)[-16:]}"
            ),
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=(
                "governed_learning_productive_wiring",
                "certified_governed_knowledge_revision_applied",
            ),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def _governed_learning_turn(
        self,
        text,
        result,
        *,
        session_id,
        now,
    ) -> LocalConversationTurn:
        from .productive_governed_learning_wiring import (
            ProductiveGovernedLearningOutcome,
        )

        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = str(getattr(config, "owner", "Carlos y Cristina")).strip()
        write_request = result.write_request
        learning_category = getattr(write_request, "learning_category", None)
        is_source_neutral = (
            write_request is not None
            and getattr(learning_category, "value", learning_category)
            != "user_preference"
        )
        if is_source_neutral:
            responses = {
                ProductiveGovernedLearningOutcome.STORED: (
                    "Bien, guardé ese aprendizaje en la memoria oficial."
                ),
                ProductiveGovernedLearningOutcome.ALREADY_STORED: (
                    "Ese aprendizaje ya estaba guardado en la memoria oficial."
                ),
                ProductiveGovernedLearningOutcome.REJECTED: (
                    "Entendido, no voy a guardar ese aprendizaje."
                ),
                ProductiveGovernedLearningOutcome.DEFERRED: (
                    "De acuerdo, lo dejamos para más adelante."
                ),
                ProductiveGovernedLearningOutcome.UNCLEAR: (
                    "No guardé ese aprendizaje porque la aprobación no fue explícita."
                ),
                ProductiveGovernedLearningOutcome.ABSTAIN: (
                    "No guardé ese aprendizaje porque no pude vincular la aprobación."
                ),
                ProductiveGovernedLearningOutcome.REVIEW_REQUIRED: (
                    "No lo guardé porque falta un alcance durable explícito."
                ),
                ProductiveGovernedLearningOutcome.MEMORY_UNAVAILABLE: (
                    "La aprobación es válida, pero la memoria oficial "
                    "no está disponible."
                ),
                ProductiveGovernedLearningOutcome.WRITE_FAILED: (
                    "La aprobación es válida, pero no pude guardar ese aprendizaje."
                ),
            }
        else:
            responses = {
                ProductiveGovernedLearningOutcome.STORED: (
                    "Bien, guardé esa preferencia en la memoria oficial."
                ),
                ProductiveGovernedLearningOutcome.ALREADY_STORED: (
                    "Esa preferencia ya estaba guardada en la memoria oficial."
                ),
                ProductiveGovernedLearningOutcome.REJECTED: (
                    "Entendido, no voy a guardar esa preferencia."
                ),
                ProductiveGovernedLearningOutcome.DEFERRED: (
                    "De acuerdo, lo dejamos para más adelante."
                ),
                ProductiveGovernedLearningOutcome.UNCLEAR: (
                    "No guardé esa preferencia porque la aprobación no fue explícita."
                ),
                ProductiveGovernedLearningOutcome.ABSTAIN: (
                    "No guardé esa preferencia porque no pude vincular la aprobación."
                ),
                ProductiveGovernedLearningOutcome.REVIEW_REQUIRED: (
                    "No la guardé porque falta un alcance durable explícito."
                ),
                ProductiveGovernedLearningOutcome.MEMORY_UNAVAILABLE: (
                    "La aprobación es válida, pero la memoria oficial "
                    "no está disponible."
                ),
                ProductiveGovernedLearningOutcome.WRITE_FAILED: (
                    "La aprobación es válida, pero no pude guardar la preferencia."
                ),
            }
        lineage = (
            result.write_request.request_id
            if result.write_request is not None
            else (
                result.approval.report_id
                if result.approval is not None
                else result.outcome.value
            )
        )
        return LocalConversationTurn(
            owner=owner or "Carlos y Cristina",
            session_id=session_id,
            sequence=self._submitted_turns + 1,
            user_text=text,
            response_text=responses[result.outcome],
            status="completed",
            pipeline_result_id=f"governed-learning-{lineage}",
            operational_response_id=(
                f"governed-learning-response-{str(lineage)[-16:]}"
            ),
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=(
                "governed_learning_productive_wiring",
                result.outcome.value,
                *result.rationale_codes,
            ),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def _gcdr_advisory_turn(
        self,
        text,
        realization,
        integration,
        *,
        session_id,
        now,
    ) -> LocalConversationTurn:
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = str(getattr(config, "owner", "Carlos y Cristina")).strip()
        lineage = realization.source_fingerprint[:16]
        return LocalConversationTurn(
            owner=owner or "Carlos y Cristina",
            session_id=session_id,
            sequence=self._submitted_turns + 1,
            user_text=text,
            response_text=realization.response_text,
            status="completed",
            pipeline_result_id=realization.advisory_report_id,
            operational_response_id=f"gcdr-advisory-response-{lineage}",
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=(
                "explicit_complex_decision_intake",
                "productive_gcdr_intake_integration",
                f"integration:{integration.status.value}",
                "governed_complex_decision_reasoning",
                "human_decision_preserved",
                f"realization:{realization.outcome.value}",
            ),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def _decision_advisory_turn(
        self,
        text,
        realization,
        *,
        session_id,
        now,
    ) -> LocalConversationTurn:
        bootstrap = getattr(self._runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)
        owner = str(getattr(config, "owner", "Carlos y Cristina")).strip()
        lineage = realization.source_fingerprint[:16]
        return LocalConversationTurn(
            owner=owner or "Carlos y Cristina",
            session_id=session_id,
            sequence=self._submitted_turns + 1,
            user_text=text,
            response_text=realization.response_text,
            status="completed",
            pipeline_result_id=realization.advisory_report_id,
            operational_response_id=f"decision-advisory-response-{lineage}",
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=(
                "explicit_human_decision_deliberation",
                "governed_decision_advisory",
                "human_decision_preserved",
                f"realization:{realization.outcome.value}",
            ),
            response_path="interceptor",
            degradation_reason="not_applicable",
            created_at=now or datetime.now().astimezone(),
        )

    def converse(
        self,
        text: str,
        *,
        now: datetime | None = None,
    ) -> LocalConversationTurn:
        """Compatibility alias routed through the one official boundary."""
        return self.submit(text, origin=ConversationOrigin.INTERNAL, now=now)


    class AnalysisModeLevel(StrEnum):
        PERSONAL = "personal"
        TECHNICAL = "technical"
        ARCHITECTURAL = "architectural"

    @dataclass(frozen=True)
    class AnalysisModeStatus:
        active: bool
        level: "OfficialConversationGateway.AnalysisModeLevel | None"

    @dataclass(frozen=True)
    class AnalysisModeCommand:
        action: str
        level: "OfficialConversationGateway.AnalysisModeLevel | None" = None

    @dataclass(frozen=True)
    class AnalysisModeProjection:
        level: "OfficialConversationGateway.AnalysisModeLevel"
        sections: tuple[tuple[str, object], ...]
        unavailable: tuple[str, ...] = ()

        def as_dict(self) -> dict[str, object]:
            return {
                "mode": "analysis",
                "level": self.level.value,
                "available": tuple(name for name, _ in self.sections),
                "sections": dict(self.sections),
                "unavailable": self.unavailable,
            }
