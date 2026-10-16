from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from queue import Empty, Queue
from threading import RLock

from core.controlled_autonomy import (
    AudioDiagnosticReader,
    AutonomousCapabilityRunner,
    AutonomyExplanation,
    AutonomyLevel,
    CapabilityAssessment,
    CapabilityDefinition,
    CapabilityModel,
    CapabilityModelSnapshot,
    CapabilityRunResult,
    ContextualInitiative,
    ContextualInitiativeSnapshot,
    ContextualInitiativeStore,
    DecisionExplanation,
    DecisionJournal,
    DecisionPolicy,
    DeterministicAutonomyExplainer,
    DeterministicContextualInitiativeEvaluator,
    DeterministicDecisionExplainer,
    DeterministicGoalBlockageDetector,
    DeterministicGoalPlanner,
    DeterministicGoalSelector,
    DeterministicNextStepProposer,
    DeterministicOperationalLearner,
    DeterministicSelfReflector,
    ExperienceMemory,
    GoalBlockageReport,
    GoalBlockageSnapshot,
    GoalBlockageStore,
    GoalPlan,
    GoalPlanSnapshot,
    GoalPlanStepStatus,
    GoalPlanStore,
    GoalProgress,
    GoalSelectionReport,
    GoalSelectionSnapshot,
    GoalSelectionStore,
    GoalStatus,
    JsonCapabilityModel,
    JsonContextualInitiativeStore,
    JsonExperienceMemory,
    JsonGoalBlockageStore,
    JsonGoalPlanStore,
    JsonGoalSelectionStore,
    JsonlDecisionJournal,
    JsonNextStepProposalStore,
    JsonOperationalLearningStore,
    JsonPersistentGoalStore,
    JsonSelfReflectionStore,
    NextStepProposal,
    NextStepProposalSnapshot,
    NextStepProposalStore,
    OperationalLearning,
    OperationalLearningSnapshot,
    OperationalLearningStore,
    PersistentGoal,
    PersistentGoalSnapshot,
    PersistentGoalStore,
    SelfReflectionReport,
    SelfReflectionSnapshot,
    SelfReflectionStore,
    default_capabilities,
    default_first_autonomous_capability_runner,
    goal_progress,
    observation_from_audio_error,
    observation_from_component_health,
    update_goal_plan_step,
)
from core.executive_coordinator import ExecutiveCoordinator, SubmissionResult
from core.executive_event_model import (
    AmbientObservationEvent,
    BatteryLowEvent,
    ExecutiveEvent,
    GenericTextEvent,
    ImportantEmailEvent,
    ReminderDueEvent,
    VerifiedNewsEvent,
    VisualCaptureResultEvent,
    text_to_executive_event,
)
from core.executive_notification_broker import (
    BrokeredEvent,
    ExecutiveNotificationBroker,
)
from core.executive_presence_attention import (
    AttentionState,
    PresenceAttentionManager,
    PresenceState,
)
from core.executive_recovery_health import RecoveryHealthCoordinator

from .autonomy_notification import render_autonomy_notification
from .models import RuntimeExecutiveSnapshot


class RuntimeExecutiveIntegration:
    """Connects the M325 executive layers to the existing desktop runtime.

    Legacy residents publish text through ``publish_text``. The text is adapted
    to an ExecutiveEvent, sequenced by the coordinator, evaluated by the broker
    and attention manager, then rendered back to text only at the UI boundary.
    """

    _COMPONENTS = (
        "executive.coordinator",
        "executive.broker",
        "executive.presentation",
    )

    def __init__(
        self,
        *,
        coordinator: ExecutiveCoordinator | None = None,
        broker: ExecutiveNotificationBroker | None = None,
        attention: PresenceAttentionManager | None = None,
        health: RecoveryHealthCoordinator | None = None,
        autonomy_runner: AutonomousCapabilityRunner | None = None,
        autonomy_policy: DecisionPolicy | None = None,
        decision_journal: DecisionJournal | None = None,
        audio_diagnostic_reader: AudioDiagnosticReader | None = None,
        experience_memory: ExperienceMemory | None = None,
        goal_store: PersistentGoalStore | None = None,
        self_reflection_store: SelfReflectionStore | None = None,
        goal_plan_store: GoalPlanStore | None = None,
        goal_blockage_store: GoalBlockageStore | None = None,
        goal_selection_store: GoalSelectionStore | None = None,
        next_step_proposal_store: NextStepProposalStore | None = None,
        capability_model: CapabilityModel | None = None,
        contextual_initiative_store: ContextualInitiativeStore | None = None,
        operational_learning_store: OperationalLearningStore | None = None,
        autonomy_deduplication_window: timedelta = timedelta(seconds=60),
        decision_journal_path: Path | str = (
            Path(".roby/autonomy/decision_journal.jsonl")
        ),
        experience_memory_path: Path | str | None = None,
        persistent_goals_path: Path | str | None = None,
        self_reflection_path: Path | str | None = None,
        goal_plans_path: Path | str | None = None,
        goal_blockages_path: Path | str | None = None,
        goal_selections_path: Path | str | None = None,
        next_step_proposals_path: Path | str | None = None,
        capability_model_path: Path | str | None = None,
        contextual_initiatives_path: Path | str | None = None,
        operational_learning_path: Path | str | None = None,
    ) -> None:
        self._lock = RLock()
        self.coordinator = coordinator or ExecutiveCoordinator()
        self.attention = attention or PresenceAttentionManager()
        self.broker = broker or ExecutiveNotificationBroker(
            attention_decider=self.attention.broker_decider,
        )
        self.health = health or RecoveryHealthCoordinator()
        resolved_experience_path = (
            Path(experience_memory_path)
            if experience_memory_path is not None
            else Path(decision_journal_path).with_name("experience_memory.json")
        )
        self.experience_memory = experience_memory or JsonExperienceMemory(
            resolved_experience_path
        )
        resolved_goal_path = (
            Path(persistent_goals_path)
            if persistent_goals_path is not None
            else Path(decision_journal_path).with_name("persistent_goals.json")
        )
        self.goal_store = goal_store or JsonPersistentGoalStore(resolved_goal_path)
        resolved_reflection_path = (
            Path(self_reflection_path)
            if self_reflection_path is not None
            else Path(decision_journal_path).with_name("self_reflections.json")
        )
        self.self_reflection_store = (
            self_reflection_store
            if self_reflection_store is not None
            else JsonSelfReflectionStore(resolved_reflection_path)
        )
        resolved_goal_plans_path = (
            Path(goal_plans_path)
            if goal_plans_path is not None
            else Path(decision_journal_path).with_name("goal_plans.json")
        )
        self.goal_plan_store = goal_plan_store or JsonGoalPlanStore(
            resolved_goal_plans_path
        )
        resolved_goal_blockages_path = (
            Path(goal_blockages_path)
            if goal_blockages_path is not None
            else Path(decision_journal_path).with_name("goal_blockages.json")
        )
        self.goal_blockage_store = goal_blockage_store or JsonGoalBlockageStore(
            resolved_goal_blockages_path
        )
        resolved_goal_selections_path = (
            Path(goal_selections_path)
            if goal_selections_path is not None
            else Path(decision_journal_path).with_name("goal_selections.json")
        )
        self.goal_selection_store = goal_selection_store or JsonGoalSelectionStore(
            resolved_goal_selections_path
        )
        resolved_next_step_proposals_path = (
            Path(next_step_proposals_path)
            if next_step_proposals_path is not None
            else Path(decision_journal_path).with_name("next_step_proposals.json")
        )
        self.next_step_proposal_store = (
            next_step_proposal_store
            if next_step_proposal_store is not None
            else JsonNextStepProposalStore(resolved_next_step_proposals_path)
        )
        resolved_capability_model_path = (
            Path(capability_model_path)
            if capability_model_path is not None
            else Path(decision_journal_path).with_name("capability_model.json")
        )
        self.capability_model = capability_model or JsonCapabilityModel(
            resolved_capability_model_path,
            defaults=default_capabilities(),
        )
        resolved_contextual_initiatives_path = (
            Path(contextual_initiatives_path)
            if contextual_initiatives_path is not None
            else Path(decision_journal_path).with_name(
                "contextual_initiatives.json"
            )
        )
        self.contextual_initiative_store = (
            contextual_initiative_store
            if contextual_initiative_store is not None
            else JsonContextualInitiativeStore(
                resolved_contextual_initiatives_path
            )
        )
        resolved_operational_learning_path = (
            Path(operational_learning_path)
            if operational_learning_path is not None
            else Path(decision_journal_path).with_name(
                "operational_learning.json"
            )
        )
        self.operational_learning_store = (
            operational_learning_store
            if operational_learning_store is not None
            else JsonOperationalLearningStore(
                resolved_operational_learning_path
            )
        )
        self.operational_learner = DeterministicOperationalLearner()
        self.goal_blockage_detector = DeterministicGoalBlockageDetector()
        self.goal_selector = DeterministicGoalSelector()
        self.next_step_proposer = DeterministicNextStepProposer()
        self.contextual_initiative_evaluator = (
            DeterministicContextualInitiativeEvaluator()
        )
        self.goal_planner = DeterministicGoalPlanner()
        self.self_reflector = DeterministicSelfReflector()
        self.autonomy_explainer = DeterministicAutonomyExplainer()
        self.decision_explainer = DeterministicDecisionExplainer()
        journal = decision_journal or JsonlDecisionJournal(decision_journal_path)
        self.decision_journal = journal
        if autonomy_runner is None:
            autonomy_runner = default_first_autonomous_capability_runner(
                self.health,
                journal=journal,
                audio_reader=audio_diagnostic_reader,
                experience_memory=self.experience_memory,
            )
        self.autonomy_runner = autonomy_runner
        self.audio_diagnostic_reader = audio_diagnostic_reader
        self.autonomy_policy = autonomy_policy or DecisionPolicy(
            autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
            minimum_confidence=0.8,
            simulation_mode=False,
        )
        self._presentations: Queue[str] = Queue()
        self._running = False
        self._published_count = 0
        self._presented_count = 0
        self._drained_count = 0
        self._autonomous_cycle_count = 0
        self._autonomy_notification_count = 0
        self._last_autonomy_result: CapabilityRunResult | None = None
        self._last_autonomy_error: str | None = None
        if autonomy_deduplication_window.total_seconds() < 0:
            raise ValueError("autonomy deduplication window must not be negative")
        self._autonomy_deduplication_window = autonomy_deduplication_window
        self._autonomy_recent: dict[tuple[object, ...], datetime] = {}
        self._autonomy_in_progress: set[tuple[object, ...]] = set()
        self._autonomy_suppressed_count = 0
        for component_id in self._COMPONENTS:
            self.health.register(component_id)
        self.coordinator.subscribe(self.broker.coordinator_handler)
        self.broker.subscribe(self._present)

    @property
    def snapshot(self) -> RuntimeExecutiveSnapshot:
        with self._lock:
            experience = self.experience_memory.snapshot()
            goals = self.goal_store.snapshot(now=datetime.now(timezone.utc))
            plans = self.goal_plan_store.snapshot()
            blockages = self.goal_blockage_store.snapshot()
            selections = self.goal_selection_store.snapshot()
            proposals = self.next_step_proposal_store.snapshot()
            capabilities = self.capability_model.snapshot()
            initiatives = self.contextual_initiative_store.snapshot()
            learnings = self.operational_learning_store.snapshot()
            return RuntimeExecutiveSnapshot(
                running=self._running,
                published_count=self._published_count,
                presented_count=self._presented_count,
                drained_count=self._drained_count,
                coordinator=self.coordinator.snapshot,
                broker=self.broker.snapshot,
                attention=self.attention.snapshot,
                health=self.health.snapshot,
                autonomous_cycle_count=self._autonomous_cycle_count,
                autonomy_notification_count=(self._autonomy_notification_count),
                autonomy_suppressed_count=self._autonomy_suppressed_count,
                autonomy_experience_count=experience.total_occurrences,
                autonomy_experience_pattern_count=len(experience.patterns),
                persistent_goal_count=len(goals.goals),
                active_persistent_goal_count=goals.active_count,
                due_persistent_goal_count=goals.due_for_review_count,
                self_reflection_count=len(
                    self.self_reflection_store.snapshot().reports
                ),
                persistent_goal_plan_count=len(plans.plans),
                active_goal_plan_count=plans.active_count,
                completed_goal_plan_count=plans.completed_count,
                blocked_goal_plan_step_count=plans.blocked_step_count,
                goal_blockage_report_count=len(blockages.reports),
                blocked_goal_report_count=blockages.blocked_report_count,
                goal_selection_report_count=len(selections.reports),
                successful_goal_selection_count=(selections.successful_selection_count),
                next_step_proposal_count=len(proposals.proposals),
                actionable_next_step_proposal_count=proposals.actionable_count,
                capability_count=len(capabilities.capabilities),
                enabled_capability_count=capabilities.enabled_count,
                contextual_initiative_count=len(initiatives.initiatives),
                proposal_candidate_count=(initiatives.proposal_candidate_count),
                operational_learning_count=len(learnings.learnings),
                actionable_operational_learning_count=learnings.actionable_count,
                last_autonomy_status=(
                    self._last_autonomy_result.status.value
                    if self._last_autonomy_result is not None
                    else None
                ),
                last_autonomy_error=self._last_autonomy_error,
            )

    def start(self, *, now: datetime | None = None) -> RuntimeExecutiveSnapshot:
        with self._lock:
            if self._running:
                return self.snapshot
            self.coordinator.start(now=now)
            self.attention.update(
                presence=PresenceState.PRESENT,
                attention=AttentionState.AVAILABLE,
                observed_at=now,
            )
            self._running = True
            for component_id in self._COMPONENTS:
                self.health.record_success(component_id, observed_at=now)
            return self.snapshot

    def stop(self, *, now: datetime | None = None) -> RuntimeExecutiveSnapshot:
        with self._lock:
            if not self._running:
                return self.snapshot
            self.attention.update(
                presence=PresenceState.AWAY,
                attention=AttentionState.AVAILABLE,
                observed_at=now,
            )
            self.coordinator.stop(now=now)
            self._running = False
            return self.snapshot

    def publish(self, event: ExecutiveEvent) -> SubmissionResult:
        self._require_running()
        try:
            result = self.coordinator.publish(event)
        except Exception as error:
            self._record_failure("executive.coordinator", error)
            raise
        self.health.record_success("executive.coordinator")
        if result.accepted:
            with self._lock:
                self._published_count += 1
        return result

    def publish_text(self, text: str) -> SubmissionResult:
        return self.publish(text_to_executive_event(text))

    def drain_notifications(self) -> tuple[str, ...]:
        self._require_running()
        try:
            self.coordinator.dispatch_pending()
            self.health.record_success("executive.coordinator")
            self.broker.dispatch_pending()
            self.health.record_success("executive.broker")
        except Exception as error:
            component_id = (
                "executive.coordinator"
                if self.coordinator.snapshot.pending_count
                else "executive.broker"
            )
            self._record_failure(component_id, error)
            raise

        drained: list[str] = []
        while True:
            try:
                drained.append(self._presentations.get_nowait())
            except Empty:
                break
        if drained:
            with self._lock:
                self._drained_count += len(drained)
        return tuple(drained)

    def update_attention(
        self,
        attention: AttentionState | str,
        *,
        observed_at: datetime | None = None,
    ) -> None:
        self.attention.update(attention=attention, observed_at=observed_at)

    def update_presence(
        self,
        presence: PresenceState | str,
        *,
        observed_at: datetime | None = None,
    ) -> None:
        self.attention.update(presence=presence, observed_at=observed_at)

    def _present(self, brokered: BrokeredEvent) -> None:
        try:
            text = render_executive_event(brokered.event)
            self._presentations.put(text)
        except Exception as error:
            self._record_failure("executive.presentation", error)
            raise
        self.health.record_success("executive.presentation")
        with self._lock:
            self._presented_count += 1

    def diagnose_audio(self) -> CapabilityRunResult | None:
        reader = self.audio_diagnostic_reader
        if reader is None:
            return None
        observation = observation_from_audio_error(reader)
        return self._run_autonomous_cycle(observation)

    def create_persistent_goal(
        self,
        *,
        title: str,
        description: str,
        priority: float,
        created_at: datetime,
        review_at: datetime | None = None,
        source: str = "runtime",
    ) -> PersistentGoal:
        return self.goal_store.create(
            title=title,
            description=description,
            priority=priority,
            created_at=created_at,
            review_at=review_at,
            source=source,
        )

    def update_persistent_goal(
        self,
        goal_id: str,
        *,
        updated_at: datetime,
        status: GoalStatus | str | None = None,
        priority: float | None = None,
        review_at: datetime | None = None,
        progress_summary: str | None = None,
    ) -> PersistentGoal:
        return self.goal_store.update(
            goal_id,
            updated_at=updated_at,
            status=status,
            priority=priority,
            review_at=review_at,
            progress_summary=progress_summary,
        )

    def persistent_goals(
        self, *, now: datetime | None = None
    ) -> PersistentGoalSnapshot:
        return self.goal_store.snapshot(now=now)

    def create_goal_plan(
        self, goal_id: str, *, planned_at: datetime | None = None
    ) -> GoalPlan:
        goal = next(
            (
                item
                for item in self.goal_store.snapshot().goals
                if item.goal_id == goal_id
            ),
            None,
        )
        if goal is None:
            raise KeyError(f"unknown persistent goal: {goal_id}")
        plan = self.goal_planner.plan(
            goal,
            planned_at=planned_at or datetime.now(timezone.utc),
        )
        self.goal_plan_store.append(plan)
        return plan

    def goal_plans(self) -> GoalPlanSnapshot:
        return self.goal_plan_store.snapshot()

    def update_goal_plan_step(
        self,
        plan_id: str,
        step_id: str,
        *,
        status: GoalPlanStepStatus | str,
        updated_at: datetime,
        evidence: tuple[str, ...] = (),
        blocked_reason: str | None = None,
    ) -> GoalPlan:
        plan = next(
            (
                item
                for item in self.goal_plan_store.snapshot().plans
                if item.plan_id == plan_id
            ),
            None,
        )
        if plan is None:
            raise KeyError(f"unknown goal plan: {plan_id}")
        updated = update_goal_plan_step(
            plan,
            step_id,
            status=status,
            updated_at=updated_at,
            evidence=evidence,
            blocked_reason=blocked_reason,
        )
        self.goal_plan_store.replace(updated)
        return updated

    def goal_progress(self, plan_id: str) -> GoalProgress:
        plan = next(
            (
                item
                for item in self.goal_plan_store.snapshot().plans
                if item.plan_id == plan_id
            ),
            None,
        )
        if plan is None:
            raise KeyError(f"unknown goal plan: {plan_id}")
        return goal_progress(plan)

    def detect_goal_blockage(
        self,
        plan_id: str,
        *,
        observed_at: datetime | None = None,
        available_capabilities: frozenset[str] = frozenset(),
        authorized_step_ids: frozenset[str] = frozenset(),
    ) -> GoalBlockageReport:
        plan = next(
            (
                item
                for item in self.goal_plan_store.snapshot().plans
                if item.plan_id == plan_id
            ),
            None,
        )
        if plan is None:
            raise KeyError(f"unknown goal plan: {plan_id}")
        report = self.goal_blockage_detector.detect(
            plan,
            experience=self.experience_memory.snapshot(),
            observed_at=observed_at or datetime.now(timezone.utc),
            available_capabilities=available_capabilities,
            authorized_step_ids=authorized_step_ids,
        )
        self.goal_blockage_store.append(report)
        return report

    def goal_blockages(self) -> GoalBlockageSnapshot:
        return self.goal_blockage_store.snapshot()

    def select_next_goal(
        self, *, observed_at: datetime | None = None
    ) -> GoalSelectionReport:
        now = observed_at or datetime.now(timezone.utc)
        report = self.goal_selector.select(
            goals=self.goal_store.snapshot(now=now),
            plans=self.goal_plan_store.snapshot(),
            blockages=self.goal_blockage_store.snapshot(),
            experience=self.experience_memory.snapshot(),
            observed_at=now,
        )
        self.goal_selection_store.append(report)
        return report

    def goal_selections(self) -> GoalSelectionSnapshot:
        return self.goal_selection_store.snapshot()

    def propose_next_goal_step(
        self,
        selection_id: str,
        *,
        proposed_at: datetime | None = None,
    ) -> NextStepProposal:
        selection = next(
            (
                item
                for item in self.goal_selection_store.snapshot().reports
                if item.selection_id == selection_id
            ),
            None,
        )
        if selection is None:
            raise KeyError(f"unknown goal selection: {selection_id}")
        proposal = self.next_step_proposer.propose(
            selection=selection,
            plans=self.goal_plan_store.snapshot(),
            blockages=self.goal_blockage_store.snapshot(),
            proposed_at=proposed_at or datetime.now(timezone.utc),
        )
        self.next_step_proposal_store.append(proposal)
        return proposal

    def next_step_proposals(self) -> NextStepProposalSnapshot:
        return self.next_step_proposal_store.snapshot()

    def register_capability(
        self, capability: CapabilityDefinition
    ) -> CapabilityDefinition:
        self.capability_model.register(capability)
        return capability

    def capabilities(self) -> CapabilityModelSnapshot:
        return self.capability_model.snapshot()

    def assess_capability(self, capability_id: str) -> CapabilityAssessment:
        return self.capability_model.assess(capability_id)

    def evaluate_contextual_initiative(
        self,
        proposal_id: str,
        *,
        observed_at: datetime | None = None,
    ) -> ContextualInitiative:
        proposal = next(
            (
                item
                for item in self.next_step_proposal_store.snapshot().proposals
                if item.proposal_id == proposal_id
            ),
            None,
        )
        if proposal is None:
            raise KeyError(f"unknown next step proposal: {proposal_id}")
        capability = (
            self.capability_model.assess(proposal.required_capability)
            if proposal.required_capability is not None
            else None
        )
        initiative = self.contextual_initiative_evaluator.evaluate(
            proposal=proposal,
            capability=capability,
            observed_at=observed_at or datetime.now(timezone.utc),
        )
        self.contextual_initiative_store.append(initiative)
        return initiative

    def contextual_initiatives(self) -> ContextualInitiativeSnapshot:
        return self.contextual_initiative_store.snapshot()

    def learn_from_operational_experience(
        self,
        situation_kind: str,
        action: str,
        *,
        observed_at: datetime | None = None,
    ) -> OperationalLearning:
        learning = self.operational_learner.learn(
            experience=self.experience_memory.snapshot(),
            situation_kind=situation_kind,
            action=action,
            observed_at=observed_at or datetime.now(timezone.utc),
        )
        self.operational_learning_store.append(learning)
        return learning

    def operational_learnings(self) -> OperationalLearningSnapshot:
        return self.operational_learning_store.snapshot()

    def assess_next_step_capability(
        self, proposal_id: str
    ) -> CapabilityAssessment | None:
        proposal = next(
            (
                item
                for item in self.next_step_proposal_store.snapshot().proposals
                if item.proposal_id == proposal_id
            ),
            None,
        )
        if proposal is None:
            raise KeyError(f"unknown next step proposal: {proposal_id}")
        if proposal.required_capability is None:
            return None
        return self.capability_model.assess(proposal.required_capability)

    def run_self_reflection(
        self, *, observed_at: datetime | None = None
    ) -> SelfReflectionReport:
        now = observed_at or datetime.now(timezone.utc)
        report = self.self_reflector.reflect(
            experience=self.experience_memory.snapshot(),
            goals=self.goal_store.snapshot(now=now),
            observed_at=now,
        )
        self.self_reflection_store.append(report)
        return report

    def self_reflections(self) -> SelfReflectionSnapshot:
        return self.self_reflection_store.snapshot()

    def explain_decision(self, decision_id: str) -> DecisionExplanation:
        entry = next(
            (
                item
                for item in self.decision_journal.entries()
                if item.decision.decision_id == decision_id
            ),
            None,
        )
        if entry is None:
            raise KeyError(f"unknown autonomy decision: {decision_id}")
        outcome = None
        last = self.last_autonomy_result
        if (
            last is not None
            and last.outcome is not None
            and last.outcome.decision_id == decision_id
        ):
            outcome = last.outcome
        return self.decision_explainer.explain(entry, outcome=outcome)

    def explain_last_autonomy(self) -> DecisionExplanation | None:
        last = self.last_autonomy_result
        if last is None or last.orchestration.journal_entry is None:
            return None
        return self.decision_explainer.explain(
            last.orchestration.journal_entry,
            outcome=last.outcome,
        )

    def explain_last_autonomy_advanced(self) -> AutonomyExplanation | None:
        with self._lock:
            result = self._last_autonomy_result
        if result is None:
            return None
        return self.autonomy_explainer.explain(result)

    @property
    def last_autonomy_result(self) -> CapabilityRunResult | None:
        with self._lock:
            return self._last_autonomy_result

    def _record_failure(
        self,
        component_id: str,
        error: BaseException | str,
    ) -> None:
        health = self.health.record_failure(component_id, error)
        observation = observation_from_component_health(health)
        self._run_autonomous_cycle(observation)

    def _run_autonomous_cycle(
        self,
        observation,
    ) -> CapabilityRunResult | None:
        fingerprint = _autonomy_observation_fingerprint(observation)
        observed_at = observation.observed_at
        with self._lock:
            previous = self._autonomy_recent.get(fingerprint)
            repeated = (
                previous is not None
                and observed_at >= previous
                and observed_at - previous < self._autonomy_deduplication_window
            )
            if fingerprint in self._autonomy_in_progress or repeated:
                self._autonomy_suppressed_count += 1
                return None
            self._autonomy_in_progress.add(fingerprint)
            self._autonomy_recent[fingerprint] = observed_at
        try:
            try:
                result = self.autonomy_runner.run(
                    observation,
                    self.autonomy_policy,
                )
            except Exception as autonomy_error:
                with self._lock:
                    self._autonomous_cycle_count += 1
                    self._last_autonomy_result = None
                    self._last_autonomy_error = (
                        f"{type(autonomy_error).__name__}: {autonomy_error}"
                    )
                return None
            self.experience_memory.remember(result)
            notification = render_autonomy_notification(result)
            with self._lock:
                self._autonomous_cycle_count += 1
                self._last_autonomy_result = result
                self._last_autonomy_error = None
                if notification is not None:
                    self._presentations.put(notification)
                    self._autonomy_notification_count += 1
            return result
        finally:
            with self._lock:
                self._autonomy_in_progress.discard(fingerprint)

    def _require_running(self) -> None:
        with self._lock:
            if not self._running:
                raise RuntimeError("runtime executive integration is not running")


def render_executive_event(event: ExecutiveEvent) -> str:
    if isinstance(event, GenericTextEvent):
        return event.text
    if isinstance(event, BatteryLowEvent):
        state = "cargando" if event.charging else "sin cargar"
        return f"Batería baja: {event.battery_percent}% ({state})."
    if isinstance(event, ReminderDueEvent):
        return event.title
    if isinstance(event, AmbientObservationEvent):
        return event.observation
    if isinstance(event, VerifiedNewsEvent):
        return f"{event.headline} — {event.publisher}"
    if isinstance(event, ImportantEmailEvent):
        return f"Correo importante de {event.sender}: {event.subject}"
    if isinstance(event, VisualCaptureResultEvent):
        return event.description
    raise TypeError(f"unsupported executive event: {type(event).__name__}")


def _autonomy_observation_fingerprint(observation) -> tuple[object, ...]:
    volatile_prefixes = (
        "consecutive_failures=",
        "recovery_attempts=",
        "observation_id=",
    )
    stable_facts = tuple(
        fact for fact in observation.facts if not fact.startswith(volatile_prefixes)
    )
    return (
        observation.kind,
        observation.source,
        observation.severity.value,
        stable_facts,
        tuple(sorted(observation.attributes.items())),
    )
