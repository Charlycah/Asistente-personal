from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .foundation import ConversationOpportunityKind
from .intellectual import (
    IntellectualContribution,
    IntellectualContributionKind,
    IntellectualContributionStatus,
)


class ConversationalAct(str, Enum):
    ANSWER = "answer"
    QUESTION = "question"
    OBSERVATION = "observation"
    CONNECTION = "connection"
    CONTINUATION = "continuation"


class ConversationalRegister(str, Enum):
    CONCISE = "concise"
    NATURAL = "natural"
    DELIBERATE = "deliberate"


class ConversationalRealizationStatus(str, Enum):
    READY = "ready"
    ABSTAINED = "abstained"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class ConversationalRealizationPolicy:
    maximum_character_count: int = 900
    maximum_segments: int = 7
    allow_title_in_utterance: bool = False
    allow_owner_address: bool = True
    require_closing_question_for_questions: bool = True

    def __post_init__(self) -> None:
        if self.maximum_character_count <= 0:
            raise ValueError("realization character limit must be positive")
        if self.maximum_segments <= 0:
            raise ValueError("realization segment limit must be positive")


@dataclass(frozen=True)
class ConversationalRealizationRequest:
    contribution: IntellectualContribution
    owner: str
    register: ConversationalRegister | str = ConversationalRegister.NATURAL
    address_owner: bool = False
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "register", ConversationalRegister(self.register))
        if not self.owner.strip():
            raise ValueError("realization owner must not be blank")
        if self.requested_at.tzinfo is None:
            raise ValueError("realization request timestamp must be timezone-aware")
        governed_owner = self.contribution.request.governance.context.owner
        if self.owner.casefold() != governed_owner.casefold():
            raise ValueError("realization owner must match governed conversation owner")


@dataclass(frozen=True)
class ConversationalRealization:
    request: ConversationalRealizationRequest
    status: ConversationalRealizationStatus | str
    act: ConversationalAct | str
    segments: tuple[str, ...]
    source_reference_ids: tuple[str, ...]
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    realization_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ConversationalRealizationStatus(self.status))
        object.__setattr__(self, "act", ConversationalAct(self.act))
        if self.created_at.tzinfo is None:
            raise ValueError(
                "conversational realization timestamp must be timezone-aware"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("conversational realization rationale must not be empty")
        if any(not item.strip() for item in self.segments):
            raise ValueError("conversational realization segments must not be blank")
        if len(set(self.source_reference_ids)) != len(self.source_reference_ids):
            raise ValueError("conversational realization sources must be unique")
        if any(not item.strip() for item in self.source_reference_ids):
            raise ValueError("conversational realization sources must not be blank")
        if self.status is ConversationalRealizationStatus.READY:
            if not self.segments:
                raise ValueError("ready conversational realization requires segments")
        elif self.segments:
            raise ValueError(
                "non-ready conversational realization cannot contain segments"
            )

        expected = sha256(
            "|".join(
                (
                    self.request.contribution.contribution_id,
                    self.request.owner.casefold(),
                    self.request.register.value,
                    str(self.request.address_owner),
                    self.status.value,
                    self.act.value,
                    ";".join(self.segments),
                    ";".join(self.source_reference_ids),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.realization_id and self.realization_id != expected:
            raise ValueError("conversational realization id is inconsistent")
        object.__setattr__(self, "realization_id", expected)

    @property
    def text(self) -> str | None:
        if self.status is not ConversationalRealizationStatus.READY:
            return None
        return " ".join(self.segments)


@runtime_checkable
class ConversationalRealizationRepository(Protocol):
    def add(self, realization: ConversationalRealization) -> None: ...

    def get(self, realization_id: str) -> ConversationalRealization | None: ...

    def list_all(self) -> tuple[ConversationalRealization, ...]: ...


class InMemoryConversationalRealizationRepository:
    def __init__(self) -> None:
        self._items: dict[str, ConversationalRealization] = {}

    def add(self, realization: ConversationalRealization) -> None:
        if realization.realization_id in self._items:
            raise ValueError("conversational realization already exists")
        self._items[realization.realization_id] = realization

    def get(self, realization_id: str) -> ConversationalRealization | None:
        return self._items.get(realization_id)

    def list_all(self) -> tuple[ConversationalRealization, ...]:
        return tuple(self._items.values())


class ConversationalRealizationLayer:
    """Realizes an approved contribution without delivering it to any channel."""

    _ACT_BY_KIND = {
        IntellectualContributionKind.RESPONSE: ConversationalAct.ANSWER,
        IntellectualContributionKind.QUESTION: ConversationalAct.QUESTION,
        IntellectualContributionKind.PERSPECTIVE: ConversationalAct.OBSERVATION,
        IntellectualContributionKind.CONTEXT: ConversationalAct.OBSERVATION,
        IntellectualContributionKind.CONNECTION: ConversationalAct.CONNECTION,
        IntellectualContributionKind.CONTINUATION: ConversationalAct.CONTINUATION,
    }

    def __init__(
        self,
        *,
        repository: ConversationalRealizationRepository | None = None,
        policy: ConversationalRealizationPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryConversationalRealizationRepository()
        self.policy = policy or ConversationalRealizationPolicy()

    @property
    def last_realization(self) -> ConversationalRealization | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def realize(
        self,
        request: ConversationalRealizationRequest,
        *,
        now: datetime | None = None,
    ) -> ConversationalRealization:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("realization timestamp must be timezone-aware")

        contribution = request.contribution
        act = self._ACT_BY_KIND[contribution.kind]
        status, rationale = self._eligibility(request, act)
        segments: tuple[str, ...] = ()

        if status is ConversationalRealizationStatus.READY:
            segments = self._segments(request, act)
            text = " ".join(segments)
            if len(segments) > self.policy.maximum_segments:
                status = ConversationalRealizationStatus.ABSTAINED
                rationale = ("realization_exceeds_segment_limit",)
                segments = ()
            elif len(text) > self.policy.maximum_character_count:
                status = ConversationalRealizationStatus.ABSTAINED
                rationale = ("realization_exceeds_character_limit",)
                segments = ()

        realization = ConversationalRealization(
            request=request,
            status=status,
            act=act,
            segments=segments,
            source_reference_ids=contribution.source_reference_ids,
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(realization)
        return realization

    def _eligibility(
        self,
        request: ConversationalRealizationRequest,
        act: ConversationalAct,
    ) -> tuple[ConversationalRealizationStatus, tuple[str, ...]]:
        contribution = request.contribution
        if contribution.status is IntellectualContributionStatus.REVIEW_REQUIRED:
            return ConversationalRealizationStatus.REVIEW_REQUIRED, (
                "intellectual_contribution_requires_review",
            )
        if contribution.status is not IntellectualContributionStatus.READY:
            return ConversationalRealizationStatus.ABSTAINED, (
                "intellectual_contribution_is_not_ready",
            )
        if contribution.text is None:
            return ConversationalRealizationStatus.ABSTAINED, (
                "intellectual_contribution_has_no_text",
            )
        if (
            act is ConversationalAct.QUESTION
            and self.policy.require_closing_question_for_questions
            and not contribution.closing_question
        ):
            return ConversationalRealizationStatus.ABSTAINED, (
                "question_realization_requires_closing_question",
            )
        if request.address_owner and not self.policy.allow_owner_address:
            return ConversationalRealizationStatus.ABSTAINED, (
                "owner_address_is_not_allowed",
            )
        return ConversationalRealizationStatus.READY, (
            "conversational_realization_ready",
        )

    def _segments(
        self,
        request: ConversationalRealizationRequest,
        act: ConversationalAct,
    ) -> tuple[str, ...]:
        contribution = request.contribution
        parts: list[str] = []
        opening = self._opening(request, act)
        if opening:
            parts.append(opening)
        if self.policy.allow_title_in_utterance and contribution.title:
            parts.append(f"{contribution.title}.")
        if contribution.thesis:
            parts.append(self._sentence(contribution.thesis))

        key_points = contribution.key_points
        if request.register is ConversationalRegister.CONCISE:
            key_points = key_points[:1]
        elif request.register is ConversationalRegister.NATURAL:
            key_points = key_points[:2]
        for point in key_points:
            parts.append(self._sentence(point))

        if contribution.closing_question:
            parts.append(self._question(contribution.closing_question))
        return tuple(parts)

    def _opening(
        self,
        request: ConversationalRealizationRequest,
        act: ConversationalAct,
    ) -> str | None:
        owner = request.owner.strip()
        prefix = f"{owner}, " if request.address_owner else ""
        explicit = (
            request.contribution.request.governance.opportunity.kind
            is ConversationOpportunityKind.RESPOND
        )
        if explicit and act is ConversationalAct.ANSWER:
            return f"{prefix}sí." if prefix else None
        labels = {
            ConversationalAct.QUESTION: "hay una pregunta que vale la pena abrir.",
            ConversationalAct.OBSERVATION: "hay algo que puede sumar contexto.",
            ConversationalAct.CONNECTION: "veo una conexión interesante.",
            ConversationalAct.CONTINUATION: "retomando ese hilo.",
            ConversationalAct.ANSWER: "una forma de verlo es esta.",
        }
        opening = labels[act]
        if request.register is ConversationalRegister.CONCISE and not prefix:
            return None
        return f"{prefix}{opening}"

    @staticmethod
    def _sentence(value: str) -> str:
        text = value.strip()
        if text.endswith((".", "!", "?")):
            return text
        return f"{text}."

    @staticmethod
    def _question(value: str) -> str:
        text = value.strip().rstrip(".")
        if text.endswith("?"):
            return text
        return f"{text}?"
