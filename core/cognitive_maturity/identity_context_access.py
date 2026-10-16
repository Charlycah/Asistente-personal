from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Iterator

from .interlocutor import InterlocutorResolution


@dataclass(frozen=True)
class IdentityContextAccessDecision:
    governed_entry: bool
    identity_resolved: bool
    session_scoped: bool
    shared_conversation_context_allowed: bool
    private_context_allowed: bool
    reason_code: str
    shared_conversation_reason_code: str
    equal_coowner_authority: bool = True
    grants_action_authority: bool = False
    inferred_identity_used: bool = False
    persisted: bool = False

    def __post_init__(self) -> None:
        if self.shared_conversation_context_allowed and not self.session_scoped:
            raise ValueError(
                "shared conversation context requires matching session scope"
            )
        if self.governed_entry and (
            self.shared_conversation_context_allowed != self.session_scoped
        ):
            raise ValueError(
                "governed shared conversation context requires matching session scope"
            )
        if self.private_context_allowed and not self.session_scoped:
            raise ValueError("private context access requires matching session scope")
        if self.governed_entry and self.private_context_allowed != (
            self.identity_resolved and self.session_scoped
        ):
            raise ValueError("governed private context requires resolved identity")
        if not self.equal_coowner_authority or self.grants_action_authority:
            raise ValueError("identity context access cannot change authority")
        if self.inferred_identity_used or self.persisted:
            raise ValueError(
                "identity context access must remain explicit and ephemeral"
            )


_UNMANAGED_COMPATIBILITY = IdentityContextAccessDecision(
    governed_entry=False,
    identity_resolved=False,
    session_scoped=True,
    shared_conversation_context_allowed=True,
    private_context_allowed=True,
    reason_code="identity_context:unmanaged_compatibility",
    shared_conversation_reason_code=(
        "identity_context:shared_conversation_unmanaged_compatibility"
    ),
)

_CURRENT_ACCESS: ContextVar[IdentityContextAccessDecision] = ContextVar(
    "roby_identity_context_access",
    default=_UNMANAGED_COMPATIBILITY,
)


class IdentityContextAccessGate:
    """Govern shared and private context without changing authority."""

    @staticmethod
    def decide(
        resolution: InterlocutorResolution,
        *,
        session_id: str,
        context_session_id: str | None = None,
    ) -> IdentityContextAccessDecision:
        requested_session = session_id.strip()
        resource_session = (context_session_id or requested_session).strip()
        session_scoped = (
            resolution.session_id == requested_session
            and resource_session == requested_session
        )
        identity_resolved = resolution.interlocutor_resolved
        shared_conversation_allowed = session_scoped
        allowed = (
            identity_resolved
            and session_scoped
            and resolution.may_use_private_context
        )
        if not session_scoped:
            reason = "identity_context:session_mismatch"
            shared_reason = "identity_context:shared_conversation_session_mismatch"
        elif not identity_resolved:
            reason = "identity_context:identity_not_resolved"
            shared_reason = "identity_context:shared_conversation_allowed"
        else:
            reason = "identity_context:private_context_allowed"
            shared_reason = "identity_context:shared_conversation_allowed"
        return IdentityContextAccessDecision(
            governed_entry=True,
            identity_resolved=identity_resolved,
            session_scoped=session_scoped,
            shared_conversation_context_allowed=shared_conversation_allowed,
            private_context_allowed=allowed,
            reason_code=reason,
            shared_conversation_reason_code=shared_reason,
        )

    @classmethod
    @contextmanager
    def activate(
        cls,
        resolution: InterlocutorResolution,
        *,
        session_id: str,
        context_session_id: str | None = None,
    ) -> Iterator[IdentityContextAccessDecision]:
        decision = cls.decide(
            resolution,
            session_id=session_id,
            context_session_id=context_session_id,
        )
        token: Token[IdentityContextAccessDecision] = _CURRENT_ACCESS.set(
            decision
        )
        try:
            yield decision
        finally:
            _CURRENT_ACCESS.reset(token)

    @staticmethod
    def current() -> IdentityContextAccessDecision:
        return _CURRENT_ACCESS.get()
