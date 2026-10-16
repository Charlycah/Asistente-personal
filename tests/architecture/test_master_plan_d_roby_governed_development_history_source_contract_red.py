from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

import pytest

from app.self_improvement_proposal_generation import (
    DiagnosticProjectEvidence,
    DiagnosticProjectFileEvidence,
)


def _source_api():
    from app.development_history_source import (
        DevelopmentHistorySourceAdapter,
        HistoricalSourceKind,
        build_development_history_source_from_environment,
    )

    return (
        DevelopmentHistorySourceAdapter,
        HistoricalSourceKind,
        build_development_history_source_from_environment,
    )


def _adapter(
    root: Path,
    *,
    max_candidates: int = 100,
    max_read_bytes: int = 4096,
    max_read_chars: int = 4096,
):
    adapter_type, _, _ = _source_api()
    return adapter_type(
        root=root,
        max_candidates=max_candidates,
        max_read_bytes=max_read_bytes,
        max_read_chars=max_read_chars,
    )


def test_red_1_history_source_adapter_and_environment_builder_exist():
    adapter_type, source_kind, builder = _source_api()

    assert inspect.isclass(adapter_type)
    assert inspect.isclass(source_kind)
    assert callable(builder)


def test_red_2_builder_requires_explicit_governed_history_root(
    tmp_path: Path,
    monkeypatch,
):
    _, _, builder = _source_api()
    monkeypatch.delenv("ROBY_DEVELOPMENT_HISTORY_ROOT", raising=False)

    assert builder() is None

    monkeypatch.setenv("ROBY_DEVELOPMENT_HISTORY_ROOT", str(tmp_path))
    adapter = builder()

    assert adapter is not None
    assert Path(adapter.root) == tmp_path.resolve()


def test_red_3_discovery_is_bounded_deterministic_and_historical(tmp_path: Path):
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    (tmp_path / "a.py").write_text("a = 1", encoding="utf-8")
    (tmp_path / "c.txt").write_text("c", encoding="utf-8")
    adapter = _adapter(tmp_path, max_candidates=2)

    first = adapter.discover()
    second = adapter.discover()

    assert first == second
    assert first.truncated is True
    assert [item.relative_path for item in first.candidates] == ["a.py", "b.md"]
    assert all(item.candidate_id for item in first.candidates)
    assert all(
        item.source_reference.startswith("development-history:")
        for item in first.candidates
    )


def test_red_4_direct_readable_suffix_allowlist_is_exact(tmp_path: Path):
    supported = (
        ".py",
        ".pyi",
        ".md",
        ".txt",
        ".json",
        ".toml",
        ".yaml",
        ".yml",
        ".ini",
        ".cfg",
        ".csv",
        ".html",
        ".htm",
    )
    for index, suffix in enumerate(supported):
        (tmp_path / f"safe-{index}{suffix}").write_text("x", encoding="utf-8")
    for name in ("bytecode.pyc", "state.db", "binary.exe", "book.pdf"):
        (tmp_path / name).write_bytes(b"x")

    candidates = _adapter(tmp_path).discover().candidates
    direct = {item.suffix for item in candidates if item.kind.value == "direct"}

    assert direct == set(supported)
    assert all(item.relative_path != "bytecode.pyc" for item in candidates)
    assert all(item.relative_path != "state.db" for item in candidates)
    assert all(item.relative_path != "binary.exe" for item in candidates)
    assert all(item.relative_path != "book.pdf" for item in candidates)


def test_red_5_sensitive_noise_and_environment_surfaces_are_excluded(
    tmp_path: Path,
):
    safe = tmp_path / "snapshot" / "app"
    safe.mkdir(parents=True)
    (safe / "module.py").write_text("SAFE = True", encoding="utf-8")
    excluded = (
        ".roby/credentials.json",
        ".git/config",
        ".pytest_cache/README.md",
        ".ruff_cache/CACHEDIR.TAG",
        "__pycache__/module.py",
        ".venv/lib/site-packages/pkg/module.py",
        "venv/lib/site-packages/pkg/module.py",
        "snapshot/.env",
        "snapshot/api_token.txt",
        "snapshot/secret.json",
    )
    for relative in excluded:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("sensitive", encoding="utf-8")

    result = _adapter(tmp_path).discover()
    paths = {item.relative_path for item in result.candidates}

    assert "snapshot/app/module.py" in paths
    assert not paths.intersection(excluded)


def test_red_6_candidate_preserves_historical_provenance(tmp_path: Path):
    snapshot = tmp_path / "HAL SET 16 2026" / "app"
    snapshot.mkdir(parents=True)
    source = snapshot / "module.py"
    source.write_text("VALUE = 1", encoding="utf-8")

    candidate = _adapter(tmp_path).discover().candidates[0]

    assert candidate.relative_path == "HAL SET 16 2026/app/module.py"
    assert candidate.snapshot_segment == "HAL SET 16 2026"
    assert candidate.suffix == ".py"
    assert candidate.size_bytes == source.stat().st_size
    assert candidate.modified_ns == source.stat().st_mtime_ns
    assert candidate.candidate_id
    assert candidate.source_reference.startswith("development-history:")
    assert "local-library:" not in candidate.source_reference
    assert "personal-document:" not in candidate.source_reference


def test_red_7_selected_direct_source_is_revalidated_and_bounded(tmp_path: Path):
    source = tmp_path / "snapshot" / "note.md"
    source.parent.mkdir()
    source.write_text("historical text", encoding="utf-8")
    adapter = _adapter(tmp_path, max_read_bytes=64, max_read_chars=64)
    candidate = adapter.discover().candidates[0]

    observation = adapter.read_selected(candidate.candidate_id)

    assert observation.candidate == candidate
    assert observation.text == "historical text"
    assert observation.trust_class == "historical"
    assert observation.current_truth is False

    source.write_text("changed historical text", encoding="utf-8")
    with pytest.raises(ValueError):
        adapter.read_selected(candidate.candidate_id)


def test_red_8_selected_source_escape_symlink_and_read_limit_fail_closed(
    tmp_path: Path,
):
    source = tmp_path / "large.txt"
    source.write_text("x" * 128, encoding="utf-8")
    adapter = _adapter(tmp_path, max_read_bytes=32, max_read_chars=32)
    candidate = adapter.discover().candidates[0]

    with pytest.raises(ValueError):
        adapter.read_selected(candidate.candidate_id)
    with pytest.raises((KeyError, ValueError)):
        adapter.read_selected("../outside.txt")

    outside = tmp_path.parent / "outside.txt"
    link = tmp_path / "linked.txt"
    outside.write_text("outside", encoding="utf-8")
    try:
        try:
            link.symlink_to(outside)
        except OSError:
            pytest.skip("symlink creation unavailable on this platform")
        assert all(
            item.relative_path != "linked.txt"
            for item in adapter.discover().candidates
        )
    finally:
        link.unlink(missing_ok=True)
        outside.unlink(missing_ok=True)


def test_red_9_zip_is_opaque_metadata_and_cannot_be_read(tmp_path: Path):
    archive = tmp_path / "OWNER_CERTIFIED_BACKUP.zip"
    archive.write_bytes(b"PK-not-opened")
    adapter = _adapter(tmp_path)
    candidate = adapter.discover().candidates[0]

    assert candidate.relative_path == archive.name
    assert candidate.suffix == ".zip"
    assert candidate.kind.value == "opaque_archive"
    with pytest.raises(ValueError):
        adapter.read_selected(candidate.candidate_id)


def test_red_10_discovery_and_read_do_not_create_durable_project_state(
    tmp_path: Path,
):
    source = tmp_path / "history.md"
    source.write_text("past", encoding="utf-8")
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    adapter = _adapter(tmp_path)
    candidate = adapter.discover().candidates[0]

    observation = adapter.read_selected(candidate.candidate_id)
    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    assert observation.text == "past"
    assert before == after


def test_red_11_history_types_are_not_current_project_evidence(tmp_path: Path):
    source = tmp_path / "app" / "module.py"
    source.parent.mkdir()
    source.write_text("VALUE = 1", encoding="utf-8")
    candidate = _adapter(tmp_path).discover().candidates[0]

    assert not isinstance(candidate, DiagnosticProjectFileEvidence)
    assert not isinstance(candidate, DiagnosticProjectEvidence)
    assert not hasattr(candidate, "content_sha256")


def test_guardrail_12_current_project_evidence_remains_hash_bound(tmp_path: Path):
    source = tmp_path / "app" / "module.py"
    test_file = tmp_path / "tests" / "test_module.py"
    source.parent.mkdir()
    test_file.parent.mkdir()
    source.write_text("VALUE = 1", encoding="utf-8")
    test_file.write_text("def test_value(): pass", encoding="utf-8")

    def evidence(path: Path, relative: str) -> DiagnosticProjectFileEvidence:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return DiagnosticProjectFileEvidence(relative, digest, "current evidence")

    project = DiagnosticProjectEvidence(
        affected_files=(evidence(source, "app/module.py"),),
        validation_tests=(evidence(test_file, "tests/test_module.py"),),
    )

    assert project.affected_files[0].content_sha256
    assert project.validation_tests[0].content_sha256


def test_guardrail_13_product_code_does_not_hardcode_owner_history_root():
    product_files = tuple(Path("app").rglob("*.py")) + tuple(Path("core").rglob("*.py"))

    offenders = [
        str(path)
        for path in product_files
        if "D:" + "\\\\Roby" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_guardrail_14_no_existing_automatic_history_cognitive_integration():
    runtime_files = (
        Path("app/runtime_environment_wiring.py"),
        Path("app/runtime_root_factory.py"),
        Path("app/governed_reasoning_runtime.py"),
        Path("app/self_improvement_proposal_generation.py"),
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in runtime_files)

    assert "ROBY_DEVELOPMENT_HISTORY_ROOT" not in combined
    assert "DevelopmentHistorySourceAdapter" not in combined
