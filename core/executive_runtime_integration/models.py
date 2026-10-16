from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.executive_coordinator import ExecutiveCoordinatorSnapshot
from core.executive_notification_broker import ExecutiveNotificationBrokerSnapshot
from core.executive_presence_attention import PresenceAttentionSnapshot
from core.executive_recovery_health import RecoveryHealthSnapshot


@dataclass(frozen=True, slots=True)
class RuntimeExecutiveSnapshot:
    running: bool
    published_count: int
    presented_count: int
    drained_count: int
    coordinator: ExecutiveCoordinatorSnapshot
    broker: ExecutiveNotificationBrokerSnapshot
    attention: PresenceAttentionSnapshot
    health: RecoveryHealthSnapshot
    autonomous_cycle_count: int = 0
    autonomy_notification_count: int = 0
    autonomy_suppressed_count: int = 0
    autonomy_experience_count: int = 0
    autonomy_experience_pattern_count: int = 0
    persistent_goal_count: int = 0
    active_persistent_goal_count: int = 0
    due_persistent_goal_count: int = 0
    self_reflection_count: int = 0
    persistent_goal_plan_count: int = 0
    active_goal_plan_count: int = 0
    completed_goal_plan_count: int = 0
    blocked_goal_plan_step_count: int = 0
    goal_blockage_report_count: int = 0
    blocked_goal_report_count: int = 0
    goal_selection_report_count: int = 0
    successful_goal_selection_count: int = 0
    next_step_proposal_count: int = 0
    actionable_next_step_proposal_count: int = 0
    capability_count: int = 0
    enabled_capability_count: int = 0
    contextual_initiative_count: int = 0
    proposal_candidate_count: int = 0
    operational_learning_count: int = 0
    actionable_operational_learning_count: int = 0
    last_autonomy_status: str | None = None
    last_autonomy_error: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        counters = (
            self.published_count,
            self.presented_count,
            self.drained_count,
            self.autonomous_cycle_count,
            self.autonomy_notification_count,
            self.autonomy_suppressed_count,
            self.autonomy_experience_count,
            self.autonomy_experience_pattern_count,
            self.persistent_goal_count,
            self.active_persistent_goal_count,
            self.due_persistent_goal_count,
            self.self_reflection_count,
            self.persistent_goal_plan_count,
            self.active_goal_plan_count,
            self.completed_goal_plan_count,
            self.blocked_goal_plan_step_count,
            self.goal_blockage_report_count,
            self.blocked_goal_report_count,
            self.goal_selection_report_count,
            self.successful_goal_selection_count,
            self.next_step_proposal_count,
            self.actionable_next_step_proposal_count,
            self.capability_count,
            self.enabled_capability_count,
            self.contextual_initiative_count,
            self.proposal_candidate_count,
            self.operational_learning_count,
            self.actionable_operational_learning_count,
        )
        if min(counters) < 0:
            raise ValueError("runtime executive counters must not be negative")
        if (
            self.actionable_operational_learning_count
            > self.operational_learning_count
        ):
            raise ValueError(
                "actionable operational learnings cannot exceed learnings"
            )
        if self.proposal_candidate_count > self.contextual_initiative_count:
            raise ValueError("proposal candidates cannot exceed initiatives")
        if self.enabled_capability_count > self.capability_count:
            raise ValueError("enabled capabilities cannot exceed capabilities")
        if self.actionable_next_step_proposal_count > self.next_step_proposal_count:
            raise ValueError("actionable proposals cannot exceed proposals")
        if (
            self.successful_goal_selection_count
            > self.goal_selection_report_count
        ):
            raise ValueError("successful selections cannot exceed selection reports")
        if self.blocked_goal_report_count > self.goal_blockage_report_count:
            raise ValueError("blocked reports cannot exceed blockage reports")
        if self.active_goal_plan_count > self.persistent_goal_plan_count:
            raise ValueError("active goal plans cannot exceed persistent goal plans")
        if self.completed_goal_plan_count > self.persistent_goal_plan_count:
            raise ValueError("completed goal plans cannot exceed persistent goal plans")
        if (
            self.active_goal_plan_count + self.completed_goal_plan_count
            > self.persistent_goal_plan_count
        ):
            raise ValueError(
                "classified goal plans cannot exceed persistent goal plans"
            )
        if self.active_persistent_goal_count > self.persistent_goal_count:
            raise ValueError("active goals cannot exceed persistent goals")
        if self.due_persistent_goal_count > self.active_persistent_goal_count:
            raise ValueError("due goals cannot exceed active goals")
        if self.presented_count > self.published_count:
            raise ValueError("presented events cannot exceed published events")
        available_notifications = (
            self.presented_count + self.autonomy_notification_count
        )
        if self.drained_count > available_notifications:
            raise ValueError(
                "drained notifications cannot exceed available presentations"
            )
        if self.updated_at.tzinfo is None:
            raise ValueError("runtime executive timestamp must be timezone-aware")
