from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from app.personal_initiative_engine import (
    InitiativeDisposition,
    InitiativeProposal,
)
from core.living_conversation_runtime_integration import (
    LivingConversationRuntimeProjection,
)
from core.social_regulation import (
    SocialRegulationAction,
    SocialRegulationSnapshot,
)
from core.unified_companion_integration import (
    UnifiedCompanionIntegrationResult,
    UnifiedCompanionIntegrationStatus,
)


class FamilyParticipationDisposition(StrEnum):
    DELIVER = "deliver"
    DEFER = "defer"
    DISCARD = "discard"


@dataclass(frozen=True)
class FamilyParticipationDecision:
    disposition: FamilyParticipationDisposition
    rationale: str
    delivered: bool = False


class GovernedFamilyConversationalParticipationAdapter:
    """Compose existing governed readiness into bounded conversation delivery."""

    def __init__(self, *, publish_text: Callable[[str], None]) -> None:
        self._publish_text = publish_text

    def participate(
        self,
        *,
        consent: bool,
        involves_private_speech: bool,
        living_conversation: LivingConversationRuntimeProjection,
        initiative: InitiativeProposal,
        social: SocialRegulationSnapshot,
        companion: UnifiedCompanionIntegrationResult,
    ) -> FamilyParticipationDecision:
        if not consent:
            return self._discard("standing_audio_consent_required")
        if involves_private_speech:
            return self._discard("private_household_speech_requires_restraint")
        if not self._living_conversation_ready(living_conversation):
            return self._discard("living_conversation_not_ready")
        if not self._companion_ready(companion):
            return self._discard("unified_companion_not_ready")
        if social.action in {
            SocialRegulationAction.RESPECT_BOUNDARY,
            SocialRegulationAction.REDUCE_INITIATIVE,
        }:
            return self._defer("social_regulation_reduces_initiative")
        if initiative.disposition is InitiativeDisposition.DEFER:
            return self._defer("initiative_deferred")
        if initiative.disposition is InitiativeDisposition.DISCARD:
            return self._discard("initiative_discarded")
        if not initiative.should_speak:
            return self._discard("initiative_does_not_authorize_speech")

        prompt = living_conversation.selected_prompt
        if prompt is None or not prompt.strip():
            return self._discard("no_governed_conversational_prompt")

        self._publish_text(prompt)
        return FamilyParticipationDecision(
            disposition=FamilyParticipationDisposition.DELIVER,
            rationale="existing_governed_conversational_delivery",
            delivered=True,
        )

    @staticmethod
    def _living_conversation_ready(
        living_conversation: LivingConversationRuntimeProjection,
    ) -> bool:
        return (
            living_conversation.eligible_for_activation
            and living_conversation.preserve_user_floor
        )

    @staticmethod
    def _companion_ready(
        companion: UnifiedCompanionIntegrationResult,
    ) -> bool:
        return (
            companion.status is UnifiedCompanionIntegrationStatus.READY
            and companion.ready
            and not companion.confirmation_required
        )

    @staticmethod
    def _defer(rationale: str) -> FamilyParticipationDecision:
        return FamilyParticipationDecision(
            disposition=FamilyParticipationDisposition.DEFER,
            rationale=rationale,
        )

    @staticmethod
    def _discard(rationale: str) -> FamilyParticipationDecision:
        return FamilyParticipationDecision(
            disposition=FamilyParticipationDisposition.DISCARD,
            rationale=rationale,
        )
