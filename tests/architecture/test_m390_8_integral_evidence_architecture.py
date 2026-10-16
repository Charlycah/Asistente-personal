from pathlib import Path

from core.cognitive_maturity import (
    M390IntegralEvidenceDiagnostic,
    SimulatedInnerStateAuthority,
)

ROOT = Path(__file__).resolve().parents[2]


def test_m390_8_is_diagnostic_not_parallel_authority() -> None:
    diagnostic = M390IntegralEvidenceDiagnostic()
    assert diagnostic.diagnostic_id == "m390_integral_evidence"
    assert not hasattr(diagnostic, "authority_id")
    assert SimulatedInnerStateAuthority.authority_id == "simulated_inner_state"


def test_m390_8_has_no_runtime_persistence_or_execution_surface() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "m390_integral_evidence.py"
    source = path.read_text(encoding="utf-8")
    forbidden = (
        "official_conversation_gateway",
        "unified_brain",
        "credentials.json",
        ".roby",
        "sqlite",
        "subprocess",
        "datetime.now",
        "persist(",
        "execute(",
        "call_llm",
    )
    assert all(token not in source for token in forbidden)


def test_m390_8_preserves_official_gateway_anchor() -> None:
    gateway = ROOT / "app" / "official_conversation_gateway.py"
    lines = gateway.read_text(encoding="utf-8").splitlines()
    assert "CanonicalCognitiveCore(" in lines[51]
