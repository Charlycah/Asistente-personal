from __future__ import annotations

from pathlib import Path

import main
from app.development_console import (
    DoctorCheck,
    onboarding_message,
    render_doctor,
    run_doctor,
)


def test_doctor_reports_missing_required_configuration(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ROBY_RUNTIME_ROOT_FACTORY", raising=False)
    monkeypatch.delenv("ROBY_LOCAL_PROVIDER_MODEL", raising=False)
    checks = run_doctor()
    by_name = {item.name: item for item in checks}
    assert not by_name["runtime_factory"].passed
    assert not by_name["provider_model"].passed


def test_doctor_creates_and_validates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    check = next(item for item in run_doctor() if item.name == "configuration")
    assert check.passed
    assert Path(".roby/config.json").exists()


def test_doctor_renderer_distinguishes_fail_and_warn():
    lines = render_doctor(
        (
            DoctorCheck("required", False, "bad"),
            DoctorCheck("optional", False, "missing", required=False),
        )
    )
    assert "[FAIL] required: bad" in lines
    assert "[WARN] optional: missing" in lines
    assert lines[-1] == "Resultado: configuración requerida"


def test_doctor_renderer_reports_ready():
    assert render_doctor((DoctorCheck("python", True, "ok"),))[-1] == (
        "Resultado: listo"
    )


def test_onboarding_is_actionable():
    text = "\n".join(onboarding_message(RuntimeError("missing factory")))
    assert "python main.py --doctor" in text
    assert ".roby/config.json" in text
    assert "ROBY_FIRST_STEPS.md" in text


def test_parser_exposes_doctor_maintenance_command():
    args = main.build_parser().parse_args(["--doctor"])
    assert args.doctor


def test_main_doctor_returns_two_when_required_check_fails(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        main,
        "run_doctor",
        lambda: (DoctorCheck("factory", False, "missing"),),
    )
    assert main.main(["--doctor"]) == 2


def test_main_doctor_returns_zero_when_ready(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        main,
        "run_doctor",
        lambda: (DoctorCheck("factory", True, "ok"),),
    )
    assert main.main(["--doctor"]) == 0


def test_main_starts_desktop_by_default(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    calls = []

    class Desktop:
        def run(self):
            calls.append("run")

    import app.desktop_bootstrap as desktop_bootstrap

    monkeypatch.setattr(
        desktop_bootstrap, "build_unified_desktop_app", lambda: Desktop()
    )
    assert main.main([]) == 0
    assert calls == ["run"]


def test_main_does_not_mutate_runtime_or_deploy():
    source = Path("main.py").read_text(encoding="utf-8")
    assert "deploy(" not in source
    assert "mutate_runtime" not in source
    assert "restart_provider" not in source
