from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol
from uuid import uuid4

from core.attention import AttentionManager
from core.identity import ROBYIdentity
from core.learning import ExperientialLearningManager
from core.mental_state import ROBYMentalState
from core.planning import Plan, PlanningManager
from core.reasoning import ReasoningManager, ReasoningResult
from core.working_memory import WorkingMemoryKind, WorkingMemoryManager


class KnowledgeSourceKind(str, Enum):
    """Tipo de fuente externa que ROBY puede consultar."""

    LLM = "llm"
    WEB = "web"
    NEWS = "news"
    ENCYCLOPEDIA = "encyclopedia"
    DOCUMENTATION = "documentation"
    LOCAL_MODEL = "local_model"
    INTERNAL = "internal"


class KnowledgeNeed(str, Enum):
    """Motivo por el que ROBY abre el gateway de conocimiento."""

    ANSWER_UNKNOWN = "answer_unknown"
    VERIFY_FACT = "verify_fact"
    CURRENT_INFORMATION = "current_information"
    EXPLAIN_TOPIC = "explain_topic"
    SUMMARIZE_SOURCE = "summarize_source"
    NO_EXTERNAL_KNOWLEDGE = "no_external_knowledge"


@dataclass(frozen=True)
class KnowledgeRequest:
    """Solicitud explícita de conocimiento externo.

    M48 mantiene a ROBY como identidad central. El gateway no reemplaza su
    criterio; solo coordina fuentes externas cuando ROBY necesita ampliar,
    verificar o actualizar información.
    """

    query: str
    need: KnowledgeNeed | str = KnowledgeNeed.ANSWER_UNKNOWN
    preferred_sources: tuple[KnowledgeSourceKind | str, ...] = ()
    person: str | None = None
    source: str = "conversation"
    confidence_required: float = 0.6
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: str = field(default_factory=lambda: uuid4().hex)
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("knowledge request query must not be empty")
        if self.person is not None and not self.person.strip():
            raise ValueError("knowledge request person must not be empty")
        if not self.source.strip():
            raise ValueError("knowledge request source must not be empty")
        if not 0 <= self.confidence_required <= 1:
            raise ValueError("confidence required must be between 0 and 1")
        if self.created_at.tzinfo is None:
            raise ValueError("knowledge request timestamp must be timezone-aware")
        if not self.request_id.strip():
            raise ValueError("knowledge request id must not be empty")
        KnowledgeNeed(self.need)
        for source_kind in self.preferred_sources:
            KnowledgeSourceKind(source_kind)

    @property
    def normalized_need(self) -> KnowledgeNeed:
        return KnowledgeNeed(self.need)

    @property
    def normalized_sources(self) -> tuple[KnowledgeSourceKind, ...]:
        return tuple(
            KnowledgeSourceKind(source_kind) for source_kind in self.preferred_sources
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.request_id,
            "query": self.query,
            "need": self.normalized_need.value,
            "preferred_sources": [source.value for source in self.normalized_sources],
            "person": self.person,
            "source": self.source,
            "confidence_required": self.confidence_required,
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class KnowledgeSourceResult:
    """Respuesta normalizada de una fuente externa."""

    content: str
    provider: str
    source_kind: KnowledgeSourceKind | str = KnowledgeSourceKind.LLM
    confidence: float = 0.7
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    citations: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("knowledge result content must not be empty")
        if not self.provider.strip():
            raise ValueError("knowledge result provider must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("knowledge result confidence must be between 0 and 1")
        if self.retrieved_at.tzinfo is None:
            raise ValueError("knowledge result timestamp must be timezone-aware")
        KnowledgeSourceKind(self.source_kind)
        for citation in self.citations:
            if not citation.strip():
                raise ValueError("knowledge result citations must not be empty")

    @property
    def normalized_source_kind(self) -> KnowledgeSourceKind:
        return KnowledgeSourceKind(self.source_kind)

    def to_dict(self) -> dict[str, object]:
        return {
            "content": self.content,
            "provider": self.provider,
            "source_kind": self.normalized_source_kind.value,
            "confidence": self.confidence,
            "retrieved_at": self.retrieved_at.isoformat(),
            "citations": list(self.citations),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class KnowledgeAnswer:
    """Resultado consolidado por el gateway de conocimiento."""

    request: KnowledgeRequest
    used_external_knowledge: bool
    summary: str
    selected_result: KnowledgeSourceResult | None = None
    alternatives: tuple[KnowledgeSourceResult, ...] = ()
    decision_reason: str = ""
    answer_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.summary.strip():
            raise ValueError("knowledge answer summary must not be empty")
        if not self.answer_id.strip():
            raise ValueError("knowledge answer id must not be empty")
        if self.used_external_knowledge and self.selected_result is None:
            raise ValueError("external knowledge answers need a selected result")

    @property
    def confidence(self) -> float:
        if self.selected_result is None:
            return 0.0
        return self.selected_result.confidence

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.answer_id,
            "request": self.request.to_dict(),
            "used_external_knowledge": self.used_external_knowledge,
            "summary": self.summary,
            "selected_result": (
                self.selected_result.to_dict()
                if self.selected_result is not None
                else None
            ),
            "alternatives": [result.to_dict() for result in self.alternatives],
            "decision_reason": self.decision_reason,
            "confidence": self.confidence,
        }


class KnowledgeProvider(Protocol):
    """Contrato mínimo para proveedores externos enchufables."""

    name: str
    source_kind: KnowledgeSourceKind

    def retrieve(self, request: KnowledgeRequest) -> KnowledgeSourceResult:
        """Obtiene conocimiento externo para una solicitud."""


@dataclass(frozen=True)
class KnowledgeContext:
    """Contexto cognitivo usado para decidir si consultar conocimiento."""

    query: str
    identity: ROBYIdentity | None = None
    mental_state: ROBYMentalState | None = None
    attention: AttentionManager | None = None
    working_memory: WorkingMemoryManager | None = None
    reasoning: ReasoningManager | None = None
    reasoning_result: ReasoningResult | None = None
    planning: PlanningManager | None = None
    plan: Plan | None = None
    learning: ExperientialLearningManager | None = None
    preferred_sources: tuple[KnowledgeSourceKind | str, ...] = ()
    person: str | None = None
    source: str = "conversation"
    allow_external: bool = True

    @property
    def latest_reasoning(self) -> ReasoningResult | None:
        if self.reasoning_result is not None:
            return self.reasoning_result
        if self.reasoning is None:
            return None
        return self.reasoning.last_result

    @property
    def latest_plan(self) -> Plan | None:
        if self.plan is not None:
            return self.plan
        if self.planning is None:
            return None
        return self.planning.last_plan


class KnowledgeGatewayEngine:
    """Motor M48 para abrir conocimiento externo sin perder identidad."""

    CURRENT_MARKERS = (
        "noticia",
        "noticias",
        "actual",
        "hoy",
        "último",
        "ultima",
        "última",
        "reciente",
        "internet",
        "precio",
        "clima",
        "cotización",
    )
    EXPLANATION_MARKERS = (
        "qué es",
        "que es",
        "quién es",
        "quien es",
        "conocés",
        "conoces",
        "libro",
        "superficie",
        "decime algo",
        "explicame",
    )

    def evaluate_need(self, context: KnowledgeContext) -> KnowledgeNeed:
        query = context.query.strip().lower()
        if not context.allow_external:
            return KnowledgeNeed.NO_EXTERNAL_KNOWLEDGE
        if any(marker in query for marker in self.CURRENT_MARKERS):
            return KnowledgeNeed.CURRENT_INFORMATION
        if any(marker in query for marker in self.EXPLANATION_MARKERS):
            return KnowledgeNeed.EXPLAIN_TOPIC
        if context.latest_reasoning is not None:
            conclusion = context.latest_reasoning.conclusion.lower()
            if "no" in conclusion and "suficiente" in conclusion:
                return KnowledgeNeed.ANSWER_UNKNOWN
        return KnowledgeNeed.NO_EXTERNAL_KNOWLEDGE

    def build_request(self, context: KnowledgeContext) -> KnowledgeRequest:
        need = self.evaluate_need(context)
        preferred_sources = context.preferred_sources
        if not preferred_sources:
            preferred_sources = self._default_sources_for(need)
        return KnowledgeRequest(
            query=context.query,
            need=need,
            preferred_sources=preferred_sources,
            person=context.person,
            source=context.source,
            confidence_required=(
                0.7 if need is KnowledgeNeed.CURRENT_INFORMATION else 0.6
            ),
        )

    def answer(
        self,
        context: KnowledgeContext,
        providers: tuple[KnowledgeProvider, ...],
    ) -> KnowledgeAnswer:
        request = self.build_request(context)
        if request.normalized_need is KnowledgeNeed.NO_EXTERNAL_KNOWLEDGE:
            return KnowledgeAnswer(
                request=request,
                used_external_knowledge=False,
                summary="ROBY no requiere conocimiento externo para este turno.",
                decision_reason="La consulta puede resolverse con contexto interno.",
            )
        results = self._retrieve_from_providers(request, providers)
        if not results:
            return KnowledgeAnswer(
                request=request,
                used_external_knowledge=False,
                summary=(
                    "ROBY necesita conocimiento externo, "
                    "pero no hay proveedor disponible."
                ),
                decision_reason=(
                    "No se encontró un proveedor compatible para la solicitud."
                ),
            )
        selected = max(results, key=lambda item: item.confidence)
        self._store_answer_in_workspace(context, selected)
        return KnowledgeAnswer(
            request=request,
            used_external_knowledge=True,
            summary=selected.content,
            selected_result=selected,
            alternatives=tuple(result for result in results if result is not selected),
            decision_reason=("Se seleccionó la fuente con mayor confianza disponible."),
        )

    def _default_sources_for(
        self,
        need: KnowledgeNeed,
    ) -> tuple[KnowledgeSourceKind, ...]:
        if need is KnowledgeNeed.CURRENT_INFORMATION:
            return (KnowledgeSourceKind.WEB, KnowledgeSourceKind.NEWS)
        if need is KnowledgeNeed.EXPLAIN_TOPIC:
            return (KnowledgeSourceKind.ENCYCLOPEDIA, KnowledgeSourceKind.LLM)
        if need is KnowledgeNeed.VERIFY_FACT:
            return (KnowledgeSourceKind.WEB, KnowledgeSourceKind.ENCYCLOPEDIA)
        if need is KnowledgeNeed.SUMMARIZE_SOURCE:
            return (KnowledgeSourceKind.DOCUMENTATION, KnowledgeSourceKind.LLM)
        return (KnowledgeSourceKind.LLM, KnowledgeSourceKind.WEB)

    def _retrieve_from_providers(
        self,
        request: KnowledgeRequest,
        providers: tuple[KnowledgeProvider, ...],
    ) -> tuple[KnowledgeSourceResult, ...]:
        preferred = set(request.normalized_sources)
        results: list[KnowledgeSourceResult] = []
        for provider in providers:
            if preferred and provider.source_kind not in preferred:
                continue
            result = provider.retrieve(request)
            if result.confidence >= request.confidence_required:
                results.append(result)
        return tuple(results)

    def _store_answer_in_workspace(
        self,
        context: KnowledgeContext,
        result: KnowledgeSourceResult,
    ) -> None:
        if context.working_memory is None:
            return
        context.working_memory.memory.remember(
            f"Conocimiento externo activo: {result.content}",
            kind=WorkingMemoryKind.FACT,
            source="knowledge_gateway",
            priority=8,
            confidence=result.confidence,
            metadata={"provider": result.provider},
        )


class KnowledgeGatewayManager:
    """Fachada M48 para proveedores y estado del gateway."""

    def __init__(
        self,
        providers: tuple[KnowledgeProvider, ...] = (),
        engine: KnowledgeGatewayEngine | None = None,
        *,
        capacity: int = 20,
    ) -> None:
        if capacity <= 0:
            raise ValueError("knowledge gateway capacity must be greater than zero")
        self.providers = providers
        self.engine = engine or KnowledgeGatewayEngine()
        self.capacity = capacity
        self.history: tuple[KnowledgeAnswer, ...] = ()
        self.last_answer: KnowledgeAnswer | None = None

    def resolve(self, context: KnowledgeContext) -> KnowledgeAnswer:
        answer = self.engine.answer(context, self.providers)
        self.last_answer = answer
        self.history = (answer, *self.history)[: self.capacity]
        return answer

    def ask(
        self,
        query: str,
        *,
        preferred_sources: tuple[KnowledgeSourceKind | str, ...] = (),
        **context_kwargs: object,
    ) -> KnowledgeAnswer:
        return self.resolve(
            KnowledgeContext(
                query=query,
                preferred_sources=preferred_sources,
                **context_kwargs,
            )
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = ["Knowledge Gateway de ROBY:"]
        if self.last_answer is None:
            lines.append("- Sin consultas externas activas")
            return tuple(lines)
        request = self.last_answer.request
        lines.append(f"- Necesidad: {request.normalized_need.value}")
        if self.last_answer.used_external_knowledge:
            selected = self.last_answer.selected_result
            if selected is not None:
                lines.append(
                    f"- Fuente activa: {selected.provider} "
                    f"({selected.normalized_source_kind.value})"
                )
                lines.append(f"- Confianza: {selected.confidence:.2f}")
        else:
            lines.append(f"- Estado: {self.last_answer.summary}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "capacity": self.capacity,
            "providers": [provider.name for provider in self.providers],
            "last_answer": (
                self.last_answer.to_dict() if self.last_answer is not None else None
            ),
            "history": [answer.to_dict() for answer in self.history],
        }
