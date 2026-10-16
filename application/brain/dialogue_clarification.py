from __future__ import annotations

from dataclasses import dataclass

from application.brain.dialogue_ambiguity import (
    DialogueAmbiguityDecision,
    DialogueAmbiguityKind,
)


@dataclass(frozen=True)
class DialogueClarificationDecision:
    required: bool
    response_text: str | None = None


class DialogueClarificationGuide:
    """Build a short clarification only for explicit ambiguous references."""

    _ALTERNATIVE_CUES = {
        "el otro",
        "la otra",
        "los otros",
        "las otras",
        "y el otro",
        "y la otra",
        "y los otros",
        "y las otras",
        "el anterior",
        "la anterior",
    }
    _DEMONSTRATIVE_CUES = {
        "ese",
        "esa",
        "esos",
        "esas",
        "eso",
        "aquello",
    }

    def guide(
        self,
        ambiguity: DialogueAmbiguityDecision,
    ) -> DialogueClarificationDecision:
        if ambiguity.kind is not DialogueAmbiguityKind.AMBIGUOUS_REFERENCE:
            return DialogueClarificationDecision(required=False)

        cue = ambiguity.cue or ""
        if cue in self._ALTERNATIVE_CUES:
            response = "¿A cuál de las opciones te referís?"
        elif cue in self._DEMONSTRATIVE_CUES:
            response = "¿A qué te referís exactamente?"
        else:
            response = "¿Podés aclararme a qué te referís?"

        return DialogueClarificationDecision(
            required=True,
            response_text=response,
        )
