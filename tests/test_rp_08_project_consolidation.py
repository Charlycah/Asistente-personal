from pathlib import Path

from scripts.clean_project_artifacts import clean_project

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_refinement_documents_are_consolidated():
    refinement = PROJECT_ROOT / "docs" / "refinement"
    expected = {
        "RP_04_NATURAL_CONVERSATION_FLOW.md",
        "RP_05_AUTONOMOUS_CONVERSATIONAL_SELF_ANALYSIS.md",
        "RP_06_GOVERNED_AMBIENT_PROACTIVE_INTEGRATION.md",
        "RP_07_RUNTIME_AMBIENT_INTEGRATION.md",
        "RP_08_PROJECT_CONSOLIDATION.md",
    }
    assert expected <= {path.name for path in refinement.iterdir()}


def test_project_structure_is_documented():
    document = PROJECT_ROOT / "docs" / "PROJECT_STRUCTURE.md"
    assert document.is_file()
    assert "package-local" in document.read_text(encoding="utf-8")


def test_cleanup_removes_transient_python_artifacts(tmp_path):
    cache = tmp_path / "package" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "module.cpython-311.pyc").write_bytes(b"bytecode")
    pytest_cache = tmp_path / ".pytest_cache"
    pytest_cache.mkdir()
    compiled = tmp_path / "orphan.pyc"
    compiled.write_bytes(b"bytecode")
    source = tmp_path / "module.py"
    source.write_text("value = 1\n", encoding="utf-8")

    removed_directories, removed_files = clean_project(tmp_path)

    assert removed_directories == 2
    assert removed_files == 2
    assert source.is_file()
    assert not cache.exists()
    assert not pytest_cache.exists()
    assert not compiled.exists()
