from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping, Sequence

from .exceptions import DomainError


class GovernedKnowledgeKind(StrEnum):
    """Stable household knowledge categories, without inference authority."""

    PERSON = "person"
    RESOURCE = "resource"
    PLACE = "place"
    PREFERENCE = "preference"
    HOUSEHOLD = "household"
    OTHER = "other"


class GovernedKnowledgeState(StrEnum):
    ACTIVE = "active"
    RETRACTED = "retracted"


@dataclass(frozen=True)
class GovernedKnowledgeFact:
    """Immutable, explicitly accepted fact about the household context."""

    fact_id: str
    owner: str
    subject: str
    predicate: str
    value: str
    kind: GovernedKnowledgeKind
    source: str
    accepted_by: tuple[str, ...]
    observed_at: datetime
    updated_at: datetime
    revision: int = 1
    supersedes_revision: int | None = None
    state: GovernedKnowledgeState = GovernedKnowledgeState.ACTIVE
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "fact_id",
            "owner",
            "subject",
            "predicate",
            "value",
            "source",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        if not isinstance(self.kind, GovernedKnowledgeKind):
            raise DomainError("kind must be a GovernedKnowledgeKind")
        if not isinstance(self.state, GovernedKnowledgeState):
            raise DomainError("state must be a GovernedKnowledgeState")
        accepted_by = _normalized_strings("accepted_by", self.accepted_by)
        if not accepted_by:
            raise DomainError("permanent knowledge requires explicit acceptance")
        object.__setattr__(self, "accepted_by", accepted_by)
        _aware_datetime("observed_at", self.observed_at)
        _aware_datetime("updated_at", self.updated_at)
        if self.updated_at < self.observed_at:
            raise DomainError("updated_at cannot precede observed_at")
        if (
            not isinstance(self.revision, int)
            or isinstance(self.revision, bool)
            or self.revision < 1
        ):
            raise DomainError("revision must be a positive integer")
        if self.revision == 1 and self.supersedes_revision is not None:
            raise DomainError("initial knowledge cannot supersede a revision")
        if self.revision > 1 and self.supersedes_revision != self.revision - 1:
            raise DomainError("knowledge revisions must supersede the prior revision")
        object.__setattr__(
            self,
            "metadata",
            _immutable_mapping("metadata", self.metadata),
        )


@dataclass(frozen=True)
class GovernedPermanentKnowledgeSnapshot:
    schema_version: str
    authority: str
    persistence_enabled: bool
    automatic_learning_enabled: bool
    conversation_authority: bool
    inference_enabled: bool
    active_facts: int
    total_revisions: int
    kinds: tuple[GovernedKnowledgeKind, ...]


class GovernedPermanentKnowledge:
    """Gateway-owned authority for explicit, revisable household facts."""

    SCHEMA_VERSION = "m347.0"
    AUTHORITY = (
        "domain.governed_permanent_knowledge:GovernedPermanentKnowledge"
    )

    def __init__(self) -> None:
        self._history: dict[str, tuple[GovernedKnowledgeFact, ...]] = {}

    @property
    def snapshot(self) -> GovernedPermanentKnowledgeSnapshot:
        current = tuple(history[-1] for history in self._history.values())
        return GovernedPermanentKnowledgeSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            persistence_enabled=False,
            automatic_learning_enabled=False,
            conversation_authority=False,
            inference_enabled=False,
            active_facts=sum(
                fact.state is GovernedKnowledgeState.ACTIVE for fact in current
            ),
            total_revisions=sum(len(history) for history in self._history.values()),
            kinds=tuple(GovernedKnowledgeKind),
        )

    def remember(
        self,
        *,
        fact_id: str,
        owner: str,
        subject: str,
        predicate: str,
        value: str,
        kind: GovernedKnowledgeKind,
        source: str,
        accepted_by: Sequence[str],
        observed_at: datetime | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> GovernedKnowledgeFact:
        if fact_id in self._history:
            raise DomainError(f"fact_id already exists: {fact_id}")
        timestamp = _observed_at(observed_at)
        fact = GovernedKnowledgeFact(
            fact_id=fact_id,
            owner=owner,
            subject=subject,
            predicate=predicate,
            value=value,
            kind=kind,
            source=source,
            accepted_by=tuple(accepted_by),
            observed_at=timestamp,
            updated_at=timestamp,
            metadata=metadata,
        )
        self._history[fact_id] = (fact,)
        return fact

    def find(self, fact_id: str) -> GovernedKnowledgeFact | None:
        history = self._history.get(fact_id)
        return history[-1] if history else None

    def active(
        self,
        *,
        owner: str | None = None,
        kind: GovernedKnowledgeKind | None = None,
    ) -> tuple[GovernedKnowledgeFact, ...]:
        if kind is not None and not isinstance(kind, GovernedKnowledgeKind):
            raise DomainError("kind must be a GovernedKnowledgeKind")
        return tuple(
            fact
            for history in self._history.values()
            if (fact := history[-1]).state is GovernedKnowledgeState.ACTIVE
            and (owner is None or fact.owner == owner)
            and (kind is None or fact.kind is kind)
        )

    def history(self, fact_id: str) -> tuple[GovernedKnowledgeFact, ...]:
        return self._history.get(fact_id, ())

    def revise(
        self,
        fact_id: str,
        *,
        value: str,
        source: str,
        accepted_by: Sequence[str],
        observed_at: datetime | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> GovernedKnowledgeFact:
        current = self._require(fact_id)
        if current.state is GovernedKnowledgeState.RETRACTED:
            raise DomainError("retracted knowledge cannot be revised")
        timestamp = _observed_at(observed_at)
        revised = replace(
            current,
            value=value,
            source=source,
            accepted_by=tuple(accepted_by),
            updated_at=timestamp,
            revision=current.revision + 1,
            supersedes_revision=current.revision,
            metadata=metadata,
        )
        self._history[fact_id] = (*self._history[fact_id], revised)
        return revised

    def retract(
        self,
        fact_id: str,
        *,
        accepted_by: Sequence[str],
        observed_at: datetime | None = None,
    ) -> GovernedKnowledgeFact:
        current = self._require(fact_id)
        if current.state is GovernedKnowledgeState.RETRACTED:
            return current
        timestamp = _observed_at(observed_at)
        retracted = replace(
            current,
            accepted_by=tuple(accepted_by),
            updated_at=timestamp,
            revision=current.revision + 1,
            supersedes_revision=current.revision,
            state=GovernedKnowledgeState.RETRACTED,
        )
        self._history[fact_id] = (*self._history[fact_id], retracted)
        return retracted

    def _require(self, fact_id: str) -> GovernedKnowledgeFact:
        fact = self.find(fact_id)
        if fact is None:
            raise DomainError(f"unknown fact_id: {fact_id}")
        return fact


def _observed_at(value: datetime | None) -> datetime:
    timestamp = value or datetime.now(timezone.utc)
    _aware_datetime("observed_at", timestamp)
    return timestamp


def _aware_datetime(field_name: str, value: datetime) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise DomainError(f"{field_name} must be timezone-aware")


def _normalized_strings(field_name: str, values: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(values)
    if not all(isinstance(value, str) and value.strip() for value in normalized):
        raise DomainError(f"{field_name} must contain only non-empty strings")
    if len(normalized) != len(set(normalized)):
        raise DomainError(f"{field_name} cannot contain duplicates")
    return normalized


def _immutable_mapping(
    field_name: str, values: Mapping[str, str] | None
) -> Mapping[str, str]:
    normalized = dict(values or {})
    if not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in normalized.items()
    ):
        raise DomainError(
            f"{field_name} must contain non-empty string keys and values"
        )
    return MappingProxyType(normalized)
