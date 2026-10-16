from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionRequest,
    GovernedConversationalSourceSelectionStatus,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.wikimedia_commons_governed_source import (
    WikimediaCommonsGovernedSourceAdapter,
)

ROOT = Path(__file__).resolve().parents[2]
ENVIRONMENT_WIRING = ROOT / "app" / "runtime_environment_wiring.py"
OFFICIAL_RUNTIME = ROOT / "app" / "official_runtime_composition.py"
ADAPTER = ROOT / "app" / "wikimedia_commons_governed_source.py"


class Runtime:
    pass


def _environment_module():
    from app import runtime_environment_wiring

    return runtime_environment_wiring


def _runtime_source() -> str:
    return OFFICIAL_RUNTIME.read_text(encoding="utf-8")


def _environment_source() -> str:
    return ENVIRONMENT_WIRING.read_text(encoding="utf-8")


def _transport(url: str, timeout: float) -> bytes:
    assert "commons.wikimedia.org/w/api.php" in url
    assert timeout == 7.0
    return (
        b'{"query":{"pages":[{"pageid":42,"title":"File:Saturn.jpg",'
        b'"imageinfo":[{"mime":"image/jpeg",'
        b'"thumburl":"https://upload.wikimedia.org/saturn.jpg",'
        b'"descriptionurl":"https://commons.wikimedia.org/wiki/'
        b'File:Saturn.jpg","timestamp":"2026-01-01T00:00:00Z",'
        b'"user":"Example","extmetadata":{}}]}]}}'
    )


def _open_visual_request() -> GovernedConversationalSourceSelectionRequest:
    return GovernedConversationalSourceSelectionRequest(
        text="mostrame fotos de Saturno",
        topics=frozenset(),
        query_text="Saturn",
        limit=4,
        timeout_seconds=7.0,
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )


def test_red_declares_canonical_opt_in_environment_contract() -> None:
    source = _environment_source()

    assert "ROBY_WIKIMEDIA_COMMONS_ENABLED" in source
    assert "ROBY_WIKIMEDIA_COMMONS_USER_AGENT" in source
    assert "build_wikimedia_commons_governed_source_from_environment" in source


def test_red_environment_builder_is_disabled_by_default(monkeypatch) -> None:
    module = _environment_module()
    monkeypatch.delenv("ROBY_WIKIMEDIA_COMMONS_ENABLED", raising=False)
    monkeypatch.delenv("ROBY_WIKIMEDIA_COMMONS_USER_AGENT", raising=False)

    builder = getattr(
        module,
        "build_wikimedia_commons_governed_source_from_environment",
    )
    assert builder(transport=_transport) is None


@pytest.mark.parametrize("user_agent", [None, "", "   "])
def test_red_enabled_missing_or_blank_user_agent_fails_closed(
    monkeypatch,
    user_agent: str | None,
) -> None:
    module = _environment_module()
    monkeypatch.setenv("ROBY_WIKIMEDIA_COMMONS_ENABLED", "1")
    if user_agent is None:
        monkeypatch.delenv("ROBY_WIKIMEDIA_COMMONS_USER_AGENT", raising=False)
    else:
        monkeypatch.setenv("ROBY_WIKIMEDIA_COMMONS_USER_AGENT", user_agent)

    builder = getattr(
        module,
        "build_wikimedia_commons_governed_source_from_environment",
    )
    assert builder(transport=_transport) is None


def test_red_enabled_explicit_user_agent_builds_canonical_adapter(
    monkeypatch,
) -> None:
    module = _environment_module()
    monkeypatch.setenv("ROBY_WIKIMEDIA_COMMONS_ENABLED", "1")
    monkeypatch.setenv(
        "ROBY_WIKIMEDIA_COMMONS_USER_AGENT",
        "ROBY-XI.2/1.0 (operator: test@example.invalid)",
    )

    builder = getattr(
        module,
        "build_wikimedia_commons_governed_source_from_environment",
    )
    adapter = builder(transport=_transport)

    assert isinstance(adapter, WikimediaCommonsGovernedSourceAdapter)
    assert adapter._transport is _transport


def test_red_builder_has_no_registration_or_execution_authority() -> None:
    source = _environment_source()

    assert "register_governed_source_query_adapter" not in source
    builder_start = source.find(
        "def build_wikimedia_commons_governed_source_from_environment"
    )
    assert builder_start >= 0
    builder_tail = source[builder_start:]
    next_definition = builder_tail.find("\ndef ", 5)
    builder_source = (
        builder_tail if next_definition < 0 else builder_tail[:next_definition]
    )
    assert "execute_governed_source_query" not in builder_source


def test_red_official_runtime_consumes_builder_and_gateway_registration() -> None:
    source = _runtime_source()

    assert "build_wikimedia_commons_governed_source_from_environment" in source
    assert "WikimediaCommonsGovernedSourceAdapter.SOURCE_ID" in source
    assert "register_governed_source_query_adapter" in source


def test_red_registration_reuses_existing_contract_and_selector() -> None:
    gateway = OfficialConversationGateway(Runtime())
    adapter = WikimediaCommonsGovernedSourceAdapter(
        user_agent="ROBY-XI.2/1.0 (operator: test@example.invalid)",
        transport=_transport,
    )

    unavailable = gateway.select_governed_conversational_source(_open_visual_request())
    assert unavailable.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE

    gateway.register_governed_source_query_adapter(
        WikimediaCommonsGovernedSourceAdapter.SOURCE_ID,
        adapter,
    )
    selection = gateway.select_governed_conversational_source(_open_visual_request())

    assert selection.status is GovernedConversationalSourceSelectionStatus.SELECTED
    assert selection.source is not None
    assert selection.source.source_id == "wikimedia_commons"
    assert selection.query is not None
    assert selection.query.mode is GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT
    assert selection.query.topics == frozenset()
    assert selection.query.query_text == "Saturn"
    assert selection.query.limit == 4
    assert selection.query.timeout_seconds == 7.0


def test_red_selected_query_executes_through_existing_executor() -> None:
    gateway = OfficialConversationGateway(Runtime())
    adapter = WikimediaCommonsGovernedSourceAdapter(
        user_agent="ROBY-XI.2/1.0 (operator: test@example.invalid)",
        transport=_transport,
    )
    gateway.register_governed_source_query_adapter(
        WikimediaCommonsGovernedSourceAdapter.SOURCE_ID,
        adapter,
    )

    selection, result = gateway.execute_selected_governed_conversational_query(
        _open_visual_request()
    )

    assert selection.query is not None
    assert result is not None
    assert result.source_result.response is not None
    assert result.source_result.execution_enabled is True
    assert result.source_result.execution_id


def test_red_no_parallel_wikimedia_authorities_or_background_runtime() -> None:
    forbidden_modules = (
        "app.wikimedia_commons_source_registry",
        "app.wikimedia_commons_query_executor",
        "app.wikimedia_commons_source_selector",
        "app.wikimedia_commons_image_presenter",
        "app.wikimedia_commons_retry_manager",
    )
    for module_name in forbidden_modules:
        with pytest.raises(ModuleNotFoundError):
            __import__(module_name)

    executor_source = (ROOT / "app" / "governed_source_query_executor.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(executor_source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imported_roots.isdisjoint(
        {"asyncio", "httpx", "requests", "socket", "threading", "urllib"}
    )


def test_red_adapter_and_later_residual_boundaries_remain_closed() -> None:
    adapter_source = ADAPTER.read_text(encoding="utf-8")
    environment_source = _environment_source()
    runtime_source = _runtime_source()

    assert "class WikimediaCommonsGovernedSourceAdapter" in adapter_source
    assert "AppliedConversationalIntelligence" not in environment_source
    assert "AppliedConversationalIntelligence" not in runtime_source
    assert "published_after" not in environment_source
    assert "published_before" not in environment_source
