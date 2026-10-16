from __future__ import annotations

from app.gmail_diagnostic_runtime import (
    GmailDiagnosticRuntime,
    GmailDiagnosticState,
    GmailDiagnosticTraceState,
)
from app.gmail_startup_wiring import announce_gmail_startup_from_environment
from infrastructure.mail.gmail_subject_announcement import GmailSubjectAnnouncement

_TRACE_ENV = "ROBY_GMAIL_DIAGNOSTIC_TRACE_ON_SUCCESS"


def _successful_announcer(result: GmailSubjectAnnouncement):
    class Announcer:
        def announce(self):
            return result

    return Announcer()


def test_success_report_is_ready_and_marks_all_stages_ok():
    report = GmailDiagnosticRuntime().from_success()

    assert report.state is GmailDiagnosticState.READY
    assert report.primary.code == "runtime_ready"
    assert len(report.trace) == 9
    assert all(stage.state is GmailDiagnosticTraceState.OK for stage in report.trace)


def test_success_report_console_has_compact_line_before_trace():
    lines = GmailDiagnosticRuntime().from_success().console_lines()

    assert len(lines) == 10
    assert lines[0] == (
        "GMAIL> READY [gmail/runtime_ready]: "
        "El subsistema Gmail completó correctamente el arranque."
    )
    assert lines[1] == "GMAIL TRACE> 1/9 Runtime: OK"
    assert lines[-1] == "GMAIL TRACE> 9/9 Runtime Completion: OK"


def test_success_trace_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv(_TRACE_ENV, raising=False)
    result = GmailSubjectAnnouncement(subjects=("Uno",), text="Tenés un correo nuevo.")
    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: _successful_announcer(result),
    )
    lines = []

    assert announce_gmail_startup_from_environment(write=lines.append) is result
    assert lines == ["Roby> Tenés un correo nuevo."]


def test_success_trace_is_emitted_only_after_success(monkeypatch):
    monkeypatch.setenv(_TRACE_ENV, "true")
    result = GmailSubjectAnnouncement(subjects=("Uno",), text="Tenés un correo nuevo.")
    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: _successful_announcer(result),
    )
    lines = []

    assert announce_gmail_startup_from_environment(write=lines.append) is result
    assert lines[0] == "Roby> Tenés un correo nuevo."
    assert lines[1].startswith("GMAIL> READY [gmail/runtime_ready]:")
    assert len(lines) == 11
    assert lines[-1].endswith("Runtime Completion: OK")


def test_success_trace_supports_empty_announcement_text(monkeypatch):
    monkeypatch.setenv(_TRACE_ENV, "yes")
    result = GmailSubjectAnnouncement(subjects=(), text="")
    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: _successful_announcer(result),
    )
    lines = []

    assert announce_gmail_startup_from_environment(write=lines.append) is result
    assert lines[0].startswith("GMAIL> READY")
    assert len(lines) == 10


def test_failure_never_emits_ready_trace(monkeypatch):
    monkeypatch.setenv(_TRACE_ENV, "true")

    class Announcer:
        def announce(self):
            raise RuntimeError("gmail unread subject lookup failed: private")

    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: Announcer(),
    )
    lines = []

    assert announce_gmail_startup_from_environment(write=lines.append) is None
    assert lines[0].startswith("GMAIL> DEGRADED")
    assert all("GMAIL> READY" not in line for line in lines)
    assert len(lines) == 10


def test_disabled_gmail_remains_silent_even_when_success_trace_requested(monkeypatch):
    monkeypatch.setenv(_TRACE_ENV, "true")
    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: None,
    )
    lines = []

    assert announce_gmail_startup_from_environment(write=lines.append) is None
    assert lines == []


def test_success_report_serialization_contains_only_stable_operational_data():
    rendered = repr(GmailDiagnosticRuntime().from_success().to_dict())

    assert "runtime_ready" in rendered
    assert "Runtime Completion" in rendered
    assert "access_token_value" not in rendered
    assert "refresh_token_value" not in rendered
    assert "credentials.json" not in rendered
