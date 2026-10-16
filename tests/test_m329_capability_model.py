from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    CapabilityAvailability,
    CapabilityDefinition,
    JsonCapabilityModel,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 28, 0, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl"
    )


def test_default_capability_model_is_persistent_and_descriptive(tmp_path):
    runtime = _runtime(tmp_path)

    snapshot = runtime.capabilities()

    assert {item.capability_id for item in snapshot.capabilities} == {
        "diagnose_audio_runtime",
        "verify_component_health",
    }
    assert runtime.snapshot.capability_count == 2
    assert runtime.snapshot.enabled_capability_count == 2
    assert runtime.snapshot.autonomous_cycle_count == 0


def test_registered_capability_survives_restart(tmp_path):
    runtime = _runtime(tmp_path)
    capability = CapabilityDefinition(
        capability_id="collect_runtime_evidence",
        description="Collect read-only runtime evidence.",
        risk="low",
        reversible=True,
        authorization_required=False,
        dependencies=("verify_component_health",),
        tags=("diagnostic",),
    )

    runtime.register_capability(capability)
    restored = _runtime(tmp_path)

    assert restored.capabilities().get(capability.capability_id) == capability


def test_capability_assessment_reports_availability(tmp_path):
    runtime = _runtime(tmp_path)

    assessment = runtime.assess_capability("verify_component_health")

    assert assessment.available
    assert assessment.availability is CapabilityAvailability.AVAILABLE
    assert assessment.risk == "low"
    assert assessment.reversible is True


def test_disabled_dependency_blocks_capability(tmp_path):
    model = JsonCapabilityModel(tmp_path / "capabilities.json")
    model.register(
        CapabilityDefinition(
            capability_id="base",
            description="Disabled base.",
            risk="low",
            reversible=True,
            authorization_required=False,
            enabled=False,
        )
    )
    model.register(
        CapabilityDefinition(
            capability_id="dependent",
            description="Depends on base.",
            risk="medium",
            reversible=True,
            authorization_required=True,
            dependencies=("base",),
        )
    )

    assessment = model.assess("dependent")

    assert assessment.availability is CapabilityAvailability.MISSING_DEPENDENCY
    assert assessment.missing_dependencies == ("base",)


def test_unknown_capability_is_explicit_not_invented(tmp_path):
    runtime = _runtime(tmp_path)

    assessment = runtime.assess_capability("repair_everything")

    assert assessment.availability is CapabilityAvailability.UNKNOWN
    assert not assessment.available
    assert assessment.reasons == ("capability_not_registered",)


def test_capability_model_rejects_duplicate_and_corrupt_data(tmp_path):
    runtime = _runtime(tmp_path)
    duplicate = runtime.capabilities().get("verify_component_health")
    assert duplicate is not None

    with pytest.raises(ValueError, match="duplicate capability id"):
        runtime.register_capability(duplicate)

    path = tmp_path / "broken.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid capability model file"):
        JsonCapabilityModel(path)
