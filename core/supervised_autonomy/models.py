from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from enum import Enum
from hashlib import sha256


class AutonomyRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROHIBITED = "prohibited"


class AutonomyStatus(str, Enum):
    PROPOSED = "proposed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    BLOCKED = "blocked"


class AutonomyEventType(str, Enum):
    PROPOSED = "proposed"
    APPROVAL_REQUIRED = "approval_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTION_AUTHORIZED = "execution_authorized"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SupervisedAutonomyPolicy:
    proposal_ttl: timedelta = timedelta(minutes=10)
    execution_ttl: timedelta = timedelta(minutes=5)
    maximum_pending: int = 100
    allow_low_risk_automatic_approval: bool = False
    require_human_approval_for_medium_risk: bool = True
    require_human_approval_for_high_risk: bool = True
    prohibited_actions: tuple[str, ...] = (
        "run_shell",
        "delete_system_files",
        "disable_security",
        "expose_credentials",
    )
    high_risk_actions: tuple[str, ...] = (
        "send_email",
        "spend_money",
        "delete_user_data",
        "publish_content",
        "unlock_door",
    )
    medium_risk_actions: tuple[str, ...] = (
        "create_calendar_event",
        "modify_reminder",
        "sync_preferences",
    )

    def __post_init__(self) -> None:
        if self.proposal_ttl <= timedelta(0):
            raise ValueError("proposal ttl must be positive")
        if self.execution_ttl <= timedelta(0):
            raise ValueError("execution ttl must be positive")
        if self.maximum_pending <= 0:
            raise ValueError("maximum pending proposals must be positive")
        action_groups = (
            self.prohibited_actions,
            self.high_risk_actions,
            self.medium_risk_actions,
        )
        if any(not action.strip() for group in action_groups for action in group):
            raise ValueError("autonomy action names must not be blank")
        if set(self.prohibited_actions) & set(self.high_risk_actions):
            raise ValueError("prohibited actions cannot also be high risk")
        if set(self.prohibited_actions) & set(self.medium_risk_actions):
            raise ValueError("prohibited actions cannot also be medium risk")


@dataclass(frozen=True)
class AutonomyProposal:
    proposal_id: str
    action: str
    description: str
    requested_by: str
    created_at: datetime
    expires_at: datetime
    risk: AutonomyRisk | str
    status: AutonomyStatus | str
    rationale: tuple[str, ...]
    approved_by: str = ""
    approved_at: datetime | None = None
    execution_deadline: datetime | None = None
    result_summary: str = ""

    def __post_init__(self) -> None:
        if not self.proposal_id.strip():
            raise ValueError("proposal id must not be blank")
        if not self.action.strip() or not self.description.strip():
            raise ValueError("proposal action and description must not be blank")
        if not self.requested_by.strip():
            raise ValueError("proposal requester must not be blank")
        if self.created_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise ValueError("proposal timestamps must be timezone-aware")
        if self.expires_at <= self.created_at:
            raise ValueError("proposal expiration must follow creation")
        AutonomyRisk(self.risk)
        AutonomyStatus(self.status)
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("proposal rationale must not be empty")
        if self.approved_at is not None and self.approved_at.tzinfo is None:
            raise ValueError("approval timestamp must be timezone-aware")
        if self.execution_deadline is not None:
            if self.execution_deadline.tzinfo is None:
                raise ValueError("execution deadline must be timezone-aware")
            if self.approved_at is None:
                raise ValueError("execution deadline requires approval")

    @property
    def normalized_risk(self) -> AutonomyRisk:
        return AutonomyRisk(self.risk)

    @property
    def normalized_status(self) -> AutonomyStatus:
        return AutonomyStatus(self.status)

    def with_changes(self, **changes: object) -> AutonomyProposal:
        return replace(self, **changes)


@dataclass(frozen=True)
class AutonomyEvent:
    event_type: AutonomyEventType | str
    proposal_id: str
    occurred_at: datetime
    actor: str
    rationale: tuple[str, ...]
    event_id: str = ""

    def __post_init__(self) -> None:
        event_type = AutonomyEventType(self.event_type)
        if not self.proposal_id.strip() or not self.actor.strip():
            raise ValueError("autonomy event identity must not be blank")
        if self.occurred_at.tzinfo is None:
            raise ValueError("autonomy event timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("autonomy event rationale must not be empty")
        expected = sha256(
            "|".join(
                (
                    event_type.value,
                    self.proposal_id,
                    self.occurred_at.isoformat(),
                    self.actor,
                    ";".join(self.rationale),
                )
            ).encode()
        ).hexdigest()
        if self.event_id and self.event_id != expected:
            raise ValueError("autonomy event id is inconsistent")
        object.__setattr__(self, "event_type", event_type)
        object.__setattr__(self, "event_id", expected)


@dataclass(frozen=True)
class ExecutionAuthorization:
    proposal_id: str
    action: str
    authorized_at: datetime
    expires_at: datetime
    authorization_id: str = ""

    def __post_init__(self) -> None:
        if not self.proposal_id.strip() or not self.action.strip():
            raise ValueError("execution authorization identity must not be blank")
        if self.authorized_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise ValueError("authorization timestamps must be timezone-aware")
        if self.expires_at <= self.authorized_at:
            raise ValueError("authorization expiration must follow authorization")
        expected = sha256(
            f"{self.proposal_id}|{self.action}|{self.authorized_at.isoformat()}".encode()
        ).hexdigest()
        if self.authorization_id and self.authorization_id != expected:
            raise ValueError("execution authorization id is inconsistent")
        object.__setattr__(self, "authorization_id", expected)


@dataclass(frozen=True)
class SupervisedAutonomySnapshot:
    proposals: tuple[AutonomyProposal, ...]
    events: tuple[AutonomyEvent, ...] = field(default_factory=tuple)
