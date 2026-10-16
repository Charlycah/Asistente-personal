from __future__ import annotations

from datetime import datetime, timezone

from core.knowledge_retrieval_orchestrator import (
    KnowledgeRetrievalStatus,
    RetrievalStrategy,
)
from core.knowledge_source_policy import KnowledgeSourceKind

from .models import (
    InMemoryKnowledgeRetrievalExecutionRepository,
    KnowledgeExecutionStatus,
    KnowledgeRetrievalArtifact,
    KnowledgeRetrievalExecution,
    KnowledgeRetrievalExecutionConfig,
    KnowledgeRetrievalExecutionRepository,
    KnowledgeRetrievalExecutionRequest,
    KnowledgeStepExecution,
    KnowledgeStepExecutionStatus,
    RetrieverRegistry,
)

_NETWORK_SOURCES = {
    KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
    KnowledgeSourceKind.WEB,
    KnowledgeSourceKind.NEWS,
    KnowledgeSourceKind.API,
}


class KnowledgeRetrievalExecutionGateway:
    def __init__(
        self,
        retrievers: RetrieverRegistry | None = None,
        config: KnowledgeRetrievalExecutionConfig | None = None,
        repository: KnowledgeRetrievalExecutionRepository | None = None,
    ) -> None:
        self.retrievers = dict(retrievers or {})
        self.config = config or KnowledgeRetrievalExecutionConfig()
        self.repository = repository or InMemoryKnowledgeRetrievalExecutionRepository()

    @property
    def last_execution(self) -> KnowledgeRetrievalExecution | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def execute(
        self,
        request: KnowledgeRetrievalExecutionRequest,
        *,
        now: datetime | None = None,
        execution_retrievers: RetrieverRegistry | None = None,
    ) -> KnowledgeRetrievalExecution:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("knowledge execution time must be timezone-aware")
        scoped = dict(execution_retrievers or {})
        overlap = self.retrievers.keys() & scoped.keys()
        if overlap:
            raise ValueError("execution retriever cannot override persistent retriever")
        execution = self._execute(request, timestamp, scoped)
        self.repository.add(execution)
        return execution

    def _execute(
        self,
        request: KnowledgeRetrievalExecutionRequest,
        timestamp: datetime,
        execution_retrievers: RetrieverRegistry,
    ) -> KnowledgeRetrievalExecution:
        if not request.execution_requested:
            return self._inactive(
                request,
                timestamp,
                KnowledgeExecutionStatus.NOT_APPLICABLE,
                "knowledge_retrieval_execution_not_requested",
            )
        if request.plan.status in {
            KnowledgeRetrievalStatus.WITHHELD,
            KnowledgeRetrievalStatus.NOT_APPLICABLE,
        }:
            return self._inactive(
                request,
                timestamp,
                KnowledgeExecutionStatus.WITHHELD,
                "knowledge_retrieval_plan_not_executable",
            )
        if not self.config.execution_enabled:
            return self._withheld_steps(
                request,
                timestamp,
                "knowledge_retrieval_execution_disabled",
            )

        results: list[KnowledgeStepExecution] = []
        halt = False
        for step in request.plan.steps:
            if halt:
                results.append(
                    KnowledgeStepExecution(
                        step=step,
                        status=KnowledgeStepExecutionStatus.SKIPPED,
                        artifact=None,
                        rationale=("prior_required_retrieval_step_failed",),
                    )
                )
                continue
            result = self._execute_step(step, execution_retrievers)
            results.append(result)
            if (
                result.status
                in {
                    KnowledgeStepExecutionStatus.FAILED,
                    KnowledgeStepExecutionStatus.WITHHELD,
                }
                and step.required
                and request.plan.strategy is not RetrievalStrategy.PARALLEL
            ):
                halt = True
            elif (
                result.status is KnowledgeStepExecutionStatus.FAILED
                and not step.required
                and not self.config.continue_after_optional_failure
            ):
                halt = True

        return self._result(request, timestamp, tuple(results))

    def _execute_step(
        self,
        step,
        execution_retrievers: RetrieverRegistry,
    ) -> KnowledgeStepExecution:
        denial = self._denial_reason(step.source)
        if denial is not None:
            return KnowledgeStepExecution(
                step=step,
                status=KnowledgeStepExecutionStatus.WITHHELD,
                artifact=None,
                rationale=(denial,),
            )
        retriever = execution_retrievers.get(step.source)
        if retriever is None:
            retriever = self.retrievers.get(step.source)
        if retriever is None:
            return KnowledgeStepExecution(
                step=step,
                status=KnowledgeStepExecutionStatus.FAILED,
                artifact=None,
                rationale=("knowledge_retriever_not_registered",),
            )
        try:
            artifact = retriever.retrieve(step)
            artifact = self._validated_artifact(step, artifact)
        except Exception as error:  # adapter errors become governed outcomes
            return KnowledgeStepExecution(
                step=step,
                status=KnowledgeStepExecutionStatus.FAILED,
                artifact=None,
                rationale=(f"knowledge_retriever_failed:{type(error).__name__}",),
            )
        return KnowledgeStepExecution(
            step=step,
            status=KnowledgeStepExecutionStatus.SUCCEEDED,
            artifact=artifact,
            rationale=("knowledge_retrieval_step_completed",),
        )

    def _denial_reason(self, source: KnowledgeSourceKind) -> str | None:
        if source is KnowledgeSourceKind.INTERNAL and not self.config.allow_internal:
            return "internal_knowledge_retrieval_not_allowed"
        if (
            source is KnowledgeSourceKind.LOCAL_DOCUMENTS
            and not self.config.allow_local_documents
        ):
            return "local_document_retrieval_not_allowed"
        if source in _NETWORK_SOURCES and not self.config.allow_network:
            return "network_knowledge_retrieval_not_allowed"
        return None

    def _validated_artifact(
        self,
        step,
        artifact: KnowledgeRetrievalArtifact,
    ) -> KnowledgeRetrievalArtifact:
        if not isinstance(artifact, KnowledgeRetrievalArtifact):
            raise TypeError("retriever must return KnowledgeRetrievalArtifact")
        if artifact.source is not step.source:
            raise ValueError("retriever returned a different source")
        if artifact.query != step.query:
            raise ValueError("retriever returned a different query")
        if len(artifact.content) > self.config.max_content_characters:
            raise ValueError("retrieval artifact exceeds content limit")
        return artifact

    @staticmethod
    def _result(
        request: KnowledgeRetrievalExecutionRequest,
        timestamp: datetime,
        steps: tuple[KnowledgeStepExecution, ...],
    ) -> KnowledgeRetrievalExecution:
        statuses = tuple(item.status for item in steps)
        succeeded = sum(
            item is KnowledgeStepExecutionStatus.SUCCEEDED for item in statuses
        )
        if succeeded == len(steps):
            status = KnowledgeExecutionStatus.COMPLETED
            rationale = "all_knowledge_retrieval_steps_completed"
        elif succeeded:
            status = KnowledgeExecutionStatus.PARTIAL
            rationale = "knowledge_retrieval_partially_completed"
        elif any(item is KnowledgeStepExecutionStatus.WITHHELD for item in statuses):
            status = KnowledgeExecutionStatus.WITHHELD
            rationale = "knowledge_retrieval_withheld"
        else:
            status = KnowledgeExecutionStatus.FAILED
            rationale = "knowledge_retrieval_failed"
        return KnowledgeRetrievalExecution(
            request=request,
            status=status,
            steps=steps,
            retrieval_performed=bool(succeeded),
            network_access_performed=any(
                item.status is KnowledgeStepExecutionStatus.SUCCEEDED
                and item.step.source in _NETWORK_SOURCES
                for item in steps
            ),
            provider_call_performed=False,
            platform_mutation_performed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )

    @staticmethod
    def _inactive(
        request: KnowledgeRetrievalExecutionRequest,
        timestamp: datetime,
        status: KnowledgeExecutionStatus,
        rationale: str,
    ) -> KnowledgeRetrievalExecution:
        steps = tuple(
            KnowledgeStepExecution(
                step=step,
                status=KnowledgeStepExecutionStatus.SKIPPED,
                artifact=None,
                rationale=(rationale,),
            )
            for step in request.plan.steps
        )
        return KnowledgeRetrievalExecution(
            request=request,
            status=status,
            steps=steps,
            retrieval_performed=False,
            network_access_performed=False,
            provider_call_performed=False,
            platform_mutation_performed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )

    @staticmethod
    def _withheld_steps(
        request: KnowledgeRetrievalExecutionRequest,
        timestamp: datetime,
        rationale: str,
    ) -> KnowledgeRetrievalExecution:
        steps = tuple(
            KnowledgeStepExecution(
                step=step,
                status=KnowledgeStepExecutionStatus.WITHHELD,
                artifact=None,
                rationale=(rationale,),
            )
            for step in request.plan.steps
        )
        return KnowledgeRetrievalExecution(
            request=request,
            status=KnowledgeExecutionStatus.WITHHELD,
            steps=steps,
            retrieval_performed=False,
            network_access_performed=False,
            provider_call_performed=False,
            platform_mutation_performed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )
