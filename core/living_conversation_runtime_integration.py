from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.living_conversation.integration import (
    LivingConversationIntegration,
    LivingConversationIntegrationStatus,
    LivingConversationNextMove,
)
from core.llm_provider import LLMRequest


@dataclass(frozen=True)
class LivingConversationRuntimeProjection:
    """Neutral immutable evidence consumed by the official cognitive runtime."""

    owner: str
    status: LivingConversationIntegrationStatus | str
    eligible_for_activation: bool
    preserve_user_floor: bool
    rhythm: str
    selected_prompt: str | None
    next_move: LivingConversationNextMove | str
    integration_id: str
    stage_reference_ids: tuple[str, ...]
    source_kind: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", LivingConversationIntegrationStatus(self.status)
        )
        object.__setattr__(
            self, "next_move", LivingConversationNextMove(self.next_move)
        )
        if not self.owner.strip():
            raise ValueError("living conversation runtime owner must not be blank")
        if not self.rhythm.strip():
            raise ValueError("living conversation runtime rhythm must not be blank")
        if not self.integration_id.strip():
            raise ValueError(
                "living conversation runtime integration id must not be blank"
            )
        if not self.source_kind.strip():
            raise ValueError(
                "living conversation runtime source kind must not be blank"
            )
        if any(not item.strip() for item in self.stage_reference_ids):
            raise ValueError("living conversation runtime references must not be blank")
        if len(self.stage_reference_ids) != len(set(self.stage_reference_ids)):
            raise ValueError("living conversation runtime references must be unique")
        if (
            self.eligible_for_activation
            and self.status is not LivingConversationIntegrationStatus.READY
        ):
            raise ValueError("only ready runtime projection may be activation eligible")
        if self.eligible_for_activation and not self.selected_prompt:
            raise ValueError("activation eligible runtime projection requires a prompt")
        if (
            self.status
            in {
                LivingConversationIntegrationStatus.PAUSED,
                LivingConversationIntegrationStatus.NOT_APPLICABLE,
            }
            and self.selected_prompt is not None
        ):
            raise ValueError("inactive runtime projection cannot select a prompt")


def project_living_conversation_integration(
    integration: LivingConversationIntegration,
) -> LivingConversationRuntimeProjection:
    """Project canonical M105 evidence without transferring its authority."""

    rhythm = integration.request.curiosity.request.interests.request.rhythm
    return LivingConversationRuntimeProjection(
        owner=integration.request.owner,
        status=integration.status,
        eligible_for_activation=integration.eligible_for_activation,
        preserve_user_floor=integration.preserve_user_floor,
        rhythm=rhythm.rhythm.value,
        selected_prompt=(
            integration.selected_prompt.prompt
            if integration.selected_prompt is not None
            else None
        ),
        next_move=integration.next_move,
        integration_id=integration.integration_id,
        stage_reference_ids=integration.stage_reference_ids,
        source_kind="m105_living_conversation_integration",
    )


@runtime_checkable
class LivingConversationIntegrationSource(Protocol):
    def resolve(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> LivingConversationRuntimeProjection | None: ...


@dataclass(frozen=True)
class LivingConversationRuntimeContributor:
    """Projects governed living-conversation evidence into one runtime turn."""

    source: LivingConversationIntegrationSource
    name: str = "living_conversation"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del request
        integration = self.source.resolve(
            owner=owner,
            session_id=session_id,
            text=text,
            now=now,
        )
        if integration is None:
            return self._skipped("living_conversation_context_unavailable")
        if integration.owner.casefold() != owner.casefold():
            raise ValueError("living conversation owner must match runtime owner")
        if integration.status is LivingConversationIntegrationStatus.REVIEW_REQUIRED:
            return self._skipped(
                "living_conversation_requires_review",
                integration.integration_id,
            )
        if integration.status in {
            LivingConversationIntegrationStatus.PAUSED,
            LivingConversationIntegrationStatus.NOT_APPLICABLE,
        }:
            return self._skipped(
                "living_conversation_is_inactive",
                integration.integration_id,
            )
        if not integration.eligible_for_activation:
            return self._skipped(
                "living_conversation_activation_not_eligible",
                integration.integration_id,
            )

        lines = [
            f"Cadencia conversacional: {integration.rhythm}.",
            f"Próximo movimiento conversacional: {integration.next_move.value}.",
        ]
        if integration.preserve_user_floor:
            lines.append(
                "Preservar el turno del usuario y evitar una continuación invasiva."
            )
        if integration.selected_prompt is not None:
            lines.append(
                "Orientación conversacional gobernada: "
                f"{integration.selected_prompt}"
            )
        references = (
            integration.integration_id,
            *integration.stage_reference_ids,
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=tuple(lines),
            reference_ids=references,
            rationale=("living_conversation_context_applied",),
        )

    def _skipped(
        self,
        rationale: str,
        reference_id: str | None = None,
    ) -> CognitiveRuntimeContribution:
        references = (reference_id,) if reference_id else ()
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.SKIPPED,
            reference_ids=references,
            rationale=(rationale,),
        )
