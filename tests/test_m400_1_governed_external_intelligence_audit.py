import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/audits/M400_1_EXTERNAL_INTELLIGENCE_AUTHORITY_MAP.json"
DOCUMENT = ROOT / "docs/M400_1_GOVERNED_EXTERNAL_INTELLIGENCE_AUDIT_AUTHORITY_MAP.md"


def _audit() -> dict[str, object]:
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def test_m400_1_is_read_only_audit() -> None:
    audit = _audit()
    assert audit["baseline"] == "M399.8"
    assert audit["productive_code_modified"] is False
    assert audit["purpose"] == "read_only_external_intelligence_authority_audit"


def test_m400_1_preserves_external_capability_authority_boundary() -> None:
    findings = _audit()["findings"]
    assert findings["m400_rule"] == (
        "external capability/evidence != cognitive authority"
    )
    assert "No external provider or source" in findings["authority_conclusion"]


def test_m400_1_identifies_legacy_provider_compatibility() -> None:
    legacy = _audit()["findings"]["legacy_compatibility"]
    assert "core.provider_router:ProviderRouter" in legacy
    assert "core.llm_service:LLMService" in legacy


def test_m400_1_maps_official_governed_provider_path() -> None:
    path = _audit()["findings"]["official_provider_path"]
    assert path == [
        "OfficialROBYRuntime",
        "RuntimeCompositionRoot",
        "ProviderHealthEvaluator",
        "LocalFirstProviderPolicy",
        "GovernedProviderRouter",
        "GovernedProviderExecutionAdapter",
        "OperationalResponseAssembler",
    ]


def test_m400_1_keeps_ollama_as_local_provider_preference() -> None:
    preferences = _audit()["findings"]["provider_preferences"]
    assert preferences["local"] == ["ollama"]
    assert preferences["remote"] == ["gemini", "mistral"]


def test_m400_1_separates_nasa_source_from_llm_provider() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    assert "NASA es una fuente de información, no un LLM provider" in document
    assert "automatic_fetch_enabled=False" in document


def test_m400_1_does_not_promote_legacy_router_to_official_path() -> None:
    path = _audit()["findings"]["official_provider_path"]
    assert "ProviderRouter" not in path
    assert "LLMService" not in path


def test_m400_1_documents_transport_authority_boundary() -> None:
    document = DOCUMENT.read_text(encoding="utf-8")
    assert "M397/M398 conservan sus autoridades de conectividad/transporte" in document
    assert "M399 conserva diagnóstico/revisión" in document


def test_m400_1_inventory_covers_required_surfaces() -> None:
    inventory = _audit()["inventory_sha256"]
    for required in (
        "core/llm_provider.py",
        "core/provider_router.py",
        "core/llm_service.py",
        "core/governed_provider_routing",
        "core/governed_provider_execution_adapter",
        "core/runtime_composition_root",
        "core/knowledge_source_policy",
        "app/llm_provider_factory.py",
        "app/governed_information_sources.py",
        "app/nasa_governed_source.py",
        "app/official_conversation_gateway.py",
    ):
        assert required in inventory
        assert len(inventory[required]) == 64


def test_m400_1_preserves_historical_document_headers() -> None:
    assert (ROOT / "README.md").read_text(encoding="utf-8").splitlines()[0] == (
        "## Milestone M393.1 — Fundamento de Memoria Relacional Enriquecida Gobernada"
    )
    assert (ROOT / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()[0] == (
        "# M347.15 — Estabilización de la serie"
    )
