from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m347_3_readme_declares_current_canonical_baseline_and_private_scope():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "M347.3 — Baseline verificable de M347.2" in readme
    assert "Un único núcleo cognitivo" in readme
    assert "Integración y unificación total" in readme
    assert "Carlos y Cristina" in readme
    assert "Chevrolet Tracker Automática Turbo 2.0" in readme
    assert "no es un producto comercial" in readme


def test_m347_3_preserves_canonical_private_credentials_file():
    credentials_path = ROOT / ".roby" / "credentials.json"

    assert credentials_path.is_file()


def test_m347_3_has_single_productive_cognitive_core_composition():
    production_roots = (
        ROOT / "app",
        ROOT / "application",
        ROOT / "core",
        ROOT / "domain",
        ROOT / "infrastructure",
        ROOT / "interfaces",
    )
    occurrences: list[Path] = []

    for production_root in production_roots:
        for source_path in production_root.rglob("*.py"):
            source = source_path.read_text(encoding="utf-8")
            if "CanonicalCognitiveCore(" in source:
                occurrences.append(source_path.relative_to(ROOT))

    assert occurrences == [Path("app/official_conversation_gateway.py")]


def test_m347_3_gateway_remains_the_only_productive_gateway_definition():
    production_roots = (
        ROOT / "app",
        ROOT / "application",
        ROOT / "core",
        ROOT / "domain",
        ROOT / "infrastructure",
        ROOT / "interfaces",
    )
    definitions: list[Path] = []

    for production_root in production_roots:
        for source_path in production_root.rglob("*.py"):
            source = source_path.read_text(encoding="utf-8")
            if "class OfficialConversationGateway" in source:
                definitions.append(source_path.relative_to(ROOT))

    assert definitions == [Path("app/official_conversation_gateway.py")]


def test_m347_3_baseline_report_exists_and_declares_no_runtime_change():
    report = (
        ROOT / "docs" / "milestones" / "M347_3_BASELINE_VERIFICABLE_M347_2.md"
    ).read_text(encoding="utf-8")

    assert "No se modificó código productivo" in report
    assert ".roby/credentials.json" in report
    assert "OfficialConversationGateway" in report
    assert "CanonicalCognitiveCore" in report
