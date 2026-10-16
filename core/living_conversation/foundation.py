from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable


class ConversationOpportunityKind(str, Enum):
    RESPOND = "respond"
    ASK = "ask"
    REFLECT = "reflect"
    SHARE = "share"
    RESUME = "resume"
    WAIT = "wait"
    SILENCE = "silence"


class ConversationDisposition(str, Enum):
    INTERVENE = "intervene"
    DEFER = "defer"
    REMAIN_SILENT = "remain_silent"
    REVIEW_REQUIRED = "review_required"


class ConversationContextMode(str, Enum):
    HOME = "home"
    WORK = "work"
    VACATION = "vacation"
    GUESTS = "guests"
    PRIVATE = "private"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ConversationOpportunity:
    kind: ConversationOpportunityKind | str
    reason: str
    value_score: float
    relevance_score: float
    confidence: float
    content_hint: str | None = None
    source_reference_ids: tuple[str, ...] = ()
    requires_review: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", ConversationOpportunityKind(self.kind))
        if not self.reason.strip():
            raise ValueError("conversation opportunity reason must not be blank")
        for name, value in (
            ("value", self.value_score),
            ("relevance", self.relevance_score),
            ("confidence", self.confidence),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"conversation opportunity {name} must be between 0 and 1"
                )
        if self.content_hint is not None and not self.content_hint.strip():
            raise ValueError("conversation opportunity content hint must not be blank")
        if len(set(self.source_reference_ids)) != len(self.source_reference_ids):
            raise ValueError("conversation opportunity references must be unique")
        if any(not item.strip() for item in self.source_reference_ids):
            raise ValueError("conversation opportunity references must not be blank")

    @property
    def score(self) -> float:
        return round(
            self.value_score * 0.45
            + self.relevance_score * 0.35
            + self.confidence * 0.20,
            6,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "reason": self.reason,
            "value_score": self.value_score,
            "relevance_score": self.relevance_score,
            "confidence": self.confidence,
            "score": self.score,
            "content_hint": self.content_hint,
            "source_reference_ids": list(self.source_reference_ids),
            "requires_review": self.requires_review,
        }


@dataclass(frozen=True)
class LivingConversationContext:
    owner: str
    mode: ConversationContextMode | str = ConversationContextMode.UNKNOWN
    user_present: bool = True
    explicit_user_turn: bool = False
    do_not_disturb: bool = False
    guests_present: bool = False
    sensitive_context: bool = False
    presence_snapshot_id: str | None = None
    relationship_snapshot_id: str | None = None
    initiative_snapshot_id: str | None = None
    social_regulation_snapshot_id: str | None = None
    adaptive_cognition_cycle_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "mode", ConversationContextMode(self.mode))
        if not self.owner.strip():
            raise ValueError("living conversation owner must not be blank")
        references = (
            self.presence_snapshot_id,
            self.relationship_snapshot_id,
            self.initiative_snapshot_id,
            self.social_regulation_snapshot_id,
            self.adaptive_cognition_cycle_id,
        )
        if any(item is not None and not item.strip() for item in references):
            raise ValueError("living conversation references must not be blank")
        if self.guests_present and self.mode is ConversationContextMode.PRIVATE:
            raise ValueError("private conversation mode cannot include guests")

    def to_dict(self) -> dict[str, object]:
        return {
            "owner": self.owner,
            "mode": self.mode.value,
            "user_present": self.user_present,
            "explicit_user_turn": self.explicit_user_turn,
            "do_not_disturb": self.do_not_disturb,
            "guests_present": self.guests_present,
            "sensitive_context": self.sensitive_context,
            "presence_snapshot_id": self.presence_snapshot_id,
            "relationship_snapshot_id": self.relationship_snapshot_id,
            "initiative_snapshot_id": self.initiative_snapshot_id,
            "social_regulation_snapshot_id": self.social_regulation_snapshot_id,
            "adaptive_cognition_cycle_id": self.adaptive_cognition_cycle_id,
        }


@dataclass(frozen=True)
class LivingConversationPolicy:
    intervention_threshold: float = 0.72
    defer_threshold: float = 0.48
    minimum_confidence: float = 0.60
    allow_unsolicited_sensitive_content: bool = False
    allow_guest_personalization: bool = False
    require_review_for_sensitive_context: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.defer_threshold < self.intervention_threshold <= 1.0:
            raise ValueError("living conversation thresholds must be ordered")
        if not 0.0 <= self.minimum_confidence <= 1.0:
            raise ValueError("living conversation confidence must be between 0 and 1")
        if self.allow_unsolicited_sensitive_content:
            raise ValueError("unsolicited sensitive content cannot be enabled")
        if self.allow_guest_personalization:
            raise ValueError("guest personalization cannot be enabled")


@dataclass(frozen=True)
class LivingConversationDecision:
    context: LivingConversationContext
    opportunity: ConversationOpportunity
    disposition: ConversationDisposition | str
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "disposition", ConversationDisposition(self.disposition)
        )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("living conversation rationale must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("living conversation timestamp must be timezone-aware")
        expected = sha256(
            "|".join(
                (
                    self.context.owner,
                    self.context.mode.value,
                    self.opportunity.kind.value,
                    f"{self.opportunity.score:.6f}",
                    self.disposition.value,
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("living conversation decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)

    @property
    def should_intervene(self) -> bool:
        return self.disposition is ConversationDisposition.INTERVENE

    def to_dict(self) -> dict[str, object]:
        return {
            "decision_id": self.decision_id,
            "context": self.context.to_dict(),
            "opportunity": self.opportunity.to_dict(),
            "disposition": self.disposition.value,
            "should_intervene": self.should_intervene,
            "rationale": list(self.rationale),
            "created_at": self.created_at.isoformat(),
        }


@runtime_checkable
class LivingConversationDecisionRepository(Protocol):
    def add(self, decision: LivingConversationDecision) -> None: ...

    def get(self, decision_id: str) -> LivingConversationDecision | None: ...

    def list_all(self) -> tuple[LivingConversationDecision, ...]: ...


class InMemoryLivingConversationDecisionRepository:
    def __init__(self) -> None:
        self._decisions: dict[str, LivingConversationDecision] = {}

    def add(self, decision: LivingConversationDecision) -> None:
        if decision.decision_id in self._decisions:
            raise ValueError("living conversation decision already exists")
        self._decisions[decision.decision_id] = decision

    def get(self, decision_id: str) -> LivingConversationDecision | None:
        return self._decisions.get(decision_id)

    def list_all(self) -> tuple[LivingConversationDecision, ...]:
        return tuple(self._decisions.values())


class LivingConversationManager:
    """Governed M93 boundary for deciding whether conversation adds value.

    The manager records a decision only. It never sends a message, calls an LLM,
    invokes a tool, updates memory, or schedules a future intervention.
    """

    def __init__(
        self,
        *,
        repository: LivingConversationDecisionRepository | None = None,
        policy: LivingConversationPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryLivingConversationDecisionRepository()
        self.policy = policy or LivingConversationPolicy()

    @property
    def last_decision(self) -> LivingConversationDecision | None:
        decisions = self.repository.list_all()
        return decisions[-1] if decisions else None

    def evaluate(
        self,
        context: LivingConversationContext,
        opportunity: ConversationOpportunity,
        *,
        now: datetime | None = None,
    ) -> LivingConversationDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("living conversation timestamp must be timezone-aware")

        disposition, rationale = self._decide(context, opportunity)
        decision = LivingConversationDecision(
            context=context,
            opportunity=opportunity,
            disposition=disposition,
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(decision)
        return decision

    def _decide(
        self,
        context: LivingConversationContext,
        opportunity: ConversationOpportunity,
    ) -> tuple[ConversationDisposition, tuple[str, ...]]:
        if context.do_not_disturb:
            return ConversationDisposition.REMAIN_SILENT, (
                "do_not_disturb_is_active",
                "human_attention_boundary_prevails",
            )
        if not context.user_present:
            return ConversationDisposition.DEFER, (
                "user_is_not_present",
                "no_message_is_emitted_or_scheduled",
            )
        if opportunity.kind in {
            ConversationOpportunityKind.WAIT,
            ConversationOpportunityKind.SILENCE,
        }:
            return ConversationDisposition.REMAIN_SILENT, (
                "opportunity_explicitly_favors_restraint",
            )
        if context.guests_present and opportunity.source_reference_ids:
            return ConversationDisposition.REMAIN_SILENT, (
                "guest_context_blocks_personalized_references",
                "privacy_prevails_over_conversational_value",
            )
        if context.sensitive_context or opportunity.requires_review:
            if self.policy.require_review_for_sensitive_context:
                return ConversationDisposition.REVIEW_REQUIRED, (
                    "sensitive_or_review_required_context",
                    "automatic_intervention_is_not_permitted",
                )
        if opportunity.confidence < self.policy.minimum_confidence:
            return ConversationDisposition.DEFER, ("confidence_below_policy_minimum",)
        if context.explicit_user_turn:
            return ConversationDisposition.INTERVENE, (
                "explicit_user_turn_requires_a_proportionate_response",
                "response_remains_subject_to_existing_social_regulation",
            )
        if opportunity.score >= self.policy.intervention_threshold:
            return ConversationDisposition.INTERVENE, (
                "expected_value_exceeds_intervention_threshold",
                "intervention_is_advisory_and_not_executed_by_m93",
            )
        if opportunity.score >= self.policy.defer_threshold:
            return ConversationDisposition.DEFER, (
                "opportunity_has_value_but_not_enough_for_intervention",
            )
        return ConversationDisposition.REMAIN_SILENT, (
            "expected_value_does_not_justify_interrupting",
        )

    @staticmethod
    def system_prompt_lines() -> tuple[str, ...]:
        return (
            "Living Conversation M93:",
            "- La presencia no obliga a hablar; el silencio puede ser la "
            "mejor decisión.",
            "- Toda intervención debe aportar valor contextual y proporcional.",
            "- Privacidad, límites humanos e invitados prevalecen sobre "
            "personalización.",
            "- M93 decide y registra; no emite mensajes, no agenda y no "
            "ejecuta acciones.",
        )
