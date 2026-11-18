"""Structural operation-to-turn matching without authorization."""

from app.cross_domain_operation_evidence import CrossDomainOperationEvidence


def matches_operation_to_turn(
    evidence: CrossDomainOperationEvidence,
    turn: object,
    turns: tuple[object, ...],
) -> bool:
    """Check structural identity only; never authorize provenance."""
    if not isinstance(evidence, CrossDomainOperationEvidence):
        return False

    owner = getattr(turn, "owner", None)
    session_id = getattr(turn, "session_id", None)
    turn_id = getattr(turn, "turn_id", None)
    sequence = getattr(turn, "sequence", None)

    if (
        not isinstance(owner, str)
        or not owner.strip()
        or not isinstance(session_id, str)
        or not session_id.strip()
        or not isinstance(turn_id, str)
        or not turn_id.strip()
        or type(sequence) is not int
        or sequence <= 0
    ):
        return False

    if owner != evidence.owner or session_id != evidence.session_id:
        return False

    try:
        iterator = iter(turns)
        for candidate in iterator:
            if (
                getattr(candidate, "owner", None) == owner
                and getattr(candidate, "session_id", None) == session_id
                and getattr(candidate, "turn_id", None) == turn_id
                and type(getattr(candidate, "sequence", None)) is int
                and getattr(candidate, "sequence", None) == sequence
            ):
                return True
    except (TypeError, AttributeError):
        return False

    return False