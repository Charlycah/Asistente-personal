from pathlib import Path


def test_cognitive_state_provider_module_is_removed():
    assert not Path("app/cognitive_state_provider.py").exists()


def test_continuous_cognitive_loop_test_uses_direct_properties():
    source = Path("tests/test_rp_10_continuous_internal_cognitive_loop.py").read_text(
        encoding="utf-8"
    )
    assert "CognitiveStateProvider" not in source
    assert "loop.current_state is state" in source
    assert "loop.snapshot.cycles == 1" in source
