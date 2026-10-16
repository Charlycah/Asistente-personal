from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .elliptical_responses import (
    EllipticalResponseDecision,
    EllipticalResponseKind,
)
from .natural_confirmations import (
    NaturalConfirmationDecision,
    NaturalConfirmationKind,
)
from .natural_conversation import (
    NaturalConversationDecision,
    NaturalConversationKind,
)


class ConversationFluencyKind(str, Enum):
    """Conservative presentation modes for naturally connected turns."""

    DIRECT = "direct"
    MARKED_CONTINUATION = "marked_continuation"
    CONFIRMED_CONTINUATION = "confirmed_continuation"
    ELLIPTICAL_CONTINUATION = "elliptical_continuation"


@dataclass(frozen=True)
class ConversationFluencyDecision:
    kind: ConversationFluencyKind
    remove_redundant_bridge: bool = False


class ConversationFluencyAnalyzer:
    """Combine existing conversational signals without resolving user intent."""

    def evaluate(
        self,
        *,
        natural: NaturalConversationDecision,
        confirmation: NaturalConfirmationDecision,
        elliptical: EllipticalResponseDecision,
    ) -> ConversationFluencyDecision:
        if (
            elliptical.kind is not EllipticalResponseKind.NONE
            and elliptical.has_context
        ):
            return ConversationFluencyDecision(
                kind=ConversationFluencyKind.ELLIPTICAL_CONTINUATION,
                remove_redundant_bridge=True,
            )
        if (
            confirmation.kind is not NaturalConfirmationKind.NONE
            and confirmation.has_context
        ):
            return ConversationFluencyDecision(
                kind=ConversationFluencyKind.CONFIRMED_CONTINUATION,
                remove_redundant_bridge=True,
            )
        if natural.kind is NaturalConversationKind.DISCOURSE_MARKER:
            return ConversationFluencyDecision(
                kind=ConversationFluencyKind.MARKED_CONTINUATION,
                remove_redundant_bridge=True,
            )
        return ConversationFluencyDecision(kind=ConversationFluencyKind.DIRECT)
