from pathlib import Path

import main


def test_m304_9_runtime_resolves_default_config_from_project_root(
    tmp_path: Path, monkeypatch
):
    captured: list[Path] = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "activate_roby_config", captured.append)
    monkeypatch.setattr(main, "activate_credentials", lambda: ())
    monkeypatch.setattr(main, "run_doctor", lambda: ())
    monkeypatch.setattr(main, "render_doctor", lambda checks: ())

    assert main.main(["--doctor"]) == 0

    assert len(captured) == 1
    assert captured[0].name == "config.json"
    assert captured[0].parent.name == ".roby"
    assert captured[0].is_absolute()
    assert captured[0] != tmp_path / ".roby" / "config.json"


def test_m304_9_distributed_project_has_no_legacy_hal_directory():
    project_root = Path(__file__).resolve().parents[1]

    assert not (project_root / "config.json").exists()
    assert not (project_root / "credentials.json").exists()
    assert not (project_root / "credential.json").exists()
