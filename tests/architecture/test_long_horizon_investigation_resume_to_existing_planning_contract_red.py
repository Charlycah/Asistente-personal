from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumptionV1,
)
from app.governed_long_horizon_investigation_resume_admission import (
    GovernedInvestigationResumeAdmission,
    GovernedInvestigationResumeAdmissionStatus,
)
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityRegistryManager,
    CapabilityRisk,
    PermissionScope,
)
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus

EXPECTED_MODULE = "app.governed_long_horizon_investigation_evidence_planning"


def _load_contract():
    spec = importlib.util.find_spec(EXPECTED_MODULE)
    assert spec is not None, "RED: planning bridge missing"
    module = importlib.import_module(EXPECTED_MODULE)
    return (
        module.GovernedInvestigationEvidencePlanningStatus,
        module.GovernedInvestigationEvidencePlanningResult,
        module.GovernedLongHorizonInvestigationEvidencePlanningV1,
    )


def test_red_bridge_module_and_minimal_public_contract_exist():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None
    assert hasattr(bridge, "consume")


def test_red_bridge_delegates_to_existing_planning_owner_not_step_two_reentry():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedEvidenceAcquisitionProductiveConsumptionV1" in source
    assert "GovernedMultiStepInvestigationPlanningReentryV1" not in source
    assert "planning_foundation" in inspect.getsource(inspect.getmodule(bridge))


def test_red_only_admitted_resume_can_invoke_planning():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert "GovernedInvestigationResumeAdmissionStatus.ADMITTED" in source
    assert "eligible_for_existing_planning" in source


def test_red_exact_requirement_object_is_forwarded_without_reconstruction():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    tree = ast.parse(source)
    assert ".requirement" in source
    assert "DiscriminatingEvidenceRequirement(" not in source
    assert all(
        not (
            isinstance(node, ast.Call)
            and getattr(node.func, "id", "") == "DiscriminatingEvidenceRequirement"
        )
        for node in ast.walk(tree)
    )


def test_red_planning_is_called_at_most_once_and_never_authorizes_or_executes():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    assert source.count(".consume(") <= 1
    for forbidden in (
        "GovernedMultiStepInvestigationAuthorizationReentryV1",
        ".authorize(",
        ".execute(",
        "OfficialMemoryGateway",
        "OfficialWorldModel",
    ):
        assert forbidden not in source


def test_red_existing_planning_status_controls_authorization_eligibility():
    status, result, _ = _load_contract()
    result_source = inspect.getsource(result)
    assert "eligible_for_authorization" in result_source
    assert "EvidenceAcquisitionPlanningStatus.PLANNABLE" in result_source
    assert hasattr(status, "PLANNED")
    assert hasattr(status, "NOT_ELIGIBLE")
    assert hasattr(status, "REVIEW_REQUIRED")


def test_red_existing_productive_planning_surface_remains_canonical():
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name="sensor.room_temperature",
            description="Read room temperature",
            kind=CapabilityKind.GENERIC,
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.READ,
            enabled=True,
            evidence_outputs=("current room temperature",),
        )
    )
    surface = GovernedEvidenceAcquisitionProductiveConsumptionV1(registry)
    assert surface._planner.CANONICAL_AUTHORITY == "planning_foundation"
    assert EvidenceAcquisitionPlanningStatus.PLANNABLE.value == "plannable"
    assert GovernedInvestigationResumeAdmissionStatus.ADMITTED.value == "admitted"
    assert (
        GovernedInvestigationResumeAdmission.__dataclass_fields__[
            "canonical_planning_authority"
        ].default
        == "planning_foundation"
    )
