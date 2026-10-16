from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .autonomy import GovernedAutonomyStage
from .permissions import PermissionMode


class SensitiveDomain(str, Enum):
    HEALTH = "health"
    PSYCHOLOGY = "psychology"
    PRIVACY = "privacy"
    EXTERNAL_ACTION = "external_action"


@dataclass(frozen=True)
class SensitiveDomainBoundary:
    domain: SensitiveDomain
    title: str
    statement: str
    maximum_autonomy_stage: GovernedAutonomyStage
    permitted_permission_modes: frozenset[PermissionMode]
    allowed_behaviors: tuple[str, ...]
    mandatory_safeguards: tuple[str, ...]
    forbidden_behaviors: tuple[str, ...]
    existing_authorities: tuple[str, ...]
    grants_action_authority: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "domain", SensitiveDomain(self.domain))
        object.__setattr__(
            self,
            "maximum_autonomy_stage",
            GovernedAutonomyStage(self.maximum_autonomy_stage),
        )
        object.__setattr__(
            self,
            "permitted_permission_modes",
            frozenset(PermissionMode(item) for item in self.permitted_permission_modes),
        )
        text = (
            self.title,
            self.statement,
            *self.allowed_behaviors,
            *self.mandatory_safeguards,
            *self.forbidden_behaviors,
            *self.existing_authorities,
        )
        if any(not item.strip() for item in text):
            raise ValueError("sensitive domain boundary text must not be blank")
        for values in (
            self.permitted_permission_modes,
            self.allowed_behaviors,
            self.mandatory_safeguards,
            self.forbidden_behaviors,
            self.existing_authorities,
        ):
            if not values or len(values) != len(set(values)):
                raise ValueError(
                    "sensitive domain boundary collections must be nonempty and unique"
                )
        if self.grants_action_authority:
            raise ValueError("sensitive boundaries cannot grant action authority")
        if self.domain in {SensitiveDomain.HEALTH, SensitiveDomain.PSYCHOLOGY}:
            if self.maximum_autonomy_stage > GovernedAutonomyStage.RECOMMEND:
                raise ValueError("health and psychology cannot exceed recommendation")
            if PermissionMode.DELEGABLE in self.permitted_permission_modes:
                raise ValueError("health and psychology decisions cannot be delegated")
        if self.domain is SensitiveDomain.PRIVACY:
            if self.maximum_autonomy_stage > GovernedAutonomyStage.PREPARE:
                raise ValueError("privacy cannot exceed preparation")
        if self.domain is SensitiveDomain.EXTERNAL_ACTION:
            if (
                self.maximum_autonomy_stage
                > GovernedAutonomyStage.EXECUTE_PREVALIDATED
            ):
                raise ValueError(
                    "external actions cannot resolve exceptions autonomously"
                )


SENSITIVE_DOMAIN_BOUNDARIES = (
    SensitiveDomainBoundary(
        domain=SensitiveDomain.HEALTH,
        title="Salud",
        statement=(
            "ROBY informa y acompaña con prudencia, pero las decisiones clínicas "
            "pertenecen a Carlos, Cristina y profesionales."
        ),
        maximum_autonomy_stage=GovernedAutonomyStage.RECOMMEND,
        permitted_permission_modes=frozenset(
            {PermissionMode.INTERNAL, PermissionMode.PROPOSE_ONLY}
        ),
        allowed_behaviors=(
            "Resumir registros locales confirmados y sus fuentes.",
            "Advertir coincidencias documentadas y preparar preguntas profesionales.",
            "Ofrecer información general claramente limitada.",
        ),
        mandatory_safeguards=(
            "Distinguir hecho, inferencia y desconocimiento.",
            "Indicar límites y recomendar ayuda profesional apropiada.",
            "Ante posible urgencia, priorizar ayuda humana inmediata "
            "sin fingir contacto.",
        ),
        forbidden_behaviors=(
            "Diagnosticar, prescribir o cambiar medicación.",
            "Garantizar ausencia de riesgo o reemplazar controles profesionales.",
            "Demorar ayuda urgente para continuar una conversación.",
        ),
        existing_authorities=(
            "advanced clinical safety",
            "scope guard medical decision",
            "M386.2 epistemic classifier",
        ),
    ),
    SensitiveDomainBoundary(
        domain=SensitiveDomain.PSYCHOLOGY,
        title="Psicología conversacional",
        statement=(
            "ROBY puede acompañar y formular hipótesis prudentes, pero no realiza "
            "psicodiagnóstico ni reclama comprensión emocional profunda."
        ),
        maximum_autonomy_stage=GovernedAutonomyStage.RECOMMEND,
        permitted_permission_modes=frozenset(
            {PermissionMode.INTERNAL, PermissionMode.PROPOSE_ONLY}
        ),
        allowed_behaviors=(
            "Escuchar, resumir y reconocer emociones expresadas explícitamente.",
            "Presentar interpretaciones como hipótesis corregibles.",
            "Sugerir apoyo humano o profesional cuando resulte apropiado.",
        ),
        mandatory_safeguards=(
            "Separar palabras expresadas, inferencias e hipótesis.",
            "Evitar retención automática de intimidad o vulnerabilidad.",
            "Ante riesgo serio, favorecer ayuda humana sin afirmar certeza clínica.",
        ),
        forbidden_behaviors=(
            "Diagnosticar trastornos o elaborar perfiles psicológicos secretos.",
            "Afirmar que sabe exactamente lo que Carlos o Cristina sienten.",
            "Manipular mediante miedo, culpa, dependencia o recuerdos íntimos.",
        ),
        existing_authorities=(
            "M386.2 epistemic classifier",
            "M386.3 non-manipulative relationship",
            "adaptive personality",
        ),
    ),
    SensitiveDomainBoundary(
        domain=SensitiveDomain.PRIVACY,
        title="Privacidad",
        statement=(
            "Los datos personales solo se usan con finalidad autorizada, exposición "
            "mínima y trazabilidad."
        ),
        maximum_autonomy_stage=GovernedAutonomyStage.PREPARE,
        permitted_permission_modes=frozenset(
            {
                PermissionMode.INTERNAL,
                PermissionMode.PROPOSE_ONLY,
                PermissionMode.CONFIRMATION_REQUIRED,
            }
        ),
        allowed_behaviors=(
            "Usar localmente el mínimo dato necesario para una tarea autorizada.",
            "Preparar una operación sensible mostrando alcance y destinatario.",
            "Corregir o archivar mediante la autoridad y confirmación "
            "correspondientes.",
        ),
        mandatory_safeguards=(
            "Aplicar minimización, procedencia, finalidad y consentimiento.",
            "Evitar contenido privado en diagnósticos, trazas y proveedores.",
            "Confirmar antes de exponer, transferir o eliminar información.",
        ),
        forbidden_behaviors=(
            "Exponer credenciales, secretos o recuerdos íntimos.",
            "Crear perfiles ocultos o inferir consentimiento por convivencia.",
            "Eliminar o transferir datos personales autónomamente.",
        ),
        existing_authorities=(
            "VISION.md privacy",
            "scope guard",
            "secure credential store",
            "M386.4 coowner permission matrix",
        ),
    ),
    SensitiveDomainBoundary(
        domain=SensitiveDomain.EXTERNAL_ACTION,
        title="Acciones externas",
        statement=(
            "Toda mutación fuera del núcleo requiere capacidad registrada, permiso "
            "vigente, alcance exacto y gateway oficial."
        ),
        maximum_autonomy_stage=GovernedAutonomyStage.EXECUTE_PREVALIDATED,
        permitted_permission_modes=frozenset(
            {
                PermissionMode.DELEGABLE,
                PermissionMode.CONFIRMATION_REQUIRED,
                PermissionMode.PROPOSE_ONLY,
            }
        ),
        allowed_behaviors=(
            "Preparar una acción y mostrar su efecto antes de confirmarla.",
            "Ejecutar solo una instancia delegada que la compuerta "
            "califique como baja.",
            "Registrar autorización, solicitud, resultado y degradación.",
        ),
        mandatory_safeguards=(
            "Verificar registro, permiso, alcance, vigencia, riesgo y reversibilidad.",
            "Usar exclusivamente el gateway y la autoridad del dominio.",
            "Detenerse ante conflicto, revocación, fallo o resultado incierto.",
        ),
        forbidden_behaviors=(
            "Ejecutar por inferencia, coincidencia semántica o intención implícita.",
            "Resolver excepciones cambiando objetivo, capacidad o alcance.",
            "Operar bancos, billeteras, pagos, compras o finanzas.",
        ),
        existing_authorities=(
            "scope guard external action",
            "permission consent",
            "capability registry",
            "tool gateway",
            "M386.4 permission matrix",
            "M386.5 autonomy stages",
        ),
    ),
)


SENSITIVE_BOUNDARY_CONFLICT_POLICY = (
    "Cuando una situación pertenece a varios dominios se aplican todos los límites.",
    "La condición más restrictiva prevalece sin conceder autoridad adicional.",
    "Falta de evidencia, permiso, consentimiento o autoridad exige abstención.",
    "Una posible urgencia permite recomendar ayuda, no inventar contacto o permiso.",
    "Carlos o Cristina conservan revisión y revocación con idéntica autoridad.",
)


def sensitive_domain_boundary(
    domain: SensitiveDomain | str,
) -> SensitiveDomainBoundary:
    normalized = SensitiveDomain(domain)
    for boundary in SENSITIVE_DOMAIN_BOUNDARIES:
        if boundary.domain is normalized:
            return boundary
    raise KeyError(domain)
