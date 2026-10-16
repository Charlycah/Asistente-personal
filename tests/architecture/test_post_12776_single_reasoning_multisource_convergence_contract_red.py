from __future__ import annotations

import inspect
from hashlib import sha256
from pathlib import Path

from app.governed_reasoning_runtime import CanonicalProductiveReasoningSource
from core.cognitive_runtime_orchestration import CognitiveRuntimeOrchestrator
from core.reasoning_runtime_integration import ReasoningRuntimeContributor
from core.runtime_composition_root import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]

PROTECTED_HASHES = {
    "core/end_to_end_local_conversation/runtime.py": (
        "c35610823e19463c20f466703324a94d1f83ead1c78633a2966f328028eadd58"
    ),
    "core/governed_operational_conversation_pipeline/models.py": (
        "f65c3f87c64c5b8cd8525aa326f31a66550711916d564fc0c90cde3d2730b063"
    ),
    "app/ordinary_turn_multisource_reachability_adapter.py": (
        "b943f0d354fc4b7fa0dbb0d4e055e9e35289ce2a3d87a855038af4bcf73c7e97"
    ),
    "app/same_episode_explicit_evidence_convergence_adapter.py": (
        "5be01adfe0c0e3a32065bcb15918013d7e20e5cb7e0092072c88df1dea5aef3d"
    ),
    "app/unified_brain.py": (
        "05f4c65fbb8a1478f9117b9b1de8c450d15211a257aa4835b8123a6babbc1750"
    ),
}

EXPLICIT_FIELDS = (
    "explicit_document_ids",
    "explicit_sources",
    "explicit_evidence_references",
)


def test_post_12776_preparation_transports_selection_into_cognitive_runtime():
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    for field in EXPLICIT_FIELDS:
        assert f"{field}=request.{field}" in source, (
            f"RED: preparation does not yet transport {field} into the existing "
            "cognitive runtime"
        )
    assert "ordinary_turn_multisource_reachability_adapter" not in source, (
        "single-Reasoning convergence must not invoke the adapter directly from "
        "preparation"
    )


def test_post_12776_orchestrator_forwards_selection_only_to_reasoning_stage():
    signature = inspect.signature(CognitiveRuntimeOrchestrator.enrich)
    source = inspect.getsource(CognitiveRuntimeOrchestrator.enrich)
    for field in EXPLICIT_FIELDS:
        assert field in signature.parameters, (
            f"RED: cognitive runtime cannot yet receive {field}"
        )
        assert f'contributor_kwargs["{field}"]' in source, (
            f"RED: cognitive runtime does not yet forward {field} through the "
            "single reasoning contributor branch"
        )
    assert 'casefold() == "reasoning"' in source


def test_post_12776_reasoning_contributor_forwards_selection_to_canonical_source():
    signature = inspect.signature(ReasoningRuntimeContributor.contribute)
    source = inspect.getsource(ReasoningRuntimeContributor.contribute)
    for field in EXPLICIT_FIELDS:
        assert field in signature.parameters, (
            f"RED: reasoning contributor cannot yet receive {field}"
        )
        assert f'source_kwargs["{field}"]' in source, (
            f"RED: reasoning contributor does not yet transport {field} to the "
            "canonical productive reasoning source"
        )
    assert 'source_kwargs["visual_context_contribution"]' in source


def test_post_12776_canonical_source_reuses_existing_multisource_convergence_once():
    signature = inspect.signature(CanonicalProductiveReasoningSource.__call__)
    source = inspect.getsource(CanonicalProductiveReasoningSource)
    for field in EXPLICIT_FIELDS:
        assert field in signature.parameters, (
            f"RED: canonical productive reasoning source cannot yet receive {field}"
        )
    assert "ordinary_turn_multisource_reachability_adapter" in source, (
        "RED: canonical reasoning source does not yet reuse the certified "
        "multisource convergence seam"
    )
    assert ".admit_and_reason(" in source, (
        "RED: explicit selection has no convergence path inside the single "
        "reasoning stage"
    )


def test_post_12776_preparation_does_not_create_second_reasoning_path():
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    assert "ordinary_turn_multisource_reachability_adapter" not in source
    assert ".admit_and_reason(" not in source


def test_post_12776_certified_upstream_and_adapters_remain_byte_identical():
    for relative_path, expected_hash in PROTECTED_HASHES.items():
        payload = (ROOT / relative_path).read_bytes()
        assert sha256(payload).hexdigest() == expected_hash, relative_path
