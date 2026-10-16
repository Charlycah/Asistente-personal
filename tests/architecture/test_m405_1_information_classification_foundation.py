from __future__ import annotations

from pathlib import Path

import pytest

from domain.information_classification import InformationClassification


def test_m405_1_taxonomy_is_exactly_the_canonical_five_values() -> None:
    assert tuple(InformationClassification) == (
        InformationClassification.UNCLASSIFIED,
        InformationClassification.PUBLIC,
        InformationClassification.PERSONAL,
        InformationClassification.PRIVATE,
        InformationClassification.SENSITIVE,
    )


def test_m405_1_taxonomy_is_nominal_not_numeric_or_ordered() -> None:
    assert InformationClassification.PUBLIC.value == "public"
    assert not isinstance(InformationClassification.PUBLIC.value, int)
    with pytest.raises(TypeError):
        _ = InformationClassification.PUBLIC < InformationClassification.PRIVATE


def test_m405_1_foundation_adds_no_global_classifier_authority() -> None:
    root = Path(__file__).resolve().parents[2]
    taxonomy = (root / "domain/information_classification.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "InformationClassificationAuthority",
        "PrivacyManager",
        "GlobalClassifier",
        "ClassificationRegistry",
        "Classified[",
    )
    assert all(token not in taxonomy for token in forbidden)


def test_m405_1_documentation_remains_historical_trace() -> None:
    root = Path(__file__).resolve().parents[2]
    document = (
        root / "docs/M405_1_INFORMATION_CLASSIFICATION_FOUNDATION.md"
    ).read_text(encoding="utf-8")
    assert "M405.1" in document
    assert "UNCLASSIFIED" in document
