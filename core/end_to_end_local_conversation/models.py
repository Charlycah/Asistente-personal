from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from pathlib import Path

from core.governed_operational_conversation_pipeline import (
    ConversationDegradationReason,
    ConversationResponsePath,
    GovernedConversationPipelineResult,
    GovernedConversationPipelineStatus,
)


class LocalConversationTurnStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    WITHHELD = "withheld"
    FAILED = "failed"


@dataclass(frozen=True)
class EndToEndLocalConversationConfig:
    journal_path: Path | str = Path(".roby/conversation_turns.jsonl")
    persist_turns: bool = True
    trace_path: Path | str | None = None
    persist_traces: bool = True
    maximum_recent_context_turns: int = 8
    maximum_recent_context_characters: int = 12_000

    def __post_init__(self) -> None:
        if self.maximum_recent_context_turns < 0:
            raise ValueError("maximum recent context turns must not be negative")
        if self.maximum_recent_context_characters < 0:
            raise ValueError("maximum recent context characters must not be negative")
        object.__setattr__(self, "journal_path", Path(self.journal_path))
        trace_path = (
            Path(self.trace_path)
            if self.trace_path is not None
            else Path(self.journal_path).with_name("operational_traces.jsonl")
        )
        object.__setattr__(self, "trace_path", trace_path)


@dataclass(frozen=True)
class LocalConversationTurn:
    owner: str
    session_id: str
    sequence: int
    user_text: str
    response_text: str
    status: LocalConversationTurnStatus | str
    pipeline_result_id: str
    operational_response_id: str
    provider_call_performed: bool
    retrieval_performed: bool
    network_access_performed: bool
    rationale: tuple[str, ...]
    response_path: ConversationResponsePath | str = ConversationResponsePath.DEGRADED
    degradation_reason: ConversationDegradationReason | str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    turn_id: str = ""

    def __post_init__(self) -> None:
        status = LocalConversationTurnStatus(self.status)
        response_path = ConversationResponsePath(self.response_path)
        degradation_reason = ConversationDegradationReason(
            self.degradation_reason
            or (
                ConversationDegradationReason.UNKNOWN
                if response_path is ConversationResponsePath.DEGRADED
                else ConversationDegradationReason.NOT_APPLICABLE
            )
        )
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        user_text = self.user_text.strip()
        response_text = self.response_text.strip()
        rationale = tuple(item.strip() for item in self.rationale)
        if not owner or not session_id or not user_text:
            raise ValueError("local conversation turn identity must be complete")
        if self.sequence < 1:
            raise ValueError("local conversation turn sequence must be positive")
        if self.created_at.tzinfo is None:
            raise ValueError("local conversation turn time must be timezone-aware")
        if not self.pipeline_result_id or not self.operational_response_id:
            raise ValueError("local conversation turn lineage must be complete")
        if not rationale or any(not item for item in rationale):
            raise ValueError("local conversation turn rationale must not be empty")
        deliverable = status in {
            LocalConversationTurnStatus.COMPLETED,
            LocalConversationTurnStatus.PARTIAL,
        }
        if deliverable != bool(response_text):
            raise ValueError("local conversation turn response is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "user_text", user_text)
        object.__setattr__(self, "response_text", response_text)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "response_path", response_path)
        object.__setattr__(self, "degradation_reason", degradation_reason)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.turn_id and self.turn_id != expected:
            raise ValueError("local conversation turn id is inconsistent")
        object.__setattr__(self, "turn_id", expected)

    @classmethod
    def from_pipeline_result(
        cls,
        *,
        sequence: int,
        result: GovernedConversationPipelineResult,
    ) -> LocalConversationTurn:
        status_by_pipeline_status = {
            GovernedConversationPipelineStatus.COMPLETED: (
                LocalConversationTurnStatus.COMPLETED
            ),
            GovernedConversationPipelineStatus.PARTIAL: (
                LocalConversationTurnStatus.PARTIAL
            ),
            GovernedConversationPipelineStatus.WITHHELD: (
                LocalConversationTurnStatus.WITHHELD
            ),
            GovernedConversationPipelineStatus.FAILED: (
                LocalConversationTurnStatus.FAILED
            ),
        }
        status = status_by_pipeline_status[result.status]
        return cls(
            owner=result.request.owner,
            session_id=result.request.session_id,
            sequence=sequence,
            user_text=result.request.text,
            response_text=result.operational_response.response_text,
            status=status,
            pipeline_result_id=result.result_id,
            operational_response_id=result.operational_response.response_id,
            provider_call_performed=result.provider_call_performed,
            retrieval_performed=result.retrieval_performed,
            network_access_performed=result.network_access_performed,
            rationale=result.rationale,
            response_path=result.response_path,
            degradation_reason=getattr(result, "degradation_reason", None),
            created_at=result.created_at,
        )

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.owner.casefold(),
                self.session_id,
                str(self.sequence),
                self.user_text,
                self.response_text,
                self.status.value,
                self.pipeline_result_id,
                self.operational_response_id,
                self.created_at.isoformat(),
                *self.rationale,
            )
        )
