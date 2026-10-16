from pathlib import Path

from core.adaptive_personality import AdaptivePersonalityAuthority
from core.cognitive_maturity import GovernedExpressiveModulation

ROOT = Path(__file__).resolve().parents[2]


def test_m390_5_is_not_a_parallel_authority() -> None:
    assert not hasattr(GovernedExpressiveModulation, "authority_id")
    assert AdaptivePersonalityAuthority.__name__ == "AdaptivePersonalityAuthority"


def test_m390_5_has_no_runtime_persistence_or_execution_surface() -> None:
    source = (
        ROOT / "core" / "cognitive_maturity" / "governed_expressive_modulation.py"
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


def test_m390_5_only_extends_existing_adaptive_personality_authority() -> None:
    source = (ROOT / "core" / "adaptive_personality.py").read_text(encoding="utf-8")
    assert source.count("class AdaptivePersonalityAuthority:") == 1
    assert "simulated_affective_modulation_applied" in source


def test_m390_5_preserves_official_gateway_anchor() -> None:
    gateway = ROOT / "app" / "official_conversation_gateway.py"
    lines = gateway.read_text(encoding="utf-8").splitlines()
    assert "CanonicalCognitiveCore(" in lines[51]
