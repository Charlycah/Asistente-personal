from __future__ import annotations

import json
import subprocess
from pathlib import Path

import main
from app.development_setup import (
    SetupOptions,
    create_runtime_directories,
    detect_ollama_models,
    render_setup_result,
    setup_environment,
)


def read_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_detect_ollama_models_parses_names(monkeypatch):
    monkeypatch.setattr("app.development_setup.shutil.which", lambda _: "ollama")

    def runner(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0],
            0,
            "NAME ID SIZE MODIFIED\nqwen2.5:7b abc 1GB now\nllama3:8b def 2GB now\n",
            "",
        )

    assert detect_ollama_models(runner) == ("qwen2.5:7b", "llama3:8b")


def test_detect_ollama_models_is_safe_when_binary_missing(monkeypatch):
    monkeypatch.setattr("app.development_setup.shutil.which", lambda _: None)
    assert detect_ollama_models() == ()


def test_detect_ollama_models_is_safe_on_failure(monkeypatch):
    monkeypatch.setattr("app.development_setup.shutil.which", lambda _: "ollama")

    def runner(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 1, "", "error")

    assert detect_ollama_models(runner) == ()


def test_create_runtime_directories_is_idempotent(tmp_path):
    first = create_runtime_directories(tmp_path)
    second = create_runtime_directories(tmp_path)
    assert first
    assert second == ()
    assert (tmp_path / ".roby/logs").is_dir()


def test_setup_creates_local_json_config(tmp_path, monkeypatch):
    monkeypatch.setattr("app.development_setup.detect_ollama_models", lambda: ())
    result = setup_environment(
        SetupOptions(
            project_root=tmp_path,
            runtime_factory="example.bootstrap:build",
            provider_model="qwen2.5:7b",
        )
    )
    data = read_config(result.config_path)
    assert data["runtime"]["factory"] == "example.bootstrap:build"
    assert data["providers"]["local"]["model"] == "qwen2.5:7b"
    assert result.pending_fields == ()


def test_setup_uses_private_roby_directory(tmp_path, monkeypatch):
    monkeypatch.setattr("app.development_setup.detect_ollama_models", lambda: ())
    result = setup_environment(SetupOptions(project_root=tmp_path))
    assert result.config_path == tmp_path / ".roby" / "config.json"
    assert result.config_path.exists()
    assert (tmp_path / ".roby" / "credentials.json").exists() is False


def test_setup_uses_single_detected_model(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.development_setup.detect_ollama_models", lambda: ("qwen2.5:7b",)
    )
    result = setup_environment(
        SetupOptions(
            project_root=tmp_path,
            runtime_factory="example.bootstrap:build",
        )
    )
    data = read_config(result.config_path)
    assert data["providers"]["local"]["model"] == "qwen2.5:7b"
    assert result.pending_fields == ()


def test_setup_reports_pending_required_fields(tmp_path, monkeypatch):
    monkeypatch.setattr("app.development_setup.detect_ollama_models", lambda: ())
    result = setup_environment(
        SetupOptions(project_root=tmp_path, runtime_factory="", provider_model="")
    )
    assert result.pending_fields == (
        "runtime.factory",
        "providers.local.model",
    )


def test_setup_accepts_custom_config_path(tmp_path, monkeypatch):
    monkeypatch.setattr("app.development_setup.detect_ollama_models", lambda: ())
    result = setup_environment(
        SetupOptions(
            project_root=tmp_path,
            config_path=Path("private/settings.json"),
            provider_model="model",
        )
    )
    assert result.config_path == tmp_path / "private" / "settings.json"
    assert result.config_path.exists()


def test_render_setup_result_has_next_step(tmp_path, monkeypatch):
    monkeypatch.setattr("app.development_setup.detect_ollama_models", lambda: ())
    result = setup_environment(SetupOptions(project_root=tmp_path))
    text = "\n".join(render_setup_result(result))
    assert "Roby Setup Assistant" in text
    assert "python main.py --doctor" in text
    assert "PENDIENTE" in text


def test_parser_exposes_setup_options():
    args = main.build_parser().parse_args(["--setup", "--model", "m"])
    assert args.setup
    assert args.model == "m"


def test_main_setup_returns_zero_and_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main.main(["--setup", "--model", "m"]) == 0
    config = read_config(tmp_path / ".roby" / "config.json")
    assert config["providers"]["local"]["model"] == "m"


def test_main_setup_uses_defaults_when_model_is_omitted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main.main(["--setup"]) == 0
    assert (tmp_path / ".roby" / "config.json").exists()


def test_setup_records_coowners_and_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr("app.development_setup.detect_ollama_models", lambda: ())
    result = setup_environment(
        SetupOptions(
            project_root=tmp_path,
            owners=("Carlos", "Cristina"),
            provider_endpoint="http://localhost:1234/v1",
            provider_model="model",
        )
    )
    data = read_config(result.config_path)
    assert data["household"]["owners"] == ["Carlos", "Cristina"]
    assert data["providers"]["local"]["endpoint"] == "http://localhost:1234/v1"


def test_setup_does_not_deploy_or_mutate_runtime():
    source = Path("app/development_setup.py").read_text(encoding="utf-8")
    assert "deploy(" not in source
    assert "mutate_runtime" not in source
    assert "restart_provider" not in source


def test_setup_result_contains_only_local_configuration_contract(
    tmp_path, monkeypatch
):
    monkeypatch.setattr("app.development_setup.detect_ollama_models", lambda: ())
    result = setup_environment(SetupOptions(project_root=tmp_path))
    assert set(result.__dataclass_fields__) == {
        "config_path",
        "created_directories",
        "detected_models",
        "pending_fields",
    }
