from __future__ import annotations

import ast
import inspect
from dataclasses import fields

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumption,
    GovernedEvidenceAcquisitionProductiveConsumptionV1,
)
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityRegistryManager,
)
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


def _requirement(
    missing: tuple[str, ...],
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


def _registry(
    *descriptors: CapabilityDescriptor,
) -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    for descriptor in descriptors:
        registry.register(descriptor)
    return registry


def _capability(
    name: str,
    *outputs: str,
) -> CapabilityDescriptor:
    return CapabilityDescriptor(
        name=name,
        description=f"Evidence provider {name}",
        evidence_outputs=outputs,
    )


def test_plannable_single_candidate_is_exposed_but_not_selected() -> None:
    registry = _registry(_capability("sensor.read", "room temperature"))
    result = GovernedEvidenceAcquisitionProductiveConsumptionV1(
        registry
    ).consume(_requirement(("room temperature",)))

    assert result.status is EvidenceAcquisitionPlanningStatus.PLANNABLE
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.capability_name == "sensor.read"
    assert not candidate.selected_for_execution
    assert not candidate.authorized_for_execution
    assert not candidate.executed
    assert not result.planning_execution_authorized
    assert not result.selects_capability
    assert not result.invokes_capabilities


def test_multiple_explicit_candidates_remain_ambiguous_and_unselected() -> None:
    registry = _registry(
        _capability("sensor.a", "room temperature"),
        _capability("sensor.b", "room temperature"),
    )
    result = GovernedEvidenceAcquisitionProductiveConsumptionV1(
        registry
    ).consume(_requirement(("room temperature",)))

    assert result.status is EvidenceAcquisitionPlanningStatus.AMBIGUOUS
    assert {item.capability_name for item in result.candidates} == {
        "sensor.a",
        "sensor.b",
    }
    assert all(not item.selected_for_execution for item in result.candidates)
    assert result.ambiguous_evidence_descriptions == ("room temperature",)


def test_partially_plannable_preserves_covered_and_unmatched_evidence() -> None:
    registry = _registry(_capability("sensor.read", "room temperature"))
    result = GovernedEvidenceAcquisitionProductiveConsumptionV1(
        registry
    ).consume(
        _requirement(("room temperature", "heating system state"))
    )

    assert result.status is EvidenceAcquisitionPlanningStatus.PARTIALLY_PLANNABLE
    assert len(result.candidates) == 1
    assert result.unmatched_evidence_descriptions == ("heating system state",)
    assert not result.planning_execution_authorized


def test_no_capability_available_fails_closed() -> None:
    result = GovernedEvidenceAcquisitionProductiveConsumptionV1(
        _registry()
    ).consume(_requirement(("unknown evidence",)))

    assert result.status is EvidenceAcquisitionPlanningStatus.NO_CAPABILITY_AVAILABLE
    assert result.candidates == ()
    assert result.unmatched_evidence_descriptions == ("unknown evidence",)
    assert not result.invokes_capabilities
    assert not result.acquires_evidence


def test_productive_consumption_preserves_exact_requirement_lineage() -> None:
    requirement = _requirement(("room temperature",))
    result = GovernedEvidenceAcquisitionProductiveConsumptionV1(
        _registry(_capability("sensor.read", "room temperature"))
    ).consume(requirement)

    assert result.requirement_id == requirement.requirement_id
    assert result.source_reference == requirement.source_reference
    assert result.world_snapshot_id == requirement.world_snapshot_id
    assert result.planning_report.requirement_id == requirement.requirement_id


def test_only_explicit_evidence_outputs_can_produce_candidates() -> None:
    registry = _registry(
        CapabilityDescriptor(
            name="room-temperature-reader",
            description="Reads room temperature",
            tags=("room temperature",),
            semantic_triggers=("room temperature",),
            evidence_outputs=(),
        )
    )
    result = GovernedEvidenceAcquisitionProductiveConsumptionV1(
        registry
    ).consume(_requirement(("room temperature",)))

    assert result.status is EvidenceAcquisitionPlanningStatus.NO_CAPABILITY_AVAILABLE
    assert result.candidates == ()


def test_productive_consumption_does_not_mutate_registry() -> None:
    registry = _registry(_capability("sensor.read", "room temperature"))
    before = registry.capabilities.copy()

    GovernedEvidenceAcquisitionProductiveConsumptionV1(registry).consume(
        _requirement(("room temperature",))
    )

    assert registry.capabilities == before


def test_productive_contract_is_non_executive_and_has_no_bypass() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedEvidenceAcquisitionProductiveConsumption)
    }
    for field_name in (
        "planning_execution_authorized",
        "selects_capability",
        "invokes_capabilities",
        "acquires_evidence",
        "creates_questions",
        "modifies_registry",
        "modifies_memory",
        "modifies_world_model",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[field_name] is False

    source = inspect.getsource(
        GovernedEvidenceAcquisitionProductiveConsumptionV1
    )
    tree = ast.parse(source)
    for forbidden in (
        "OfficialCapabilityGateway",
        "OfficialConversationGateway",
        "OfficialMemoryGateway",
        "GovernedEpistemicCuriosity",
        "requests.",
        "socket.",
        "subprocess.",
    ):
        assert forbidden not in source
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name
            in {"execute", "acquire", "emit", "remember", "persist", "select"}
        )
        for node in ast.walk(tree)
    )
