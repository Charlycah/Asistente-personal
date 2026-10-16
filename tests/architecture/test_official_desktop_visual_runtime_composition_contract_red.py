from __future__ import annotations

import dataclasses
import importlib
import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.ui_adapter import UIResponse
from core.end_to_end_local_conversation import LocalConversationTurn

MODULE = "app.same_turn_governed_visual_result_exposure"
ROOT = Path(__file__).resolve().parents[2]


def _module():
    return importlib.import_module(MODULE)


def _turn(text: str = "respuesta") -> LocalConversationTurn:
    return LocalConversationTurn(
        owner="Carlos y Cristina",
        session_id="desktop-main",
        sequence=1,
        user_text="consulta",
        response_text=text,
        status="completed",
        pipeline_result_id="pipeline-1",
        operational_response_id="response-1",
        provider_call_performed=False,
        retrieval_performed=True,
        network_access_performed=True,
        rationale=("same_turn_governed_result",),
        response_path="interceptor",
    )


def _applied(text: str = "respuesta") -> object:
    return SimpleNamespace(
        natural_answer_text=text,
        conversational_result=SimpleNamespace(items=()),
    )


def test_same_turn_exposure_is_immutable() -> None:
    module = _module()
    exposure = module.SameTurnGovernedVisualResult(
        turn=_turn(),
        applied_result=_applied(),
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        exposure.applied_result = None


def test_recognized_path_executes_applied_owner_turn_once() -> None:
    module = _module()
    calls = {"applied": 0, "fallback": 0}
    turn = _turn()
    applied = _applied()

    def execute_applied(text: str, session_id: str | None = None) -> object:
        calls["applied"] += 1
        return SimpleNamespace(turn=turn, applied_result=applied)

    def execute_fallback(text: str, session_id: str | None = None) -> object:
        calls["fallback"] += 1
        return _turn("fallback")

    result = module.expose_same_turn_governed_visual_result(
        execute_applied=execute_applied,
        execute_fallback=execute_fallback,
        text="James Webb",
        session_id="desktop-main",
    )

    assert calls == {"applied": 1, "fallback": 0}
    assert result.turn is turn
    assert result.applied_result is applied


def test_fallback_path_executes_normal_owner_turn_once() -> None:
    module = _module()
    calls = {"applied": 0, "fallback": 0}
    turn = _turn("normal")

    def execute_applied(text: str, session_id: str | None = None) -> object:
        calls["applied"] += 1
        return None

    def execute_fallback(text: str, session_id: str | None = None) -> object:
        calls["fallback"] += 1
        return turn

    result = module.expose_same_turn_governed_visual_result(
        execute_applied=execute_applied,
        execute_fallback=execute_fallback,
        text="hola",
        session_id="desktop-main",
    )

    assert calls == {"applied": 1, "fallback": 1}
    assert result.turn is turn
    assert result.applied_result is None


def test_exposure_preserves_exact_admitted_applied_result() -> None:
    module = _module()
    turn = _turn()
    applied = _applied()

    result = module.SameTurnGovernedVisualResult(
        turn=turn,
        applied_result=applied,
    )

    assert result.turn is turn
    assert result.applied_result is applied


def test_exposure_does_not_parse_visual_identity_from_text() -> None:
    module = _module()
    source = inspect.getsource(module).casefold()

    assert "preview_url" not in source
    assert "http://" not in source
    assert "https://" not in source
    assert "urlparse" not in source


def test_existing_turn_contract_remains_unchanged() -> None:
    expected = (
        "owner",
        "session_id",
        "sequence",
        "user_text",
        "response_text",
        "status",
        "pipeline_result_id",
        "operational_response_id",
        "provider_call_performed",
        "retrieval_performed",
        "network_access_performed",
        "rationale",
        "response_path",
        "degradation_reason",
        "created_at",
        "turn_id",
    )
    assert tuple(LocalConversationTurn.__dataclass_fields__) == expected


def test_existing_ui_response_contract_remains_unchanged() -> None:
    assert tuple(UIResponse.__dataclass_fields__) == (
        "text",
        "status",
        "session_id",
        "needs_input",
    )


def test_exposure_source_has_no_parallel_authority() -> None:
    module = _module()
    source = inspect.getsource(module).casefold()
    forbidden = (
        "officialconversationgateway(",
        "unifiedbrain(",
        "governedsourcequeryexecutor(",
        "nasagovernedsourceadapter",
        "desktopconversationcontroller(",
        "thread(",
        "threadpool",
        "mainloop(",
    )

    assert not any(token in source for token in forbidden)


def test_exposure_does_not_claim_reachability_or_freshness() -> None:
    module = _module()
    source = inspect.getsource(module).casefold()

    assert "mostrame fotos" not in source
    assert "últimas" not in source
    assert "ultimas" not in source
    assert "newest" not in source
    assert "latest" not in source


def test_runtime_composition_has_same_turn_exposure_surface() -> None:
    module = _module()
    method = getattr(
        module.SameTurnVisualRuntimeComposition,
        "process_with_visual_result",
        None,
    )

    assert callable(method)


def test_ui_composition_has_same_turn_visual_transport_surface() -> None:
    module = _module()
    method = getattr(
        module.SameTurnVisualUIAdapterComposition,
        "submit_text_with_visual_companion",
        None,
    )

    assert callable(method)


def test_desktop_controller_has_optional_same_turn_visual_surface() -> None:
    from app.desktop_ui import DesktopConversationController

    method = getattr(
        DesktopConversationController,
        "submit_with_visual_companion",
        None,
    )

    assert callable(method)
