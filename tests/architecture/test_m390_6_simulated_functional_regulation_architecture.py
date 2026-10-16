from pathlib import Path

from core.cognitive_maturity import (
    SimulatedFunctionalRegulation,
    SimulatedInnerStateAuthority,
)

ROOT = Path(__file__).resolve().parents[2]


def test_m390_6_is_not_a_parallel_authority() -> None:
    assert not hasattr(SimulatedFunctionalRegulation, "authority_id")
    assert SimulatedInnerStateAuthority.authority_id == "simulated_inner_state"


def test_m390_6_has_no_hidden_runtime_or_state_surface() -> None:
    source = (
        ROOT
        / "core"
        / "cognitive_maturity"
        / "simulated_functional_regulation.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "official_conversation_gateway",
        "unified_brain",
        "sqlite",
        "requests.",
        "subprocess",
        "datetime.now",
        "persist(",
        "execute(",
        "call_llm",
    )
    assert all(item not in source for item in forbidden)


def test_m390_6_never_builds_a_new_inner_state_snapshot() -> None:
    source = (
        ROOT
        / "core"
        / "cognitive_maturity"
        / "simulated_functional_regulation.py"
    ).read_text(encoding="utf-8")
    assert "SimulatedInnerStateAuthority(" not in source
    assert "SimulatedInnerStateSnapshot(" not in source


def test_m390_6_preserves_official_gateway_anchor() -> None:
    gateway = ROOT / "app" / "official_conversation_gateway.py"
    lines = gateway.read_text(encoding="utf-8").splitlines()
    assert "CanonicalCognitiveCore(" in lines[51]
