from __future__ import annotations

from app.gmail_diagnostic_runtime import (
    GmailDiagnosticRuntime,
    GmailDiagnosticState,
    GmailDiagnosticTraceState,
)
from app.gmail_startup_wiring import announce_gmail_startup_from_environment
from infrastructure.mail.gmail_subject_announcement import GmailSubjectAnnouncement


def test_exception_trace_has_nine_ordered_stages():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("gmail unread subject lookup failed")
    )
    assert len(report.trace) == 9
    assert tuple(stage.ordinal for stage in report.trace) == tuple(range(1, 10))
    assert all(stage.total == 9 for stage in report.trace)


def test_subject_lookup_marks_startup_announcement_failed():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("gmail unread subject lookup failed")
    )
    assert report.trace[7].key == "startup_announcement"
    assert report.trace[7].state is GmailDiagnosticTraceState.FAILED
    assert report.trace[8].state is GmailDiagnosticTraceState.NOT_EXECUTED


def test_configuration_failure_stops_later_trace_stages():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("gmail startup account address is not configured")
    )
    assert report.trace[0].state is GmailDiagnosticTraceState.OK
    assert report.trace[1].state is GmailDiagnosticTraceState.FAILED
    assert all(
        stage.state is GmailDiagnosticTraceState.NOT_EXECUTED
        for stage in report.trace[2:]
    )


def test_google_auth_import_failure_marks_dependency_stage():
    report = GmailDiagnosticRuntime().from_exception(ImportError("private module"))
    assert report.trace[2].key == "google_auth"
    assert report.trace[2].state is GmailDiagnosticTraceState.FAILED


def test_secure_store_failure_marks_secure_store_stage():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("secure credential store read failed")
    )
    assert report.trace[4].key == "secure_credential_store"
    assert report.trace[4].state is GmailDiagnosticTraceState.FAILED


def test_token_failure_marks_token_and_scopes_stage():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("gmail oauth credentials are unavailable")
    )
    assert report.trace[5].key == "token"
    assert report.trace[5].state is GmailDiagnosticTraceState.FAILED


def test_disabled_environment_has_silent_console_and_disabled_trace(monkeypatch):
    monkeypatch.delenv("ROBY_GMAIL_ENABLED", raising=False)
    report = GmailDiagnosticRuntime().inspect_environment()
    assert report.state is GmailDiagnosticState.DISABLED
    assert report.console_lines() == ()
    assert report.trace[0].state is GmailDiagnosticTraceState.DISABLED
    assert all(
        stage.state is GmailDiagnosticTraceState.NOT_EXECUTED
        for stage in report.trace[1:]
    )


def test_compact_diagnostic_remains_first_console_line():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("gmail unread subject lookup failed")
    )
    lines = report.console_lines()
    assert lines[0].startswith(
        "GMAIL> DEGRADED [startup_announcement/subject_lookup_failed]:"
    )
    assert lines[1] == "GMAIL TRACE> 1/9 Runtime: OK"


def test_trace_console_lines_are_stable_and_machine_readable():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("secure credential store read failed")
    )
    assert "GMAIL TRACE> 5/9 Secure Credential Store: FAILED" in report.console_lines()
    assert report.console_lines()[-1].endswith("Runtime Completion: NOT_EXECUTED")


def test_trace_serialization_contains_no_exception_text():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("gmail unread subject lookup failed: private-value")
    )
    rendered = repr(report.to_dict())
    assert "private-value" not in rendered
    assert rendered.count("ordinal") == 9


def test_startup_wiring_emits_trace_after_runtime_failure(monkeypatch):
    class Announcer:
        def announce(self):
            raise RuntimeError("gmail unread subject lookup failed: private")

    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: Announcer(),
    )
    lines = []
    assert announce_gmail_startup_from_environment(write=lines.append) is None
    assert len(lines) == 10
    assert lines[0].startswith("GMAIL> DEGRADED")
    assert lines[8].endswith("Startup Announcement: FAILED")
    assert "private" not in " ".join(lines)


def test_successful_startup_contract_remains_unchanged(monkeypatch):
    result = GmailSubjectAnnouncement(subjects=(), text="")

    class Announcer:
        def announce(self):
            return result

    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: Announcer(),
    )
    lines = []
    assert announce_gmail_startup_from_environment(write=lines.append) is result
    assert lines == []
