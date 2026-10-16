from __future__ import annotations

from core.controlled_autonomy import CapabilityRunResult, CapabilityRunStatus
from core.controlled_autonomy.contracts import OutcomeStatus


def render_autonomy_notification(result: CapabilityRunResult) -> str | None:
    """Render one concise user-facing explanation for an executed cycle."""

    if result.status is not CapabilityRunStatus.EXECUTED:
        return None
    candidate = result.candidate
    outcome = result.outcome
    if candidate is None or outcome is None:
        return None
    if candidate.action == "diagnose_audio_runtime":
        return _render_audio_result(outcome.status, outcome.evidence)
    if candidate.action == "verify_component_health":
        return _render_health_result(outcome.status, outcome.evidence)
    return (
        "Roby completó una acción autónoma de solo lectura: "
        f"{candidate.action}. Resultado: {_status_label(outcome.status)}. "
        "No realizó cambios automáticos."
    )


def _render_audio_result(
    status: OutcomeStatus,
    evidence: tuple[str, ...],
) -> str:
    if status is OutcomeStatus.SUCCEEDED:
        return (
            "Diagnóstico autónomo de audio completado: el motor está "
            "operativo. No fue necesario realizar cambios."
        )
    detail = _evidence_value(evidence, "error")
    if status is OutcomeStatus.DEGRADED:
        suffix = f" Detalle: {detail}." if detail else ""
        return (
            "Diagnóstico autónomo de audio completado: detecté una "
            f"degradación.{suffix} No realicé cambios automáticos."
        )
    if status is OutcomeStatus.FAILED:
        suffix = f" Detalle: {detail}." if detail else ""
        return (
            "No pude completar el diagnóstico autónomo de audio."
            f"{suffix} Se requiere revisión del usuario."
        )
    return (
        "El diagnóstico autónomo de audio no obtuvo un resultado "
        "concluyente. No realicé cambios automáticos."
    )


def _render_health_result(
    status: OutcomeStatus,
    evidence: tuple[str, ...],
) -> str:
    component = _evidence_value(evidence, "component_id") or "desconocido"
    health_state = _evidence_value(evidence, "health_state")
    if health_state:
        result_text = f"estado {health_state}"
    else:
        result_text = _status_label(status)
    return (
        f"Verificación autónoma de {component} completada: {result_text}. "
        "No realicé cambios automáticos."
    )


def _evidence_value(evidence: tuple[str, ...], key: str) -> str | None:
    prefix = f"{key}="
    for item in evidence:
        if item.startswith(prefix):
            value = item[len(prefix) :].strip()
            return value or None
    return None


def _status_label(status: OutcomeStatus) -> str:
    labels = {
        OutcomeStatus.SUCCEEDED: "correcto",
        OutcomeStatus.DEGRADED: "degradado",
        OutcomeStatus.FAILED: "fallido",
        OutcomeStatus.UNKNOWN: "desconocido",
        OutcomeStatus.NOT_EXECUTED: "no ejecutado",
    }
    return labels[status]
