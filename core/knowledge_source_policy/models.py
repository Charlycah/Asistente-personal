from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.governed_provider_routing import GovernedProviderRoute


class KnowledgeSourceKind(str, Enum):
    INTERNAL = "internal"
    LOCAL_DOCUMENTS = "local_documents"
    OFFICIAL_DOCUMENTATION = "official_documentation"
    WEB = "web"
    NEWS = "news"
    API = "api"


class KnowledgeSourceStatus(str, Enum):
    INTERNAL_SUFFICIENT = "internal_sufficient"
    LOCAL_SOURCE_PREFERRED = "local_source_preferred"
    EXTERNAL_SOURCE_REQUIRED = "external_source_required"
    VERIFICATION_REQUIRED = "verification_required"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class KnowledgeSourceAction(str, Enum):
    USE_INTERNAL = "use_internal"
    USE_LOCAL_SOURCE = "use_local_source"
    DECLARE_EXTERNAL_REQUIREMENT = "declare_external_requirement"
    DECLARE_VERIFICATION_REQUIREMENT = "declare_verification_requirement"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class KnowledgeSourceNeed:
    query: str
    internal_confidence: float = 1.0
    current_information_required: bool = False
    explicit_external_request: bool = False
    verification_required: bool = False
    local_documents_available: bool = False
    preferred_sources: tuple[KnowledgeSourceKind | str, ...] = ()
    sensitive: bool = False

    def __post_init__(self) -> None:
        query = self.query.strip()
        sources = tuple(KnowledgeSourceKind(item) for item in self.preferred_sources)
        if not query:
            raise ValueError("knowledge source query must not be blank")
        if not 0 <= self.internal_confidence <= 1:
            raise ValueError("internal confidence must be between zero and one")
        if len(sources) != len(set(sources)):
            raise ValueError("preferred knowledge sources must be unique")
        object.__setattr__(self, "query", query)
        object.__setattr__(self, "preferred_sources", sources)


@dataclass(frozen=True)
class KnowledgeSourcePolicyConfig:
    minimum_internal_confidence: float = 0.75
    prefer_local_documents: bool = True
    allow_external_sources: bool = True
    require_verification_for_low_confidence: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_internal_confidence <= 1:
            raise ValueError("minimum internal confidence must be between zero and one")


@dataclass(frozen=True)
class KnowledgeSourcePolicyRequest:
    owner: str
    provider_route: GovernedProviderRoute
    need: KnowledgeSourceNeed
    policy_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("knowledge source policy owner must not be blank")
        source_owner = self.provider_route.request.owner
        if owner.casefold() != source_owner.casefold():
            raise ValueError("knowledge source policy owner must match route owner")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class KnowledgeSourceDecision:
    request: KnowledgeSourcePolicyRequest
    status: KnowledgeSourceStatus | str
    action: KnowledgeSourceAction | str
    selected_sources: tuple[KnowledgeSourceKind | str, ...]
    external_knowledge_required: bool
    verification_required: bool
    retrieval_allowed: bool
    network_access_allowed: bool
    provider_call_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = ""

    def __post_init__(self) -> None:
        status = KnowledgeSourceStatus(self.status)
        action = KnowledgeSourceAction(self.action)
        sources = tuple(KnowledgeSourceKind(item) for item in self.selected_sources)
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("knowledge source timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("knowledge source rationale must not be empty")
        if len(sources) != len(set(sources)):
            raise ValueError("selected knowledge sources must be unique")
        if any(
            (
                self.retrieval_allowed,
                self.network_access_allowed,
                self.provider_call_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M169 cannot authorize retrieval or execution")
        external_statuses = {
            KnowledgeSourceStatus.EXTERNAL_SOURCE_REQUIRED,
            KnowledgeSourceStatus.VERIFICATION_REQUIRED,
        }
        if self.external_knowledge_required != (status in external_statuses):
            raise ValueError("external knowledge flag must match source status")
        if self.verification_required != (
            status is KnowledgeSourceStatus.VERIFICATION_REQUIRED
        ):
            raise ValueError("verification flag must match source status")
        if status is KnowledgeSourceStatus.INTERNAL_SUFFICIENT and sources != (
            KnowledgeSourceKind.INTERNAL,
        ):
            raise ValueError("internal source status requires internal source")
        if status is KnowledgeSourceStatus.LOCAL_SOURCE_PREFERRED and sources != (
            KnowledgeSourceKind.LOCAL_DOCUMENTS,
        ):
            raise ValueError("local source status requires local documents")
        if (
            status
            in {
                KnowledgeSourceStatus.WITHHELD,
                KnowledgeSourceStatus.NOT_APPLICABLE,
            }
            and sources
        ):
            raise ValueError("inactive source policy cannot select sources")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "selected_sources", sources)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("knowledge source decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.provider_route.route_id,
                self.request.need.query.casefold(),
                self.status.value,
                self.action.value,
                ",".join(item.value for item in self.selected_sources),
                str(self.external_knowledge_required),
                str(self.verification_required),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class KnowledgeSourcePolicyRepository(Protocol):
    def add(self, decision: KnowledgeSourceDecision) -> None: ...

    def get(self, decision_id: str) -> KnowledgeSourceDecision | None: ...

    def list_all(self) -> tuple[KnowledgeSourceDecision, ...]: ...


class InMemoryKnowledgeSourcePolicyRepository:
    def __init__(self) -> None:
        self._items: dict[str, KnowledgeSourceDecision] = {}

    def add(self, decision: KnowledgeSourceDecision) -> None:
        if decision.decision_id in self._items:
            raise ValueError("knowledge source decision already exists")
        self._items[decision.decision_id] = decision

    def get(self, decision_id: str) -> KnowledgeSourceDecision | None:
        return self._items.get(decision_id)

    def list_all(self) -> tuple[KnowledgeSourceDecision, ...]:
        return tuple(self._items.values())
