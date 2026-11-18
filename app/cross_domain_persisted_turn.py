"""Non-authorizing verification of a persisted conversation turn."""

from core.end_to_end_local_conversation.models import LocalConversationTurn


def matches_persisted_turn(
    turn: LocalConversationTurn,
    *,
    journal: object,
) -> bool:
    """Check journal consistency, never provenance authorization."""
    if not isinstance(turn, LocalConversationTurn):
        return False

    if type(turn.sequence) is not int or turn.sequence <= 0:
        return False

    if not isinstance(turn.owner, str) or not turn.owner.strip():
        return False

    if not isinstance(turn.session_id, str) or not turn.session_id.strip():
        return False

    if not isinstance(turn.turn_id, str) or not turn.turn_id:
        return False

    reader = getattr(journal, "list_for_session", None)
    if not callable(reader):
        return False

    try:
        records = reader(turn.owner, turn.session_id)

        if not isinstance(records, tuple):
            return False

        matching = tuple(
            candidate
            for candidate in records
            if isinstance(candidate, LocalConversationTurn)
            and candidate.owner == turn.owner
            and candidate.session_id == turn.session_id
            and type(candidate.sequence) is int
            and candidate.sequence == turn.sequence
            and candidate.turn_id == turn.turn_id
        )

        return len(matching) == 1 and matching[0] == turn

    except Exception:
        return False