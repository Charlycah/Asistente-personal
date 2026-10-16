from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CoownerIdentity(str, Enum):
    CARLOS = "Carlos"
    CRISTINA = "Cristina"


class PermissionRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionMode(str, Enum):
    INTERNAL = "internal"
    DELEGABLE = "delegable"
    CONFIRMATION_REQUIRED = "confirmation_required"
    PROPOSE_ONLY = "propose_only"
    FORBIDDEN = "forbidden"


EQUAL_COOWNERS = frozenset({CoownerIdentity.CARLOS, CoownerIdentity.CRISTINA})


@dataclass(frozen=True)
class CoownerPermissionRule:
    action_id: str
    title: str
    risk: PermissionRisk
    mode: PermissionMode
    authorized_coowners: frozenset[CoownerIdentity]
    existing_authorities: tuple[str, ...]
    constraints: tuple[str, ...]
    external_effect: bool
    persistent_effect: bool
    audit_required: bool
    grants_action_authority: bool = False

    def __post_init__(self) -> None:
        text = (
            self.action_id,
            self.title,
            *self.existing_authorities,
            *self.constraints,
        )
        if any(not item.strip() for item in text):
            raise ValueError("coowner permission rule text must not be blank")
        for values in (self.existing_authorities, self.constraints):
            if not values or len(values) != len(set(values)):
                raise ValueError(
                    "coowner permission rule collections must be nonempty and unique"
                )
        if self.authorized_coowners != EQUAL_COOWNERS:
            raise ValueError("Carlos and Cristina must have equal permission authority")
        if self.grants_action_authority:
            raise ValueError("permission matrix cannot grant action authority")
        if (self.external_effect or self.persistent_effect) and not self.audit_required:
            raise ValueError("external or persistent effects require audit")
        if self.mode is PermissionMode.INTERNAL and (
            self.external_effect or self.persistent_effect
        ):
            raise ValueError("internal permission mode cannot create effects")
        if self.mode is PermissionMode.DELEGABLE and self.risk in {
            PermissionRisk.HIGH,
            PermissionRisk.CRITICAL,
        }:
            raise ValueError("high-risk actions cannot use standing delegation")


def _rule(
    action_id: str,
    title: str,
    risk: PermissionRisk,
    mode: PermissionMode,
    authorities: tuple[str, ...],
    constraints: tuple[str, ...],
    *,
    external_effect: bool = False,
    persistent_effect: bool = False,
    audit_required: bool = False,
) -> CoownerPermissionRule:
    return CoownerPermissionRule(
        action_id=action_id,
        title=title,
        risk=risk,
        mode=mode,
        authorized_coowners=EQUAL_COOWNERS,
        existing_authorities=authorities,
        constraints=constraints,
        external_effect=external_effect,
        persistent_effect=persistent_effect,
        audit_required=audit_required,
    )


COOWNER_PERMISSION_MATRIX = (
    _rule(
        "conversation_response",
        "Responder y explicar",
        PermissionRisk.LOW,
        PermissionMode.INTERNAL,
        ("governed conversation pipeline",),
        ("No presentar inferencias como hechos.", "No ejecutar acciones implícitas."),
    ),
    _rule(
        "read_only_analysis",
        "Analizar y reflexionar en modo de solo lectura",
        PermissionRisk.LOW,
        PermissionMode.INTERNAL,
        ("cognitive runtime", "M386.2 epistemic classifier"),
        ("No persistir conclusiones.", "No autoimplementar recomendaciones."),
    ),
    _rule(
        "memory_recall",
        "Recuperar memoria conjunta autorizada",
        PermissionRisk.LOW,
        PermissionMode.INTERNAL,
        ("canonical memory runtime",),
        ("Respetar procedencia y vigencia.", "No exponer contenido en diagnósticos."),
    ),
    _rule(
        "memory_write_correct_archive",
        "Guardar, corregir o archivar memoria",
        PermissionRisk.MEDIUM,
        PermissionMode.CONFIRMATION_REQUIRED,
        ("canonical memory runtime",),
        (
            "La orden explícita vale solo para esa operación.",
            "Conservar trazabilidad.",
        ),
        persistent_effect=True,
        audit_required=True,
    ),
    _rule(
        "learning_activation",
        "Activar un aprendizaje conductual",
        PermissionRisk.HIGH,
        PermissionMode.CONFIRMATION_REQUIRED,
        ("learning governance", "evolution guard"),
        ("Exigir candidato revisable.", "Permitir evaluación y reversión."),
        persistent_effect=True,
        audit_required=True,
    ),
    _rule(
        "planning_and_recommendation",
        "Planificar, comparar y recomendar",
        PermissionRisk.LOW,
        PermissionMode.INTERNAL,
        ("cognitive planning", "governed reasoning"),
        ("Planificar no autoriza ejecutar.", "Mostrar límites e incertidumbre."),
    ),
    _rule(
        "external_information_read",
        "Consultar una fuente externa aprobada",
        PermissionRisk.MEDIUM,
        PermissionMode.DELEGABLE,
        ("capability registry", "permission consent", "tool gateway"),
        ("Requerir delegación activa y acotada.", "Aplicar minimización de datos."),
        external_effect=True,
        audit_required=True,
    ),
    _rule(
        "sensor_observation",
        "Observar voz, cámara, Android, sensores o ambiente",
        PermissionRisk.MEDIUM,
        PermissionMode.DELEGABLE,
        ("multimodal observation contracts", "permission consent"),
        ("Requerir consentimiento vigente por canal.", "Declarar degradación."),
        external_effect=True,
        audit_required=True,
    ),
    _rule(
        "external_message_or_write",
        "Enviar mensajes o escribir en sistemas externos",
        PermissionRisk.HIGH,
        PermissionMode.CONFIRMATION_REQUIRED,
        ("permission consent", "tool gateway", "domain capability policy"),
        ("Mostrar destinatario y efecto.", "Confirmar inmediatamente antes de actuar."),
        external_effect=True,
        persistent_effect=True,
        audit_required=True,
    ),
    _rule(
        "physical_device_control",
        "Controlar un dispositivo físico",
        PermissionRisk.HIGH,
        PermissionMode.CONFIRMATION_REQUIRED,
        ("device gateway", "permission consent"),
        ("Verificar estado y alcance.", "Evitar ejecución irreversible u opaca."),
        external_effect=True,
        audit_required=True,
    ),
    _rule(
        "health_or_psychological_decision",
        "Decidir en nombre de Carlos o Cristina sobre salud",
        PermissionRisk.HIGH,
        PermissionMode.PROPOSE_ONLY,
        ("advanced clinical safety", "M386.3 behavior principles"),
        ("Informar y acompañar.", "Derivar decisiones a personas y profesionales."),
    ),
    _rule(
        "permanent_personal_data_deletion",
        "Eliminar permanentemente información personal",
        PermissionRisk.CRITICAL,
        PermissionMode.CONFIRMATION_REQUIRED,
        ("domain data authority", "permission consent"),
        (
            "Identificar el objetivo exacto.",
            "Confirmar recuperación o irreversibilidad.",
        ),
        persistent_effect=True,
        audit_required=True,
    ),
    _rule(
        "credential_secret_exposure",
        "Exponer credenciales o secretos",
        PermissionRisk.CRITICAL,
        PermissionMode.FORBIDDEN,
        ("secure credential store",),
        ("Conservar secretos aislados.", "Permitir solo uso interno autorizado."),
        external_effect=True,
        audit_required=True,
    ),
    _rule(
        "unbounded_destructive_action",
        "Ejecutar acciones destructivas sin objetivo acotado",
        PermissionRisk.CRITICAL,
        PermissionMode.FORBIDDEN,
        ("M386.3 behavior principles",),
        ("Rechazar objetivos ambiguos.", "Exigir diseño recuperable y revisable."),
        external_effect=True,
        persistent_effect=True,
        audit_required=True,
    ),
    _rule(
        "self_modification_or_permission_expansion",
        "Modificar código, límites, pesos o permisos por autoridad propia",
        PermissionRisk.CRITICAL,
        PermissionMode.FORBIDDEN,
        ("evolution guard", "M386.3 behavior principles"),
        ("Proponer cambios para revisión humana.", "No elevar autonomía propia."),
        persistent_effect=True,
        audit_required=True,
    ),
)


COOWNER_PERMISSION_CONFLICT_POLICY = (
    "Carlos y Cristina poseen idéntica autoridad para autorizar o revocar.",
    "Una instrucción puntual no crea una delegación permanente.",
    "Una denegación o revocación vigente bloquea la acción.",
    "Instrucciones incompatibles requieren aclaración y no permiten "
    "elegir propietario.",
    "La matriz clasifica permisos pero no reemplaza la autoridad de dominio.",
)


def coowner_permission_rule(action_id: str) -> CoownerPermissionRule:
    normalized = action_id.strip().casefold()
    for rule in COOWNER_PERMISSION_MATRIX:
        if rule.action_id.casefold() == normalized:
            return rule
    raise KeyError(action_id)
