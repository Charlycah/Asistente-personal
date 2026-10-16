from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class CapabilityRegistrySignal(str, Enum):
    """Señales de M62 para describir el catálogo de capacidades."""

    REGISTRY_READY = "registry_ready"
    CAPABILITY_DISCOVERED = "capability_discovered"
    CAPABILITY_DECLARED = "capability_declared"
    TOOL_GATEWAY_COMPATIBLE = "tool_gateway_compatible"
    CONTRACT_PRESERVED = "contract_preserved"
    SEMANTIC_MATCH = "semantic_match"


class CapabilityKind(str, Enum):
    """Familias de capacidades externas registrables."""

    WEATHER = "weather"
    MAIL = "mail"
    CAMERA = "camera"
    FILES = "files"
    CALENDAR = "calendar"
    WEB = "web"
    GENERIC = "generic"


class CapabilityRisk(str, Enum):
    """Riesgo declarativo de una capacidad antes de permisos finos."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PermissionScope(str, Enum):
    """Ámbito mínimo de permiso asociado a una capacidad."""

    NONE = "none"
    READ = "read"
    WRITE = "write"
    DEVICE = "device"
    NETWORK = "network"


class CapabilityInitiationPolicy(str, Enum):
    """Explicit policy for governed capability initiation."""

    UNDECLARED = "undeclared"
    NEVER = "never"
    HUMAN_APPROVAL = "human_approval"
    GOVERNED_AUTONOMOUS = "governed_autonomous"


class CapabilityEffectClass(str, Enum):
    """Declared external-effect class used by initiative governance."""

    UNDECLARED = "undeclared"
    READ_ONLY = "read_only"
    STATE_CHANGING = "state_changing"


class CapabilityInteractionScope(str, Enum):
    """Declared interaction surface for governed initiative decisions."""

    UNDECLARED = "undeclared"
    INTERNAL = "internal"
    HUMAN = "human"
    DEVICE = "device"
    EXTERNAL = "external"


@dataclass(frozen=True)
class CapabilityRegistryPolicy:
    """Política base para mantener el catálogo acotado y auditable."""

    max_capabilities: int = 100
    allow_duplicate_registration: bool = False

    def __post_init__(self) -> None:
        if self.max_capabilities <= 0:
            raise ValueError("capability registry limit must be positive")


@dataclass(frozen=True)
class CapabilityDescriptor:
    """Descriptor formal de una capacidad disponible para ROBY."""

    name: str
    description: str
    kind: CapabilityKind | str = CapabilityKind.GENERIC
    risk: CapabilityRisk | str = CapabilityRisk.LOW
    permission_scope: PermissionScope | str = PermissionScope.NONE
    enabled: bool = True
    requires_confirmation: bool = False
    tags: tuple[str, ...] = ()
    semantic_triggers: tuple[str, ...] = ()
    supported_intents: tuple[str, ...] = ()
    example_utterances: tuple[str, ...] = ()
    evidence_outputs: tuple[str, ...] = ()
    initiation_policy: CapabilityInitiationPolicy | str = (
        CapabilityInitiationPolicy.UNDECLARED
    )
    effect_class: CapabilityEffectClass | str = CapabilityEffectClass.UNDECLARED
    interaction_scope: CapabilityInteractionScope | str = (
        CapabilityInteractionScope.UNDECLARED
    )
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("capability name must not be empty")
        if not self.description.strip():
            raise ValueError("capability description must not be empty")
        CapabilityKind(self.kind)
        CapabilityRisk(self.risk)
        PermissionScope(self.permission_scope)
        CapabilityInitiationPolicy(self.initiation_policy)
        CapabilityEffectClass(self.effect_class)
        CapabilityInteractionScope(self.interaction_scope)
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("capability tags must not be blank")
        semantic_groups = (
            self.semantic_triggers,
            self.supported_intents,
            self.example_utterances,
        )
        if any(not item.strip() for group in semantic_groups for item in group):
            raise ValueError("capability semantic descriptors must not be blank")
        if any(not item.strip() for item in self.evidence_outputs):
            raise ValueError("capability evidence outputs must not be blank")
        if any(not key.strip() for key in self.metadata):
            raise ValueError("capability metadata keys must not be blank")

    @property
    def normalized_kind(self) -> CapabilityKind:
        return CapabilityKind(self.kind)

    @property
    def normalized_risk(self) -> CapabilityRisk:
        return CapabilityRisk(self.risk)

    @property
    def normalized_permission_scope(self) -> PermissionScope:
        return PermissionScope(self.permission_scope)

    @property
    def normalized_initiation_policy(self) -> CapabilityInitiationPolicy:
        return CapabilityInitiationPolicy(self.initiation_policy)

    @property
    def normalized_effect_class(self) -> CapabilityEffectClass:
        return CapabilityEffectClass(self.effect_class)

    @property
    def normalized_interaction_scope(self) -> CapabilityInteractionScope:
        return CapabilityInteractionScope(self.interaction_scope)

    def to_tool_capability_kwargs(self) -> dict[str, Any]:
        """Devuelve los campos compatibles con ToolCapability de M61."""

        return {
            "name": self.name,
            "description": self.description,
            "risk_level": self.normalized_risk.value,
            "enabled": self.enabled,
            "requires_confirmation": self.requires_confirmation,
            "metadata": {
                **self.metadata,
                "kind": self.normalized_kind.value,
                "permission_scope": self.normalized_permission_scope.value,
                "tags": "|".join(self.tags),
                "semantic_triggers": "|".join(self.semantic_triggers),
                "supported_intents": "|".join(self.supported_intents),
                "example_utterances": "|".join(self.example_utterances),
                "evidence_outputs": "|".join(self.evidence_outputs),
                "initiation_policy": self.normalized_initiation_policy.value,
                "effect_class": self.normalized_effect_class.value,
                "interaction_scope": self.normalized_interaction_scope.value,
            },
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "kind": self.normalized_kind.value,
            "risk": self.normalized_risk.value,
            "permission_scope": self.normalized_permission_scope.value,
            "enabled": self.enabled,
            "requires_confirmation": self.requires_confirmation,
            "tags": list(self.tags),
            "semantic_triggers": list(self.semantic_triggers),
            "supported_intents": list(self.supported_intents),
            "example_utterances": list(self.example_utterances),
            "evidence_outputs": list(self.evidence_outputs),
            "initiation_policy": self.normalized_initiation_policy.value,
            "effect_class": self.normalized_effect_class.value,
            "interaction_scope": self.normalized_interaction_scope.value,
            "metadata": dict(self.metadata),
        }

    def semantic_terms(self) -> tuple[str, ...]:
        """Términos amplios que permiten descubrir la capacidad por intención."""

        raw_terms: list[str] = [self.name, self.description]
        raw_terms.extend(self.tags)
        raw_terms.extend(self.semantic_triggers)
        raw_terms.extend(self.supported_intents)
        raw_terms.extend(self.example_utterances)
        raw_terms.extend(str(value) for value in self.metadata.values())

        normalized: list[str] = []
        for term in raw_terms:
            cleaned = term.strip()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return tuple(normalized)


@dataclass(frozen=True)
class CapabilityRegistrySnapshot:
    """Snapshot del catálogo y de las capacidades relevantes al turno."""

    signals: tuple[CapabilityRegistrySignal | str, ...]
    total_capabilities: int
    enabled_capabilities: tuple[str, ...]
    requested_capabilities: tuple[str, ...]
    declared_kinds: tuple[CapabilityKind | str, ...]
    gateway_compatible: bool
    semantic_matches: dict[str, tuple[str, ...]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("capability registry signals must not be empty")
        for signal in self.signals:
            CapabilityRegistrySignal(signal)
        if self.total_capabilities < 0:
            raise ValueError("capability registry total must not be negative")
        if any(not name.strip() for name in self.enabled_capabilities):
            raise ValueError("enabled capabilities must not be blank")
        if any(not name.strip() for name in self.requested_capabilities):
            raise ValueError("requested capabilities must not be blank")
        for kind in self.declared_kinds:
            CapabilityKind(kind)
        for name, terms in self.semantic_matches.items():
            if not name.strip():
                raise ValueError("semantic match capability name must not be blank")
            if any(not term.strip() for term in terms):
                raise ValueError("semantic match terms must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("capability registry timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("capability registry snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[CapabilityRegistrySignal, ...]:
        return tuple(CapabilityRegistrySignal(signal) for signal in self.signals)

    @property
    def normalized_kinds(self) -> tuple[CapabilityKind, ...]:
        return tuple(CapabilityKind(kind) for kind in self.declared_kinds)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        kinds = ", ".join(kind.value for kind in self.normalized_kinds)
        lines = [
            "Capability Registry M62:",
            f"- Señales: {signals}",
            f"- Capacidades totales: {self.total_capabilities}",
            f"- Familias declaradas: {kinds or 'none'}",
            f"- Compatible con Tool Gateway M61: "
            f"{str(self.gateway_compatible).lower()}",
            "- Regla: las herramientas se descubren por capacidad, no por API.",
            "- Regla: el registro describe; el gateway enruta y audita.",
        ]
        lines.extend(
            f"- Capacidad habilitada: {name}" for name in self.enabled_capabilities
        )
        lines.extend(
            f"- Capacidad relevante al turno: {name}"
            for name in self.requested_capabilities
        )
        for name, terms in sorted(self.semantic_matches.items()):
            joined = ", ".join(terms)
            lines.append(f"- Coincidencia semántica: {name} ← {joined}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "total_capabilities": self.total_capabilities,
            "enabled_capabilities": list(self.enabled_capabilities),
            "requested_capabilities": list(self.requested_capabilities),
            "declared_kinds": [kind.value for kind in self.normalized_kinds],
            "gateway_compatible": self.gateway_compatible,
            "semantic_matches": {
                name: list(terms) for name, terms in self.semantic_matches.items()
            },
            "created_at": self.created_at.isoformat(),
        }


class CapabilityRegistryEngine:
    """Motor puro de M62 para descubrimiento declarativo."""

    _TERMS_BY_CAPABILITY = {
        "weather.current": ("clima", "tiempo", "weather"),
        "weather.forecast": ("pronóstico", "pronostico", "extendido"),
        "mail.read": ("correo", "mail", "gmail", "email", "emails"),
        "camera.capture": ("cámara", "camara", "camera", "foto", "imagen"),
    }

    def evaluate_turn(
        self,
        text: str,
        *,
        capabilities: dict[str, CapabilityDescriptor],
        gateway_compatible: bool,
        now: datetime | None = None,
    ) -> CapabilityRegistrySnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("capability registry timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("capability registry text must not be empty")

        enabled = tuple(
            sorted(
                name for name, descriptor in capabilities.items() if descriptor.enabled
            )
        )
        requested, semantic_matches = self._requested_capabilities_for(
            text, capabilities
        )
        kinds = tuple(
            sorted(
                {descriptor.normalized_kind for descriptor in capabilities.values()},
                key=lambda kind: kind.value,
            )
        )
        signals = self._signals_for(requested, capabilities, gateway_compatible)
        return CapabilityRegistrySnapshot(
            signals=signals,
            total_capabilities=len(capabilities),
            enabled_capabilities=enabled,
            requested_capabilities=requested,
            declared_kinds=kinds,
            gateway_compatible=gateway_compatible,
            semantic_matches=semantic_matches,
            created_at=timestamp,
        )

    def _requested_capabilities_for(
        self,
        text: str,
        capabilities: dict[str, CapabilityDescriptor],
    ) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
        normalized = text.casefold()
        requested: list[str] = []
        semantic_matches: dict[str, tuple[str, ...]] = {}
        for name, descriptor in capabilities.items():
            terms = (
                *self._TERMS_BY_CAPABILITY.get(name, ()),
                *descriptor.semantic_terms(),
            )
            matched = tuple(term for term in terms if term.casefold() in normalized)
            if matched:
                requested.append(name)
                semantic_matches[name] = matched[:5]
        return tuple(sorted(requested)), semantic_matches

    def _signals_for(
        self,
        requested: tuple[str, ...],
        capabilities: dict[str, CapabilityDescriptor],
        gateway_compatible: bool,
    ) -> tuple[CapabilityRegistrySignal, ...]:
        signals = [
            CapabilityRegistrySignal.REGISTRY_READY,
            CapabilityRegistrySignal.CONTRACT_PRESERVED,
        ]
        if capabilities:
            signals.append(CapabilityRegistrySignal.CAPABILITY_DECLARED)
        if requested:
            signals.append(CapabilityRegistrySignal.CAPABILITY_DISCOVERED)
            signals.append(CapabilityRegistrySignal.SEMANTIC_MATCH)
        if gateway_compatible:
            signals.append(CapabilityRegistrySignal.TOOL_GATEWAY_COMPATIBLE)
        return tuple(signals)


class CapabilityRegistryManager:
    """Fachada de M62 para declarar, buscar y observar capacidades."""

    def __init__(
        self,
        policy: CapabilityRegistryPolicy | None = None,
        engine: CapabilityRegistryEngine | None = None,
    ) -> None:
        self.policy = policy or CapabilityRegistryPolicy()
        self.engine = engine or CapabilityRegistryEngine()
        self._capabilities: dict[str, CapabilityDescriptor] = {}
        self._history: list[CapabilityRegistrySnapshot] = []

    @property
    def capabilities(self) -> dict[str, CapabilityDescriptor]:
        return dict(self._capabilities)

    @property
    def history(self) -> tuple[CapabilityRegistrySnapshot, ...]:
        return tuple(self._history)

    @property
    def last_snapshot(self) -> CapabilityRegistrySnapshot | None:
        return self._history[-1] if self._history else None

    def register(self, descriptor: CapabilityDescriptor) -> None:
        if (
            descriptor.name in self._capabilities
            and not self.policy.allow_duplicate_registration
        ):
            raise ValueError("capability already registered")
        if (
            descriptor.name not in self._capabilities
            and len(self._capabilities) >= self.policy.max_capabilities
        ):
            raise ValueError("capability registry limit exceeded")
        self._capabilities[descriptor.name] = descriptor

    def get(self, name: str) -> CapabilityDescriptor | None:
        return self._capabilities.get(name)

    def register_many(self, descriptors: tuple[CapabilityDescriptor, ...]) -> None:
        for descriptor in descriptors:
            self.register(descriptor)

    def semantic_search(self, text: str) -> tuple[CapabilityDescriptor, ...]:
        snapshot = self.engine.evaluate_turn(
            text,
            capabilities=self._capabilities,
            gateway_compatible=False,
        )
        return tuple(
            self._capabilities[name] for name in snapshot.requested_capabilities
        )

    def by_kind(self, kind: CapabilityKind | str) -> tuple[CapabilityDescriptor, ...]:
        normalized_kind = CapabilityKind(kind)
        return tuple(
            descriptor
            for descriptor in self._capabilities.values()
            if descriptor.normalized_kind is normalized_kind
        )

    def enabled_names(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                name
                for name, descriptor in self._capabilities.items()
                if descriptor.enabled
            )
        )

    def observe_turn(
        self,
        text: str,
        *,
        gateway_compatible: bool = False,
    ) -> CapabilityRegistrySnapshot:
        snapshot = self.engine.evaluate_turn(
            text,
            capabilities=self._capabilities,
            gateway_compatible=gateway_compatible,
        )
        self._history.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return (
                "Capability Registry M62:",
                "- Estado: registry_ready",
                "- Regla: las capacidades deben estar declaradas antes de usarse.",
            )
        return self.last_snapshot.system_prompt_lines()


def default_semantic_capabilities() -> tuple[CapabilityDescriptor, ...]:
    """Catálogo semántico base para herramientas reales de Fase VI."""

    return (
        CapabilityDescriptor(
            "weather.current",
            "Responde estado actual del clima y recomendaciones inmediatas.",
            kind=CapabilityKind.WEATHER,
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.NETWORK,
            tags=("weather", "clima", "temperatura"),
            semantic_triggers=(
                "clima",
                "tiempo",
                "frío",
                "frio",
                "calor",
                "temperatura",
                "llueve",
                "lluvia",
                "paraguas",
                "abrigo",
                "cómo está el día",
                "como esta el dia",
            ),
            supported_intents=(
                "weather_query",
                "current_conditions",
                "clothing_advice",
                "rain_advice",
            ),
            example_utterances=(
                "ROBY, cómo está el clima?",
                "ROBY, qué frío hace",
                "ROBY, necesito abrigo?",
                "ROBY, me llevo paraguas?",
            ),
        ),
        CapabilityDescriptor(
            "weather.forecast",
            "Responde pronóstico extendido y evolución del tiempo.",
            kind=CapabilityKind.WEATHER,
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.NETWORK,
            tags=("forecast", "extendido", "pronóstico"),
            semantic_triggers=(
                "pronóstico",
                "pronostico",
                "extendido",
                "semana",
                "fin de semana",
                "mañana",
                "manana",
                "va a llover",
                "va a refrescar",
            ),
            supported_intents=("forecast_query", "future_weather"),
            example_utterances=(
                "ROBY, cómo viene el extendido?",
                "ROBY, va a llover mañana?",
            ),
        ),
        CapabilityDescriptor(
            "mail.read",
            "Lee, busca y resume correos sin modificar la casilla.",
            kind=CapabilityKind.MAIL,
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.READ,
            tags=("mail", "gmail", "correo"),
            semantic_triggers=(
                "correo",
                "correos",
                "mail",
                "gmail",
                "email",
                "emails",
                "me escribió",
                "me escribio",
                "llegó algo",
                "llego algo",
                "urgente",
                "inbox",
            ),
            supported_intents=(
                "mail_read",
                "mail_search",
                "mail_summary",
                "urgent_mail_detection",
            ),
            example_utterances=(
                "ROBY, tengo correos nuevos?",
                "ROBY, hay algo importante?",
                "ROBY, me escribió Carlos?",
            ),
        ),
        CapabilityDescriptor(
            "mail.send",
            "Redacta o envía correos con autorización explícita.",
            kind=CapabilityKind.MAIL,
            risk=CapabilityRisk.HIGH,
            permission_scope=PermissionScope.WRITE,
            requires_confirmation=True,
            tags=("mail", "send", "reply"),
            semantic_triggers=(
                "respondé",
                "responde",
                "contestale",
                "enviá",
                "envia",
                "mandale",
                "redactá",
                "redacta",
                "reenviá",
                "reenvia",
            ),
            supported_intents=("mail_reply", "mail_draft", "mail_send"),
            example_utterances=(
                "ROBY, contestale el correo",
                "ROBY, redactá una respuesta",
            ),
        ),
        CapabilityDescriptor(
            "camera.capture",
            "Captura o analiza imagen local con permiso de dispositivo.",
            kind=CapabilityKind.CAMERA,
            risk=CapabilityRisk.MEDIUM,
            permission_scope=PermissionScope.DEVICE,
            requires_confirmation=True,
            tags=("camera", "vision", "imagen"),
            semantic_triggers=(
                "mirá",
                "mira",
                "qué ves",
                "que ves",
                "cámara",
                "camara",
                "foto",
                "imagen",
                "leer este papel",
                "este objeto",
            ),
            supported_intents=("vision_capture", "visual_question"),
            example_utterances=(
                "ROBY, mirá esto",
                "ROBY, qué ves?",
                "ROBY, podés leer este papel?",
            ),
        ),
        CapabilityDescriptor(
            "files.read",
            "Busca, abre y resume archivos locales o adjuntos autorizados.",
            kind=CapabilityKind.FILES,
            risk=CapabilityRisk.MEDIUM,
            permission_scope=PermissionScope.READ,
            tags=("files", "documents", "pdf"),
            semantic_triggers=(
                "archivo",
                "documento",
                "pdf",
                "contrato",
                "factura",
                "buscá",
                "busca",
                "abrime",
                "resumime",
            ),
            supported_intents=("file_search", "file_read", "document_summary"),
            example_utterances=(
                "ROBY, buscá el contrato",
                "ROBY, resumime este PDF",
            ),
        ),
        CapabilityDescriptor(
            "calendar.read",
            "Consulta agenda, horarios y eventos sin modificar calendario.",
            kind=CapabilityKind.CALENDAR,
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.READ,
            tags=("calendar", "agenda", "eventos"),
            semantic_triggers=(
                "agenda",
                "calendario",
                "reunión",
                "reunion",
                "evento",
                "horario",
                "tengo libre",
                "qué tengo hoy",
                "que tengo hoy",
            ),
            supported_intents=("calendar_read", "availability_check"),
            example_utterances=(
                "ROBY, qué tengo hoy?",
                "ROBY, estoy libre a la tarde?",
            ),
        ),
        CapabilityDescriptor(
            "web.search",
            "Busca información pública actualizada en la web.",
            kind=CapabilityKind.WEB,
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.NETWORK,
            tags=("web", "search", "internet"),
            semantic_triggers=(
                "buscá en internet",
                "busca en internet",
                "noticias",
                "actualizado",
                "último",
                "ultimo",
                "precio",
                "sitio web",
                "online",
            ),
            supported_intents=("web_search", "fresh_information"),
            example_utterances=(
                "ROBY, buscá noticias actualizadas",
                "ROBY, cuál es el precio actual?",
            ),
        ),
    )
