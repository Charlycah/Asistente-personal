"""R-P0-LISTENING-S1: RED for explicit governed voice activation.

This test deliberately fails against the current local configuration.
No production code or configuration is changed in the RED phase.
"""

import json
from pathlib import Path

from app.roby_config import environment_values
from app.voice_session_gate import VoiceSessionGate


def test_r_p0_listening_s1_local_voice_requires_explicit_wake_word():
    config_path = Path(".roby/config.json")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    listening = data["services"]["voice"]["continuous_listening"]

    assert listening.get("enabled") is True
    assert listening.get("require_wake_word") is True, (
        "La configuracion gobernada debe declarar explicitamente "
        "require_wake_word=true; no basta con un valor implicito."
    )
    assert environment_values(data)["ROBY_VOICE_REQUIRE_WAKE_WORD"] == "true"


def test_r_p0_listening_s1_protected_gate_preserves_addressed_followups():
    class Clock:
        now = 100.0

        def __call__(self):
            return self.now

    clock = Clock()
    gate = VoiceSessionGate(
        wake_aliases=("roby", "robi"),
        require_wake_word=True,
        active_window_seconds=8,
        clock=clock,
    )

    assert not gate.evaluate("Cristina esta conversando al lado").accepted
    addressed = gate.evaluate("Roby, podemos conversar un rato")
    assert addressed.accepted
    assert addressed.command == "podemos conversar un rato"
    assert gate.evaluate("claro, contame algo mas").accepted
    clock.now += 9
    assert not gate.evaluate("Cristina sigue conversando al lado").accepted


def test_r_p0_listening_s1_m309_permissive_mode_remains_available():
    gate = VoiceSessionGate(
        wake_aliases=("roby",),
        require_wake_word=False,
    )
    decision = gate.evaluate("me decis los correos")
    assert decision.accepted
    assert decision.reason == "continuous"
