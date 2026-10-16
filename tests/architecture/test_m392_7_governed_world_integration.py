from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.governed_context_representation import ContextRepresentationStatus
from core.governed_world_integration import (
    GovernedWorldIntegrationSnapshot,
    WorldIntegrationStatus,
)

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


def _snapshot() -> GovernedWorldIntegrationSnapshot:
    return InternalWorldModelFoundation().integrated_world(*_domains())


def test_m392_7_integrates_six_governed_domains() -> None:
    snapshot = _snapshot()
    assert snapshot.schema_version == "m392.7"
    assert len(snapshot.evidence_codes) == 8


def test_m392_7_preserves_internal_world_authority() -> None:
    assert _snapshot().canonical_authority == "internal_world_model"


def test_m392_7_preserves_domain_instances() -> None:
    domains = _domains()
    snapshot = InternalWorldModelFoundation().integrated_world(*domains)
    assert snapshot.household is domains[0]
    assert snapshot.people is domains[1]
    assert snapshot.places is domains[2]
    assert snapshot.objects is domains[3]
    assert snapshot.timeline is domains[4]
    assert snapshot.context is domains[5]


def test_m392_7_empty_domains_produce_empty_world() -> None:
    assert _snapshot().status is WorldIntegrationStatus.EMPTY


def test_m392_7_propagates_review_required() -> None:
    domains = list(_domains())
    domains[5] = replace(
        domains[5],
        status=ContextRepresentationStatus.REVIEW_REQUIRED,
        risk_codes=("explicit-review",),
    )
    snapshot = InternalWorldModelFoundation().integrated_world(*domains)
    assert snapshot.status is WorldIntegrationStatus.REVIEW_REQUIRED
    assert "domain_review_required:context" in snapshot.risk_codes


def test_m392_7_does_not_copy_domain_risk_codes() -> None:
    domains = list(_domains())
    domains[5] = replace(
        domains[5],
        status=ContextRepresentationStatus.REVIEW_REQUIRED,
        risk_codes=("source-specific-risk",),
    )
    snapshot = InternalWorldModelFoundation().integrated_world(*domains)
    assert "source-specific-risk" not in snapshot.risk_codes
    assert domains[5].risk_codes == ("source-specific-risk",)


def test_m392_7_is_deterministic() -> None:
    domains = _domains()
    foundation = InternalWorldModelFoundation()
    first = foundation.integrated_world(*domains)
    second = foundation.integrated_world(*domains)
    assert first == second


def test_m392_7_snapshot_is_immutable() -> None:
    snapshot = _snapshot()
    with pytest.raises(FrozenInstanceError):
        snapshot.status = WorldIntegrationStatus.COMPLETE  # type: ignore[misc]


def test_m392_7_is_read_only_and_non_operational() -> None:
    snapshot = _snapshot()
    assert snapshot.read_only is True
    assert snapshot.persistence_added is False
    assert snapshot.inference_added is False
    assert snapshot.source_data_modified is False
    assert snapshot.authority_added is False
    assert snapshot.automation_added is False
    assert snapshot.runtime_behavior_changed is False
    assert snapshot.starts_background_process is False


def test_m392_7_source_domains_reject_parallel_authority() -> None:
    household = _domains()[0]
    with pytest.raises(ValueError, match="preserve world authority"):
        replace(household, canonical_authority="parallel_world")


def test_m392_7_preserves_canonical_core_position() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [
        index + 1
        for index, line in enumerate(lines)
        if "CanonicalCognitiveCore(" in line
    ]
    assert hits == [52]


def test_m392_7_does_not_reference_private_credentials() -> None:
    paths = (
        ROOT / "core" / "governed_world_integration.py",
        ROOT / "app" / "internal_world_model_foundation.py",
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "credentials.json" not in text


def test_m392_7_documentation_exists() -> None:
    path = ROOT / "docs" / "M392_7_GOVERNED_WORLD_INTEGRATION.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "internal_world_model" in text
    assert "no crea" in text.casefold()
