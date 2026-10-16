from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .permissions import EQUAL_COOWNERS, CoownerIdentity

_SAFE_SESSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class InterlocutorResolutionStatus(str, Enum):
    UNKNOWN = "unknown"
    PENDING_CONFIRMATION = "pending_confirmation"
    RESOLVED = "resolved"
    CONFLICT = "conflict"
    REVOKED = "revoked"


class InterlocutorResolutionSource(str, Enum):
    EXPLICIT_DECLARATION = "explicit_declaration"
    EXPLICIT_SESSION_SELECTION = "explicit_session_selection"
    EXPLICIT_RECONFIRMATION = "explicit_reconfirmation"


class InterlocutorResolutionAction(str, Enum):
    DECLARE = "declare"
    REVOKE = "revoke"


def _coowner(
    value: CoownerIdentity | str | None,
) -> CoownerIdentity | None:
    if value is None:
        return None
    if isinstance(value, CoownerIdentity):
        return value
    normalized = value.strip().casefold()
    for coowner in EQUAL_COOWNERS:
        if coowner.value.casefold() == normalized:
            return coowner
    raise ValueError("interlocutor must be Carlos or Cristina")


@dataclass(frozen=True)
class InterlocutorResolutionRequest:
    session_id: str
    action: InterlocutorResolutionAction | str
    source: InterlocutorResolutionSource | str
    declared_interlocutor: CoownerIdentity | str | None = None
    current_interlocutor: CoownerIdentity | str | None = None
    confirmed: bool = False
    replace_existing: bool = False

    def __post_init__(self) -> None:
        session_id = self.session_id.strip()
        if not _SAFE_SESSION.fullmatch(session_id):
            raise ValueError("interlocutor session id must be a safe identifier")
        action = InterlocutorResolutionAction(self.action)
        source = InterlocutorResolutionSource(self.source)
        declared = _coowner(self.declared_interlocutor)
        current = _coowner(self.current_interlocutor)
        if action is InterlocutorResolutionAction.DECLARE and declared is None:
            raise ValueError("interlocutor declaration requires a coowner")
        if action is InterlocutorResolutionAction.REVOKE and declared is not None:
            raise ValueError("interlocutor revocation cannot declare a coowner")
        if action is InterlocutorResolutionAction.REVOKE and not self.confirmed:
            raise ValueError("interlocutor revocation requires confirmation")
        if action is InterlocutorResolutionAction.REVOKE and source is not (
            InterlocutorResolutionSource.EXPLICIT_RECONFIRMATION
        ):
            raise ValueError("interlocutor revocation requires reconfirmation")
        if self.replace_existing and (
            action is not InterlocutorResolutionAction.DECLARE
            or not self.confirmed
        ):
            raise ValueError("interlocutor replacement must be confirmed")
        if self.replace_existing and source is not (
            InterlocutorResolutionSource.EXPLICIT_RECONFIRMATION
        ):
            raise ValueError("interlocutor replacement requires reconfirmation")
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "declared_interlocutor", declared)
        object.__setattr__(self, "current_interlocutor", current)


@dataclass(frozen=True)
class InterlocutorResolution:
    session_id: str
    status: InterlocutorResolutionStatus | str
    source: InterlocutorResolutionSource | None
    interlocutor: CoownerIdentity | None
    candidate: CoownerIdentity | None
    reason_code: str
    resolution_id: str = ""
    scope: str = "session"
    equal_coowner_authority: bool = True
    grants_action_authority: bool = False
    biometric_evidence_used: bool = False
    inferred_identity_used: bool = False

    def __post_init__(self) -> None:
        status = InterlocutorResolutionStatus(self.status)
        source = (
            InterlocutorResolutionSource(self.source)
            if self.source is not None
            else None
        )
        interlocutor = _coowner(self.interlocutor)
        candidate = _coowner(self.candidate)
        if not _SAFE_SESSION.fullmatch(self.session_id):
            raise ValueError("interlocutor resolution session is invalid")
        if not re.fullmatch(r"[a-z0-9][a-z0-9._:-]{0,127}", self.reason_code):
            raise ValueError("interlocutor resolution reason must be a safe code")
        if self.scope != "session":
            raise ValueError("interlocutor resolution must be session scoped")
        if not self.equal_coowner_authority or self.grants_action_authority:
            raise ValueError("interlocutor resolution cannot alter coowner authority")
        if self.biometric_evidence_used or self.inferred_identity_used:
            raise ValueError("interlocutor resolution must use explicit evidence")
        if status is InterlocutorResolutionStatus.RESOLVED:
            if interlocutor is None or candidate is None:
                raise ValueError("resolved interlocutor requires one coowner")
            if interlocutor is not candidate:
                raise ValueError("resolved interlocutor must match candidate")
        elif interlocutor is not None:
            raise ValueError("unresolved status cannot expose an interlocutor")
        if status is InterlocutorResolutionStatus.PENDING_CONFIRMATION and (
            candidate is None
        ):
            raise ValueError("pending interlocutor requires a candidate")
        if status in {
            InterlocutorResolutionStatus.UNKNOWN,
            InterlocutorResolutionStatus.REVOKED,
        } and candidate is not None:
            raise ValueError("unknown or revoked identity cannot expose a candidate")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "interlocutor", interlocutor)
        object.__setattr__(self, "candidate", candidate)
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.resolution_id and self.resolution_id != expected:
            raise ValueError("interlocutor resolution id is inconsistent")
        object.__setattr__(self, "resolution_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.session_id,
                self.status.value,
                self.source.value if self.source else "none",
                self.interlocutor.value if self.interlocutor else "none",
                self.candidate.value if self.candidate else "none",
                self.reason_code,
            )
        )

    @property
    def interlocutor_resolved(self) -> bool:
        return self.status is InterlocutorResolutionStatus.RESOLVED

    @property
    def may_use_private_context(self) -> bool:
        return self.interlocutor_resolved


class CanonicalInterlocutorResolver:
    """Resolve only explicit session-scoped declarations by equal coowners."""

    def resolve(
        self,
        request: InterlocutorResolutionRequest,
    ) -> InterlocutorResolution:
        if request.action is InterlocutorResolutionAction.REVOKE:
            return self._result(
                request,
                InterlocutorResolutionStatus.REVOKED,
                interlocutor=None,
                candidate=None,
                reason="interlocutor:revoked",
            )
        candidate = request.declared_interlocutor
        if not request.confirmed:
            return self._result(
                request,
                InterlocutorResolutionStatus.PENDING_CONFIRMATION,
                interlocutor=None,
                candidate=candidate,
                reason="interlocutor:confirmation_required",
            )
        changing = (
            request.current_interlocutor is not None
            and request.current_interlocutor is not candidate
        )
        if changing and not request.replace_existing:
            return self._result(
                request,
                InterlocutorResolutionStatus.CONFLICT,
                interlocutor=None,
                candidate=candidate,
                reason="interlocutor:replacement_confirmation_required",
            )
        return self._result(
            request,
            InterlocutorResolutionStatus.RESOLVED,
            interlocutor=candidate,
            candidate=candidate,
            reason=(
                "interlocutor:explicitly_replaced"
                if changing
                else "interlocutor:explicitly_resolved"
            ),
        )

    @staticmethod
    def unresolved(session_id: str) -> InterlocutorResolution:
        return InterlocutorResolution(
            session_id=session_id,
            status=InterlocutorResolutionStatus.UNKNOWN,
            source=None,
            interlocutor=None,
            candidate=None,
            reason_code="interlocutor:not_declared",
        )

    @staticmethod
    def _result(
        request: InterlocutorResolutionRequest,
        status: InterlocutorResolutionStatus,
        *,
        interlocutor: CoownerIdentity | None,
        candidate: CoownerIdentity | None,
        reason: str,
    ) -> InterlocutorResolution:
        return InterlocutorResolution(
            session_id=request.session_id,
            status=status,
            source=request.source,
            interlocutor=interlocutor,
            candidate=candidate,
            reason_code=reason,
        )
