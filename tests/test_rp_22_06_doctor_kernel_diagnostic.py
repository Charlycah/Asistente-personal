from app.development_console import run_doctor
from core.cognitive_planning import (
    CognitiveKernelDiagnostic,
    CognitiveKernelDiagnosticReport,
)


def test_kernel_diagnostic_validates_all_versioned_contracts():
    report = CognitiveKernelDiagnostic().run()

    assert report.schema_version == "rp22.16"
    assert report.passed
    assert report.failure_codes == ()
    assert "explanation_schema_valid" in report.check_codes
    assert "calibration_schema_valid" in report.check_codes
    assert "metrics_snapshot_valid" in report.check_codes
    assert "observability_export_valid" in report.check_codes
    assert "decision_log_valid" in report.check_codes
    assert "trace_local_analysis_valid" in report.check_codes


def test_kernel_diagnostic_report_is_serializable_and_immutable():
    report = CognitiveKernelDiagnostic().run()

    assert report.as_dict()["passed"] is True
    assert report.as_dict()["schema_version"] == "rp22.16"
    assert isinstance(report.check_codes, tuple)


def test_doctor_includes_required_cognitive_kernel_check(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    check = next(item for item in run_doctor() if item.name == "cognitive_kernel")

    assert check.required
    assert check.passed
    assert "rp22.16" in check.detail


def test_doctor_reports_diagnostic_failure_without_leaking_detail(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)

    def broken_run(self):
        return CognitiveKernelDiagnosticReport(
            schema_version="rp22.16",
            passed=False,
            check_codes=("kernel_constructed",),
            failure_codes=("metrics_snapshot_invalid",),
        )

    monkeypatch.setattr(CognitiveKernelDiagnostic, "run", broken_run)

    check = next(item for item in run_doctor() if item.name == "cognitive_kernel")

    assert not check.passed
    assert "metrics_snapshot_invalid" in check.detail
    assert "narrative" not in check.detail


def test_kernel_diagnostic_has_no_filesystem_side_effects(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    report = CognitiveKernelDiagnostic().run()

    assert report.passed
    assert list(tmp_path.iterdir()) == []
