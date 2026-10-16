from __future__ import annotations

from datetime import datetime, timedelta, timezone

from core.conversation_entry_point import (
    ConversationEntryAction,
    ConversationEntryKind,
    ConversationEntryPoint,
    ConversationEntryRequest,
)
from core.natural_greeting_response import (
    NaturalGreetingRequest,
    NaturalGreetingResponder,
)
from core.roby_voice_style_policy import (
    ROBYVoiceStylePolicy,
    ROBYVoiceStyleRequest,
)
from core.runtime_readiness_gate import RuntimeReadinessStatus

from .models import (
    ConsoleApplicationStatus,
    ConsoleIO,
    ConsoleTurnAction,
    ConsoleTurnStatus,
    InMemoryROBYConsoleRepository,
    ROBYConsoleConfig,
    ROBYConsoleRepository,
    ROBYConsoleSession,
    ROBYConsoleSessionRequest,
    ROBYConsoleTurn,
)


class ROBYConsoleApplication:
    """Runs a governed console session over the operational conversation edge."""

    def __init__(
        self,
        *,
        io: ConsoleIO,
        config: ROBYConsoleConfig | None = None,
        entry_point: ConversationEntryPoint | None = None,
        greeting_responder: NaturalGreetingResponder | None = None,
        voice_policy: ROBYVoiceStylePolicy | None = None,
        repository: ROBYConsoleRepository | None = None,
    ) -> None:
        self.io = io
        self.config = config or ROBYConsoleConfig()
        self.entry_point = entry_point or ConversationEntryPoint()
        self.greeting_responder = greeting_responder or NaturalGreetingResponder()
        self.voice_policy = voice_policy or ROBYVoiceStylePolicy()
        self.repository = repository or InMemoryROBYConsoleRepository()

    def run(
        self,
        request: ROBYConsoleSessionRequest,
        *,
        now: datetime | None = None,
    ) -> ROBYConsoleSession:
        started = now or datetime.now(timezone.utc)
        self._validate_time(started)
        if request.readiness_result.status not in {
            RuntimeReadinessStatus.READY,
            RuntimeReadinessStatus.DEGRADED,
        }:
            self.io.write(self.config.assistant_prefix + self.config.blocked_response)
            return self._save(
                ROBYConsoleSession(
                    request=request,
                    status=ConsoleApplicationStatus.BLOCKED,
                    turns=(),
                    started_at=started,
                    ended_at=started,
                    rationale=("runtime_readiness_blocked_console",),
                )
            )

        turns: list[ROBYConsoleTurn] = []
        recent_responses: list[str] = []
        for sequence in range(1, self.config.max_turns + 1):
            raw = self.io.read(self.config.prompt)
            if raw is None:
                break
            timestamp = (
                started + timedelta(microseconds=sequence - 1)
                if now is not None
                else datetime.now(timezone.utc)
            )
            turn = self.process_turn(
                request,
                raw,
                sequence=sequence,
                recent_responses=tuple(recent_responses),
                now=timestamp,
            )
            turns.append(turn)
            if turn.response_text:
                recent_responses.append(turn.response_text)
                self.io.write(self.config.assistant_prefix + turn.response_text)
            if turn.action is ConsoleTurnAction.STOP_SESSION:
                break

        ended = (
            started + timedelta(microseconds=len(turns))
            if now is not None
            else datetime.now(timezone.utc)
        )
        status = ConsoleApplicationStatus.STOPPED
        rationale = ("console_session_completed",)
        return self._save(
            ROBYConsoleSession(
                request=request,
                status=status,
                turns=tuple(turns),
                started_at=started,
                ended_at=ended,
                rationale=rationale,
            )
        )

    def process_turn(
        self,
        request: ROBYConsoleSessionRequest,
        text: str,
        *,
        sequence: int,
        recent_responses: tuple[str, ...] = (),
        now: datetime | None = None,
    ) -> ROBYConsoleTurn:
        timestamp = now or datetime.now(timezone.utc)
        self._validate_time(timestamp)
        normalized = text.strip()
        if normalized.casefold() in self.config.exit_commands:
            return self._turn(
                request,
                sequence,
                normalized,
                ConsoleTurnStatus.ROUTED,
                ConsoleTurnAction.STOP_SESSION,
                "",
                timestamp,
                rationale=("console_exit_requested",),
            )

        entry = self.entry_point.classify(
            ConversationEntryRequest(
                owner=request.owner,
                text=normalized,
                readiness_result=request.readiness_result,
                session_id=request.session_id,
            ),
            now=timestamp,
        )
        if entry.kind is ConversationEntryKind.GREETING:
            greeting = self.greeting_responder.respond(
                NaturalGreetingRequest(
                    owner=request.owner,
                    entry_result=entry,
                    session_id=request.session_id,
                    recent_responses=recent_responses,
                ),
                now=timestamp,
            )
            voice = self.voice_policy.apply(
                ROBYVoiceStyleRequest(
                    owner=request.owner,
                    greeting_result=greeting,
                ),
                now=timestamp,
            )
            return self._turn(
                request,
                sequence,
                normalized,
                ConsoleTurnStatus.DELIVERED,
                ConsoleTurnAction.WRITE_RESPONSE,
                voice.response_text,
                timestamp,
                entry=entry,
                greeting=greeting,
                voice=voice,
                rationale=("natural_greeting_delivered",),
            )
        if entry.action is ConversationEntryAction.REQUEST_COMPLETION:
            return self._turn(
                request,
                sequence,
                normalized,
                ConsoleTurnStatus.INCOMPLETE,
                ConsoleTurnAction.REQUEST_COMPLETION,
                self.config.incomplete_response,
                timestamp,
                entry=entry,
                rationale=("console_message_incomplete",),
            )
        return self._turn(
            request,
            sequence,
            normalized,
            ConsoleTurnStatus.ROUTED,
            ConsoleTurnAction.AWAIT_PIPELINE,
            self.config.pending_response,
            timestamp,
            entry=entry,
            rationale=("conversation_pipeline_not_connected",),
        )

    @staticmethod
    def _validate_time(timestamp: datetime) -> None:
        if timestamp.tzinfo is None:
            raise ValueError("console timestamp must be timezone-aware")

    @staticmethod
    def _turn(
        request: ROBYConsoleSessionRequest,
        sequence: int,
        text: str,
        status: ConsoleTurnStatus,
        action: ConsoleTurnAction,
        response: str,
        timestamp: datetime,
        *,
        entry=None,
        greeting=None,
        voice=None,
        rationale: tuple[str, ...],
    ) -> ROBYConsoleTurn:
        return ROBYConsoleTurn(
            owner=request.owner,
            session_id=request.session_id,
            sequence=sequence,
            input_text=text,
            status=status,
            action=action,
            response_text=response,
            entry_result=entry,
            greeting_result=greeting,
            voice_result=voice,
            provider_call_performed=False,
            network_access_performed=False,
            platform_mutation_performed=False,
            rationale=rationale,
            created_at=timestamp,
        )

    def _save(self, session: ROBYConsoleSession) -> ROBYConsoleSession:
        self.repository.add(session)
        return session
