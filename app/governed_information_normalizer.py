from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum

from .governed_information_sources import (
    GovernedInformationItem,
    GovernedInformationSources,
    InformationRegion,
)
from .personal_interest_center import InterestTopic
from .relevance_evaluator import RelevanceCandidate


class NormalizedInformationKind(StrEnum):
    NEWS = "news"
    RELEASE = "release"
    EVENT = "event"
    GUIDANCE = "guidance"
    DISCOVERY = "discovery"


class InformationVerificationStatus(StrEnum):
    CONFIRMED = "confirmed"
    REPORTED = "reported"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class RawGovernedInformation:
    source_id: str
    external_id: str
    title: str
    topics: frozenset[InterestTopic]
    kind: NormalizedInformationKind = NormalizedInformationKind.NEWS
    verification: InformationVerificationStatus = InformationVerificationStatus.REPORTED
    published_at: datetime | None = None
    event_at: datetime | None = None
    region: InformationRegion | None = None
    location: str | None = None
    is_free: bool = False
    time_sensitive: bool = False
    importance: int = 0
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class NormalizedGovernedInformation:
    canonical_id: str
    source_id: str
    external_id: str
    title: str
    topics: frozenset[InterestTopic]
    kind: NormalizedInformationKind
    verification: InformationVerificationStatus
    published_at: datetime | None
    event_at: datetime | None
    region: InformationRegion
    location: str | None
    is_free: bool
    time_sensitive: bool
    importance: int
    tags: tuple[str, ...]
    source_confidence: int

    def as_relevance_candidate(self) -> RelevanceCandidate:
        return RelevanceCandidate(
            title=self.title,
            topics=self.topics,
            location=self.location,
            is_free=self.is_free,
            time_sensitive=self.time_sensitive,
            importance=self.importance,
            source_confidence=self.source_confidence,
            verification=self.verification.value,
            information_kind=self.kind.value,
            published_at=self.published_at,
            event_at=self.event_at,
            region=self.region.value,
        )


@dataclass(frozen=True)
class GovernedInformationNormalizerSnapshot:
    schema_version: str
    authority: str
    network_enabled: bool
    autonomous_execution_enabled: bool


class GovernedInformationNormalizer:
    """Canonical pure normalizer for already supplied governed information."""

    SCHEMA_VERSION = "m343.8"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"

    def __init__(self, sources: GovernedInformationSources) -> None:
        self._sources = sources

    @property
    def snapshot(self) -> GovernedInformationNormalizerSnapshot:
        return GovernedInformationNormalizerSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            network_enabled=False,
            autonomous_execution_enabled=False,
        )

    def normalize(
        self,
        raw: RawGovernedInformation,
    ) -> NormalizedGovernedInformation:
        item = GovernedInformationItem(
            source_id=raw.source_id,
            external_id=raw.external_id,
            title=raw.title,
            topics=raw.topics,
            published_at=self._utc_or_none(raw.published_at),
            location=self._clean_optional(raw.location),
            is_free=raw.is_free,
            time_sensitive=raw.time_sensitive,
            importance=raw.importance,
        )
        self._sources.accept(item)
        source = self._sources.source_for(raw.source_id)
        region = raw.region or self._default_region(source.classification.regions)
        return NormalizedGovernedInformation(
            canonical_id=self._canonical_id(raw.source_id, raw.external_id),
            source_id=source.source_id,
            external_id=raw.external_id.strip(),
            title=self._normalize_text(raw.title),
            topics=frozenset(raw.topics),
            kind=raw.kind,
            verification=raw.verification,
            published_at=self._utc_or_none(raw.published_at),
            event_at=self._utc_or_none(raw.event_at),
            region=region,
            location=self._clean_optional(raw.location),
            is_free=raw.is_free,
            time_sensitive=raw.time_sensitive,
            importance=raw.importance,
            tags=self._normalize_tags(raw.tags),
            source_confidence=source.classification.confidence,
        )

    def normalize_to_candidate(
        self,
        raw: RawGovernedInformation,
    ) -> RelevanceCandidate:
        return self.normalize(raw).as_relevance_candidate()

    @staticmethod
    def _canonical_id(source_id: str, external_id: str) -> str:
        source = GovernedInformationNormalizer._slug(source_id)
        external = GovernedInformationNormalizer._slug(external_id)
        if not source or not external:
            raise ValueError("canonical information identity cannot be empty")
        return f"{source}:{external}"

    @staticmethod
    def _slug(value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().casefold())
        return normalized.strip("-")

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(value.split())

    @staticmethod
    def _clean_optional(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        return cleaned or None

    @staticmethod
    def _normalize_tags(tags: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(
            dict.fromkeys(
                GovernedInformationNormalizer._slug(tag)
                for tag in tags
                if GovernedInformationNormalizer._slug(tag)
            )
        )
        return normalized

    @staticmethod
    def _utc_or_none(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _default_region(
        regions: frozenset[InformationRegion],
    ) -> InformationRegion:
        for preferred in (
            InformationRegion.CABA,
            InformationRegion.ARGENTINA,
            InformationRegion.GLOBAL,
        ):
            if preferred in regions:
                return preferred
        return sorted(regions, key=lambda item: item.value)[0]
