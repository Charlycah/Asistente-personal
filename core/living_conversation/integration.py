from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .curiosity import (
    IntellectualCuriosityPlan,
    IntellectualCuriosityPrompt,
    IntellectualCuriosityStatus,
)
from .feedback import ConversationalFeedbackStatus
from .interests import SharedIntellectualInterestStatus
from .presence import ConversationalPresenceStatus
from .realization import ConversationalRealizationStatus
from .rhythm import ConversationalRhythm, ConversationalRhythmStatus


class LivingConversationIntegrationStatus(str, Enum):
    READY = "ready"
    REVIEW_REQUIRED = "review_required"
    PAUSED = "paused"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationNextMove(str, Enum):
    EXPLORE = "explore"
    CLARIFY = "clarify"
    WAIT = "wait"
    CLOSE = "close"
    NONE = "none"


@dataclass(frozen=True)
class LivingConversationIntegrationPolicy:
    require_generated_curiosity: bool = True
    block_when_user_floor_is_preserved: bool = True
    block_when_follow_up_is_disallowed: bool = True


@dataclass(frozen=True)
class LivingConversationIntegrationRequest:
    curiosity: IntellectualCuriosityPlan
    owner: str
    cycle_label: str = "living-conversation"
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("integration owner must not be blank")
        if self.owner.casefold() != self.curiosity.request.owner.casefold():
            raise ValueError("integration owner must match curiosity owner")
        if not self.cycle_label.strip():
            raise ValueError("integration cycle label must not be blank")
        if self.requested_at.tzinfo is None:
            raise ValueError("integration request timestamp must be aware")


@dataclass(frozen=True)
class LivingConversationIntegration:
    request: LivingConversationIntegrationRequest
    status: LivingConversationIntegrationStatus | str
    next_move: LivingConversationNextMove | str
    selected_prompt: IntellectualCuriosityPrompt | None
    eligible_for_activation: bool
    preserve_user_floor: bool
    stage_reference_ids: tuple[str, ...]
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    integration_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", LivingConversationIntegrationStatus(self.status)
        )
        object.__setattr__(
            self, "next_move", LivingConversationNextMove(self.next_move)
        )
        if not self.stage_reference_ids or any(
            not item.strip() for item in self.stage_reference_ids
        ):
            raise ValueError("integration stage references must not be empty")
        if len(self.stage_reference_ids) != len(set(self.stage_reference_ids)):
            raise ValueError("integration stage references must be unique")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("integration rationale must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("integration timestamp must be aware")
        if (
            self.eligible_for_activation
            and self.status is not LivingConversationIntegrationStatus.READY
        ):
            raise ValueError("only ready integration may be eligible for activation")
        if self.eligible_for_activation and self.selected_prompt is None:
            raise ValueError("activation eligibility requires a selected prompt")
        if (
            self.status
            in {
                LivingConversationIntegrationStatus.PAUSED,
                LivingConversationIntegrationStatus.NOT_APPLICABLE,
            }
            and self.selected_prompt is not None
        ):
            raise ValueError("inactive integration cannot select a prompt")
        expected = sha256(
            "|".join(
                (
                    self.request.curiosity.plan_id,
                    self.request.owner.casefold(),
                    self.request.cycle_label,
                    self.status.value,
                    self.next_move.value,
                    self.selected_prompt.prompt if self.selected_prompt else "",
                    str(self.eligible_for_activation),
                    str(self.preserve_user_floor),
                    ";".join(self.stage_reference_ids),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.integration_id and self.integration_id != expected:
            raise ValueError("integration id is inconsistent")
        object.__setattr__(self, "integration_id", expected)


@runtime_checkable
class LivingConversationIntegrationRepository(Protocol):
    def add(self, integration: LivingConversationIntegration) -> None: ...
    def get(self, integration_id: str) -> LivingConversationIntegration | None: ...
    def list_all(self) -> tuple[LivingConversationIntegration, ...]: ...


class InMemoryLivingConversationIntegrationRepository:
    def __init__(self) -> None:
        self._items: dict[str, LivingConversationIntegration] = {}

    def add(self, integration: LivingConversationIntegration) -> None:
        if integration.integration_id in self._items:
            raise ValueError("living conversation integration already exists")
        self._items[integration.integration_id] = integration

    def get(self, integration_id: str) -> LivingConversationIntegration | None:
        return self._items.get(integration_id)

    def list_all(self) -> tuple[LivingConversationIntegration, ...]:
        return tuple(self._items.values())


class LivingConversationIntegrator:
    """Closes the M93-M104 loop without activating or delivering conversation."""

    def __init__(
        self,
        *,
        repository: LivingConversationIntegrationRepository | None = None,
        policy: LivingConversationIntegrationPolicy | None = None,
    ) -> None:
        self.repository = (
            repository or InMemoryLivingConversationIntegrationRepository()
        )
        self.policy = policy or LivingConversationIntegrationPolicy()

    @property
    def last_integration(self) -> LivingConversationIntegration | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def integrate(
        self,
        request: LivingConversationIntegrationRequest,
        *,
        now: datetime | None = None,
    ) -> LivingConversationIntegration:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("integration timestamp must be aware")
        self._validate_chain(request)
        status, next_move, prompt, eligible, rationale = self._evaluate(request)
        rhythm = request.curiosity.request.interests.request.rhythm
        result = LivingConversationIntegration(
            request=request,
            status=status,
            next_move=next_move,
            selected_prompt=prompt,
            eligible_for_activation=eligible,
            preserve_user_floor=rhythm.preserve_user_floor,
            stage_reference_ids=self._stage_references(request),
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(result)
        return result

    def _validate_chain(self, request: LivingConversationIntegrationRequest) -> None:
        curiosity = request.curiosity
        interests = curiosity.request.interests
        rhythm = interests.request.rhythm
        feedback = rhythm.request.feedback
        presence = feedback.request.presence
        realization = presence.request.realization
        contribution = realization.request.contribution
        owners = (
            curiosity.request.owner,
            interests.request.owner,
            rhythm.request.owner,
            feedback.request.owner,
            presence.request.owner,
            realization.request.owner,
            contribution.request.governance.context.owner,
        )
        if any(owner.casefold() != request.owner.casefold() for owner in owners):
            raise ValueError("living conversation chain owner mismatch")

    def _evaluate(self, request: LivingConversationIntegrationRequest):
        curiosity = request.curiosity
        interests = curiosity.request.interests
        rhythm = interests.request.rhythm
        feedback = rhythm.request.feedback
        presence = feedback.request.presence
        realization = presence.request.realization

        non_applicable = (
            curiosity.status is IntellectualCuriosityStatus.NOT_APPLICABLE
            or interests.status is SharedIntellectualInterestStatus.NOT_APPLICABLE
            or rhythm.status is ConversationalRhythmStatus.NOT_APPLICABLE
            or feedback.status is ConversationalFeedbackStatus.NOT_APPLICABLE
            or presence.status is ConversationalPresenceStatus.ABSTAINED
            or realization.status is ConversationalRealizationStatus.ABSTAINED
        )
        if non_applicable:
            return (
                LivingConversationIntegrationStatus.NOT_APPLICABLE,
                LivingConversationNextMove.NONE,
                None,
                False,
                ("conversation_chain_is_not_applicable",),
            )

        review_required = (
            curiosity.status is IntellectualCuriosityStatus.REVIEW_REQUIRED
            or interests.status is SharedIntellectualInterestStatus.REVIEW_REQUIRED
            or rhythm.status is ConversationalRhythmStatus.REVIEW_REQUIRED
            or feedback.status is ConversationalFeedbackStatus.REVIEW_REQUIRED
            or presence.status is ConversationalPresenceStatus.REVIEW_REQUIRED
            or realization.status is ConversationalRealizationStatus.REVIEW_REQUIRED
        )
        if review_required:
            return (
                LivingConversationIntegrationStatus.REVIEW_REQUIRED,
                LivingConversationNextMove.CLARIFY,
                curiosity.prompts[0] if curiosity.prompts else None,
                False,
                ("upstream_review_is_required",),
            )

        if rhythm.rhythm is ConversationalRhythm.CLOSING:
            return (
                LivingConversationIntegrationStatus.PAUSED,
                LivingConversationNextMove.CLOSE,
                None,
                False,
                ("conversational_rhythm_is_closing",),
            )
        if (
            self.policy.block_when_user_floor_is_preserved
            and rhythm.preserve_user_floor
        ):
            return (
                LivingConversationIntegrationStatus.PAUSED,
                LivingConversationNextMove.WAIT,
                None,
                False,
                ("user_floor_must_be_preserved",),
            )
        if (
            self.policy.block_when_follow_up_is_disallowed
            and not rhythm.allow_follow_up_prompt
        ):
            return (
                LivingConversationIntegrationStatus.PAUSED,
                LivingConversationNextMove.WAIT,
                None,
                False,
                ("follow_up_prompt_is_disallowed",),
            )
        if curiosity.status is IntellectualCuriosityStatus.INSUFFICIENT:
            return (
                LivingConversationIntegrationStatus.PAUSED,
                LivingConversationNextMove.WAIT,
                None,
                False,
                ("curiosity_is_insufficient",),
            )
        if self.policy.require_generated_curiosity and (
            curiosity.status is not IntellectualCuriosityStatus.GENERATED
            or not curiosity.prompts
        ):
            return (
                LivingConversationIntegrationStatus.PAUSED,
                LivingConversationNextMove.WAIT,
                None,
                False,
                ("generated_curiosity_is_required",),
            )
        return (
            LivingConversationIntegrationStatus.READY,
            LivingConversationNextMove.EXPLORE,
            curiosity.prompts[0],
            True,
            ("living_conversation_cycle_is_coherent", "curiosity_is_eligible"),
        )

    @staticmethod
    def _stage_references(
        request: LivingConversationIntegrationRequest,
    ) -> tuple[str, ...]:
        curiosity = request.curiosity
        interests = curiosity.request.interests
        rhythm = interests.request.rhythm
        feedback = rhythm.request.feedback
        presence = feedback.request.presence
        realization = presence.request.realization
        contribution = realization.request.contribution
        reflection = contribution.request.reflection
        timing = contribution.request.timing
        governance = contribution.request.governance
        return (
            governance.decision_id,
            timing.timing_id,
            reflection.reflection_id,
            contribution.contribution_id,
            realization.realization_id,
            presence.presence_id,
            feedback.assessment_id,
            rhythm.decision_id,
            interests.assessment_id,
            curiosity.plan_id,
        )
