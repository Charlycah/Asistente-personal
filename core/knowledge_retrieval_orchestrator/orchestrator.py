from __future__ import annotations

from datetime import datetime, timezone

from core.knowledge_source_policy import KnowledgeSourceStatus

from .models import (
    InMemoryKnowledgeRetrievalRepository,
    KnowledgeRetrievalAction,
    KnowledgeRetrievalConfig,
    KnowledgeRetrievalPlan,
    KnowledgeRetrievalRepository,
    KnowledgeRetrievalRequest,
    KnowledgeRetrievalStatus,
    KnowledgeRetrievalStep,
    RetrievalStrategy,
)


class KnowledgeRetrievalOrchestrator:
    def __init__(
        self,
        config: KnowledgeRetrievalConfig | None = None,
        repository: KnowledgeRetrievalRepository | None = None,
    ) -> None:
        self.config = config or KnowledgeRetrievalConfig()
        self.repository = repository or InMemoryKnowledgeRetrievalRepository()

    @property
    def last_plan(self) -> KnowledgeRetrievalPlan | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def orchestrate(
        self,
        request: KnowledgeRetrievalRequest,
        *,
        now: datetime | None = None,
    ) -> KnowledgeRetrievalPlan:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("knowledge retrieval time must be timezone-aware")
        plan = self._orchestrate(request, timestamp)
        self.repository.add(plan)
        return plan

    def _orchestrate(
        self,
        request: KnowledgeRetrievalRequest,
        timestamp: datetime,
    ) -> KnowledgeRetrievalPlan:
        if not request.orchestration_requested:
            return self._inactive(
                request,
                timestamp,
                KnowledgeRetrievalStatus.NOT_APPLICABLE,
                KnowledgeRetrievalAction.NONE,
                "knowledge_retrieval_orchestration_not_requested",
            )
        decision = request.source_decision
        if decision.status in {
            KnowledgeSourceStatus.WITHHELD,
            KnowledgeSourceStatus.NOT_APPLICABLE,
        }:
            return self._inactive(
                request,
                timestamp,
                KnowledgeRetrievalStatus.WITHHELD,
                KnowledgeRetrievalAction.WITHHOLD,
                "knowledge_source_decision_not_available",
            )
        steps = self._steps(request)
        if decision.status is KnowledgeSourceStatus.INTERNAL_SUFFICIENT:
            return self._active(
                request,
                timestamp,
                KnowledgeRetrievalStatus.INTERNAL_PLANNED,
                KnowledgeRetrievalAction.PREPARE_INTERNAL,
                RetrievalStrategy.DIRECT,
                steps,
                "internal_knowledge_retrieval_planned",
            )
        if decision.status is KnowledgeSourceStatus.LOCAL_SOURCE_PREFERRED:
            return self._active(
                request,
                timestamp,
                KnowledgeRetrievalStatus.LOCAL_PLANNED,
                KnowledgeRetrievalAction.PREPARE_LOCAL,
                RetrievalStrategy.DIRECT,
                steps,
                "local_knowledge_retrieval_planned",
            )
        if decision.status is KnowledgeSourceStatus.VERIFICATION_REQUIRED:
            strategy = (
                RetrievalStrategy.PARALLEL
                if self.config.parallel_verification and len(steps) > 1
                else RetrievalStrategy.SEQUENTIAL
            )
            return self._active(
                request,
                timestamp,
                KnowledgeRetrievalStatus.VERIFICATION_PLANNED,
                KnowledgeRetrievalAction.PREPARE_VERIFICATION,
                strategy,
                steps,
                "knowledge_verification_retrieval_planned",
            )
        return self._active(
            request,
            timestamp,
            KnowledgeRetrievalStatus.EXTERNAL_PLANNED,
            KnowledgeRetrievalAction.PREPARE_EXTERNAL,
            (
                RetrievalStrategy.SEQUENTIAL
                if len(steps) > 1
                else RetrievalStrategy.DIRECT
            ),
            steps,
            "external_knowledge_retrieval_planned",
        )

    def _steps(
        self,
        request: KnowledgeRetrievalRequest,
    ) -> tuple[KnowledgeRetrievalStep, ...]:
        query = request.source_decision.request.need.query
        sources = request.source_decision.selected_sources[: self.config.max_sources]
        verification = (
            request.source_decision.status
            is KnowledgeSourceStatus.VERIFICATION_REQUIRED
        )
        return tuple(
            KnowledgeRetrievalStep(
                source=source,
                priority=index,
                required=not verification or index <= 2,
                query=query,
            )
            for index, source in enumerate(sources, start=1)
        )

    @staticmethod
    def _active(
        request: KnowledgeRetrievalRequest,
        timestamp: datetime,
        status: KnowledgeRetrievalStatus,
        action: KnowledgeRetrievalAction,
        strategy: RetrievalStrategy,
        steps: tuple[KnowledgeRetrievalStep, ...],
        rationale: str,
    ) -> KnowledgeRetrievalPlan:
        return KnowledgeRetrievalPlan(
            request=request,
            status=status,
            action=action,
            strategy=strategy,
            steps=steps,
            verification_required=(
                status is KnowledgeRetrievalStatus.VERIFICATION_PLANNED
            ),
            retrieval_allowed=False,
            network_access_allowed=False,
            provider_call_allowed=False,
            platform_mutation_allowed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )

    @staticmethod
    def _inactive(
        request: KnowledgeRetrievalRequest,
        timestamp: datetime,
        status: KnowledgeRetrievalStatus,
        action: KnowledgeRetrievalAction,
        rationale: str,
    ) -> KnowledgeRetrievalPlan:
        return KnowledgeRetrievalPlan(
            request=request,
            status=status,
            action=action,
            strategy=RetrievalStrategy.DIRECT,
            steps=(),
            verification_required=False,
            retrieval_allowed=False,
            network_access_allowed=False,
            provider_call_allowed=False,
            platform_mutation_allowed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )
