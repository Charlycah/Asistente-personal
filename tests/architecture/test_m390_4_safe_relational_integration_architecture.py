from __future__ import annotations

from inspect import getsource

from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import SafeRelationalAffectiveIntegration


def test_m390_4_is_not_a_parallel_authority() -> None:
    evaluator = SafeRelationalAffectiveIntegration()
    assert not hasattr(evaluator, "authority_id")
    assert evaluator.grants_authority is False
    assert evaluator.persists_state is False
    assert evaluator.infers_identity is False
    assert evaluator.infers_presence is False
    assert evaluator.modifies_relationships is False
    assert evaluator.modifies_personality is False


def test_m390_4_has_no_runtime_or_raw_relationship_dependencies() -> None:
    source = getsource(SafeRelationalAffectiveIntegration)
    forbidden = (
        "relationship_snapshot",
        "personality_profile",
        "OfficialConversationGateway",
        "memory_gateway",
        "OfficialMemoryGateway",
    )
    for token in forbidden:
        assert token not in source


def test_m390_4_preserves_official_gateway_core_line() -> None:
    source_file = __import__(
        "app.official_conversation_gateway", fromlist=["__file__"]
    ).__file__
    lines = open(source_file, encoding="utf-8").read().splitlines()
    assert "CanonicalCognitiveCore(" in lines[51]
    assert OfficialConversationGateway is not None
