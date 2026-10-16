from __future__ import annotations

import inspect

from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


def test_red_inspection_has_bounded_canonical_availability_projection_seam() -> None:
    assert hasattr(
        OfficialRuntimeCapabilityRegistry,
        "bind_runtime_availability_reader",
    ), (
        "RED: bounded conversational inspection has no read-only seam for the "
        "existing canonical runtime availability authority"
    )


def test_red_inspection_distinguishes_enabled_from_runtime_availability() -> None:
    source = inspect.getsource(OfficialRuntimeCapabilityRegistry._inspection_response)
    assert "availability" in source.casefold(), (
        "RED: inspection still publishes declarative enabled state without a "
        "separate runtime-availability fact"
    )


def test_red_unknown_availability_fails_closed_instead_of_claiming_available() -> None:
    source = inspect.getsource(OfficialRuntimeCapabilityRegistry._inspection_response)
    assert "unknown" in source.casefold() or "desconoc" in source.casefold(), (
        "RED: inspection has no explicit fail-closed UNKNOWN availability semantics"
    )


def test_protective_inspection_keeps_existing_interface_snapshot() -> None:
    source = inspect.getsource(OfficialRuntimeCapabilityRegistry._inspection_response)
    assert "interface_snapshot" in source


def test_protective_inspection_does_not_consume_planning_or_risk_metadata() -> None:
    source = inspect.getsource(OfficialRuntimeCapabilityRegistry._inspection_response)
    forbidden = (
        "planning_capability_evidence",
        "requires_confirmation",
        "normalized_risk",
        "permission_scope",
        "initiation_policy",
        "effect_class",
    )
    assert all(token not in source for token in forbidden)


def test_protective_registry_does_not_reconstruct_capability_graph_for_inspection() -> (
    None
):
    source = inspect.getsource(OfficialRuntimeCapabilityRegistry._inspection_response)
    assert "RuntimeCapabilityGraph" not in source
    assert "declared_capability_nodes" not in source


def test_protective_inspection_does_not_execute_capabilities() -> None:
    source = inspect.getsource(OfficialRuntimeCapabilityRegistry._inspection_response)
    assert "execute_registration" not in source
    assert ".execute(" not in source
