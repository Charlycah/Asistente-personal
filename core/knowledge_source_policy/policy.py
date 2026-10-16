from __future__ import annotations

from datetime import datetime, timezone

from core.governed_provider_routing import ProviderRouteStatus

from .models import (
    InMemoryKnowledgeSourcePolicyRepository,
    KnowledgeSourceAction,
    KnowledgeSourceDecision,
    KnowledgeSourceKind,
    KnowledgeSourcePolicyConfig,
    KnowledgeSourcePolicyRepository,
    KnowledgeSourcePolicyRequest,
    KnowledgeSourceStatus,
)


class KnowledgeSourcePolicy:
    def __init__(
        self,
        config: KnowledgeSourcePolicyConfig | None = None,
        repository: KnowledgeSourcePolicyRepository | None = None,
    ) -> None:
        self.config = config or KnowledgeSourcePolicyConfig()
        self.repository = repository or InMemoryKnowledgeSourcePolicyRepository()

    @property
    def last_decision(self) -> KnowledgeSourceDecision | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def decide(
        self,
        request: KnowledgeSourcePolicyRequest,
        *,
        now: datetime | None = None,
    ) -> KnowledgeSourceDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("knowledge source evaluation time must be timezone-aware")
        decision = self._decide(request, timestamp)
        self.repository.add(decision)
        return decision

    def _decide(
        self,
        request: KnowledgeSourcePolicyRequest,
        timestamp: datetime,
    ) -> KnowledgeSourceDecision:
        if not request.policy_requested:
            return self._inactive(
                request,
                timestamp,
                KnowledgeSourceStatus.NOT_APPLICABLE,
                KnowledgeSourceAction.NONE,
                "knowledge_source_policy_not_requested",
            )
        route_status = request.provider_route.status
        if route_status in {
            ProviderRouteStatus.WITHHELD,
            ProviderRouteStatus.NOT_APPLICABLE,
        }:
            return self._inactive(
                request,
                timestamp,
                KnowledgeSourceStatus.WITHHELD,
                KnowledgeSourceAction.WITHHOLD,
                "provider_route_not_available",
            )
        need = request.need
        if need.current_information_required or need.explicit_external_request:
            return self._external(
                request,
                timestamp,
                verification=False,
                rationale="external_knowledge_explicitly_required",
            )
        if need.verification_required:
            return self._external(
                request,
                timestamp,
                verification=True,
                rationale="knowledge_verification_required",
            )
        if (
            self.config.prefer_local_documents
            and need.local_documents_available
            and KnowledgeSourceKind.LOCAL_DOCUMENTS
            in self._preferred_or_default_sources(request)
        ):
            return self._decision(
                request,
                timestamp,
                KnowledgeSourceStatus.LOCAL_SOURCE_PREFERRED,
                KnowledgeSourceAction.USE_LOCAL_SOURCE,
                (KnowledgeSourceKind.LOCAL_DOCUMENTS,),
                False,
                False,
                "local_documents_preferred",
            )
        if need.internal_confidence >= self.config.minimum_internal_confidence:
            return self._decision(
                request,
                timestamp,
                KnowledgeSourceStatus.INTERNAL_SUFFICIENT,
                KnowledgeSourceAction.USE_INTERNAL,
                (KnowledgeSourceKind.INTERNAL,),
                False,
                False,
                "internal_knowledge_sufficient",
            )
        if not self.config.allow_external_sources:
            return self._inactive(
                request,
                timestamp,
                KnowledgeSourceStatus.WITHHELD,
                KnowledgeSourceAction.WITHHOLD,
                "external_knowledge_not_allowed",
            )
        verification = self.config.require_verification_for_low_confidence
        return self._external(
            request,
            timestamp,
            verification=verification,
            rationale=(
                "internal_confidence_requires_verification"
                if verification
                else "internal_confidence_requires_external_source"
            ),
        )

    def _external(
        self,
        request: KnowledgeSourcePolicyRequest,
        timestamp: datetime,
        *,
        verification: bool,
        rationale: str,
    ) -> KnowledgeSourceDecision:
        if not self.config.allow_external_sources:
            return self._inactive(
                request,
                timestamp,
                KnowledgeSourceStatus.WITHHELD,
                KnowledgeSourceAction.WITHHOLD,
                "external_knowledge_not_allowed",
            )
        sources = tuple(
            item
            for item in self._preferred_or_default_sources(request)
            if item is not KnowledgeSourceKind.INTERNAL
            and item is not KnowledgeSourceKind.LOCAL_DOCUMENTS
        )
        if not sources:
            sources = (KnowledgeSourceKind.WEB,)
        return self._decision(
            request,
            timestamp,
            (
                KnowledgeSourceStatus.VERIFICATION_REQUIRED
                if verification
                else KnowledgeSourceStatus.EXTERNAL_SOURCE_REQUIRED
            ),
            (
                KnowledgeSourceAction.DECLARE_VERIFICATION_REQUIREMENT
                if verification
                else KnowledgeSourceAction.DECLARE_EXTERNAL_REQUIREMENT
            ),
            sources,
            True,
            verification,
            rationale,
        )

    @staticmethod
    def _preferred_or_default_sources(
        request: KnowledgeSourcePolicyRequest,
    ) -> tuple[KnowledgeSourceKind, ...]:
        if request.need.preferred_sources:
            return request.need.preferred_sources
        if request.need.current_information_required:
            return (KnowledgeSourceKind.NEWS, KnowledgeSourceKind.WEB)
        return (
            KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
            KnowledgeSourceKind.WEB,
        )

    @staticmethod
    def _decision(
        request: KnowledgeSourcePolicyRequest,
        timestamp: datetime,
        status: KnowledgeSourceStatus,
        action: KnowledgeSourceAction,
        sources: tuple[KnowledgeSourceKind, ...],
        external_required: bool,
        verification_required: bool,
        rationale: str,
    ) -> KnowledgeSourceDecision:
        return KnowledgeSourceDecision(
            request=request,
            status=status,
            action=action,
            selected_sources=sources,
            external_knowledge_required=external_required,
            verification_required=verification_required,
            retrieval_allowed=False,
            network_access_allowed=False,
            provider_call_allowed=False,
            platform_mutation_allowed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )

    @staticmethod
    def _inactive(
        request: KnowledgeSourcePolicyRequest,
        timestamp: datetime,
        status: KnowledgeSourceStatus,
        action: KnowledgeSourceAction,
        rationale: str,
    ) -> KnowledgeSourceDecision:
        return KnowledgeSourcePolicy._decision(
            request,
            timestamp,
            status,
            action,
            (),
            False,
            False,
            rationale,
        )
