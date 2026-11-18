"""Runtime-owned authorization boundary for cross-domain context."""

from app.cross_domain_context_adapter import (
    resolve_authorized_cross_domain_context,
)
from app.cross_domain_context_provenance import (
    CrossDomainContextProvenance,
)
from app.cross_domain_context_resolver import (
    ContextDecision,
    ContextResolution,
)


def resolve_runtime_cross_domain_context(
    text: str,
    *,
    runtime: object,
    session_id: str,
    provenance: CrossDomainContextProvenance,
) -> ContextResolution:
    """Resolve context using the runtime's identity gate and turn reader."""

    unresolved = ContextResolution(
        decision=ContextDecision.UNRESOLVED,
        reason="runtime_context_not_authorized",
    )

    try:
        from core.cognitive_maturity import IdentityContextAccessGate

        gate = IdentityContextAccessGate.current()

        if (
            gate.governed_entry is not True
            or gate.session_scoped is not True
            or gate.shared_conversation_context_allowed is not True
        ):
            return unresolved

        bootstrap = getattr(runtime, "bootstrap", None)
        config = getattr(bootstrap, "config", None)

        owner = getattr(config, "owner", None)
        configured_session = getattr(config, "session_id", None)

        if not isinstance(owner, str) or not owner.strip():
            return unresolved

        if (
            not isinstance(configured_session, str)
            or not configured_session.strip()
            or configured_session != session_id
        ):
            return unresolved

        reader = getattr(runtime, "authorized_recent_turns", None)

        if not callable(reader):
            return unresolved

        if getattr(reader, "__self__", None) is not runtime:
            return unresolved

        return resolve_authorized_cross_domain_context(
            text,
            owner=owner,
            session_id=configured_session,
            context_allowed=True,
            authorized_turns_reader=reader,
            provenance=provenance,
        )
    except Exception:
        return unresolved
