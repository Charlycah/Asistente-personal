from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timezone
from importlib import import_module

from app.official_runtime_composition import (
    OfficialROBYRuntime,
    OfficialRuntimeComposition,
)
from app.runtime_capability_graph import RuntimeCapabilityGraph, RuntimeCapabilityNode
from app.runtime_health_readiness import (
    RuntimeCapabilityAvailability,
    RuntimeCapabilityReadiness,
    RuntimeCapabilityRequirement,
    RuntimeHealthReadinessReport,
    RuntimeReadinessLevel,
)
from app.runtime_operational_snapshot import RuntimeOperationalHealth
from core.cognitive_maturity.current_registry_resolution_path_availability import (
    CurrentRegistryResolutionPathAvailabilityObservation,
    CurrentRegistryResolutionPathAvailabilityReport,
    CurrentRegistryResolutionPathAvailabilityStatus,
)
from core.cognitive_maturity.epistemic_resolution_binding import (
    EpistemicResolutionBinding,
)
from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
)

MODULE = "core.cognitive_maturity.canonical_runtime_readiness_projection"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY
NOW = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


def _contract():
    return import_module(MODULE)


def _binding(name: str, output: str) -> EpistemicResolutionBinding:
    return EpistemicResolutionBinding(
        capability_name=name,
        declared_evidence_output=output,
        epistemic_need_identity=IDENTITY,
        epistemic_need_source_reference="inner-continuity-report-123",
        epistemic_need_lineage_kind="explicit_inner_continuity_gap",
        provenance_authority="governed_explicit_epistemic_resolution_declaration",
        evidence_codes=("explicit_epistemic_resolution_binding",),
    )


def _registry_report(*observations):
    return CurrentRegistryResolutionPathAvailabilityReport(
        assessment_id="epistemic-sufficiency-1234567890abcdef",
        requirement_id="discrimination-requirement-1234567890abcdef",
        epistemic_need_identity=IDENTITY,
        reasoning_source_reference="scenario-123",
        world_snapshot_id="world-1",
        self_gap_source_reference="inner-continuity-report-123",
        self_gap_lineage_kind="explicit_inner_continuity_gap",
        observations=tuple(observations),
    )


def _observation(name, output, status):
    return CurrentRegistryResolutionPathAvailabilityObservation(
        binding=_binding(name, output),
        status=status,
    )


def _runtime(graph: RuntimeCapabilityGraph | None) -> OfficialROBYRuntime:
    composition = OfficialRuntimeComposition(
        conversation=object(),
        bootstrap=object(),
        root=object(),
        lifecycle=object(),
        supervisor=object(),
    )
    return OfficialROBYRuntime(composition, capability_graph=graph)


def _graph(*capability_ids: str) -> RuntimeCapabilityGraph:
    return RuntimeCapabilityGraph(
        RuntimeCapabilityNode(RuntimeCapabilityRequirement(capability_id))
        for capability_id in capability_ids
    )


def _readiness(capability_id, availability):
    ready = availability in {
        RuntimeCapabilityAvailability.AVAILABLE,
        RuntimeCapabilityAvailability.DEGRADED,
    }
    return RuntimeCapabilityReadiness(
        capability_id=capability_id,
        availability=availability,
        ready=ready,
        degraded=availability is RuntimeCapabilityAvailability.DEGRADED,
        blockers=("fixture:blocker",) if not ready else (),
        warnings=("fixture:warning",)
        if availability is RuntimeCapabilityAvailability.DEGRADED
        else (),
        required_residents=("resident.required",),
        optional_residents=("resident.optional",),
        description="Canonical fixture readiness.",
    )


def _readiness_report(*items):
    return RuntimeHealthReadinessReport(
        evaluated_at=NOW,
        snapshot_generated_at=NOW,
        level=RuntimeReadinessLevel.READY,
        health=RuntimeOperationalHealth.HEALTHY,
        ready=True,
        degraded=False,
        blocked=False,
        runtime_available=True,
        blockers=(),
        warnings=(),
        capabilities=tuple(items),
    )


def _project(contract, registry_report, runtime):
    return contract.CanonicalRuntimeReadinessProjector().project(
        registry_report,
        runtime,
    )


def test_r1_missing_canonical_graph_is_not_provisioned() -> None:
    contract = _contract()
    observation = _observation(
        "fixture.alpha",
        "fixture.alpha_output",
        CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE,
    )

    result = _project(contract, _registry_report(observation), _runtime(None))

    assert result.observations[0].registry_observation == observation
    assert result.observations[0].status.value == "readiness_not_provisioned"
    assert result.observations[0].runtime_readiness is None


def test_r2_missing_exact_runtime_node_is_not_declared() -> None:
    contract = _contract()
    observation = _observation(
        "fixture.alpha",
        "fixture.alpha_output",
        CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE,
    )
    runtime = _runtime(_graph("fixture.beta"))

    result = _project(contract, _registry_report(observation), runtime)

    assert result.observations[0].registry_observation == observation
    assert result.observations[0].status.value == "readiness_not_declared"
    assert result.observations[0].runtime_readiness is None


def test_r3_canonical_unknown_remains_unknown(monkeypatch) -> None:
    contract = _contract()
    observation = _observation(
        "fixture.alpha",
        "fixture.alpha_output",
        CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE,
    )
    runtime = _runtime(_graph("fixture.alpha"))
    readiness = _readiness("fixture.alpha", RuntimeCapabilityAvailability.UNKNOWN)
    report = _readiness_report(readiness)
    monkeypatch.setattr(runtime, "readiness_graph", lambda graph: report)

    result = _project(contract, _registry_report(observation), runtime)

    projected = result.observations[0]
    assert projected.status.value == "unknown"
    assert projected.runtime_readiness == readiness


def test_r4_available_degraded_unavailable_are_preserved(monkeypatch) -> None:
    contract = _contract()
    statuses = (
        RuntimeCapabilityAvailability.AVAILABLE,
        RuntimeCapabilityAvailability.DEGRADED,
        RuntimeCapabilityAvailability.UNAVAILABLE,
    )
    names = ("fixture.alpha", "fixture.beta", "fixture.gamma")
    observations = tuple(
        _observation(
            name,
            f"{name}_output",
            CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE,
        )
        for name in names
    )
    runtime = _runtime(_graph(*names))
    readiness = tuple(_readiness(name, status) for name, status in zip(names, statuses))
    report = _readiness_report(*readiness)
    monkeypatch.setattr(runtime, "readiness_graph", lambda graph: report)

    result = _project(contract, _registry_report(*observations), runtime)

    assert tuple(item.status.value for item in result.observations) == (
        "available",
        "degraded",
        "unavailable",
    )
    assert tuple(item.runtime_readiness for item in result.observations) == readiness


def test_r5_runtime_readiness_is_for_c_and_preserves_c_d_binding(monkeypatch) -> None:
    contract = _contract()
    observation = _observation(
        "fixture.alpha",
        "fixture.precise_evidence_output",
        CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE,
    )
    runtime = _runtime(_graph("fixture.alpha"))
    readiness = _readiness("fixture.alpha", RuntimeCapabilityAvailability.AVAILABLE)
    monkeypatch.setattr(
        runtime,
        "readiness_graph",
        lambda graph: _readiness_report(readiness),
    )

    result = _project(contract, _registry_report(observation), runtime)

    projected = result.observations[0]
    assert projected.registry_observation.binding == observation.binding
    assert projected.runtime_readiness.capability_id == "fixture.alpha"
    assert projected.registry_observation.binding.declared_evidence_output == (
        "fixture.precise_evidence_output"
    )


def test_r6_non_registry_available_paths_are_preserved_without_promotion() -> None:
    contract = _contract()
    statuses = (
        CurrentRegistryResolutionPathAvailabilityStatus.NOT_REGISTERED,
        CurrentRegistryResolutionPathAvailabilityStatus.EVIDENCE_DECLARATION_MISMATCH,
        CurrentRegistryResolutionPathAvailabilityStatus.DISABLED,
    )
    observations = tuple(
        _observation(f"fixture.{index}", f"fixture.output.{index}", status)
        for index, status in enumerate(statuses)
    )
    runtime = _runtime(_graph("fixture.0", "fixture.1", "fixture.2"))

    result = _project(contract, _registry_report(*observations), runtime)

    assert tuple(
        item.registry_observation for item in result.observations
    ) == observations
    assert all(item.status is None for item in result.observations)
    assert all(item.runtime_readiness is None for item in result.observations)


def test_r7_anchor_order_and_canonical_readiness_evidence_are_preserved(
    monkeypatch,
) -> None:
    contract = _contract()
    first = _observation(
        "fixture.beta",
        "fixture.beta_output",
        CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE,
    )
    second = _observation(
        "fixture.alpha",
        "fixture.alpha_output",
        CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE,
    )
    runtime = _runtime(_graph("fixture.alpha", "fixture.beta"))
    beta = _readiness("fixture.beta", RuntimeCapabilityAvailability.DEGRADED)
    alpha = _readiness("fixture.alpha", RuntimeCapabilityAvailability.AVAILABLE)
    monkeypatch.setattr(
        runtime,
        "readiness_graph",
        lambda graph: _readiness_report(alpha, beta),
    )
    source = _registry_report(first, second)

    result = _project(contract, source, runtime)

    for name in (
        "assessment_id",
        "requirement_id",
        "epistemic_need_identity",
        "reasoning_source_reference",
        "world_snapshot_id",
        "self_gap_source_reference",
        "self_gap_lineage_kind",
    ):
        assert getattr(result, name) == getattr(source, name)
    assert tuple(item.registry_observation for item in result.observations) == (
        first,
        second,
    )
    assert result.observations[0].runtime_readiness == beta
    assert result.observations[0].runtime_readiness.warnings == ("fixture:warning",)
    assert result.observations[1].runtime_readiness == alpha


def test_r8_projector_is_read_only_derivational_and_non_selective() -> None:
    contract = _contract()
    projector = contract.CanonicalRuntimeReadinessProjector()

    assert projector.read_only is True
    assert projector.derivational is True
    forbidden = (
        "mutates_capability_registry",
        "mutates_official_runtime",
        "creates_runtime_capability_graph",
        "reconstructs_runtime_capability_graph",
        "creates_dependency_declarations",
        "creates_readiness_authority",
        "uses_parallel_capability_model",
        "performs_semantic_capability_matching",
        "discovers_substitute_resolution_paths",
        "filters_paths",
        "ranks_sources",
        "ranks_capabilities",
        "selects_sources",
        "selects_capabilities",
        "plans_acquisition",
        "authorizes_acquisition",
        "acquires_evidence",
        "creates_questions",
        "assigns_question_worthiness",
        "assigns_relevance",
        "invokes_curiosity",
        "creates_goals",
        "invokes_initiative",
        "invokes_conversation",
        "persists_results",
        "modifies_memory",
        "creates_learning_candidate",
        "executes_actions",
        "grants_authority",
        "claims_subjective_experience",
        "claims_consciousness",
    )
    available = {item.name for item in fields(projector)}
    assert set(forbidden) <= available
    assert all(getattr(projector, name) is False for name in forbidden)
