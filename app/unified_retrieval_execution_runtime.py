from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.external_retrieval_execution import EXTERNAL_SOURCES
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.knowledge_retrieval_execution import (
    KnowledgeRetrievalExecution,
    KnowledgeRetrievalExecutionConfig,
    KnowledgeRetrievalExecutionGateway,
    KnowledgeRetrievalExecutionRequest,
    RetrieverRegistry,
)

from .external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway


@dataclass(frozen=True)
class UnifiedRetrievalExecutionSnapshot:
    evaluations: int
    external_sources: tuple[str, ...]
    last_owner: str | None
    last_status: str | None
    last_network_access_performed: bool


class OfficialUnifiedRetrievalExecutionRuntimeGateway:
    """Single official execution authority for governed retrieval plans."""

    def __init__(
        self,
        external_runtime: OfficialExternalRetrievalRuntimeGateway,
        *,
        retrievers: dict | None = None,
        config: KnowledgeRetrievalExecutionConfig | None = None,
    ) -> None:
        self.external_runtime = external_runtime
        merged = dict(retrievers or {})
        for source in EXTERNAL_SOURCES:
            merged[source] = external_runtime
        self._gateway = KnowledgeRetrievalExecutionGateway(
            merged,
            config=config,
        )
        self._evaluations = 0
        self._last_execution: KnowledgeRetrievalExecution | None = None

    @property
    def snapshot(self) -> UnifiedRetrievalExecutionSnapshot:
        last = self._last_execution
        return UnifiedRetrievalExecutionSnapshot(
            evaluations=self._evaluations,
            external_sources=tuple(sorted(source.value for source in EXTERNAL_SOURCES)),
            last_owner=last.request.owner if last is not None else None,
            last_status=last.status.value if last is not None else None,
            last_network_access_performed=(
                last.network_access_performed if last is not None else False
            ),
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        del now
        normalized = request.text.strip().casefold()
        status_requested = any(
            trigger in normalized
            for trigger in (
                "estado de ejecución unificada de recuperación",
                "estado de ejecucion unificada de recuperacion",
            )
        )
        if status_requested:
            snapshot = self.snapshot
            return GovernedOperationalInterception(
                response_text=(
                    "Estado del Unified Retrieval Execution Runtime:\n"
                    f"- Evaluaciones: {snapshot.evaluations}\n"
                    f"- Último estado: {snapshot.last_status or 'ninguno'}\n"
                    "- Autoridad externa: M260.\n"
                    "- Proveedores y mutaciones: no autorizados."
                ),
                rationale="unified_retrieval_execution_status_completed",
            )
        audit_requested = any(
            trigger in normalized
            for trigger in (
                "audita ejecución unificada de recuperación",
                "audita ejecucion unificada de recuperacion",
            )
        )
        if audit_requested:
            return GovernedOperationalInterception(
                response_text=(
                    "Auditoría del Unified Retrieval Execution Runtime:\n"
                    "- Planificación histórica: preservada.\n"
                    "- Fuentes externas: delegadas exclusivamente a M260.\n"
                    "- Validación y referencias: gobernadas.\n"
                    "- Ejecución implícita: no permitida."
                ),
                rationale="unified_retrieval_execution_audit_completed",
            )
        return None

    @property
    def last_execution(self) -> KnowledgeRetrievalExecution | None:
        return self._last_execution

    def execute(
        self,
        request: KnowledgeRetrievalExecutionRequest,
        *,
        now: datetime | None = None,
        execution_retrievers: RetrieverRegistry | None = None,
    ) -> KnowledgeRetrievalExecution:
        result = self._gateway.execute(
            request,
            now=now,
            execution_retrievers=execution_retrievers,
        )
        self._evaluations += 1
        self._last_execution = result
        return result
