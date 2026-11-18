"""Fail-closed adapter for cross-domain conversational context."""

from collections.abc import Callable

from app.cross_domain_context_provenance import (
    CrossDomainContextProvenance,
)
from app.cross_domain_context_resolver import (
    ContextDecision,
    ContextResolution,
    resolve_cross_domain_reference,
)


def resolve_authorized_cross_domain_context(
    text: str,
    *,
    owner: str,
    session_id: str,
    context_allowed: bool,
    authorized_turns_reader: Callable[[], tuple[object, ...]],
    provenance: CrossDomainContextProvenance,
) -> ContextResolution:
    """Resolve context without authorizing or executing capabilities."""

    unresolved = ContextResolution(
        decision=ContextDecision.UNRESOLVED,
        reason="cross_domain_context_unavailable",
    )

    if context_allowed is not True:
        return unresolved

    if not isinstance(owner, str) or not owner.strip():
        return unresolved

    if not isinstance(session_id, str) or not session_id.strip():
        return unresolved

    if not isinstance(text, str) or not text.strip():
        return unresolved

    if not callable(authorized_turns_reader):
        return unresolved

    if not isinstance(provenance, CrossDomainContextProvenance):
        return unresolved

    try:
        turns = authorized_turns_reader()
        if not isinstance(turns, (tuple, list)):
            return unresolved

        antecedents = provenance.authorized_antecedents(
            tuple(turns),
            owner=owner,
            session_id=session_id,
        )

        return resolve_cross_domain_reference(
            text,
            antecedents,
            owner=owner,
            session_id=session_id,
        )
    except Exception:
        return unresolved
