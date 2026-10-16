from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

from core.knowledge_retrieval_execution import KnowledgeRetrievalArtifact
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep

from .models import (
    EXTERNAL_SOURCES,
    ExternalClientRegistry,
    ExternalRetrievalAction,
    ExternalRetrievalClientRequest,
    ExternalRetrievalClientResult,
    ExternalRetrievalExecutionConfig,
    ExternalRetrievalExecutionRepository,
    ExternalRetrievalExecutionRequest,
    ExternalRetrievalExecutionResult,
    ExternalRetrievalStatus,
    InMemoryExternalRetrievalExecutionRepository,
)


class ExternalRetrievalExecutionAdapter:
    def __init__(
        self,
        clients: ExternalClientRegistry | None = None,
        *,
        config: ExternalRetrievalExecutionConfig | None = None,
        repository: ExternalRetrievalExecutionRepository | None = None,
        gateway_owner: str = "knowledge-retrieval-gateway",
    ) -> None:
        owner = gateway_owner.strip()
        if not owner:
            raise ValueError("external retrieval gateway owner must not be blank")
        self._clients = dict(clients or {})
        if any(source not in EXTERNAL_SOURCES for source in self._clients):
            raise ValueError("external retrieval clients require external sources")
        self._config = config or ExternalRetrievalExecutionConfig()
        self._repository = repository or InMemoryExternalRetrievalExecutionRepository()
        self._gateway_owner = owner

    @property
    def last_execution(self) -> ExternalRetrievalExecutionResult | None:
        items = self._repository.list_all()
        return items[-1] if items else None

    def retrieve(self, step: KnowledgeRetrievalStep) -> KnowledgeRetrievalArtifact:
        result = self.execute(
            ExternalRetrievalExecutionRequest(
                owner=self._gateway_owner,
                step=step,
            )
        )
        if result.status is not ExternalRetrievalStatus.COMPLETED:
            reason = result.rationale[0].replace(" ", "_").lower()
            raise RuntimeError(reason)
        client_result = result.client_result
        if client_result is None:  # protected by result invariants
            raise RuntimeError("external_retrieval_result_missing")
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
        created_at = now or datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            raise ValueError("external retrieval time must be timezone-aware")
        step = request.step
        if not request.execution_requested:
            return self._store(
                request,
                ExternalRetrievalStatus.NOT_APPLICABLE,
                ExternalRetrievalAction.NONE,
                None,
                False,
                ("External retrieval was not requested.",),
                created_at,
            )
        if not self._config.execution_enabled:
            return self._store(
                request,
                ExternalRetrievalStatus.WITHHELD,
                ExternalRetrievalAction.WITHHOLD,
                None,
                False,
                ("External retrieval is disabled by configuration.",),
                created_at,
            )
        if step.source not in EXTERNAL_SOURCES:
            return self._store(
                request,
                ExternalRetrievalStatus.NOT_APPLICABLE,
                ExternalRetrievalAction.NONE,
                None,
                False,
                ("Retrieval step is not an external source.",),
                created_at,
            )
        if step.source not in self._config.allowed_sources:
            return self._store(
                request,
                ExternalRetrievalStatus.WITHHELD,
                ExternalRetrievalAction.WITHHOLD,
                None,
                False,
                ("External source is not allowed by configuration.",),
                created_at,
            )
        if len(step.query) > self._config.maximum_query_characters:
            return self._store(
                request,
                ExternalRetrievalStatus.WITHHELD,
                ExternalRetrievalAction.WITHHOLD,
                None,
                False,
                ("External retrieval query exceeds the governed size limit.",),
                created_at,
            )
        client = self._clients.get(step.source)
        if client is None:
            return self._store(
                request,
                ExternalRetrievalStatus.WITHHELD,
                ExternalRetrievalAction.WITHHOLD,
                None,
                False,
                ("External retrieval client is not registered.",),
                created_at,
            )
        client_request = ExternalRetrievalClientRequest(
            source=step.source,
            query=step.query,
            maximum_content_characters=self._config.maximum_content_characters,
            maximum_references=self._config.maximum_references,
        )
        try:
            result = client.retrieve(client_request)
        except Exception as error:
            return self._store(
                request,
                ExternalRetrievalStatus.FAILED,
                ExternalRetrievalAction.REPORT_FAILURE,
                None,
                True,
                (f"External retrieval client failed: {type(error).__name__}.",),
                created_at,
            )
        rejection = self._validate(step, result)
        if rejection is not None:
            return self._store(
                request,
                ExternalRetrievalStatus.REJECTED,
                ExternalRetrievalAction.REJECT_RESULT,
                None,
                True,
                (rejection,),
                created_at,
            )
        normalized = ExternalRetrievalClientResult(
            source=result.source,
            query=result.query,
            content=result.content,
            references=result.references,
        )
        return self._store(
            request,
            ExternalRetrievalStatus.COMPLETED,
            ExternalRetrievalAction.EXECUTE_EXTERNAL_RETRIEVAL,
            normalized,
            True,
            ("Governed external retrieval completed successfully.",),
            created_at,
        )

    def _validate(
        self,
        step: KnowledgeRetrievalStep,
        result: object,
    ) -> str | None:
        if not isinstance(result, ExternalRetrievalClientResult):
            return "External retrieval client returned an invalid result type."
        if result.source is not step.source:
            return "External retrieval result source does not match the governed step."
        if result.query != step.query:
            return "External retrieval result query does not match the governed step."
        if len(result.content) > self._config.maximum_content_characters:
            return "External retrieval content exceeds the governed size limit."
        if len(result.references) > self._config.maximum_references:
            return "External retrieval references exceed the governed count limit."
        if self._config.require_https_references and any(
            not self._is_https_reference(reference) for reference in result.references
        ):
            return "External retrieval result contains a non-HTTPS reference."
        return None

    @staticmethod
    def _is_https_reference(reference: str) -> bool:
        parsed = urlparse(reference)
        return parsed.scheme.casefold() == "https" and bool(parsed.netloc)

    def _store(
        self,
        request: ExternalRetrievalExecutionRequest,
        status: ExternalRetrievalStatus,
        action: ExternalRetrievalAction,
        client_result: ExternalRetrievalClientResult | None,
        attempted: bool,
        rationale: tuple[str, ...],
        created_at: datetime,
    ) -> ExternalRetrievalExecutionResult:
        result = ExternalRetrievalExecutionResult(
            request=request,
            status=status,
            action=action,
            client_result=client_result,
            network_access_performed=attempted,
            provider_call_performed=False,
            platform_mutation_performed=False,
            rationale=rationale,
            created_at=created_at,
        )
        self._repository.add(result)
        return result
