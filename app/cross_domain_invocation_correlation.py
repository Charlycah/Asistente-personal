"""Non-authorizing correlation of cross-domain invocations."""

from dataclasses import dataclass
from secrets import token_urlsafe

from app.cross_domain_persisted_turn import matches_persisted_turn
from core.end_to_end_local_conversation.models import LocalConversationTurn


@dataclass(frozen=True)
class InvocationCorrelation:
    """Structural association, never a provenance authorization."""

    invocation_id: str
    owner: str
    session_id: str
    execution_id: str
    turn_id: str
    sequence: int


@dataclass
class _Invocation:
    owner: str
    session_id: str
    execution_id: str | None = None
    closed: bool = False


def _valid(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


class CrossDomainInvocationCorrelator:
    """Track invocation-local associations without granting authority."""

    def __init__(self) -> None:
        self._invocations: dict[str, _Invocation] = {}
        self._used_executions: set[str] = set()
        self._used_turns: set[tuple[str, str, str]] = set()

    def begin(self, *, owner: str, session_id: str) -> str:
        if not _valid(owner) or not _valid(session_id):
            raise ValueError("invalid invocation identity")

        invocation_id = token_urlsafe(32)
        while invocation_id in self._invocations:
            invocation_id = token_urlsafe(32)

        self._invocations[invocation_id] = _Invocation(
            owner=owner,
            session_id=session_id,
        )
        return invocation_id

    def capture(
        self,
        invocation_id: str,
        *,
        owner: str,
        session_id: str,
        execution_id: str,
        succeeded: bool,
    ) -> bool:
        invocation = self._invocations.get(invocation_id)

        if (
            invocation is None
            or invocation.closed
            or invocation.execution_id is not None
            or not _valid(execution_id)
            or invocation.owner != owner
            or invocation.session_id != session_id
            or succeeded is not True
            or execution_id in self._used_executions
        ):
            return False

        invocation.execution_id = execution_id
        self._used_executions.add(execution_id)
        return True

    def bind(
        self,
        invocation_id: str,
        *,
        turn: LocalConversationTurn,
        journal: object,
    ) -> InvocationCorrelation | None:
        invocation = self._invocations.get(invocation_id)

        if invocation is None or invocation.closed:
            return None

        # A bind attempt consumes the invocation, including failed attempts.
        invocation.closed = True

        if invocation.execution_id is None:
            return None

        if not isinstance(turn, LocalConversationTurn):
            return None

        if turn.owner != invocation.owner or turn.session_id != invocation.session_id:
            return None

        turn_key = (turn.owner, turn.session_id, turn.turn_id)
        if turn_key in self._used_turns:
            return None

        if not matches_persisted_turn(turn, journal=journal):
            return None

        self._used_turns.add(turn_key)
        return InvocationCorrelation(
            invocation_id=invocation_id,
            owner=invocation.owner,
            session_id=invocation.session_id,
            execution_id=invocation.execution_id,
            turn_id=turn.turn_id,
            sequence=turn.sequence,
        )

    def close(self, invocation_id: str) -> bool:
        invocation = self._invocations.get(invocation_id)
        if invocation is None or invocation.closed:
            return False
        invocation.closed = True
        return True
