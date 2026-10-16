from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from application.brain.dialogue_ambiguity import (
    DialogueAmbiguityDecision,
    DialogueAmbiguityKind,
)


class DialogueRepairKind(str, Enum):
    """Bounded repair outcomes owned by the Brain."""

    NONE = "none"
    CLARIFICATION_PENDING = "clarification_pending"
    REPAIRED = "repaired"


@dataclass(frozen=True)
class DialogueRepairDecision:
    kind: DialogueRepairKind
    repaired_reference: str | None = None


class DialogueRepairAnalyzer:
    """Recognize the next clear turn as a repair of a pending clarification."""

    def evaluate(
        self,
        text: str,
        *,
        ambiguity: DialogueAmbiguityDecision,
        clarification_pending: bool,
    ) -> DialogueRepairDecision:
        candidate = text.strip()
        if ambiguity.kind is DialogueAmbiguityKind.AMBIGUOUS_REFERENCE:
            return DialogueRepairDecision(DialogueRepairKind.CLARIFICATION_PENDING)
        if clarification_pending and candidate:
            return DialogueRepairDecision(
                DialogueRepairKind.REPAIRED,
                repaired_reference=candidate,
            )
        return DialogueRepairDecision(DialogueRepairKind.NONE)
