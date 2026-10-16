from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Iterable, Mapping

from .personal_interest_center import InterestTopic
from .relevance_evaluator import RelevanceCandidate


class InformationSourceKind(StrEnum):
    OFFICIAL = "official"
    PUBLIC_INSTITUTION = "public_institution"
    EDITORIAL = "editorial"


class InformationSourceStatus(StrEnum):
    DECLARED = "declared"
    DISABLED = "disabled"


class InformationSourceCapability(StrEnum):
    OPEN_VISUAL_SUBJECT_QUERY = "open_visual_subject_query"
    EXTERNAL_IMAGE_NEWEST_FIRST_QUERY = "external_image_newest_first_query"


class InformationAuthority(StrEnum):
    PRIMARY = "primary"
    INSTITUTIONAL = "institutional"
    SPECIALIZED = "specialized"
    GENERAL = "general"


class InformationProvenance(StrEnum):
    FIRST_PARTY = "first_party"
    PUBLIC_BODY = "public_body"
    EDITORIAL_REVIEW = "editorial_review"
    AGGREGATED = "aggregated"


class InformationEvidenceKind(StrEnum):
    OFFICIAL_RECORD = "official_record"
    OFFICIAL_ANNOUNCEMENT = "official_announcement"
    SCIENTIFIC_GUIDANCE = "scientific_guidance"
    EDITORIAL_REPORTING = "editorial_reporting"


class InformationCoverage(StrEnum):
    GLOBAL = "global"
    NATIONAL = "national"
    LOCAL = "local"
    TOPICAL = "topical"


class InformationRegion(StrEnum):
    GLOBAL = "global"
    ARGENTINA = "argentina"
    CABA = "caba"


@dataclass(frozen=True)
class InformationSourceClassification:
    authority: InformationAuthority
    provenance: InformationProvenance
    evidence: InformationEvidenceKind
    coverage: InformationCoverage
    regions: frozenset[InformationRegion]
    confidence: int

    def __post_init__(self) -> None:
        if not self.regions:
            raise ValueError("information source classification needs a region")
        if not 0 <= self.confidence <= 100:
            raise ValueError("information source confidence must be between 0 and 100")


@dataclass(frozen=True)
class GovernedInformationSource:
    source_id: str
    name: str
    kind: InformationSourceKind
    topics: frozenset[InterestTopic]
    status: InformationSourceStatus = InformationSourceStatus.DECLARED
    network_enabled: bool = False
    automatic_fetch_enabled: bool = False
    capabilities: frozenset[InformationSourceCapability] = frozenset()
    classification: InformationSourceClassification = InformationSourceClassification(
        authority=InformationAuthority.GENERAL,
        provenance=InformationProvenance.EDITORIAL_REVIEW,
        evidence=InformationEvidenceKind.EDITORIAL_REPORTING,
        coverage=InformationCoverage.TOPICAL,
        regions=frozenset({InformationRegion.GLOBAL}),
        confidence=60,
    )

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("information source id cannot be empty")
        if not self.name.strip():
            raise ValueError("information source name cannot be empty")
        if (
            not self.topics
            and InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY
            not in self.capabilities
        ):
            raise ValueError("information source needs at least one topic")
        if self.network_enabled or self.automatic_fetch_enabled:
            raise ValueError("M343.5 information sources must remain inactive")


@dataclass(frozen=True)
class GovernedInformationItem:
    source_id: str
    external_id: str
    title: str
    topics: frozenset[InterestTopic]
    published_at: datetime | None = None
    location: str | None = None
    is_free: bool = False
    time_sensitive: bool = False
    importance: int = 0

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("information item source id cannot be empty")
        if not self.external_id.strip():
            raise ValueError("information item external id cannot be empty")
        if not self.title.strip():
            raise ValueError("information item title cannot be empty")
        if not self.topics:
            raise ValueError("information item needs at least one topic")


@dataclass(frozen=True)
class GovernedInformationSourcesSnapshot:
    schema_version: str
    authority: str
    sources: tuple[GovernedInformationSource, ...]
    network_enabled: bool
    automatic_fetch_enabled: bool


DEFAULT_GOVERNED_INFORMATION_SOURCES: tuple[GovernedInformationSource, ...] = (
    GovernedInformationSource(
        source_id="nasa",
        name="NASA",
        kind=InformationSourceKind.OFFICIAL,
        classification=InformationSourceClassification(
            authority=InformationAuthority.PRIMARY,
            provenance=InformationProvenance.FIRST_PARTY,
            evidence=InformationEvidenceKind.OFFICIAL_ANNOUNCEMENT,
            coverage=InformationCoverage.GLOBAL,
            regions=frozenset({InformationRegion.GLOBAL}),
            confidence=98,
        ),
        topics=frozenset(
            {
                InterestTopic.SPACE_EXPLORATION,
                InterestTopic.NASA_MISSIONS,
                InterestTopic.INTERNATIONAL_SPACE_STATION,
                InterestTopic.JAMES_WEBB_SPACE_TELESCOPE,
            }
        ),
    ),
    GovernedInformationSource(
        source_id="cultura_caba",
        name="Cultura de la Ciudad de Buenos Aires",
        kind=InformationSourceKind.PUBLIC_INSTITUTION,
        classification=InformationSourceClassification(
            authority=InformationAuthority.INSTITUTIONAL,
            provenance=InformationProvenance.PUBLIC_BODY,
            evidence=InformationEvidenceKind.OFFICIAL_RECORD,
            coverage=InformationCoverage.LOCAL,
            regions=frozenset({InformationRegion.ARGENTINA, InformationRegion.CABA}),
            confidence=96,
        ),
        topics=frozenset(
            {
                InterestTopic.CULTURE_CABA,
                InterestTopic.MUSIC,
                InterestTopic.THEATRE,
                InterestTopic.MUSEUMS,
                InterestTopic.FREE_ACTIVITIES,
            }
        ),
    ),
    GovernedInformationSource(
        source_id="apple_audiovisual",
        name="Catálogo audiovisual de Apple",
        kind=InformationSourceKind.OFFICIAL,
        classification=InformationSourceClassification(
            authority=InformationAuthority.PRIMARY,
            provenance=InformationProvenance.FIRST_PARTY,
            evidence=InformationEvidenceKind.OFFICIAL_RECORD,
            coverage=InformationCoverage.GLOBAL,
            regions=frozenset(
                {InformationRegion.GLOBAL, InformationRegion.ARGENTINA}
            ),
            confidence=94,
        ),
        topics=frozenset(
            {
                InterestTopic.CINEMA,
                InterestTopic.SERIES,
                InterestTopic.RELEASES,
                InterestTopic.SCIENCE_FICTION,
                InterestTopic.HARD_SCIENCE_FICTION,
                InterestTopic.DOCUMENTARIES,
            }
        ),
    ),
    GovernedInformationSource(
        source_id="argentina_healthy_eating",
        name="Alimentación saludable del Ministerio de Salud",
        kind=InformationSourceKind.PUBLIC_INSTITUTION,
        classification=InformationSourceClassification(
            authority=InformationAuthority.INSTITUTIONAL,
            provenance=InformationProvenance.PUBLIC_BODY,
            evidence=InformationEvidenceKind.SCIENTIFIC_GUIDANCE,
            coverage=InformationCoverage.NATIONAL,
            regions=frozenset({InformationRegion.ARGENTINA}),
            confidence=97,
        ),
        topics=frozenset(
            {
                InterestTopic.HEALTHY_EATING,
                InterestTopic.EVIDENCE_BASED_NUTRITION,
                InterestTopic.HEALTHY_RECIPES,
                InterestTopic.MEDITERRANEAN_CUISINE,
                InterestTopic.ARGENTINE_CUISINE,
            }
        ),
    ),
    GovernedInformationSource(
        source_id="technology_editorial",
        name="Fuente editorial de tecnología",
        kind=InformationSourceKind.EDITORIAL,
        classification=InformationSourceClassification(
            authority=InformationAuthority.SPECIALIZED,
            provenance=InformationProvenance.EDITORIAL_REVIEW,
            evidence=InformationEvidenceKind.EDITORIAL_REPORTING,
            coverage=InformationCoverage.TOPICAL,
            regions=frozenset({InformationRegion.GLOBAL}),
            confidence=78,
        ),
        topics=frozenset(
            {
                InterestTopic.TECHNOLOGY,
                InterestTopic.ARTIFICIAL_INTELLIGENCE,
                InterestTopic.PROGRAMMING,
                InterestTopic.PROGRAMMING_LANGUAGES,
                InterestTopic.SOFTWARE_ENGINEERING,
            }
        ),
    ),
    GovernedInformationSource(
        source_id="sports_editorial",
        name="Fuente editorial deportiva",
        kind=InformationSourceKind.EDITORIAL,
        classification=InformationSourceClassification(
            authority=InformationAuthority.SPECIALIZED,
            provenance=InformationProvenance.EDITORIAL_REVIEW,
            evidence=InformationEvidenceKind.EDITORIAL_REPORTING,
            coverage=InformationCoverage.NATIONAL,
            regions=frozenset({InformationRegion.ARGENTINA}),
            confidence=76,
        ),
        topics=frozenset(
            {
                InterestTopic.SPORTS,
                InterestTopic.BOCA_JUNIORS,
                InterestTopic.RIVER_PLATE,
            }
        ),
    ),
)


class GovernedInformationSources:
    """Canonical registry and validator for inactive information sources."""

    SCHEMA_VERSION = "m343.5"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"

    def __init__(
        self,
        sources: Iterable[GovernedInformationSource] = (
            DEFAULT_GOVERNED_INFORMATION_SOURCES
        ),
    ) -> None:
        source_items = tuple(sources)
        indexed = {source.source_id.casefold(): source for source in source_items}
        if not indexed:
            raise ValueError("at least one governed information source is required")
        if len(indexed) != len(source_items):
            raise ValueError("information source ids must be unique")
        self._sources = indexed

    @property
    def snapshot(self) -> GovernedInformationSourcesSnapshot:
        return GovernedInformationSourcesSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            sources=tuple(self._sources.values()),
            network_enabled=False,
            automatic_fetch_enabled=False,
        )

    @property
    def sources(self) -> Mapping[str, GovernedInformationSource]:
        return MappingProxyType(self._sources)

    def source_for(self, source_id: str) -> GovernedInformationSource:
        try:
            return self._sources[source_id.strip().casefold()]
        except KeyError as exc:
            raise KeyError(f"unknown governed information source: {source_id}") from exc

    def admit_non_default(self, source: GovernedInformationSource) -> None:
        """Admit one explicit inactive source into this runtime registry only."""
        normalized_source_id = source.source_id.strip().casefold()
        existing = self._sources.get(normalized_source_id)
        if existing is not None:
            if existing != source:
                raise ValueError(
                    "governed information source id already has a declaration"
                )
            return
        self._sources[normalized_source_id] = source

    def classify(self, source_id: str) -> InformationSourceClassification:
        """Return the canonical classification owned by the existing registry."""
        return self.source_for(source_id).classification

    def accept(self, item: GovernedInformationItem) -> RelevanceCandidate:
        source = self.source_for(item.source_id)
        if source.status is not InformationSourceStatus.DECLARED:
            raise ValueError("information source is not declared for ingestion")
        if not item.topics.issubset(source.topics):
            raise ValueError("information item contains undeclared source topics")
        return RelevanceCandidate(
            title=item.title,
            topics=item.topics,
            location=item.location,
            is_free=item.is_free,
            time_sensitive=item.time_sensitive,
            importance=item.importance,
        )
