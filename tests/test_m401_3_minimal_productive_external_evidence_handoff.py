from __future__ import annotations

from pathlib import Path

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

ROOT = Path(__file__).resolve().parents[1]


def test_m401_3_turn_request_owns_explicit_external_evidence_handoff() -> None:
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="main",
        text="Hola",
    )
    assert request.external_evidence == ()


def test_m401_3_preparation_hands_turn_evidence_to_existing_cognitive_runtime() -> None:
    source = (ROOT / "core/runtime_composition_root/preparation.py").read_text(
        encoding="utf-8"
    )
    assert "external_evidence=request.external_evidence" in source
    assert source.index("external_evidence=request.external_evidence") < source.index(
        "tool_runtime = self.dependencies.tool_runtime"
    )


def test_m401_3_productive_gateway_exposes_only_explicit_per_turn_handoff() -> None:
    source = (ROOT / "app/official_conversation_gateway.py").read_text(encoding="utf-8")
    signature_region = source[
        source.index("    def submit(") : source.index("    def submit_observed")
    ]
    assert "external_evidence:" in signature_region
    assert "external_evidence=external_evidence" not in signature_region
    assert "external_evidence=(" in signature_region


def test_m401_3_end_to_end_runtime_carries_handoff_in_same_turn_request() -> None:
    source = (ROOT / "core/end_to_end_local_conversation/runtime.py").read_text(
        encoding="utf-8"
    )
    assert (
        "external_evidence: tuple[CognitiveExternalEvidenceAdmission, ...] = ()"
        in source
    )
    assert "external_evidence=external_evidence" in source


def test_m401_3_does_not_create_external_acquisition_subsystem() -> None:
    changed_sources = (
        ROOT / "core/governed_operational_conversation_pipeline/models.py",
        ROOT / "core/runtime_composition_root/preparation.py",
        ROOT / "core/end_to_end_local_conversation/runtime.py",
        ROOT / "app/official_conversation_gateway.py",
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in changed_sources)
    forbidden = (
        "ExternalEvidenceAcquirer",
        "ExternalAcquisitionManager",
        "BackgroundExternalFetcher",
        "poll_external_evidence",
    )
    assert all(item not in text for item in forbidden)


def test_m401_3_m400_remains_independent_from_cognitive_handoff() -> None:
    package = ROOT / "core/governed_external_intelligence"
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(package.glob("*.py"))
    )
    assert "cognitive_runtime_orchestration" not in text
    assert "M401" not in text
