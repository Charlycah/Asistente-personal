from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol

from core.document_extraction import StructuredDocument


@dataclass(frozen=True)
class WebEnrichmentRequest:
    document: StructuredDocument
    explicit_user_consent: bool = False
    user_requested: bool = True
    allowed_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        fields = tuple(item.strip() for item in self.allowed_fields if item.strip())
        if len(fields) != len(set(fields)):
            raise ValueError("web enrichment allowed fields must be unique")
        object.__setattr__(self, "allowed_fields", fields)


@dataclass(frozen=True)
class EnrichmentSource:
    title: str
    provider: str
    url: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.provider.strip():
            raise ValueError("enrichment source title and provider are required")
        if self.url is not None and not self.url.strip():
            raise ValueError("enrichment source URL must not be blank")


@dataclass(frozen=True)
class EnrichmentFinding:
    key: str
    value: str
    confidence: float
    source_indexes: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if not self.key.strip() or not self.value.strip():
            raise ValueError("enrichment finding key and value are required")
        if not 0 <= self.confidence <= 1:
            raise ValueError("enrichment confidence must be between zero and one")
        if any(index < 0 for index in self.source_indexes):
            raise ValueError("enrichment source indexes must not be negative")


@dataclass(frozen=True)
class WebEnrichmentResult:
    query_fields: Mapping[str, str]
    findings: tuple[EnrichmentFinding, ...]
    sources: tuple[EnrichmentSource, ...]
    provider_name: str
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.provider_name.strip():
            raise ValueError("web enrichment provider name is required")
        if any(
            index >= len(self.sources)
            for item in self.findings
            for index in item.source_indexes
        ):
            raise ValueError("enrichment finding references an unknown source")


class WebEnrichmentProvider(Protocol):
    def enrich(self, fields: Mapping[str, str]) -> WebEnrichmentResult:
        """Return passive external information without executing side effects."""
