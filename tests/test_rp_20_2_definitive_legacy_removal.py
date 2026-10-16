from pathlib import Path

from core.governed_provider_execution_adapter import GovernedProviderExecutionAdapter


def test_legacy_application_composition_was_physically_removed() -> None:
    assert not Path("app/bootstrap.py").exists()


def test_obsolete_llm_provider_layer_was_removed_from_contract_module() -> None:
    source = Path("core/llm_provider.py").read_text(encoding="utf-8")
    assert "class LLMProviderLayer" not in source
    assert "class LLMProviderSnapshot" not in source


def test_execution_adapter_has_governed_name_and_module() -> None:
    assert (
        GovernedProviderExecutionAdapter.__name__ == "GovernedProviderExecutionAdapter"
    )
    assert not Path("core/local_provider_execution_adapter").exists()


def test_official_sources_do_not_reference_removed_surfaces() -> None:
    roots = (Path("app"), Path("core"))
    forbidden = (
        "app.bootstrap",
        "build_app(",
        "LLMProviderLayer",
        "local_provider_execution_adapter",
        "LocalProviderExecutionAdapter",
    )
    for root in roots:
        for path in root.rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            for token in forbidden:
                assert token not in source, f"{token!r} remains in {path}"
