from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, replace

from .interlocutor import (
    CanonicalInterlocutorResolver,
    InterlocutorResolution,
    InterlocutorResolutionAction,
    InterlocutorResolutionRequest,
    InterlocutorResolutionStatus,
)
from .permissions import CoownerIdentity


@dataclass(frozen=True)
class InterlocutorSessionSnapshot:
    states: tuple[InterlocutorResolution, ...]
    retained_sessions: int
    resolved_sessions: int
    capacity: int
    persisted: bool = False
    grants_action_authority: bool = False

    def __post_init__(self) -> None:
        if self.capacity < 1:
            raise ValueError("interlocutor session capacity must be positive")
        if self.retained_sessions != len(self.states):
            raise ValueError("interlocutor retained session count is inconsistent")
        expected_resolved = sum(
            item.status is InterlocutorResolutionStatus.RESOLVED
            for item in self.states
        )
        if self.resolved_sessions != expected_resolved:
            raise ValueError("interlocutor resolved session count is inconsistent")
        session_ids = tuple(item.session_id for item in self.states)
        if len(session_ids) != len(set(session_ids)):
            raise ValueError("interlocutor snapshot sessions must be unique")
        if self.persisted or self.grants_action_authority:
            raise ValueError("interlocutor session snapshot must remain temporary")


class ActiveInterlocutorSessionState:
    """Hold bounded, non-persistent interlocutor resolution per session."""

    def __init__(
        self,
        *,
        resolver: CanonicalInterlocutorResolver | None = None,
        max_sessions: int = 32,
    ) -> None:
        if max_sessions < 1:
            raise ValueError("active interlocutor session capacity must be positive")
        self._resolver = resolver or CanonicalInterlocutorResolver()
        self._max_sessions = max_sessions
        self._states: OrderedDict[str, InterlocutorResolution] = OrderedDict()
        self._confirmed: dict[str, CoownerIdentity] = {}

    def apply(
        self,
        request: InterlocutorResolutionRequest,
    ) -> InterlocutorResolution:
        session_id = request.session_id
        authoritative_current = self._confirmed.get(session_id)
        governed_request = replace(
            request,
            current_interlocutor=authoritative_current,
        )
        result = self._resolver.resolve(governed_request)
        if result.status is InterlocutorResolutionStatus.RESOLVED:
            if result.interlocutor is None:
                raise ValueError("resolved session requires an interlocutor")
            self._confirmed[session_id] = result.interlocutor
        elif result.status is InterlocutorResolutionStatus.REVOKED:
            self._confirmed.pop(session_id, None)
        self._retain(result)
        return result

    def current(self, session_id: str) -> InterlocutorResolution:
        normalized = session_id.strip()
        state = self._states.get(normalized)
        if state is None:
            return self._resolver.unresolved(normalized)
        self._states.move_to_end(normalized)
        return state

    def revoke(
        self,
        request: InterlocutorResolutionRequest,
    ) -> InterlocutorResolution:
        if request.action is not InterlocutorResolutionAction.REVOKE:
            raise ValueError("interlocutor session revoke requires revoke action")
        return self.apply(request)

    @property
    def snapshot(self) -> InterlocutorSessionSnapshot:
        states = tuple(self._states.values())
        return InterlocutorSessionSnapshot(
            states=states,
            retained_sessions=len(states),
            resolved_sessions=sum(
                item.status is InterlocutorResolutionStatus.RESOLVED
                for item in states
            ),
            capacity=self._max_sessions,
        )

    def _retain(self, result: InterlocutorResolution) -> None:
        session_id = result.session_id
        self._states[session_id] = result
        self._states.move_to_end(session_id)
        while len(self._states) > self._max_sessions:
            evicted_session, _ = self._states.popitem(last=False)
            self._confirmed.pop(evicted_session, None)
