from __future__ import annotations

from datetime import datetime

from core.cognitive_maturity import (
    IdentityContextAccessGate,
    IdentityContextEvidenceAdapter,
    MemoryKnowledgeEvidenceAdapter,
    ResponseActionEvidenceAdapter,
)
from core.cognitive_runtime_orchestration import CognitiveExternalEvidenceAdmission
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)
from core.local_runtime_bootstrap import LocalRuntimeBootstrap
from core.operational_trace_model import (
    JsonLinesOperationalTraceStore,
    OperationalTraceRecorder,
    OperationalTurnTrace,
)

from .journal import JsonLinesLocalConversationJournal, LocalConversationJournal
from .models import EndToEndLocalConversationConfig, LocalConversationTurn


class EndToEndLocalConversation:
    """Runs one real local turn through the official M179/M178/M177 runtime."""

    def __init__(
        self,
        *,
        bootstrap: LocalRuntimeBootstrap,
        config: EndToEndLocalConversationConfig | None = None,
        journal: LocalConversationJournal | None = None,
        trace_recorder: OperationalTraceRecorder | None = None,
    ) -> None:
        self.bootstrap = bootstrap
        self.config = config or EndToEndLocalConversationConfig()
        self.journal = journal or JsonLinesLocalConversationJournal(
            self.config.journal_path
        )
        self.trace_recorder = trace_recorder
        if self.trace_recorder is None and self.config.persist_traces:
            self.trace_recorder = OperationalTraceRecorder(
                JsonLinesOperationalTraceStore(self.config.trace_path)
            )

    @property
    def history(self) -> tuple[LocalConversationTurn, ...]:
        return self.journal.list_for_session(
            self.bootstrap.config.owner,
            self.bootstrap.config.session_id,
        )

    @property
    def traces(self) -> tuple[OperationalTurnTrace, ...]:
        recorder = self.trace_recorder
        if recorder is None:
            return ()
        events = recorder.store.list_for_session(
            self.bootstrap.config.owner,
            self.bootstrap.config.session_id,
        )
        trace_ids = tuple(dict.fromkeys(event.trace_id for event in events))
        return tuple(
            trace
            for trace_id in trace_ids
            if (trace := recorder.store.get_trace(trace_id)) is not None
        )

    def converse(
        self,
        text: str,
        *,
        now: datetime | None = None,
        external_evidence: tuple[CognitiveExternalEvidenceAdmission, ...] = (),
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
    ) -> LocalConversationTurn:
        normalized = text.strip()
        if not normalized:
            raise ValueError("local conversation text must not be blank")
        if not self.bootstrap.is_running:
            raise RuntimeError("local runtime must be running before conversation")
        composition = self.bootstrap.composition
        if composition is None:
            composition = self.bootstrap.start(now=now)
        sequence = len(self.history) + 1
        started = None
        if self.trace_recorder is not None:
            started = self.trace_recorder.start_turn(
                owner=self.bootstrap.config.owner,
                session_id=self.bootstrap.config.session_id,
                turn_sequence=sequence,
                now=now,
            )
        recent_context = self._recent_context()
        request = GovernedConversationPipelineRequest(
            owner=self.bootstrap.config.owner,
            session_id=self.bootstrap.config.session_id,
            text=normalized,
            recent_context=recent_context,
            external_evidence=external_evidence,
            explicit_document_ids=explicit_document_ids,
            explicit_sources=explicit_sources,
            explicit_evidence_references=explicit_evidence_references,
            integrated_visual_context=integrated_visual_context,
        )
        IdentityContextEvidenceAdapter().observe_resolution(
            coownership_scoped=(request.owner.casefold() == "carlos y cristina"),
            session_scoped=bool(request.session_id),
            context_bounded=(
                len(recent_context) <= self.config.maximum_recent_context_turns
                and sum(
                    len(item.user_text) + len(item.assistant_text)
                    for item in recent_context
                )
                <= self.config.maximum_recent_context_characters
            ),
            interlocutor_resolved=(
                IdentityContextEvidenceAdapter.current_interlocutor_resolved()
            ),
        )
        result = composition.conversation_pipeline.process(
            request,
            now=now,
        )
        ResponseActionEvidenceAdapter().observe_response_status(
            result.operational_response.status
        )
        MemoryKnowledgeEvidenceAdapter().observe_knowledge_execution(
            result.retrieval_execution
        )
        turn = LocalConversationTurn.from_pipeline_result(
            sequence=sequence,
            result=result,
        )
        memory_runtime = composition.preparation.dependencies.memory_runtime
        if (
            memory_runtime is not None
            and IdentityContextAccessGate.current().private_context_allowed
        ):
            memory_runtime.record(owner=result.request.owner, text=result.request.text)
        pipeline_event = None
        if self.trace_recorder is not None and started is not None:
            pipeline_event = self.trace_recorder.finish_pipeline(
                started=started,
                turn=turn,
                platform_mutation_performed=result.platform_mutation_performed,
                now=now,
            )
        if self.config.persist_turns:
            self.journal.append(turn)
            if self.trace_recorder is not None and pipeline_event is not None:
                self.trace_recorder.record_persistence(
                    pipeline_event=pipeline_event,
                    turn=turn,
                    now=now,
                )
        return turn

    def _recent_context(self) -> tuple[ConversationalContextTurn, ...]:
        if not (
            IdentityContextAccessGate.current().shared_conversation_context_allowed
        ):
            return ()
        max_turns = self.config.maximum_recent_context_turns
        max_characters = self.config.maximum_recent_context_characters
        if max_turns == 0 or max_characters == 0:
            return ()
        selected: list[ConversationalContextTurn] = []
        used_characters = 0
        for turn in reversed(self.history):
            if not turn.response_text:
                continue
            character_count = len(turn.user_text) + len(turn.response_text)
            if selected and used_characters + character_count > max_characters:
                break
            if not selected and character_count > max_characters:
                continue
            selected.append(
                ConversationalContextTurn(
                    user_text=turn.user_text,
                    assistant_text=turn.response_text,
                )
            )
            used_characters += character_count
            if len(selected) >= max_turns:
                break
        return tuple(reversed(selected))
