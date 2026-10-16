from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from types import MappingProxyType
from typing import Mapping


class ExternalIntelligenceCapability(str, Enum):
    INFERENCE_PROVIDER = "inference_provider"
    INFORMATION_SOURCE = "information_source"


class ExternalExecutionScope(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class ExternalIntelligenceStatus(str, Enum):
    PREPARED = "prepared"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ExternalIntelligenceRequest:
    request_id: str
    owner: str
    capability: ExternalIntelligenceCapability | str
    purpose: str
    target_id: str | None = None
    external_access_requested: bool = True
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        request_id = self.request_id.strip()
        owner = self.owner.strip()
        purpose = self.purpose.strip()
        target_id = self.target_id.strip().casefold() if self.target_id else None
        if not request_id:
            raise ValueError("external intelligence request requires request_id")
        if not owner:
            raise ValueError("external intelligence request requires owner")
        if not purpose:
            raise ValueError("external intelligence request requires explicit purpose")
        metadata = MappingProxyType(
            {
                str(key).strip(): str(value).strip()
                for key, value in (self.metadata or {}).items()
                if str(key).strip()
            }
        )
        object.__setattr__(self, "request_id", request_id)
        object.__setattr__(self, "owner", owner)
        object.__setattr__(
            self,
            "capability",
            ExternalIntelligenceCapability(self.capability),
        )
        object.__setattr__(self, "purpose", purpose)
        object.__setattr__(self, "target_id", target_id)
        object.__setattr__(self, "metadata", metadata)


@dataclass(frozen=True)
class ExternalIntelligenceProvenance:
    actor_id: str
    capability: ExternalIntelligenceCapability | str
    execution_scope: ExternalExecutionScope | str
    network_used: bool
    observed_at: datetime
    trace_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        actor_id = self.actor_id.strip().casefold()
        trace_ids = tuple(item.strip() for item in self.trace_ids)
        if not actor_id:
            raise ValueError("external intelligence provenance requires actor_id")
        if self.observed_at.tzinfo is None:
            raise ValueError(
                "external intelligence provenance time must be timezone-aware"
            )
        if any(not item for item in trace_ids):
            raise ValueError("external intelligence trace ids must not be blank")
        if len(set(trace_ids)) != len(trace_ids):
            raise ValueError("external intelligence trace ids must be unique")
        scope = ExternalExecutionScope(self.execution_scope)
        object.__setattr__(self, "actor_id", actor_id)
        object.__setattr__(
            self,
            "capability",
            ExternalIntelligenceCapability(self.capability),
        )
        object.__setattr__(self, "execution_scope", scope)
        object.__setattr__(
            self,
            "observed_at",
            self.observed_at.astimezone(timezone.utc),
        )
        object.__setattr__(self, "trace_ids", trace_ids)


@dataclass(frozen=True)
class ExternalInferenceEvidence:
    text: str
    provider: str
    model: str | None = None
    accepted_by_provider: bool = True
    provider_error: str | None = None

    def __post_init__(self) -> None:
        provider = self.provider.strip().casefold()
        if not provider:
            raise ValueError("external inference evidence requires provider")
        object.__setattr__(self, "provider", provider)
        object.__setattr__(self, "text", self.text.strip())
        if self.model is not None:
            object.__setattr__(self, "model", self.model.strip() or None)
        if self.provider_error is not None:
            object.__setattr__(
                self,
                "provider_error",
                self.provider_error.strip() or None,
            )


@dataclass(frozen=True)
class ExternalInformationEvidence:
    source_id: str
    items: tuple[Mapping[str, object], ...]
    source_status: str = "succeeded"
    source_error: str | None = None

    def __post_init__(self) -> None:
        source_id = self.source_id.strip().casefold()
        source_status = self.source_status.strip().casefold()
        source_error = self.source_error.strip() if self.source_error else None
        if not source_id:
            raise ValueError("external information evidence requires source_id")
        if not source_status:
            raise ValueError("external information evidence requires source status")
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(self, "source_status", source_status)
        object.__setattr__(self, "source_error", source_error)
        object.__setattr__(
            self,
            "items",
            tuple(MappingProxyType(dict(item)) for item in self.items),
        )


@dataclass(frozen=True)
class ExternalIntelligenceEnvelope:
    request: ExternalIntelligenceRequest
    provenance: ExternalIntelligenceProvenance
    status: ExternalIntelligenceStatus | str
    inference: ExternalInferenceEvidence | None = None
    information: ExternalInformationEvidence | None = None
    rationale: tuple[str, ...] = ()
    envelope_id: str = ""

    def __post_init__(self) -> None:
        status = ExternalIntelligenceStatus(self.status)
        rationale = tuple(item.strip() for item in self.rationale)
        if not rationale or any(not item for item in rationale):
            raise ValueError(
                "external intelligence envelope rationale must not be empty"
            )
        if self.provenance.capability is not self.request.capability:
            raise ValueError(
                "external intelligence provenance capability must match request"
            )
        if self.request.capability is ExternalIntelligenceCapability.INFERENCE_PROVIDER:
            if self.inference is None or self.information is not None:
                raise ValueError("inference request requires only inference evidence")
            if self.inference.provider != self.provenance.actor_id:
                raise ValueError("inference provider must match provenance actor")
        else:
            if self.information is None or self.inference is not None:
                raise ValueError(
                    "information request requires only information evidence"
                )
            if self.information.source_id != self.provenance.actor_id:
                raise ValueError("information source must match provenance actor")
        object.__setattr__(self, "status", status)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.envelope_id and self.envelope_id != expected:
            raise ValueError("external intelligence envelope id is inconsistent")
        object.__setattr__(self, "rationale", rationale)
        object.__setattr__(self, "envelope_id", expected)

    @property
    def cognitive_authority_granted(self) -> bool:
        return False

    def _identity_payload(self) -> str:
        evidence_identity = (
            self.inference.provider
            if self.inference is not None
            else self.information.source_id
        )
        return "|".join(
            (
                self.request.request_id,
                self.request.owner.casefold(),
                self.request.capability.value,
                self.request.purpose,
                self.provenance.actor_id,
                self.provenance.execution_scope.value,
                str(self.provenance.network_used),
                self.provenance.observed_at.isoformat(),
                evidence_identity,
                self.status.value,
                *self.rationale,
            )
        )
