from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum

from .interlocutor import (
    InterlocutorResolutionAction,
    InterlocutorResolutionRequest,
    InterlocutorResolutionSource,
)
from .permissions import CoownerIdentity


class InterlocutorDeclarationKind(str, Enum):
    NO_MATCH = "no_match"
    DECLARATION = "declaration"
    CONFIRMATION = "confirmation"
    REPLACEMENT = "replacement"
    REVOCATION = "revocation"


@dataclass(frozen=True)
class InterlocutorDeclarationInterpretation:
    kind: InterlocutorDeclarationKind | str
    candidate: CoownerIdentity | None
    request: InterlocutorResolutionRequest | None
    response_code: str
    matched: bool
    grants_action_authority: bool = False

    def __post_init__(self) -> None:
        kind = InterlocutorDeclarationKind(self.kind)
        if not re.fullmatch(
            r"[a-z0-9][a-z0-9._:-]{0,127}", self.response_code
        ):
            raise ValueError("interlocutor interpretation requires a safe code")
        if kind is InterlocutorDeclarationKind.NO_MATCH:
            if self.matched or self.candidate is not None or self.request is not None:
                raise ValueError("unmatched interlocutor text cannot claim identity")
        elif not self.matched or self.request is None:
            raise ValueError("matched interlocutor command requires a request")
        if self.grants_action_authority:
            raise ValueError("interlocutor interpretation cannot grant authority")
        object.__setattr__(self, "kind", kind)


class ExplicitInterlocutorDeclarationInterpreter:
    """Interpret only exact, allow-listed identity commands."""

    _DECLARATIONS = {
        "soy carlos": CoownerIdentity.CARLOS,
        "soy cristina": CoownerIdentity.CRISTINA,
        "me identifico como carlos": CoownerIdentity.CARLOS,
        "me identifico como cristina": CoownerIdentity.CRISTINA,
    }
    _CONFIRMATIONS = {
        "confirmo que soy carlos": CoownerIdentity.CARLOS,
        "confirmo que soy cristina": CoownerIdentity.CRISTINA,
    }
    _REPLACEMENTS = {
        "confirmo cambiar interlocutor a carlos": CoownerIdentity.CARLOS,
        "confirmo cambiar interlocutor a cristina": CoownerIdentity.CRISTINA,
    }
    _REVOCATIONS = frozenset(
        {
            "confirmo revocar la identificacion del interlocutor",
            "confirmo cerrar la identificacion del interlocutor",
        }
    )

    def interpret(
        self,
        text: str,
        *,
        session_id: str,
    ) -> InterlocutorDeclarationInterpretation:
        normalized = self._normalize(text)
        if normalized in self._DECLARATIONS:
            candidate = self._DECLARATIONS[normalized]
            return self._declaration(
                candidate,
                session_id=session_id,
                confirmed=False,
            )
        if normalized in self._CONFIRMATIONS:
            candidate = self._CONFIRMATIONS[normalized]
            return self._declaration(
                candidate,
                session_id=session_id,
                confirmed=True,
            )
        if normalized in self._REPLACEMENTS:
            candidate = self._REPLACEMENTS[normalized]
            request = InterlocutorResolutionRequest(
                session_id=session_id,
                action=InterlocutorResolutionAction.DECLARE,
                source=InterlocutorResolutionSource.EXPLICIT_RECONFIRMATION,
                declared_interlocutor=candidate,
                confirmed=True,
                replace_existing=True,
            )
            return InterlocutorDeclarationInterpretation(
                kind=InterlocutorDeclarationKind.REPLACEMENT,
                candidate=candidate,
                request=request,
                response_code="interlocutor:replacement_confirmed",
                matched=True,
            )
        if normalized in self._REVOCATIONS:
            request = InterlocutorResolutionRequest(
                session_id=session_id,
                action=InterlocutorResolutionAction.REVOKE,
                source=InterlocutorResolutionSource.EXPLICIT_RECONFIRMATION,
                confirmed=True,
            )
            return InterlocutorDeclarationInterpretation(
                kind=InterlocutorDeclarationKind.REVOCATION,
                candidate=None,
                request=request,
                response_code="interlocutor:revocation_confirmed",
                matched=True,
            )
        return InterlocutorDeclarationInterpretation(
            kind=InterlocutorDeclarationKind.NO_MATCH,
            candidate=None,
            request=None,
            response_code="interlocutor:no_explicit_command",
            matched=False,
        )

    @staticmethod
    def _declaration(
        candidate: CoownerIdentity,
        *,
        session_id: str,
        confirmed: bool,
    ) -> InterlocutorDeclarationInterpretation:
        request = InterlocutorResolutionRequest(
            session_id=session_id,
            action=InterlocutorResolutionAction.DECLARE,
            source=InterlocutorResolutionSource.EXPLICIT_DECLARATION,
            declared_interlocutor=candidate,
            confirmed=confirmed,
        )
        return InterlocutorDeclarationInterpretation(
            kind=(
                InterlocutorDeclarationKind.CONFIRMATION
                if confirmed
                else InterlocutorDeclarationKind.DECLARATION
            ),
            candidate=candidate,
            request=request,
            response_code=(
                "interlocutor:declaration_confirmed"
                if confirmed
                else "interlocutor:confirmation_required"
            ),
            matched=True,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        decomposed = unicodedata.normalize("NFKD", text.strip().casefold())
        without_marks = "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        )
        without_terminal_punctuation = re.sub(
            r"[.!?]+$", "", without_marks.strip()
        )
        return " ".join(without_terminal_punctuation.split())
