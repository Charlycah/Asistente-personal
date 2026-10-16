from __future__ import annotations

import inspect
from datetime import datetime, timezone

from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


class _NoopInterceptor:
    def intercept(self, request, *, now):
        del request, now
        return None


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="se2-s1-b",
        text=text,
    )


def _registry() -> OfficialRuntimeCapabilityRegistry:
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="test.bounded_explanation",
        description="Bounded capability explanation sentinel.",
        interceptor=_NoopInterceptor(),
        tags=("sentinel-tag", "read-only"),
    )
    return registry


def test_red_inspection_reuses_existing_official_interface_snapshot() -> None:
    source = inspect.getsource(OfficialRuntimeCapabilityRegistry._inspection_response)
    assert "interface_snapshot" in source, (
        "RED: conversational capability inspection still bypasses the existing "
        "official immutable RuntimeCapabilityView projection"
    )
    assert "capability_names" not in source, (
        "RED: bounded self-explanation must consume the existing interface view "
        "rather than fall back to the names-only projection"
    )


def test_red_conversation_explains_existing_view_description_and_status() -> None:
    registry = _registry()

    result = registry.intercept(
        _request("¿Qué capacidades tenés integradas?"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.rationale == "runtime_capability_registry_inspection_completed"
    assert "test.bounded_explanation" in result.response_text
    assert "Bounded capability explanation sentinel." in result.response_text, (
        "RED: the existing RuntimeCapabilityView.description is not yet published "
        "by bounded conversational self-explanation"
    )
    assert "habilitada" in result.response_text.casefold(), (
        "RED: the existing RuntimeCapabilityView.enabled state is not yet explained "
        "without transferring execution authority"
    )


def test_red_conversation_explains_existing_view_tags_without_descriptor_access() -> (
    None
):
    registry = _registry()

    result = registry.intercept(
        _request("¿Qué capacidades tenés integradas?"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert "sentinel-tag" in result.response_text
    assert "read-only" in result.response_text


def test_protective_inspection_preserves_empty_registry_fail_safe() -> None:
    registry = OfficialRuntimeCapabilityRegistry()
    assert registry._inspection_response() == (
        "No hay capacidades operacionales registradas en el runtime oficial."
    )


def test_protective_inspection_does_not_consume_planning_evidence() -> None:
    source = inspect.getsource(OfficialRuntimeCapabilityRegistry._inspection_response)
    assert "planning_capability_evidence" not in source
    assert "requires_confirmation" not in source
    assert "normalized_risk" not in source


def test_protective_inspection_does_not_read_private_descriptor_semantics() -> None:
    source = inspect.getsource(OfficialRuntimeCapabilityRegistry._inspection_response)
    assert "registration.descriptor" not in source
    assert "permission_scope" not in source
    assert "initiation_policy" not in source
    assert "effect_class" not in source
