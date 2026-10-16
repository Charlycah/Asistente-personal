from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.governed_context_representation import ContextRepresentationStatus
from core.governed_world_stabilization import WorldStabilizationStatus

ROOT = Path(__file__).resolve().parents[2]


def _domains():
    foundation = InternalWorldModelFoundation()
    return (
        foundation.household_representation(),
        foundation.people_representation(),
        foundation.places_representation(),
        foundation.objects_representation(),
        foundation.timeline_representation(),
        foundation.context_representation(),
    )


def _snapshot():
    return InternalWorldModelFoundation().integrated_world(*_domains())


def _report():
    return InternalWorldModelFoundation().stabilize_integrated_world(_snapshot())


def test_m392_8_audits_integrated_world() -> None:
    report = _report()
    assert report.schema_version == "m392.8"
    assert report.status is WorldStabilizationStatus.STABLE


def test_m392_8_preserves_internal_world_authority() -> None:
    assert _report().canonical_authority == "internal_world_model"


def test_m392_8_checks_all_six_domains() -> None:
    assert _report().checked_domains == (
        "household",
        "people",
        "places",
        "objects",
        "timeline",
        "context",
    )


def test_m392_8_preserves_integration_fingerprint() -> None:
    snapshot = _snapshot()
    report = InternalWorldModelFoundation().stabilize_integrated_world(snapshot)
    assert report.integration_fingerprint == snapshot.source_fingerprint


def test_m392_8_preserves_review_required() -> None:
    domains = list(_domains())
    domains[5] = replace(
        domains[5],
        status=ContextRepresentationStatus.REVIEW_REQUIRED,
        risk_codes=("explicit-review",),
    )
    snapshot = InternalWorldModelFoundation().integrated_world(*domains)
    report = InternalWorldModelFoundation().stabilize_integrated_world(snapshot)
    assert report.status is WorldStabilizationStatus.REVIEW_REQUIRED
    assert "domain_review_required:context" in report.risk_codes


def test_m392_8_detects_integration_schema_mismatch() -> None:
    snapshot = replace(_snapshot(), schema_version="m392.invalid")
    report = InternalWorldModelFoundation().stabilize_integrated_world(snapshot)
    assert "integration_schema_mismatch" in report.risk_codes


def test_m392_8_detects_domain_schema_mismatch() -> None:
    snapshot = _snapshot()
    household = replace(snapshot.household, schema_version="m392.invalid")
    snapshot = replace(snapshot, household=household)
    report = InternalWorldModelFoundation().stabilize_integrated_world(snapshot)
    assert "domain_schema_mismatch:household" in report.risk_codes


def test_m392_8_is_deterministic() -> None:
    foundation = InternalWorldModelFoundation()
    snapshot = _snapshot()
    assert foundation.stabilize_integrated_world(snapshot) == (
        foundation.stabilize_integrated_world(snapshot)
    )


def test_m392_8_report_is_immutable() -> None:
    report = _report()
    with pytest.raises(FrozenInstanceError):
        report.status = WorldStabilizationStatus.REVIEW_REQUIRED  # type: ignore[misc]


def test_m392_8_is_read_only_and_non_operational() -> None:
    report = _report()
    assert report.read_only is True
    assert report.persistence_added is False
    assert report.inference_added is False
    assert report.source_data_modified is False
    assert report.authority_added is False
    assert report.automation_added is False
    assert report.runtime_behavior_changed is False
    assert report.starts_background_process is False


def test_m392_8_does_not_modify_snapshot() -> None:
    snapshot = _snapshot()
    before = snapshot
    InternalWorldModelFoundation().stabilize_integrated_world(snapshot)
    assert snapshot == before


def test_m392_8_evidence_declares_full_lineage() -> None:
    evidence = _report().evidence_codes
    for version in ("m392.1", "m392.2", "m392.3", "m392.4", "m392.5", "m392.6"):
        assert any(version in code for code in evidence)
    assert "integration:m392.7" in evidence


def test_m392_8_preserves_canonical_core_position() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [
        index + 1
        for index, line in enumerate(lines)
        if "CanonicalCognitiveCore(" in line
    ]
    assert hits == [52]


def test_m392_8_does_not_reference_private_credentials() -> None:
    paths = (
        ROOT / "core" / "governed_world_stabilization.py",
        ROOT / "app" / "internal_world_model_foundation.py",
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "credentials.json" not in text


def test_m392_8_documentation_exists() -> None:
    path = ROOT / "docs" / "M392_8_WORLD_MODEL_STABILIZATION.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "internal_world_model" in text
    assert "no crea" in text.casefold()
