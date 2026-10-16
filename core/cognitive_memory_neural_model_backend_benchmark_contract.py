"""Pure, advisory validation for a future offline model/backend experiment.

No acquisition, execution, provider loading, or productive admission occurs here.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

MODEL_REPOSITORY = "BAAI/bge-reranker-v2-m3"
EXECUTION_PROVIDER = "CPUExecutionProvider"
REFERENCE_ABS_TOLERANCE = 1e-4
GO_DECISION = "GO_FOR_ADMISSION_REVIEW"
EXPERIMENT_PHASES = (
    "ACQUISITION",
    "VERIFICATION",
    "OFFLINE_BENCHMARK",
    "ADMISSION_REVIEW",
)
_SHA256 = re.compile(r"[0-9a-fA-F]{64}\Z")
_REVISION = re.compile(r"[0-9a-fA-F]{40}\Z")


@dataclass(frozen=True)
class ArtifactHash:
    path: str
    sha256: str


@dataclass(frozen=True)
class ExperimentManifest:
    model_repository: str
    model_revision: str
    license_id: str
    artifact_hashes: tuple[ArtifactHash, ...]
    onnx_artifact_sha256: str
    python_version: str
    runtime_version: str
    execution_provider: str
    optimization_mode: str
    quantization_mode: str
    corpus_version: str
    hardware_fingerprint: str


@dataclass(frozen=True)
class ModelBackendBenchmarkReport:
    manifest_verified: bool
    measured_offline: bool
    synthetic_non_private: bool
    candidate_membership_unchanged: bool
    governance_violations: int
    lexical_exact_regressions: int
    semantic_mrr_delta: float
    semantic_ndcg_delta: float
    semantic_cases_improved: int
    semantic_cases_total: int
    scores_valid: bool
    parity_passed: bool
    p50_latency_ms: float
    p95_latency_ms: float
    max_latency_ms: float
    cold_start_ms: float
    warmup_runs: int
    measured_samples: int
    execution_provider: str


def validate_manifest(manifest: object) -> bool:
    if not isinstance(manifest, ExperimentManifest):
        return False
    if manifest.model_repository != MODEL_REPOSITORY:
        return False
    if not _REVISION.fullmatch(manifest.model_revision):
        return False
    if manifest.license_id != "Apache-2.0":
        return False
    if manifest.execution_provider != EXECUTION_PROVIDER:
        return False
    if not manifest.artifact_hashes:
        return False
    if not all(
        isinstance(artifact, ArtifactHash)
        and bool(artifact.path)
        and not artifact.path.startswith(("/", "\\"))
        and ".." not in artifact.path.replace("\\", "/").split("/")
        and bool(_SHA256.fullmatch(artifact.sha256))
        for artifact in manifest.artifact_hashes
    ):
        return False
    if len({a.path for a in manifest.artifact_hashes}) != len(manifest.artifact_hashes):
        return False
    hashes = {a.path: a.sha256 for a in manifest.artifact_hashes}
    if not {"config.json", "tokenizer.json", "model.onnx"} <= hashes.keys():
        return False
    if hashes["model.onnx"] != manifest.onnx_artifact_sha256:
        return False
    return all(
        isinstance(value, str) and bool(value.strip())
        for value in (
            manifest.python_version,
            manifest.runtime_version,
            manifest.optimization_mode,
            manifest.quantization_mode,
            manifest.corpus_version,
            manifest.hardware_fingerprint,
        )
    )


def phase_can_authorize_next(phase: str) -> bool:
    del phase
    return False


def reference_parity(reference: object, observed: object) -> bool:
    try:
        left = tuple(reference)
        right = tuple(observed)
        if not left or len(left) != len(right):
            return False
        if not all(
            isinstance(a, (int, float))
            and not isinstance(a, bool)
            and isinstance(b, (int, float))
            and not isinstance(b, bool)
            and math.isfinite(a)
            and math.isfinite(b)
            and abs(a - b) <= REFERENCE_ABS_TOLERANCE
            for a, b in zip(left, right)
        ):
            return False
        def rank(values):
            return sorted(
                range(len(values)), key=lambda index: (-values[index], index)
            )

        return rank(left) == rank(right)
    except (TypeError, ValueError, OverflowError):
        return False


def latency_evidence_complete(report: object) -> bool:
    if not isinstance(report, ModelBackendBenchmarkReport):
        return False
    values = (
        report.p50_latency_ms,
        report.p95_latency_ms,
        report.max_latency_ms,
        report.cold_start_ms,
    )
    if not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
        for value in values
    ):
        return False
    return (
        report.p50_latency_ms <= report.p95_latency_ms <= report.max_latency_ms
        and type(report.warmup_runs) is int
        and report.warmup_runs > 0
        and type(report.measured_samples) is int
        and report.measured_samples > 0
    )


def go_no_go(report: object) -> str:
    if not isinstance(report, ModelBackendBenchmarkReport):
        return "NO-GO"
    if not latency_evidence_complete(report):
        return "NO-GO"
    if not all(
        value is True
        for value in (
            report.manifest_verified,
            report.measured_offline,
            report.synthetic_non_private,
            report.candidate_membership_unchanged,
            report.scores_valid,
            report.parity_passed,
        )
    ):
        return "NO-GO"
    if report.execution_provider != EXECUTION_PROVIDER:
        return "NO-GO"
    if type(report.governance_violations) is not int:
        return "NO-GO"
    if type(report.lexical_exact_regressions) is not int:
        return "NO-GO"
    if report.governance_violations != 0 or report.lexical_exact_regressions != 0:
        return "NO-GO"
    if not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
        for value in (report.semantic_mrr_delta, report.semantic_ndcg_delta)
    ):
        return "NO-GO"
    if type(report.semantic_cases_improved) is not int:
        return "NO-GO"
    if type(report.semantic_cases_total) is not int:
        return "NO-GO"
    if not (
        report.semantic_cases_total > 0
        and report.semantic_cases_total // 2 < report.semantic_cases_improved
        <= report.semantic_cases_total
    ):
        return "NO-GO"
    return GO_DECISION
