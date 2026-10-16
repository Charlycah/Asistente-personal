"""M377 negative carrier contract. No production mutation or new authority."""

import inspect
from dataclasses import fields
from datetime import datetime, timezone

from core.end_to_end_local_conversation.models import LocalConversationTurn
from core.governed_operational_conversation_pipeline.models import (
    GovernedConversationPipelineResult,
    GovernedConversationPreparation,
)


def test_red_preparation_retains_optional_typed_profile_evidence():
    """RED: preparation must retain the already computed profile, not recalculate it."""
    names = {item.name for item in fields(GovernedConversationPreparation)}
    assert "adaptive_personality_profile" in names, (
        "M377 RED: M177 preparation has no turn-scoped profile evidence"
    )


def test_red_local_turn_transports_optional_expression_evidence():
    """RED: local turn needs a correlated expression seam, not a global last tone."""
    names = {item.name for item in fields(LocalConversationTurn)}
    assert "adaptive_personality_profile" in names, (
        "M377 RED: M180 turn has no correlated expression evidence"
    )


def test_existing_preparation_constructor_keeps_seven_fields_and_frozen_contract():
    """Positive guard: preserve positional order and frozen dataclass."""
    names = [item.name for item in fields(GovernedConversationPreparation)]
    assert names[:7] == [
        "owner", "session_id", "text", "provider_route", "inference_request",
        "retrieval_plan", "strategy_application_evidence",
    ]
    assert GovernedConversationPreparation.__dataclass_params__.frozen


def test_local_turn_sha256_identity_is_stable_for_same_historical_payload():
    """Positive guard: existing identity payload remains deterministic."""
    kwargs = dict(
        owner="owner", session_id="S1", sequence=1, user_text="hola",
        response_text="respuesta", status="completed", pipeline_result_id="p1",
        operational_response_id="r1", provider_call_performed=False,
        retrieval_performed=False, network_access_performed=False,
        rationale=("completed",),
        created_at=datetime(2026, 10, 10, tzinfo=timezone.utc),
    )
    a = LocalConversationTurn(**kwargs)
    b = LocalConversationTurn(**kwargs)
    assert a.turn_id == b.turn_id
    assert a._identity_payload() == b._identity_payload()
    assert len(a.turn_id) == 64
    assert LocalConversationTurn.__dataclass_params__.frozen


def test_pipeline_result_identity_payload_excludes_profile_name():
    """Positive guard: no profile field is introduced into historical hash recipe."""
    source = inspect.getsource(GovernedConversationPipelineResult._identity_payload)
    assert "adaptive_personality_profile" not in source


def test_gateway_submit_keeps_public_entrypoint():
    """Positive guard: Gateway.submit remains an existing method."""
    from app.official_conversation_gateway import OfficialConversationGateway
    assert callable(OfficialConversationGateway.submit)
    params = inspect.signature(OfficialConversationGateway.submit).parameters
    assert "text" in params and "session_id" in params
