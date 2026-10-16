from __future__ import annotations

from dataclasses import dataclass

from .decision_kernel import CognitiveDecisionKernel
from .observability import CognitiveObservabilityProfile
from .planner import CognitivePlanner


@dataclass(frozen=True)
class CognitiveKernelDiagnosticReport:
    """Side-effect-free validation report for Doctor integration."""

    schema_version: str
    passed: bool
    check_codes: tuple[str, ...]
    failure_codes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "passed": self.passed,
            "check_codes": list(self.check_codes),
            "failure_codes": list(self.failure_codes),
        }


class CognitiveKernelDiagnostic:
    """Validate kernel contracts without providers, persistence, or external I/O."""

    SCHEMA_VERSION = "rp22.16"

    def run(self) -> CognitiveKernelDiagnosticReport:
        checks: list[str] = []
        failures: list[str] = []

        try:
            kernel = CognitiveDecisionKernel()
            checks.append("kernel_constructed")
        except Exception:
            return self._report(checks, ("kernel_construction_failed",))

        try:
            plan = CognitivePlanner().plan("Hola")
            decision = kernel.consolidate(plan)
            checks.append("decision_consolidated")
        except Exception:
            return self._report(checks, ("decision_consolidation_failed",))

        self._check(
            decision.explanation.schema_version == "rp22.02",
            "explanation_schema_valid",
            "explanation_schema_invalid",
            checks,
            failures,
        )
        self._check(
            decision.calibration.schema_version == "rp22.03",
            "calibration_schema_valid",
            "calibration_schema_invalid",
            checks,
            failures,
        )

        try:
            snapshot = kernel.metrics_snapshot
            payload = snapshot.as_dict()
            metrics_valid = (
                snapshot.schema_version == "rp22.04"
                and payload.get("total_decisions") == 1
            )
        except Exception:
            metrics_valid = False
        self._check(
            metrics_valid,
            "metrics_snapshot_valid",
            "metrics_snapshot_invalid",
            checks,
            failures,
        )

        try:
            export = kernel.export_observability(
                decision,
                profile=CognitiveObservabilityProfile.DIAGNOSTIC,
            )
            export_payload = export.as_dict()
            observability_valid = (
                export.schema_version == "rp22.05"
                and export_payload.get("explanation", {}).get("narrative")
                == "[redacted]"
                and "explanation_narrative_redacted" in export.redaction_codes
            )
        except Exception:
            observability_valid = False
        self._check(
            observability_valid,
            "observability_export_valid",
            "observability_export_invalid",
            checks,
            failures,
        )

        try:
            decision_log = kernel.decision_log_snapshot
            log_payload = decision_log.as_dict()
            decision_log_valid = (
                decision_log.schema_version == "rp22.07"
                and log_payload.get("total_recorded") == 1
                and len(log_payload.get("events", [])) == 1
                and "narrative" not in str(log_payload)
            )
        except Exception:
            decision_log_valid = False
        self._check(
            decision_log_valid,
            "decision_log_valid",
            "decision_log_invalid",
            checks,
            failures,
        )

        try:
            trace_snapshot = kernel.trace_snapshot
            trace_payload = trace_snapshot.as_dict()
            correlation = decision.correlation
            trace_valid = (
                trace_snapshot.schema_version == "rp22.08"
                and trace_payload.get("total_correlations") == 1
                and correlation is not None
                and len(correlation.trace_id) == 24
                and "Hola" not in str(trace_payload)
            )
        except Exception:
            trace_valid = False
        self._check(
            trace_valid,
            "decision_trace_valid",
            "decision_trace_invalid",
            checks,
            failures,
        )

        try:
            query_result = kernel.query_traces()
            query_payload = query_result.as_dict()
            trace_query_valid = (
                query_result.schema_version == "rp22.09"
                and query_payload.get("matched_count") == 1
                and query_payload.get("returned_count") == 1
                and "Hola" not in str(query_payload)
                and query_result.applied_limit <= 50
            )
        except Exception:
            trace_query_valid = False
        self._check(
            trace_query_valid,
            "trace_retention_query_valid",
            "trace_retention_query_invalid",
            checks,
            failures,
        )

        try:
            analysis = kernel.analyze_traces()
            analysis_payload = analysis.as_dict()
            trace_analysis_valid = (
                analysis.schema_version == "rp22.10"
                and analysis_payload.get("analyzed_traces") == 1
                and sum(analysis_payload.get("policy_counts", {}).values()) == 1
                and "Hola" not in str(analysis_payload)
            )
        except Exception:
            trace_analysis_valid = False
        self._check(
            trace_analysis_valid,
            "trace_local_analysis_valid",
            "trace_local_analysis_invalid",
            checks,
            failures,
        )

        try:
            anomaly = kernel.detect_trace_anomalies()
            anomaly_payload = anomaly.as_dict()
            trace_anomaly_valid = (
                anomaly.schema_version == "rp22.11"
                and anomaly_payload.get("sample_size") == 1
                and anomaly_payload.get("eligible") is False
                and "Hola" not in str(anomaly_payload)
            )
        except Exception:
            trace_anomaly_valid = False
        self._check(
            trace_anomaly_valid,
            "trace_local_anomaly_detection_valid",
            "trace_local_anomaly_detection_invalid",
            checks,
            failures,
        )

        try:
            priority = kernel.prioritize_trace_anomalies()
            priority_payload = priority.as_dict()
            trace_priority_valid = (
                priority.schema_version == "rp22.12"
                and priority_payload.get("prioritized_count") == 0
                and "Hola" not in str(priority_payload)
            )
        except Exception:
            trace_priority_valid = False
        self._check(
            trace_priority_valid,
            "trace_local_anomaly_priority_valid",
            "trace_local_anomaly_priority_invalid",
            checks,
            failures,
        )

        try:
            consolidation = kernel.consolidate_trace_anomalies((priority, priority))
            consolidation_payload = consolidation.as_dict()
            trace_consolidation_valid = (
                consolidation.schema_version == "rp22.13"
                and consolidation_payload.get("input_snapshot_count") == 2
                and consolidation_payload.get("consolidated_count") == 0
                and "Hola" not in str(consolidation_payload)
            )
        except Exception:
            trace_consolidation_valid = False
        self._check(
            trace_consolidation_valid,
            "trace_local_anomaly_consolidation_valid",
            "trace_local_anomaly_consolidation_invalid",
            checks,
            failures,
        )

        try:
            lifecycle = kernel.update_trace_anomaly_lifecycle(consolidation)
            lifecycle_payload = lifecycle.as_dict()
            trace_lifecycle_valid = (
                lifecycle.schema_version == "rp22.14"
                and lifecycle_payload.get("record_count") == 0
                and "Hola" not in str(lifecycle_payload)
            )
        except Exception:
            trace_lifecycle_valid = False
        self._check(
            trace_lifecycle_valid,
            "trace_local_anomaly_lifecycle_valid",
            "trace_local_anomaly_lifecycle_invalid",
            checks,
            failures,
        )

        try:
            lifecycle_view = kernel.query_trace_anomaly_lifecycle()
            lifecycle_view_payload = lifecycle_view.as_dict()
            trace_lifecycle_query_valid = (
                lifecycle_view.schema_version == "rp22.15"
                and lifecycle_view_payload.get("returned_count") == 0
                and "Hola" not in str(lifecycle_view_payload)
            )
        except Exception:
            trace_lifecycle_query_valid = False
        self._check(
            trace_lifecycle_query_valid,
            "trace_local_anomaly_lifecycle_query_valid",
            "trace_local_anomaly_lifecycle_query_invalid",
            checks,
            failures,
        )

        try:
            lifecycle_comparison = kernel.compare_trace_anomaly_lifecycle(lifecycle)
            lifecycle_comparison_payload = lifecycle_comparison.as_dict()
            trace_lifecycle_comparison_valid = (
                lifecycle_comparison.schema_version == "rp22.16"
                and lifecycle_comparison_payload.get("changed_count") == 0
                and "Hola" not in str(lifecycle_comparison_payload)
            )
        except Exception:
            trace_lifecycle_comparison_valid = False
        self._check(
            trace_lifecycle_comparison_valid,
            "trace_local_anomaly_lifecycle_comparison_valid",
            "trace_local_anomaly_lifecycle_comparison_invalid",
            checks,
            failures,
        )

        try:
            lifecycle_assessment = kernel.assess_trace_anomaly_lifecycle(
                lifecycle_comparison
            )
            lifecycle_assessment_payload = lifecycle_assessment.as_dict()
            trace_lifecycle_assessment_valid = (
                lifecycle_assessment.schema_version == "rp22.17"
                and lifecycle_assessment_payload.get("status") == "stable"
                and "Hola" not in str(lifecycle_assessment_payload)
            )
        except Exception:
            trace_lifecycle_assessment_valid = False
        self._check(
            trace_lifecycle_assessment_valid,
            "trace_local_anomaly_lifecycle_assessment_valid",
            "trace_local_anomaly_lifecycle_assessment_invalid",
            checks,
            failures,
        )

        try:
            lifecycle_guidance = kernel.advise_trace_anomaly_lifecycle(
                lifecycle_assessment
            )
            lifecycle_guidance_payload = lifecycle_guidance.as_dict()
            trace_lifecycle_guidance_valid = (
                lifecycle_guidance.schema_version == "rp22.18"
                and lifecycle_guidance_payload.get("urgency") == "none"
                and "Hola" not in str(lifecycle_guidance_payload)
            )
        except Exception:
            trace_lifecycle_guidance_valid = False
        self._check(
            trace_lifecycle_guidance_valid,
            "trace_local_anomaly_lifecycle_guidance_valid",
            "trace_local_anomaly_lifecycle_guidance_invalid",
            checks,
            failures,
        )

        try:
            explanation_serializable = isinstance(
                decision.explanation.as_dict(), dict
            )
            calibration_serializable = isinstance(
                decision.calibration.as_dict(), dict
            )
            serializable = explanation_serializable and calibration_serializable
        except Exception:
            serializable = False
        self._check(
            serializable,
            "contracts_serializable",
            "contracts_not_serializable",
            checks,
            failures,
        )

        return self._report(checks, tuple(failures))

    @classmethod
    def _report(
        cls,
        checks: list[str],
        failures: tuple[str, ...],
    ) -> CognitiveKernelDiagnosticReport:
        return CognitiveKernelDiagnosticReport(
            schema_version=cls.SCHEMA_VERSION,
            passed=not failures,
            check_codes=tuple(checks),
            failure_codes=failures,
        )

    @staticmethod
    def _check(
        condition: bool,
        success_code: str,
        failure_code: str,
        checks: list[str],
        failures: list[str],
    ) -> None:
        if condition:
            checks.append(success_code)
        else:
            failures.append(failure_code)
