from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.governed_information_sources import (
    GovernedInformationSource,
    GovernedInformationSources,
    InformationAuthority,
    InformationCoverage,
    InformationEvidenceKind,
    InformationProvenance,
    InformationRegion,
    InformationSourceClassification,
    InformationSourceKind,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


def test_nasa_is_classified_as_primary_first_party_source() -> None:
    classification = GovernedInformationSources().classify("nasa")

    assert classification.authority is InformationAuthority.PRIMARY
    assert classification.provenance is InformationProvenance.FIRST_PARTY
    assert classification.confidence == 98
    assert InformationRegion.GLOBAL in classification.regions


def test_cultura_caba_is_local_public_institution() -> None:
    classification = GovernedInformationSources().classify("cultura_caba")

    assert classification.authority is InformationAuthority.INSTITUTIONAL
    assert classification.coverage is InformationCoverage.LOCAL
    assert classification.regions == frozenset(
        {InformationRegion.ARGENTINA, InformationRegion.CABA}
    )


def test_editorial_sources_remain_distinct_from_primary_sources() -> None:
    registry = GovernedInformationSources()

    technology = registry.classify("technology_editorial")
    sports = registry.classify("sports_editorial")

    assert technology.authority is InformationAuthority.SPECIALIZED
    assert sports.provenance is InformationProvenance.EDITORIAL_REVIEW
    assert technology.evidence is InformationEvidenceKind.EDITORIAL_REPORTING


def test_custom_audiovisual_source_uses_same_canonical_contract() -> None:
    audiovisual = GovernedInformationSource(
        source_id="audiovisual_official",
        name="Fuente audiovisual oficial",
        kind=InformationSourceKind.OFFICIAL,
        topics=frozenset(
            {
                InterestTopic.CINEMA,
                InterestTopic.SERIES,
                InterestTopic.RELEASES,
                InterestTopic.HARD_SCIENCE_FICTION,
            }
        ),
        classification=InformationSourceClassification(
            authority=InformationAuthority.PRIMARY,
            provenance=InformationProvenance.FIRST_PARTY,
            evidence=InformationEvidenceKind.OFFICIAL_ANNOUNCEMENT,
            coverage=InformationCoverage.GLOBAL,
            regions=frozenset(
                {InformationRegion.GLOBAL, InformationRegion.ARGENTINA}
            ),
            confidence=95,
        ),
    )

    classification = GovernedInformationSources((audiovisual,)).classify(
        "audiovisual_official"
    )

    assert classification.confidence == 95
    assert InformationRegion.ARGENTINA in classification.regions


def test_classification_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="between 0 and 100"):
        InformationSourceClassification(
            authority=InformationAuthority.GENERAL,
            provenance=InformationProvenance.AGGREGATED,
            evidence=InformationEvidenceKind.EDITORIAL_REPORTING,
            coverage=InformationCoverage.GLOBAL,
            regions=frozenset({InformationRegion.GLOBAL}),
            confidence=101,
        )


def test_classification_requires_geographic_scope() -> None:
    with pytest.raises(ValueError, match="needs a region"):
        InformationSourceClassification(
            authority=InformationAuthority.GENERAL,
            provenance=InformationProvenance.AGGREGATED,
            evidence=InformationEvidenceKind.EDITORIAL_REPORTING,
            coverage=InformationCoverage.GLOBAL,
            regions=frozenset(),
            confidence=50,
        )


def test_gateway_exposes_classification_through_single_registry() -> None:
    gateway = object.__new__(OfficialConversationGateway)

    class Runtime:
        pass

    OfficialConversationGateway.__init__(gateway, Runtime())

    assert gateway.classify_information_source("nasa").confidence == 98
    assert gateway.governed_information_sources.schema_version == "m343.5"


def test_m343_7_does_not_add_network_or_parallel_authorities() -> None:
    source = Path("app/governed_information_sources.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_roots.isdisjoint(
        {"asyncio", "requests", "socket", "subprocess", "threading", "urllib"}
    )
    assert "class SourceClassifier" not in source
    assert "class GovernedInformationSources" in source
