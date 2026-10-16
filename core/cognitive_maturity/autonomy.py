from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from core.controlled_autonomy import AutonomyLevel, RiskLevel

from .permissions import PermissionMode


class GovernedAutonomyStage(IntEnum):
    INFORM = 0
    RECOMMEND = 1
    PREPARE = 2
    EXECUTE_PREVALIDATED = 3
    RESOLVE_MINOR_EXCEPTIONS = 4
    REQUEST_EXPANSION = 5


@dataclass(frozen=True)
class GovernedAutonomyStageDefinition:
    stage: GovernedAutonomyStage
    title: str
    purpose: str
    runtime_level: AutonomyLevel
    maximum_runtime_risk: RiskLevel
    permitted_permission_modes: frozenset[PermissionMode]
    required_conditions: tuple[str, ...]
    forbidden_behaviors: tuple[str, ...]
    may_execute: bool
    requires_active_delegation: bool
    requires_reversibility: bool
    requires_audit: bool
    request_only: bool = False
    may_expand_scope: bool = False
    grants_action_authority: bool = False

    def __post_init__(self) -> None:
        text = (
            self.title,
            self.purpose,
            *self.required_conditions,
            *self.forbidden_behaviors,
        )
        if any(not item.strip() for item in text):
            raise ValueError("governed autonomy stage text must not be blank")
        for values in (
            self.permitted_permission_modes,
            self.required_conditions,
            self.forbidden_behaviors,
        ):
            if not values or len(values) != len(set(values)):
                raise ValueError(
                    "governed autonomy stage collections must be nonempty and unique"
                )
        if self.grants_action_authority or self.may_expand_scope:
            raise ValueError("autonomy stages cannot grant or expand authority")
        executable_stages = {
            GovernedAutonomyStage.EXECUTE_PREVALIDATED,
            GovernedAutonomyStage.RESOLVE_MINOR_EXCEPTIONS,
        }
        if self.may_execute is not (self.stage in executable_stages):
            raise ValueError("only stages three and four may describe execution")
        if self.may_execute:
            if self.runtime_level is not AutonomyLevel.AUTONOMOUS_LOW_RISK:
                raise ValueError("execution requires existing low-risk autonomy gate")
            if self.maximum_runtime_risk is not RiskLevel.LOW:
                raise ValueError("autonomous execution must remain low risk")
            if not all(
                (
                    self.requires_active_delegation,
                    self.requires_reversibility,
                    self.requires_audit,
                )
            ):
                raise ValueError(
                    "autonomous execution requires delegation, reversal and audit"
                )
        if self.request_only is not (
            self.stage is GovernedAutonomyStage.REQUEST_EXPANSION
        ):
            raise ValueError("only stage five is request-only")


def _stage(
    stage: GovernedAutonomyStage,
    title: str,
    purpose: str,
    runtime_level: AutonomyLevel,
    modes: frozenset[PermissionMode],
    conditions: tuple[str, ...],
    forbidden: tuple[str, ...],
    *,
    may_execute: bool = False,
    requires_active_delegation: bool = False,
    requires_reversibility: bool = False,
    requires_audit: bool = False,
    request_only: bool = False,
) -> GovernedAutonomyStageDefinition:
    return GovernedAutonomyStageDefinition(
        stage=stage,
        title=title,
        purpose=purpose,
        runtime_level=runtime_level,
        maximum_runtime_risk=RiskLevel.LOW,
        permitted_permission_modes=modes,
        required_conditions=conditions,
        forbidden_behaviors=forbidden,
        may_execute=may_execute,
        requires_active_delegation=requires_active_delegation,
        requires_reversibility=requires_reversibility,
        requires_audit=requires_audit,
        request_only=request_only,
    )


GOVERNED_AUTONOMY_STAGES = (
    _stage(
        GovernedAutonomyStage.INFORM,
        "Informar",
        "Observar, describir y explicar sin recomendar ni actuar.",
        AutonomyLevel.OBSERVE_ONLY,
        frozenset({PermissionMode.INTERNAL}),
        ("Conservar evidencia y límites.", "No producir efectos externos."),
        ("Recomendar como si fuera una decisión.", "Ejecutar o persistir cambios."),
    ),
    _stage(
        GovernedAutonomyStage.RECOMMEND,
        "Recomendar",
        "Comparar alternativas y sugerir una opción sin ejecutarla.",
        AutonomyLevel.RECOMMEND,
        frozenset({PermissionMode.INTERNAL, PermissionMode.PROPOSE_ONLY}),
        ("Explicar razones y riesgos.", "Mantener la decisión en Carlos y Cristina."),
        ("Presentar la recomendación como orden.", "Ejecutar la opción elegida."),
    ),
    _stage(
        GovernedAutonomyStage.PREPARE,
        "Preparar",
        "Construir un plan o borrador listo para revisión, sin ejecutarlo.",
        AutonomyLevel.CONFIRM_BEFORE_ACTION,
        frozenset(
            {
                PermissionMode.INTERNAL,
                PermissionMode.PROPOSE_ONLY,
                PermissionMode.CONFIRMATION_REQUIRED,
            }
        ),
        ("Identificar efecto y destinatario.", "Esperar confirmación efectiva."),
        ("Confundir preparación con autorización.", "Usar confirmación anterior."),
    ),
    _stage(
        GovernedAutonomyStage.EXECUTE_PREVALIDATED,
        "Ejecutar lo preconvalidado",
        "Ejecutar una acción concreta dentro de una delegación activa y acotada.",
        AutonomyLevel.AUTONOMOUS_LOW_RISK,
        frozenset({PermissionMode.DELEGABLE}),
        (
            "Superar matriz, consentimiento y compuerta de riesgo bajo.",
            "Registrar decisión, ejecución y resultado.",
        ),
        ("Ejecutar riesgo alto o crítico.", "Ampliar alcance durante la ejecución."),
        may_execute=True,
        requires_active_delegation=True,
        requires_reversibility=True,
        requires_audit=True,
    ),
    _stage(
        GovernedAutonomyStage.RESOLVE_MINOR_EXCEPTIONS,
        "Resolver excepciones menores",
        "Elegir una recuperación segura dentro de la misma facultad delegada.",
        AutonomyLevel.AUTONOMOUS_LOW_RISK,
        frozenset({PermissionMode.DELEGABLE}),
        (
            "Mantener objetivo, alcance, riesgo y permiso originales.",
            "Aplicar límites de reintento y prevención de bucles.",
        ),
        (
            "Cambiar de objetivo o capacidad.",
            "Ocultar degradación o convertir una excepción en nueva regla.",
        ),
        may_execute=True,
        requires_active_delegation=True,
        requires_reversibility=True,
        requires_audit=True,
    ),
    _stage(
        GovernedAutonomyStage.REQUEST_EXPANSION,
        "Solicitar ampliación",
        "Explicar por qué una facultad nueva podría ser útil y pedir revisión.",
        AutonomyLevel.RECOMMEND,
        frozenset({PermissionMode.PROPOSE_ONLY}),
        ("Describir beneficio, riesgo y límites.", "Esperar decisión humana."),
        ("Concederse la facultad solicitada.", "Actuar mientras espera aprobación."),
        request_only=True,
    ),
)


AUTONOMY_GOVERNANCE_POLICY = (
    "Una etapa de autonomía nunca equivale a permiso de acción.",
    "La matriz, el consentimiento y la compuerta operativa se aplican conjuntamente.",
    "Toda denegación, revocación o conflicto bloquea la acción afectada.",
    "La falta de evidencia, confianza o capacidad obliga a degradar o abstenerse.",
    "Las acciones altas, críticas, irreversibles o no acotadas nunca son autónomas.",
    "Solo Carlos o Cristina pueden aprobar una ampliación de facultades.",
)


def governed_autonomy_stage(
    stage: GovernedAutonomyStage | int,
) -> GovernedAutonomyStageDefinition:
    normalized = GovernedAutonomyStage(stage)
    for definition in GOVERNED_AUTONOMY_STAGES:
        if definition.stage is normalized:
            return definition
    raise KeyError(stage)

