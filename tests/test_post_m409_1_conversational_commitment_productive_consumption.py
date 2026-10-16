from __future__ import annotations

from app.runtime_root_factory import build_runtime_root


def test_runtime_root_reuses_conversation_intelligence_instances_end_to_end():
    root = build_runtime_root()
    dependencies = root.dependencies
    gateway = dependencies.conversation_intelligence_runtime

    assert dependencies.adaptive_conversation_intelligence is gateway.adaptive
    assert dependencies.conversational_repair_intelligence is gateway.repair
    assert dependencies.conversational_grounding_intelligence is gateway.grounding
    assert dependencies.conversational_commitment_intelligence is gateway.commitment
    assert (
        dependencies.adaptive_conversation_operational_consolidation
        is gateway.consolidation
    )


def test_runtime_root_activates_m196_to_m200_contributors_in_order():
    root = build_runtime_root()
    runtime = root.compose().preparation.dependencies.cognitive_runtime

    assert runtime is not None
    assert tuple(item.name for item in runtime.contributors[:5]) == (
        "adaptive_conversation_intelligence",
        "conversational_repair_intelligence",
        "conversational_grounding_intelligence",
        "conversational_commitment_intelligence",
        "adaptive_conversation_operational_consolidation",
    )
