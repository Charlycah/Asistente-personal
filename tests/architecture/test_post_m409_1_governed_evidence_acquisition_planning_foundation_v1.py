from __future__ import annotations

import ast
import inspect
from dataclasses import fields

from app.planning_foundation import PlanningFoundation
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityRegistryManager,
    CapabilityRisk,
    PermissionScope,
)
from core.evidence_acquisition_planning import (
    EvidenceAcquisitionPlanningReport,
    EvidenceAcquisitionPlanningStatus,
    GovernedEvidenceAcquisitionPlanner,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


def _requirement(
    *missing: str,
) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-1234567890abcdef",
        hypothesis_ids=("h1", "h2"),
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        known_elements=("fact-shared",),
        missing_evidence_descriptions=missing,
        evidence_codes=("comparison:indistinguishable",),
    )


def _registry(*descriptors: CapabilityDescriptor) -> CapabilityRegistryManager:
    manager = CapabilityRegistryManager()
    for descriptor in descriptors:
        manager.register(descriptor)
    return manager


def _descriptor(
    name: str,
    *outputs: str,
    enabled: bool = True,
    scope: PermissionScope = PermissionScope.READ,
) -> CapabilityDescriptor:
    return CapabilityDescriptor(
        name=name,
        description=f"Capability {name}",
        kind=CapabilityKind.GENERIC,
        risk=CapabilityRisk.LOW,
        permission_scope=scope,
        enabled=enabled,
        evidence_outputs=outputs,
    )


def test_explicit_evidence_output_makes_requirement_plannable() -> None:
    evidence = "current heating-system state"
    planner = GovernedEvidenceAcquisitionPlanner(
        _registry(_descriptor("home.heating.read", evidence))
    )

    result = planner.plan(_requirement(evidence))

    assert result.status is EvidenceAcquisitionPlanningStatus.PLANNABLE
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.capability_name == "home.heating.read"
    assert candidate.declared_evidence_output == evidence
    assert not candidate.selected_for_execution
    assert not candidate.executed


def test_no_explicit_capability_match_fails_closed() -> None:
    planner = GovernedEvidenceAcquisitionPlanner(
        _registry(_descriptor("weather.read", "current outdoor temperature"))
    )

    result = planner.plan(_requirement("current heating-system state"))

    assert (
        result.status
        is EvidenceAcquisitionPlanningStatus.NO_CAPABILITY_AVAILABLE
    )
    assert result.candidates == ()
    assert result.unmatched_evidence_descriptions == (
        "current heating-system state",
    )


def test_multiple_explicit_sources_remain_ambiguous() -> None:
    evidence = "current room temperature"
    planner = GovernedEvidenceAcquisitionPlanner(
        _registry(
            _descriptor("sensor.room_temperature", evidence),
            _descriptor("human.room_temperature", evidence),
        )
    )

    result = planner.plan(_requirement(evidence))

    assert result.status is EvidenceAcquisitionPlanningStatus.AMBIGUOUS
    assert tuple(item.capability_name for item in result.candidates) == (
        "human.room_temperature",
        "sensor.room_temperature",
    )
    assert result.ambiguous_evidence_descriptions == (evidence,)


def test_partial_match_is_visible_without_inventing_missing_capability() -> None:
    planner = GovernedEvidenceAcquisitionPlanner(
        _registry(_descriptor("home.window.read", "current window state"))
    )

    result = planner.plan(
        _requirement("current window state", "current heating-system state")
    )

    assert result.status is EvidenceAcquisitionPlanningStatus.PARTIALLY_PLANNABLE
    assert len(result.candidates) == 1
    assert result.unmatched_evidence_descriptions == (
        "current heating-system state",
    )


def test_disabled_capability_is_not_plannable() -> None:
    evidence = "current room temperature"
    planner = GovernedEvidenceAcquisitionPlanner(
        _registry(_descriptor("sensor.room_temperature", evidence, enabled=False))
    )

    result = planner.plan(_requirement(evidence))

    assert (
        result.status
        is EvidenceAcquisitionPlanningStatus.NO_CAPABILITY_AVAILABLE
    )
    assert result.candidates == ()


def test_plan_preserves_requirement_lineage_exactly() -> None:
    evidence = "current heating-system state"
    requirement = _requirement(evidence)
    result = GovernedEvidenceAcquisitionPlanner(
        _registry(_descriptor("home.heating.read", evidence))
    ).plan(requirement)

    assert result.requirement_id == requirement.requirement_id
    assert result.hypothesis_ids == requirement.hypothesis_ids
    assert result.source_reference == requirement.source_reference
    assert result.world_snapshot_id == requirement.world_snapshot_id


def test_planning_reuses_existing_authorities_and_never_executes() -> None:
    defaults = {
        field.name: field.default
        for field in fields(EvidenceAcquisitionPlanningReport)
    }
    assert defaults["canonical_authority"] == "planning_foundation"
    assert defaults["planning_execution_authorized"] is False
    assert defaults["creates_questions"] is False
    assert defaults["acquires_evidence"] is False
    assert defaults["invokes_capabilities"] is False
    assert defaults["executes_actions"] is False
    assert PlanningFoundation().snapshot.planning_execution_authorized is False


def test_planner_has_no_operational_or_curiosity_bypass() -> None:
    source = inspect.getsource(GovernedEvidenceAcquisitionPlanner)
    tree = ast.parse(source)
    for forbidden in (
        "OfficialConversationGateway",
        "OfficialMemoryGateway",
        "Curiosity",
        "Android",
        "requests.",
        "socket.",
        "subprocess.",
        ".execute(",
        ".intercept(",
    ):
        assert forbidden not in source
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name
            in {"execute", "acquire", "ask", "persist", "learn", "emit"}
        )
        for node in ast.walk(tree)
    )


def test_official_runtime_registry_preserves_explicit_evidence_outputs() -> None:
    from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry

    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="home.heating.read",
        description="Read current heating state",
        interceptor=object(),
        evidence_outputs=("current heating-system state",),
    )

    registration = registry.registration_for("home.heating.read")
    assert registration is not None
    assert registration.descriptor.evidence_outputs == (
        "current heating-system state",
    )
