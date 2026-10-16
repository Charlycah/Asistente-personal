from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .foundation import (
    ConversationDisposition,
    ConversationOpportunity,
    ConversationOpportunityKind,
    LivingConversationDecision,
)
from .timing import ConversationTimingDecision, TimingRecommendation


class ReflectionStatus(str, Enum):
    GENERATED = "generated"
    ABSTAINED = "abstained"
    REVIEW_REQUIRED = "review_required"


class ReflectionForm(str, Enum):
    RESPONSE = "response"
    QUESTION = "question"
    OBSERVATION = "observation"
    CONNECTION = "connection"
    CONTINUATION = "continuation"


class ReflectionTone(str, Enum):
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    THOUGHTFUL = "thoughtful"
    WARM = "warm"


@dataclass(frozen=True)
class ReflectionGenerationPolicy:
    maximum_key_points: int = 3
    maximum_text_length: int = 480
    require_sources_for_non_response: bool = True
    allow_sensitive_without_review: bool = False

    def __post_init__(self) -> None:
        if self.maximum_key_points <= 0:
            raise ValueError("maximum reflection key points must be positive")
        if self.maximum_text_length < 80:
            raise ValueError("maximum reflection text length must be at least 80")
        if self.allow_sensitive_without_review:
            raise ValueError("sensitive reflection cannot bypass review")


@dataclass(frozen=True)
class ReflectionDraft:
    opportunity: ConversationOpportunity
    governance_decision_id: str
    timing_decision_id: str
    status: ReflectionStatus | str
    form: ReflectionForm | str
    tone: ReflectionTone | str
    opening: str | None
    key_points: tuple[str, ...]
    closing_question: str | None
    source_reference_ids: tuple[str, ...]
    rationale: tuple[str, ...]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reflection_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ReflectionStatus(self.status))
        object.__setattr__(self, "form", ReflectionForm(self.form))
        object.__setattr__(self, "tone", ReflectionTone(self.tone))
        if not self.governance_decision_id.strip():
            raise ValueError("governance decision id must not be blank")
        if not self.timing_decision_id.strip():
            raise ValueError("timing decision id must not be blank")
        if self.generated_at.tzinfo is None:
            raise ValueError("reflection generation timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("reflection rationale must not be empty")
        if len(set(self.source_reference_ids)) != len(self.source_reference_ids):
            raise ValueError("reflection source references must be unique")
        if any(not item.strip() for item in self.source_reference_ids):
            raise ValueError("reflection source references must not be blank")
        if any(not item.strip() for item in self.key_points):
            raise ValueError("reflection key points must not be blank")
        if self.opening is not None and not self.opening.strip():
            raise ValueError("reflection opening must not be blank")
        if self.closing_question is not None and not self.closing_question.strip():
            raise ValueError("reflection closing question must not be blank")
        if self.status is ReflectionStatus.GENERATED and self.opening is None:
            raise ValueError("generated reflection must include an opening")
        if self.status is not ReflectionStatus.GENERATED and (
            self.opening is not None
            or self.key_points
            or self.closing_question is not None
        ):
            raise ValueError("non-generated reflection cannot contain draft content")

        expected = sha256(
            "|".join(
                (
                    self.governance_decision_id,
                    self.timing_decision_id,
                    self.status.value,
                    self.form.value,
                    self.tone.value,
                    self.opening or "",
                    ";".join(self.key_points),
                    self.closing_question or "",
                    ";".join(self.source_reference_ids),
                    ";".join(self.rationale),
                    self.generated_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.reflection_id and self.reflection_id != expected:
            raise ValueError("reflection id is inconsistent")
        object.__setattr__(self, "reflection_id", expected)

    @property
    def text(self) -> str | None:
        if self.status is not ReflectionStatus.GENERATED:
            return None
        parts = [self.opening or "", *self.key_points]
        if self.closing_question:
            parts.append(self.closing_question)
        return " ".join(parts)


@runtime_checkable
class ReflectionDraftRepository(Protocol):
    def add(self, draft: ReflectionDraft) -> None: ...

    def get(self, reflection_id: str) -> ReflectionDraft | None: ...

    def list_all(self) -> tuple[ReflectionDraft, ...]: ...


class InMemoryReflectionDraftRepository:
    def __init__(self) -> None:
        self._drafts: dict[str, ReflectionDraft] = {}

    def add(self, draft: ReflectionDraft) -> None:
        if draft.reflection_id in self._drafts:
            raise ValueError("reflection draft already exists")
        self._drafts[draft.reflection_id] = draft

    def get(self, reflection_id: str) -> ReflectionDraft | None:
        return self._drafts.get(reflection_id)

    def list_all(self) -> tuple[ReflectionDraft, ...]:
        return tuple(self._drafts.values())


class ReflectionGenerator:
    """Builds a bounded draft; it never speaks, schedules, or calls an LLM."""

    _FORM_BY_KIND = {
        ConversationOpportunityKind.RESPOND: ReflectionForm.RESPONSE,
        ConversationOpportunityKind.ASK: ReflectionForm.QUESTION,
        ConversationOpportunityKind.REFLECT: ReflectionForm.CONNECTION,
        ConversationOpportunityKind.SHARE: ReflectionForm.OBSERVATION,
        ConversationOpportunityKind.RESUME: ReflectionForm.CONTINUATION,
        ConversationOpportunityKind.WAIT: ReflectionForm.OBSERVATION,
        ConversationOpportunityKind.SILENCE: ReflectionForm.OBSERVATION,
    }

    _TONE_BY_FORM = {
        ReflectionForm.RESPONSE: ReflectionTone.WARM,
        ReflectionForm.QUESTION: ReflectionTone.CURIOUS,
        ReflectionForm.OBSERVATION: ReflectionTone.NEUTRAL,
        ReflectionForm.CONNECTION: ReflectionTone.THOUGHTFUL,
        ReflectionForm.CONTINUATION: ReflectionTone.WARM,
    }

    def __init__(
        self,
        *,
        repository: ReflectionDraftRepository | None = None,
        policy: ReflectionGenerationPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryReflectionDraftRepository()
        self.policy = policy or ReflectionGenerationPolicy()

    @property
    def last_draft(self) -> ReflectionDraft | None:
        drafts = self.repository.list_all()
        return drafts[-1] if drafts else None

    def generate(
        self,
        governance: LivingConversationDecision,
        timing: ConversationTimingDecision,
        *,
        now: datetime | None = None,
    ) -> ReflectionDraft:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("reflection generation timestamp must be timezone-aware")
        if governance.opportunity != timing.opportunity:
            raise ValueError(
                "governance and timing must reference the same opportunity"
            )
        if governance.context != timing.context.conversation:
            raise ValueError("governance and timing contexts must match")

        opportunity = governance.opportunity
        form = self._FORM_BY_KIND[opportunity.kind]
        tone = self._TONE_BY_FORM[form]
        status, rationale = self._eligibility(governance, timing)
        opening: str | None = None
        key_points: tuple[str, ...] = ()
        closing: str | None = None

        if status is ReflectionStatus.GENERATED:
            opening, key_points, closing = self._compose(opportunity, form)
            text = " ".join((opening, *key_points, closing or "")).strip()
            if len(text) > self.policy.maximum_text_length:
                status = ReflectionStatus.ABSTAINED
                rationale = ("generated_draft_exceeds_length_limit",)
                opening, key_points, closing = None, (), None

        draft = ReflectionDraft(
            opportunity=opportunity,
            governance_decision_id=governance.decision_id,
            timing_decision_id=timing.timing_id,
            status=status,
            form=form,
            tone=tone,
            opening=opening,
            key_points=key_points,
            closing_question=closing,
            source_reference_ids=opportunity.source_reference_ids,
            rationale=rationale,
            generated_at=timestamp,
        )
        self.repository.add(draft)
        return draft

    def _eligibility(
        self,
        governance: LivingConversationDecision,
        timing: ConversationTimingDecision,
    ) -> tuple[ReflectionStatus, tuple[str, ...]]:
        opportunity = governance.opportunity
        if governance.disposition is ConversationDisposition.REVIEW_REQUIRED:
            return ReflectionStatus.REVIEW_REQUIRED, ("governance_requires_review",)
        if (
            opportunity.requires_review
            or timing.recommendation is TimingRecommendation.REVIEW_REQUIRED
        ):
            return ReflectionStatus.REVIEW_REQUIRED, ("opportunity_requires_review",)
        if governance.disposition is not ConversationDisposition.INTERVENE:
            return ReflectionStatus.ABSTAINED, (
                "governance_does_not_authorize_intervention",
            )
        if timing.recommendation is not TimingRecommendation.INTERVENE_NOW:
            return ReflectionStatus.ABSTAINED, ("timing_window_is_not_open",)
        if opportunity.kind in {
            ConversationOpportunityKind.WAIT,
            ConversationOpportunityKind.SILENCE,
        }:
            return ReflectionStatus.ABSTAINED, (
                "opportunity_kind_does_not_support_generation",
            )
        if not opportunity.content_hint:
            return ReflectionStatus.ABSTAINED, ("content_hint_is_required",)
        if (
            self.policy.require_sources_for_non_response
            and opportunity.kind is not ConversationOpportunityKind.RESPOND
            and not opportunity.source_reference_ids
        ):
            return ReflectionStatus.ABSTAINED, ("source_reference_is_required",)
        return ReflectionStatus.GENERATED, ("bounded_reflection_draft_generated",)

    def _compose(
        self,
        opportunity: ConversationOpportunity,
        form: ReflectionForm,
    ) -> tuple[str, tuple[str, ...], str | None]:
        hint = (opportunity.content_hint or "").strip()
        reason = opportunity.reason.strip()
        if form is ReflectionForm.RESPONSE:
            return hint, (), None
        if form is ReflectionForm.QUESTION:
            return (
                f"Hay algo que podría valer la pena explorar: {hint}.",
                (),
                ("¿Te gustaría pensarlo juntos?"),
            )
        if form is ReflectionForm.CONNECTION:
            return f"Se me ocurre una conexión: {hint}.", (reason,), ("¿Cómo la ves?")
        if form is ReflectionForm.CONTINUATION:
            return (
                f"Podríamos retomar esto: {hint}.",
                (reason,),
                ("¿Querés que sigamos desde ahí?"),
            )
        return f"Quizás te interese esta observación: {hint}.", (reason,), None

    @staticmethod
    def system_prompt_lines() -> tuple[str, ...]:
        return (
            "M96 sólo compone un borrador estructurado y trazable.",
            "No habla, no envía, no agenda y no llama a un LLM.",
            "No inventa hechos: usa únicamente el content_hint y las "
            "fuentes recibidas.",
            "Se abstiene si M93 no autoriza o M95 no habilita el momento.",
        )
