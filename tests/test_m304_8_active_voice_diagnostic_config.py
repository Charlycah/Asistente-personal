import json
from pathlib import Path


def test_m304_8_active_roby_config_enables_voice_diagnostics():
    config_path = Path(".roby/config.json")
    data = json.loads(config_path.read_text(encoding="utf-8"))

    listening = data["services"]["voice"]["continuous_listening"]

    assert listening["diagnostic_mode"] is True
