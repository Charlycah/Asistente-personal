from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.external_retrieval_execution import (
    ExternalRetrievalClient,
    ExternalRetrievalExecutionAdapter,
    ExternalRetrievalExecutionConfig,
    ExternalRetrievalExecutionRequest,
    ExternalRetrievalExecutionResult,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.knowledge_source_policy import KnowledgeSourceKind


@dataclass(frozen=True)
class ExternalRetrievalRuntimeSnapshot:
    evaluations: int
    registered_sources: tuple[str, ...]
    last_owner: str | None
    last_status: str | None
    last_action: str | None
    last_network_access_performed: bool


class OfficialExternalRetrievalRuntimeGateway:
    """Official governed facade for explicit external retrieval execution."""

    _STATUS_TRIGGERS = (
        "estado del runtime de recuperación externa",
        "estado del runtime de recuperacion externa",
        "estado de recuperación externa",
        "estado de recuperacion externa",
    )
    _AUDIT_TRIGGERS = (
        "auditá runtime de recuperación externa",
        "audita runtime de recuperacion externa",
        "evaluá runtime de recuperación externa",
        "evalua runtime de recuperacion externa",
    )

    def __init__(
        self,
        clients: dict[KnowledgeSourceKind, ExternalRetrievalClient] | None = None,
        *,
        config: ExternalRetrievalExecutionConfig | None = None,
    ) -> None:
        normalized = dict(clients or {})
        self._registered_sources = tuple(sorted(source.value for source in normalized))
        self._adapter = ExternalRetrievalExecutionAdapter(
            normalized,
            config=config,
            gateway_owner="official-external-retrieval-runtime",
        )
        self._evaluations = 0
        self._last_result: ExternalRetrievalExecutionResult | None = None

    @property
    def snapshot(self) -> ExternalRetrievalRuntimeSnapshot:
        last = self._last_result
        return ExternalRetrievalRuntimeSnapshot(
            evaluations=self._evaluations,
            registered_sources=self._registered_sources,
            last_owner=last.request.owner if last is not None else None,
            last_status=last.status.value if last is not None else None,
            last_action=last.action.value if last is not None else None,
            last_network_access_performed=(
                last.network_access_performed if last is not None else False
            ),
        )

    def retrieve(self, step):
        result = self.execute(
            ExternalRetrievalExecutionRequest(
                owner="official-unified-retrieval-runtime",
                step=step,
            )
        )
        if result.client_result is None:
            reason = result.rationale[0].replace(" ", "_").lower()
            raise RuntimeError(reason)
        client_result = result.client_result
        from core.knowledge_retrieval_execution import KnowledgeRetrievalArtifact

        return KnowledgeRetrievalArtifact(
            source=client_result.source,
            query=client_result.query,
            content=client_result.content,
            references=client_result.references,
        )

    def execute(
        self,
        request: ExternalRetrievalExecutionRequest,
        *,
        now: datetime | None = None,
    ) -> ExternalRetrievalExecutionResult:
        result = self._adapter.execute(request, now=now)
        self._evaluations += 1
        self._last_result = result
        return result

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        del now
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._status_response(),
                rationale="official_external_retrieval_runtime_status_completed",
            )
        if not any(trigger in normalized for trigger in self._AUDIT_TRIGGERS):
            return None
        snapshot = self.snapshot
        sources = ", ".join(snapshot.registered_sources) or "ninguna"
        return GovernedOperationalInterception(
            response_text="\n".join(
                (
                    "Auditoría del External Retrieval Runtime:",
                    f"- Evaluaciones gobernadas: {snapshot.evaluations}",
                    f"- Fuentes con cliente explícito: {sources}",
                    "- Acceso de red implícito: no ejecutado.",
                    "- Proveedores de inferencia: no invocados.",
                    "- Mutaciones de plataforma: no ejecutadas.",
                    (
                        "- Resultados externos: validados por fuente, consulta, "
                        "límites y referencias HTTPS."
                    ),
                )
            ),
            rationale="official_external_retrieval_runtime_audit_completed",
        )

    def _status_response(self) -> str:
        snapshot = self.snapshot
        sources = ", ".join(snapshot.registered_sources) or "ninguna"
        return "\n".join(
            (
                "Estado del External Retrieval Runtime:",
                f"- Evaluaciones gobernadas: {snapshot.evaluations}",
                f"- Fuentes registradas: {sources}",
                f"- Último estado: {snapshot.last_status or 'ninguno'}",
                f"- Última acción: {snapshot.last_action or 'ninguna'}",
                "- Modo: explícito, gobernado y sin clientes de red predeterminados.",
            )
        )
