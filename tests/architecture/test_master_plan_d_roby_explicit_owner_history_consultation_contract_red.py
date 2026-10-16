from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.development_history_source import DevelopmentHistorySourceAdapter
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _api():
    from app.development_history_consultation_runtime import (
        DevelopmentHistoryConsultationInterceptionPort,
        build_development_history_consultation_runtime_from_environment,
        development_history_consult_descriptor,
    )

    return (
        DevelopmentHistoryConsultationInterceptionPort,
        build_development_history_consultation_runtime_from_environment,
        development_history_consult_descriptor,
    )


def _request(text: str, session_id: str = "history-session"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


def _port(root: Path, *, max_candidates: int = 20):
    port_type, _, _ = _api()
    source = DevelopmentHistorySourceAdapter(
        root=root,
        max_candidates=max_candidates,
        max_read_bytes=4096,
        max_read_chars=4096,
    )
    return port_type(source)


def test_red_1_consultation_port_builder_and_descriptor_exist() -> None:
    port_type, builder, descriptor = _api()
    assert port_type is not None
    assert callable(builder)
    assert descriptor().name == "development_history.consult"


def test_red_2_descriptor_is_human_read_only_and_not_autonomous() -> None:
    _, _, descriptor = _api()
    item = descriptor()
    assert item.normalized_permission_scope.value == "read"
    assert item.normalized_effect_class.value == "read_only"
    assert item.normalized_interaction_scope.value == "human"
    assert item.normalized_initiation_policy.value == "human_approval"


def test_red_3_only_explicit_development_history_intent_is_admitted(
    tmp_path: Path,
) -> None:
    (tmp_path / "plan.md").write_text("past", encoding="utf-8")
    port = _port(tmp_path)
    now = datetime.now(timezone.utc)
    assert port.intercept(_request("mostrame la historia"), now=now) is None
    assert port.intercept(_request("buscá archivos de ROBY"), now=now) is None
    admitted = port.intercept(
        _request("consultá el historial de desarrollo de ROBY: plan"),
        now=now,
    )
    assert admitted is not None


def test_red_4_discovery_matches_metadata_and_never_reads_content(
    tmp_path: Path,
) -> None:
    (tmp_path / "alpha.md").write_text("needle-only-in-content", encoding="utf-8")
    (tmp_path / "needle-name.md").write_text("other", encoding="utf-8")
    port = _port(tmp_path)
    now = datetime.now(timezone.utc)
    result = port.intercept(
        _request("consultá D:\\Roby por needle"),
        now=now,
    )
    assert result is not None
    assert "needle-name.md" in result.response_text
    assert "alpha.md" not in result.response_text
    assert "needle-only-in-content" not in result.response_text


def test_red_5_disambiguation_exposes_only_safe_relative_metadata(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "HAL SET 16 2026"
    folder.mkdir()
    (folder / "plan-a.md").write_text("a", encoding="utf-8")
    (folder / "plan-b.md").write_text("b", encoding="utf-8")
    port = _port(tmp_path)
    result = port.intercept(
        _request("consultá el historial de desarrollo: plan"),
        now=datetime.now(timezone.utc),
    )
    assert result is not None
    assert "HAL SET 16 2026/plan-a.md" in result.response_text
    assert "HAL SET 16 2026/plan-b.md" in result.response_text
    assert str(tmp_path) not in result.response_text
    assert "development-history:" not in result.response_text


def test_red_6_follow_up_selection_is_session_scoped_and_ordinal(
    tmp_path: Path,
) -> None:
    (tmp_path / "plan-a.md").write_text("first", encoding="utf-8")
    (tmp_path / "plan-b.md").write_text("second", encoding="utf-8")
    port = _port(tmp_path)
    now = datetime.now(timezone.utc)
    port.intercept(
        _request("consultá el historial de desarrollo: plan", "session-a"),
        now=now,
    )
    assert port.intercept(_request("2", "session-b"), now=now) is None
    selected = port.intercept(_request("2", "session-a"), now=now)
    assert selected is not None
    assert "second" in selected.response_text


def test_red_7_follow_up_accepts_only_presented_relative_path(
    tmp_path: Path,
) -> None:
    (tmp_path / "plan-a.md").write_text("first", encoding="utf-8")
    (tmp_path / "plan-b.md").write_text("second", encoding="utf-8")
    port = _port(tmp_path)
    now = datetime.now(timezone.utc)
    discovery = port.source.discover()
    hidden_id = discovery.candidates[1].candidate_id
    port.intercept(
        _request("consultá el historial de desarrollo: plan"),
        now=now,
    )
    assert port.intercept(_request(hidden_id), now=now) is None
    port.intercept(
        _request("consultá el historial de desarrollo: plan"),
        now=now,
    )
    selected = port.intercept(_request("plan-b.md"), now=now)
    assert selected is not None
    assert "second" in selected.response_text


def test_red_8_pending_selection_expires_and_can_be_cancelled(
    tmp_path: Path,
) -> None:
    (tmp_path / "plan-a.md").write_text("first", encoding="utf-8")
    (tmp_path / "plan-b.md").write_text("second", encoding="utf-8")
    port = _port(tmp_path)
    now = datetime.now(timezone.utc)
    port.intercept(
        _request("consultá el historial de desarrollo: plan"),
        now=now,
    )
    assert port.intercept(_request("cancelá la consulta"), now=now) is not None
    assert port.intercept(_request("1"), now=now) is None
    port.intercept(
        _request("consultá el historial de desarrollo: plan"),
        now=now,
    )
    expired = port.intercept(_request("1"), now=now + timedelta(minutes=6))
    assert expired is None


def test_red_9_zip_is_presented_as_opaque_and_never_selected_for_read(
    tmp_path: Path,
) -> None:
    (tmp_path / "OWNER_BACKUP.zip").write_bytes(b"PK-not-opened")
    port = _port(tmp_path)
    now = datetime.now(timezone.utc)
    result = port.intercept(
        _request("consultá D:\\Roby por OWNER_BACKUP"),
        now=now,
    )
    assert result is not None
    assert "OWNER_BACKUP.zip" in result.response_text
    assert "opaque" in result.response_text.casefold()
    follow_up = port.intercept(_request("1"), now=now)
    assert follow_up is not None
    assert "no se puede leer" in follow_up.response_text.casefold()


def test_red_10_builder_registers_only_when_history_root_is_configured(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _, builder, _ = _api()
    registry = OfficialRuntimeCapabilityRegistry()
    monkeypatch.delenv("ROBY_DEVELOPMENT_HISTORY_ROOT", raising=False)
    assert builder(registry) is None
    assert "development_history.consult" not in registry.capability_names
    monkeypatch.setenv("ROBY_DEVELOPMENT_HISTORY_ROOT", str(tmp_path))
    runtime = builder(registry)
    assert runtime is not None
    assert "development_history.consult" in registry.capability_names


def test_red_11_official_registry_executes_explicit_owner_consultation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _, builder, _ = _api()
    (tmp_path / "roadmap.md").write_text("historical roadmap", encoding="utf-8")
    monkeypatch.setenv("ROBY_DEVELOPMENT_HISTORY_ROOT", str(tmp_path))
    registry = OfficialRuntimeCapabilityRegistry()
    builder(registry)
    result = registry.intercept(
        _request("consultá el historial de desarrollo de ROBY: roadmap"),
        now=datetime.now(timezone.utc),
    )
    assert result is not None
    assert "historical roadmap" in result.response_text


def test_guardrail_1_history_source_remains_non_current_truth(tmp_path: Path) -> None:
    (tmp_path / "past.md").write_text("past", encoding="utf-8")
    source = DevelopmentHistorySourceAdapter(root=tmp_path)
    candidate = source.discover().candidates[0]
    observation = source.read_selected(candidate.candidate_id)
    assert observation.trust_class == "historical"
    assert observation.current_truth is False


def test_guardrail_2_history_source_has_no_cognitive_or_mutation_imports() -> None:
    import inspect

    import app.development_history_source as source_module

    source = inspect.getsource(source_module)
    forbidden = (
        "DiagnosticProjectEvidence",
        "Memory",
        "KnowledgeRuntime",
        "Reasoning",
        "proposal_generation",
        "write_text(",
        "write_bytes(",
    )
    assert all(item not in source for item in forbidden)


def test_guardrail_3_level2_is_not_required_for_direct_owner_route() -> None:
    import inspect

    import app.runtime_capability_registry as registry_module

    source = inspect.getsource(
        registry_module.OfficialRuntimeCapabilityRegistry.intercept
    )
    assert "execute_read_only_evidence_registration" not in source
    assert "governed_level2" not in source
