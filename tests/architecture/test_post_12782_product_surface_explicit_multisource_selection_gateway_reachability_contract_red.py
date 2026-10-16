from __future__ import annotations

import inspect
from hashlib import sha256
from pathlib import Path

from app.desktop_ui import DesktopConversationController, DesktopROBYAdapter
from app.runtime_ui_adapter import LocalConversationUIAdapter
from app.unified_brain import UnifiedBrain

ROOT = Path(__file__).resolve().parents[2]

EXPLICIT_FIELDS = (
    "explicit_document_ids",
    "explicit_sources",
    "explicit_evidence_references",
)

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
}


def _parameters(callable_object) -> dict[str, inspect.Parameter]:
    return dict(inspect.signature(callable_object).parameters)


def test_post_12782_desktop_contract_can_carry_explicit_selection():
    protocol_parameters = _parameters(DesktopROBYAdapter.submit_text)
    controller_parameters = _parameters(DesktopConversationController.submit)
    controller_source = inspect.getsource(DesktopConversationController.submit)

    for field in EXPLICIT_FIELDS:
        assert field in protocol_parameters, (
            f"RED: desktop adapter contract cannot yet carry {field}"
        )
        assert protocol_parameters[field].default == ()
        assert field in controller_parameters, (
            f"RED: product conversation surface cannot yet receive {field}"
        )
        assert controller_parameters[field].default == ()
        assert f"{field}={field}" in controller_source, (
            "RED: desktop controller does not transport "
            f"{field} to its existing adapter"
        )


def test_post_12782_local_ui_adapter_transports_selection_to_unified_brain():
    parameters = _parameters(LocalConversationUIAdapter.submit_text)
    submit_source = inspect.getsource(LocalConversationUIAdapter.submit_text)
    internal_source = inspect.getsource(LocalConversationUIAdapter._submit)

    for field in EXPLICIT_FIELDS:
        assert field in parameters, (
            f"RED: local conversation UI adapter cannot yet receive {field}"
        )
        assert parameters[field].default == ()
        assert f"{field}={field}" in submit_source
        assert f"{field}={field}" in internal_source, (
            f"RED: local conversation UI adapter does not transport {field}"
        )


def test_post_12782_unified_brain_transports_selection_to_existing_gateway():
    parameters = _parameters(UnifiedBrain.process)
    source = inspect.getsource(UnifiedBrain.process)

    for field in EXPLICIT_FIELDS:
        assert field in parameters, f"RED: UnifiedBrain cannot yet receive {field}"
        assert parameters[field].default == ()
        assert f"{field}={field}" in source, (
            f"RED: UnifiedBrain does not transport {field} to the existing gateway"
        )


def test_post_12782_transport_does_not_create_selection_or_reasoning_authority():
    combined_source = "\n".join(
        (
            inspect.getsource(DesktopConversationController.submit),
            inspect.getsource(LocalConversationUIAdapter.submit_text),
            inspect.getsource(LocalConversationUIAdapter._submit),
            inspect.getsource(UnifiedBrain.process),
        )
    )
    assert "ordinary_turn_multisource_reachability_adapter" not in combined_source
    assert "admit_and_reason" not in combined_source
    assert "SameEpisodeExplicitEvidenceConvergenceAdapterV1" not in combined_source
    assert "PersonalDocumentReasoningAdmissionAdapterV1" not in combined_source


def test_post_12782_certified_gateway_and_downstream_remain_byte_identical():
    for relative_path, expected_hash in PROTECTED_HASHES.items():
        payload = (ROOT / relative_path).read_bytes()
        assert sha256(payload).hexdigest() == expected_hash, relative_path
