from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.cognitive_runtime_orchestration import (
    CognitiveExternalEvidenceAdmission,
    CognitiveStrategyApplicationEvidence,
)
from core.governed_provider_execution_adapter import LocalProviderExecutionResult
from core.governed_provider_routing import GovernedProviderRoute
from core.governed_reasoning.explicit_hypothesis_source import (
    GovernedExplicitHypothesisSource,
)
from core.knowledge_retrieval_execution import KnowledgeRetrievalExecution
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalPlan
from core.llm_provider import LLMRequest
from core.operational_response_assembly import OperationalResponse
from core.persistent_world_model import PersistentWorldSnapshot
from core.visual_context_integration import IntegratedVisualContext

from .response_origin import ResponseOriginMetadata


@dataclass(frozen=True)
class GovernedConversationTurnIdentity:
    conversation_id: str
    request_id: str
    turn_id: str
    trace_id: str


def build_governed_conversation_turn_identity(
    request: "GovernedConversationPipelineRequest",
    now: datetime,
) -> GovernedConversationTurnIdentity:
    if now.tzinfo is None:
        raise ValueError("conversation turn identity time must be timezone-aware")
    base = f"{request.owner.casefold()}|{request.session_id}"
    conversation_id = sha256(base.encode()).hexdigest()
    request_id = sha256(f"{base}|{request.text}|{now.isoformat()}".encode()).hexdigest()
    turn_id = sha256(f"{conversation_id}|{request_id}".encode()).hexdigest()
    trace_id = sha256(f"{turn_id}|conversation".encode()).hexdigest()
    return GovernedConversationTurnIdentity(
        conversation_id=conversation_id,
        request_id=request_id,
        turn_id=turn_id,
        trace_id=trace_id,
    )


class GovernedConversationPipelineStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    WITHHELD = "withheld"
    FAILED = "failed"


class ConversationResponsePath(str, Enum):
    PROVIDER = "provider"
    INTERCEPTOR = "interceptor"
    DEGRADED = "degraded"


class ConversationDegradationReason(str, Enum):
    NOT_APPLICABLE = "not_applicable"
    PIPELINE_DISABLED = "pipeline_disabled"
    INPUT_LIMIT_EXCEEDED = "input_limit_exceeded"
    TURN_FAILED_SAFELY = "turn_failed_safely"
    PROVIDER_RESPONSE_UNAVAILABLE = "provider_response_unavailable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GovernedConversationPipelineConfig:
    execution_enabled: bool = True
    maximum_input_characters: int = 32_000
    execute_retrieval: bool = True

    def __post_init__(self) -> None:
        if self.maximum_input_characters < 1:
            raise ValueError("maximum input characters must be positive")


@dataclass(frozen=True)
class ConversationalContextTurn:
    user_text: str
    assistant_text: str

    def __post_init__(self) -> None:
        user_text = self.user_text.strip()
        assistant_text = self.assistant_text.strip()
        if not user_text or not assistant_text:
            raise ValueError("conversational context turn must be complete")
        object.__setattr__(self, "user_text", user_text)
        object.__setattr__(self, "assistant_text", assistant_text)


@dataclass(frozen=True)
class ExplicitLongitudinalTopicDeclaration:
    topic_key: str

    def __post_init__(self) -> None:
        if not self.topic_key.strip():
            raise ValueError(
                "explicit longitudinal topic declaration must not be blank"
            )
        if self.topic_key != " ".join(self.topic_key.split()):
            raise ValueError(
                "explicit longitudinal topic declaration must already be canonical"
            )


@dataclass(frozen=True)
class GovernedConversationPipelineRequest:
    owner: str
    session_id: str
    text: str
    recent_context: tuple[ConversationalContextTurn, ...] = ()
    external_evidence: tuple[CognitiveExternalEvidenceAdmission, ...] = ()
    explicit_document_ids: tuple[str, ...] = ()
    explicit_sources: tuple[object, ...] = ()
    explicit_evidence_references: tuple[object, ...] = ()
    integrated_visual_context: IntegratedVisualContext | None = None
    explicit_hypothesis_source: GovernedExplicitHypothesisSource | None = None
    hypothesis_world_snapshot: PersistentWorldSnapshot | None = None
    explicit_longitudinal_topic_declaration: (
        ExplicitLongitudinalTopicDeclaration | None
    ) = None

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        text = self.text.strip()
        if not owner:
            raise ValueError("conversation pipeline owner must not be blank")
        if not session_id:
            raise ValueError("conversation pipeline session id must not be blank")
        if not text:
            raise ValueError("conversation pipeline text must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        context = tuple(self.recent_context)
        external_evidence = tuple(self.external_evidence)
        if any(
            not isinstance(item, CognitiveExternalEvidenceAdmission)
            for item in external_evidence
        ):
            raise TypeError(
                "conversation external evidence must use the canonical M401 admission"
            )
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "recent_context", context)
        object.__setattr__(self, "external_evidence", external_evidence)
        object.__setattr__(
            self, "explicit_document_ids", tuple(self.explicit_document_ids)
        )
        object.__setattr__(self, "explicit_sources", tuple(self.explicit_sources))
        object.__setattr__(
            self,
            "explicit_evidence_references",
            tuple(self.explicit_evidence_references),
        )
        if (self.explicit_hypothesis_source is None) != (
            self.hypothesis_world_snapshot is None
        ):
            raise ValueError(
                "explicit hypothesis source and world snapshot "
                "must be admitted together"
            )


@dataclass(frozen=True)
class GovernedConversationPreparation:
    owner: str
    session_id: str
    text: str
    provider_route: GovernedProviderRoute
    inference_request: LLMRequest
    retrieval_plan: KnowledgeRetrievalPlan | None = None
    strategy_application_evidence: CognitiveStrategyApplicationEvidence | None = None

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        text = self.text.strip()
        if not owner or not session_id or not text:
            raise ValueError("conversation preparation identity must be complete")
        if owner.casefold() != self.provider_route.request.owner.casefold():
            raise ValueError("conversation preparation owner must match route owner")
        if self.retrieval_plan and (
            owner.casefold() != self.retrieval_plan.request.owner.casefold()
        ):
            raise ValueError("conversation preparation owner must match plan owner")
        if not self.inference_request.prompt.strip():
            raise ValueError("conversation preparation prompt must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "text", text)


@dataclass(frozen=True)
class GovernedOperationalInterception:
    response_text: str
    rationale: str = "governed_operational_interception_completed"
    origin: ResponseOriginMetadata = field(default_factory=ResponseOriginMetadata.local)
    network_access_performed: bool = False

    def __post_init__(self) -> None:
        text = self.response_text.strip()
        rationale = self.rationale.strip()
        if not text or not rationale:
            raise ValueError("operational interception must be complete")
        object.__setattr__(self, "response_text", text)
        object.__setattr__(self, "rationale", rationale)


@runtime_checkable
class GovernedOperationalInterceptionPort(Protocol):
    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None: ...


@runtime_checkable
class OfficialConversationExecutionPort(Protocol):
    def evaluate_turn(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ): ...


@runtime_checkable
class GovernedConversationPreparationPort(Protocol):
    def prepare(
        self, request: GovernedConversationPipelineRequest
    ) -> GovernedConversationPreparation: ...


@dataclass(frozen=True)
class GovernedConversationPipelineResult:
    request: GovernedConversationPipelineRequest
    status: GovernedConversationPipelineStatus | str
    preparation: GovernedConversationPreparation | None
    provider_execution: LocalProviderExecutionResult | None
    retrieval_execution: KnowledgeRetrievalExecution | None
    operational_response: OperationalResponse
    provider_call_performed: bool
    retrieval_performed: bool
    network_access_performed: bool
    platform_mutation_performed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result_id: str = ""
    response_origin: ResponseOriginMetadata = field(
        default_factory=ResponseOriginMetadata.general_knowledge
    )
    response_path: ConversationResponsePath | str = ConversationResponsePath.DEGRADED
    degradation_reason: ConversationDegradationReason | str | None = None

    def __post_init__(self) -> None:
        status = GovernedConversationPipelineStatus(self.status)
        response_path = ConversationResponsePath(self.response_path)
        degradation_reason = ConversationDegradationReason(
            self.degradation_reason
            or (
                ConversationDegradationReason.UNKNOWN
                if response_path is ConversationResponsePath.DEGRADED
                else ConversationDegradationReason.NOT_APPLICABLE
            )
        )
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("conversation pipeline timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("conversation pipeline rationale must not be empty")
        if self.platform_mutation_performed:
            raise ValueError("M177 cannot mutate the platform")
        response = self.operational_response
        if self.provider_call_performed != response.provider_call_performed:
            raise ValueError("provider call lineage is inconsistent")
        if self.retrieval_performed != response.retrieval_performed:
            raise ValueError("retrieval lineage is inconsistent")
        if self.network_access_performed != response.network_access_performed:
            raise ValueError("network lineage is inconsistent")
        if response.request.provider_execution is not self.provider_execution:
            raise ValueError("provider execution lineage must be exact")
        if response.request.retrieval_execution is not self.retrieval_execution:
            raise ValueError("retrieval execution lineage must be exact")
        if (
            response_path is ConversationResponsePath.PROVIDER
            and not self.provider_call_performed
        ):
            raise ValueError("provider response path requires a provider call")
        if (
            response_path is ConversationResponsePath.INTERCEPTOR
            and self.provider_call_performed
        ):
            raise ValueError("interceptor response path cannot perform a provider call")
        if (
            response_path is not ConversationResponsePath.DEGRADED
            and degradation_reason is not ConversationDegradationReason.NOT_APPLICABLE
        ):
            raise ValueError("non-degraded response cannot have a degradation reason")
        if (
            response_path is ConversationResponsePath.DEGRADED
            and degradation_reason is ConversationDegradationReason.NOT_APPLICABLE
        ):
            raise ValueError("degraded response requires a degradation reason")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "response_path", response_path)
        object.__setattr__(self, "degradation_reason", degradation_reason)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.result_id and self.result_id != expected:
            raise ValueError("conversation pipeline result id is inconsistent")
        object.__setattr__(self, "result_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.session_id,
                self.request.text,
                self.status.value,
                self.preparation.provider_route.route_id if self.preparation else "",
                self.provider_execution.execution_id if self.provider_execution else "",
                self.retrieval_execution.execution_id
                if self.retrieval_execution
                else "",
                self.operational_response.response_id,
                self.response_path.value,
                self.degradation_reason.value,
                self.response_origin.origin.value,
                self.response_origin.confidence.value,
                self.response_origin.freshness,
                str(self.response_origin.verifiable),
                str(self.response_origin.abstained),
                str(self.response_origin.confidence_record.evidence_count),
                str(self.response_origin.confidence_record.conflicting_sources),
                self.response_origin.confidence_record.verification.value,
                self.response_origin.confidence_record.decision.value,
                self.response_origin.confidence_record.reason_code,
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class GovernedConversationPipelineRepository(Protocol):
    def add(self, result: GovernedConversationPipelineResult) -> None: ...
    def get(self, result_id: str) -> GovernedConversationPipelineResult | None: ...
    def list_all(self) -> tuple[GovernedConversationPipelineResult, ...]: ...


class InMemoryGovernedConversationPipelineRepository:
    def __init__(self) -> None:
        self._items: dict[str, GovernedConversationPipelineResult] = {}

    def add(self, result: GovernedConversationPipelineResult) -> None:
        if result.result_id in self._items:
            raise ValueError("conversation pipeline result already exists")
        self._items[result.result_id] = result

    def get(self, result_id: str) -> GovernedConversationPipelineResult | None:
        return self._items.get(result_id)

    def list_all(self) -> tuple[GovernedConversationPipelineResult, ...]:
        return tuple(self._items.values())
