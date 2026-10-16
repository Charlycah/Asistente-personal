from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.productive_temporary_rule_intake import (
    ProductiveTemporaryRuleIntakeStatus,
)
from app.runtime_root_factory import build_runtime_root

NOW = datetime(2026, 8, 17, 22, 45, tzinfo=timezone.utc)
SESSION = "rf-e-3a8-session"
OTHER = "rf-e-3a8-other"
RULE_TEXT = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)
CASE_TEXT = (
    "La estación depende exclusivamente del sensor T para recibir temperatura. "
    "El sensor T dejó de responder y no existe alternativa."
)
UNKNOWN_CASE = (
    "La estación depende exclusivamente del sensor T para recibir temperatura. "
    "El sensor T dejó de responder y no sabemos si existe otra fuente."
)


def _root(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    return build_runtime_root()


def _reasoning(root):
    return root.dependencies.governed_reasoning_runtime


def test_teaching_productively_stores_only_session_local_compiled_spec(
    monkeypatch, tmp_path
):
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.SPEC_STORED
    assert result.pending_specs == 1
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_supported_case_instantiates_and_admits_into_same_canonical_registry(
    monkeypatch, tmp_path
):
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)
    registry = reasoning.orchestrator.inference_engine.registry

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    reasoning.evaluate_text(
        owner="Carlos",
        text=CASE_TEXT,
        now=NOW + timedelta(minutes=1),
        scope_reference=SESSION,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.RULE_ADMITTED
    assert result.admission is not None
    assert result.projection is not None
    assert result.pending_specs == 0
    assert registry.get(
        result.admission.rule.rule_id,
        result.admission.rule.version,
    ) is result.admission.rule
    assert result.admission.scope_reference == SESSION
    assert result.admission.rule.requires_review is True
    assert result.admission.rule.temporary is True


def test_unknown_alternative_never_admits_rule_or_projects_false_claim(
    monkeypatch, tmp_path
):
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    reasoning.evaluate_text(
        owner="Carlos",
        text=UNKNOWN_CASE,
        now=NOW + timedelta(minutes=1),
        scope_reference=SESSION,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status in {
        ProductiveTemporaryRuleIntakeStatus.CASE_INSUFFICIENT,
        ProductiveTemporaryRuleIntakeStatus.CASE_UNSUPPORTED,
    }
    assert result.projection is None
    assert result.admission is None
    assert result.pending_specs == 1
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_pending_teaching_is_isolated_from_other_session(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    reasoning.evaluate_text(
        owner="Carlos",
        text=CASE_TEXT,
        now=NOW + timedelta(minutes=1),
        scope_reference=OTHER,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.NO_CHANGE
    assert reasoning.productive_temporary_rule_intake.pending_count(SESSION) == 1
    assert reasoning.productive_temporary_rule_intake.pending_count(OTHER) == 0
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_pending_teaching_expires_without_admission(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    reasoning.evaluate_text(
        owner="Carlos",
        text=CASE_TEXT,
        now=NOW + timedelta(minutes=31),
        scope_reference=SESSION,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.NO_CHANGE
    assert result.pending_specs == 0
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_duplicate_teaching_is_idempotent_and_bounded(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    for offset in range(2):
        reasoning.evaluate_text(
            owner="Carlos",
            text=RULE_TEXT,
            now=NOW + timedelta(seconds=offset),
            scope_reference=SESSION,
        )

    intake = reasoning.productive_temporary_rule_intake
    assert intake.pending_count(SESSION) == 1


def test_ordinary_text_does_not_create_rule_intake_state(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text="¿Cómo está el estado del sistema?",
        now=NOW,
        scope_reference=SESSION,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.NO_CHANGE
    assert result.pending_specs == 0
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_intake_result_preserves_governed_non_persistent_limits(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.canonical_authority == "governed_reasoning"
    assert result.session_local is True
    for name in (
        "persistent",
        "creates_memory",
        "creates_learning_candidate",
        "modifies_learning",
        "grants_authority",
        "executes_actions",
    ):
        assert getattr(result, name) is False


def test_legacy_evaluate_text_without_scope_skips_productive_intake(
    monkeypatch, tmp_path
):
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(owner="Carlos", text=RULE_TEXT, now=NOW)

    assert reasoning.productive_temporary_rule_intake.last_result is None
    assert reasoning.orchestrator.inference_engine.registry.list() == ()
