from __future__ import annotations

import json
from pathlib import Path

import core.governed_external_intelligence as external_intelligence

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/M400_9_GOVERNED_EXTERNAL_INTELLIGENCE_STABILIZATION_CLOSURE.md"
MANIFEST = ROOT / "docs/quality/M400_9_EXTERNAL_INTELLIGENCE_CLOSURE.json"
PACKAGE = ROOT / "core/governed_external_intelligence"


def _doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_m400_9_declares_c00_through_c15() -> None:
    text = _doc()
    for number in range(16):
        assert f"M400-C{number:02d}" in text


def test_m400_9_closure_adds_no_new_external_capability() -> None:
    text = _doc()
    assert "adds no new provider, source" in text
    assert "must open a new governed stage" in text


def test_m400_9_current_external_intelligence_core_excludes_cross_layer_adapter() -> (
    None
):  # noqa: E501
    expected = {
        "__init__.py",
        "assessment.py",
        "boundary.py",
        "corroboration.py",
        "models.py",
        "provider_integration.py",
        "verification.py",
    }
    assert {path.name for path in PACKAGE.glob("*.py")} == expected


def test_m400_9_manifest_preserves_historical_external_intelligence_snapshot() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = data["external_intelligence_files"]
    assert len(files) == 8
    assert "core/governed_external_intelligence/source_integration.py" in files
    assert files["core/governed_external_intelligence/source_integration.py"] == (
        "12dc640472bfc8477a0505fa1fdeb8f1624ab1c94c23e0593bea294857f08b3d"
    )
    assert not (PACKAGE / "source_integration.py").exists()


def test_m400_9_manifest_denies_external_cognitive_authority() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["cognitive_authority_granted_to_external_components"] is False
    assert data["truth_certification_enabled"] is False
    assert data["automatic_external_acquisition_enabled"] is False


def test_m400_9_closed_chain_is_complete_and_ordered() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["closed_chain"] == [
        "explicit_external_need",
        "governed_route_or_query",
        "existing_execution_authority",
        "external_intelligence_boundary",
        "external_evidence",
        "provenance",
        "verification",
        "assessment",
        "corroboration",
        "roby_interpretation_and_decision",
    ]


def test_m400_9_public_api_snapshot_is_historical_not_current_topology() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    historical_api = data["public_api"]
    assert "GovernedExternalInformationSourceIntegration" in historical_api
    assert (
        "GovernedExternalInformationSourceIntegration"
        not in external_intelligence.__all__
    )
    assert set(external_intelligence.__all__) == (
        set(historical_api) - {"GovernedExternalInformationSourceIntegration"}
    )


def test_m400_9_package_contains_no_external_execution_calls() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in PACKAGE.glob("*.py")
    )
    forbidden = (
        ".generate(",
        ".execute(",
        "urlopen",
        "requests.",
        "shell=True",
        "run_forever",
    )
    assert not any(token in source for token in forbidden)


def test_m400_9_package_declares_no_cognitive_authority_id() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in PACKAGE.glob("*.py")
    )
    assert "authority_id" not in source
    assert "AUTHORITY_ID = " not in source


def test_m400_9_truth_certification_remains_false() -> None:
    text = _doc()
    assert "truth_certified` remains false" in text
    assert "Verification is not truth certification" in text
    assert "Assessment is not truth certification" in text
    assert "Corroboration is not truth certification" in text


def test_m400_9_provider_and_source_families_remain_distinct() -> None:
    text = _doc()
    assert "Providers and sources remain distinct" in text
    assert "NASA remains" in text
    assert "`Information Source`" in text
    assert "not an LLM\nprovider" in text
    assert "Ollama remains preserved as a governed local provider" in text


def test_m400_9_preserves_existing_execution_authorities() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authority = data["authority"]
    assert authority["provider_routing"].startswith("existing governed")
    assert authority["provider_execution"].startswith("existing governed")
    assert authority["source_execution"] == "OfficialConversationGateway remains owner"
    assert authority["connectivity_transport"] == "M397/M398 remain owners"


def test_m400_9_documents_epistemic_limits() -> None:
    text = _doc()
    for rule in (
        "Confidence is not certainty",
        "Majority is not truth",
        "Actor diversity is not epistemic independence",
        "Execution trace is not truth certification",
    ):
        assert rule in text


def test_m400_9_documentation_is_synchronized() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    assert "## Milestone M400.9" in readme
    assert "## M400.9" in changelog
    assert "M400.9 — Regla de cierre de Governed External Intelligence" in rules
    assert readme.startswith("## Milestone M393.1")
    assert changelog.startswith("# M347.15 — Estabilización de la serie")


def test_m400_9_closure_requires_full_quality_gate() -> None:
    text = _doc()
    assert "M361 regeneration" in text
    assert "`ruff check .`" in text
    assert "complete\n`pytest -q` suite" in text
    assert "is CLOSED" in text
