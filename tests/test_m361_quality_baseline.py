import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs" / "M361_QUALITY_BASELINE.md"
SNAPSHOT = ROOT / "docs" / "quality" / "M361_QUALITY_BASELINE.json"
GENERATOR = ROOT / "scripts" / "generate_quality_baseline.py"


def test_m361_quality_baseline_artifacts_exist() -> None:
    assert DOCUMENT.is_file()
    assert SNAPSHOT.is_file()
    assert GENERATOR.is_file()


def test_m361_snapshot_records_verified_predecessor_and_scope() -> None:
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["milestone"] == "M361"
    assert data["canonical_predecessor"] == "M360.0.e"
    assert data["verified_predecessor_tests"] == 8677
    assert data["scope"] == "static_repository_baseline"


def test_m361_snapshot_has_sane_structural_metrics() -> None:
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    production = data["production"]
    tests = data["tests"]
    assert production["module_count"] > 800
    assert production["non_empty_lines"] > 100_000
    assert tests["module_count"] > 600
    assert tests["non_empty_lines"] > 70_000
    assert production["bare_exception_handlers"] == 0
    assert production["syntax_errors"] == []


def test_m361_defines_criticality_debt_and_quality_gates() -> None:
    text = DOCUMENT.read_text(encoding="utf-8")
    for expected in (
        "Matriz de criticidad",
        "Mapa inicial de deuda técnica",
        "Quality gates desde M361",
        "ToolGatewayManager",
        "cero manejadores `except:` desnudos",
        "pruebas unitarias, negativas, de composición y degradación",
        "No introduce comportamiento productivo",
    ):
        assert expected in text


def test_m361_generator_reproduces_committed_snapshot() -> None:
    before = SNAPSHOT.read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(GENERATOR)], cwd=ROOT, check=True)
    after = SNAPSHOT.read_text(encoding="utf-8")
    assert after == before
