from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class ScopeGuardSignal(str, Enum):
    """Señales de M71 para delimitar alcance operativo seguro."""

    SCOPE_GUARD_READY = "scope_guard_ready"
    SCOPE_EVALUATED = "scope_evaluated"
    FORBIDDEN_DOMAIN_DETECTED = "forbidden_domain_detected"
    REVIEW_DOMAIN_DETECTED = "review_domain_detected"
    SAFE_DOMAIN_DETECTED = "safe_domain_detected"
    HUMAN_APPROVAL_REQUIRED = "human_approval_required"
    CONTRACT_PRESERVED = "contract_preserved"


class ScopeGuardStatus(str, Enum):
    """Resultado normalizado de una evaluación de alcance."""

    IN_SCOPE = "in_scope"
    REVIEW_REQUIRED = "review_required"
    OUT_OF_SCOPE = "out_of_scope"


class ScopeDomain(str, Enum):
    """Dominios operativos reconocidos por el guardrail de alcance."""

    BANKING = "banking"
    WALLET = "wallet"
    PURCHASE = "purchase"
    FINANCE = "finance"
    MEDICAL_DECISION = "medical_decision"
    LEGAL_DECISION = "legal_decision"
    EXTERNAL_ACTION = "external_action"
    PERSONAL_OPERATIONS = "personal_operations"
    HOUSEHOLD_MEMORY = "household_memory"
    DOCUMENTS = "documents"
    CALENDAR = "calendar"
    KNOWLEDGE = "knowledge"
    TASKS = "tasks"
    CONVERSATION = "conversation"


@dataclass(frozen=True)
class ScopeGuardPolicy:
    """Política normativa de Fase VII para autonomía personal supervisada."""

    forbidden_domains: tuple[ScopeDomain | str, ...] = (
        ScopeDomain.BANKING,
        ScopeDomain.WALLET,
        ScopeDomain.PURCHASE,
        ScopeDomain.FINANCE,
    )
    review_domains: tuple[ScopeDomain | str, ...] = (
        ScopeDomain.MEDICAL_DECISION,
        ScopeDomain.LEGAL_DECISION,
        ScopeDomain.EXTERNAL_ACTION,
    )
    allowed_domains: tuple[ScopeDomain | str, ...] = (
        ScopeDomain.PERSONAL_OPERATIONS,
        ScopeDomain.HOUSEHOLD_MEMORY,
        ScopeDomain.DOCUMENTS,
        ScopeDomain.CALENDAR,
        ScopeDomain.KNOWLEDGE,
        ScopeDomain.TASKS,
        ScopeDomain.CONVERSATION,
    )
    require_human_approval_for_review: bool = True
    most_restrictive_policy_wins: bool = True
    max_audit_records: int = 100

    def __post_init__(self) -> None:
        self._validate_domains(self.forbidden_domains, "forbidden")
        self._validate_domains(self.review_domains, "review")
        self._validate_domains(self.allowed_domains, "allowed")
        if self.max_audit_records <= 0:
            raise ValueError("scope guard audit limit must be positive")
        forbidden = set(self.normalized_forbidden_domains)
        review = set(self.normalized_review_domains)
        allowed = set(self.normalized_allowed_domains)
        if forbidden & allowed:
            raise ValueError("forbidden domains must not be allowed")
        if forbidden & review:
            raise ValueError("forbidden domains must not be review-only")

    @staticmethod
    def _validate_domains(domains: tuple[ScopeDomain | str, ...], label: str) -> None:
        if any(not str(domain).strip() for domain in domains):
            raise ValueError(f"{label} domains must not be blank")
        for domain in domains:
            ScopeDomain(domain)

    @property
    def normalized_forbidden_domains(self) -> tuple[ScopeDomain, ...]:
        return tuple(ScopeDomain(domain) for domain in self.forbidden_domains)

    @property
    def normalized_review_domains(self) -> tuple[ScopeDomain, ...]:
        return tuple(ScopeDomain(domain) for domain in self.review_domains)

    @property
    def normalized_allowed_domains(self) -> tuple[ScopeDomain, ...]:
        return tuple(ScopeDomain(domain) for domain in self.allowed_domains)


@dataclass(frozen=True)
class ScopeGuardDecision:
    """Decisión auditable que define si ROBY puede continuar dentro del alcance."""

    status: ScopeGuardStatus | str
    detected_domains: tuple[ScopeDomain | str, ...]
    allowed_domains: tuple[ScopeDomain | str, ...]
    review_required_domains: tuple[ScopeDomain | str, ...]
    blocked_domains: tuple[ScopeDomain | str, ...]
    rationale: str
    can_continue: bool
    human_approval_required: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        ScopeGuardStatus(self.status)
        domain_groups = (
            self.detected_domains,
            self.allowed_domains,
            self.review_required_domains,
            self.blocked_domains,
        )
        for group in domain_groups:
            for domain in group:
                ScopeDomain(domain)
        if not self.rationale.strip():
            raise ValueError("scope guard rationale must not be empty")
        if (
            self.normalized_status is ScopeGuardStatus.OUT_OF_SCOPE
            and self.can_continue
        ):
            raise ValueError("out-of-scope decisions must not continue")
        if self.created_at.tzinfo is None:
            raise ValueError("scope guard timestamp must be timezone-aware")
        if not self.decision_id.strip():
            raise ValueError("scope guard decision id must not be empty")

    @property
    def normalized_status(self) -> ScopeGuardStatus:
        return ScopeGuardStatus(self.status)

    @property
    def normalized_detected_domains(self) -> tuple[ScopeDomain, ...]:
        return tuple(ScopeDomain(domain) for domain in self.detected_domains)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.decision_id,
            "status": self.normalized_status.value,
            "detected_domains": [
                ScopeDomain(domain).value for domain in self.detected_domains
            ],
            "allowed_domains": [
                ScopeDomain(domain).value for domain in self.allowed_domains
            ],
            "review_required_domains": [
                ScopeDomain(domain).value for domain in self.review_required_domains
            ],
            "blocked_domains": [
                ScopeDomain(domain).value for domain in self.blocked_domains
            ],
            "rationale": self.rationale,
            "can_continue": self.can_continue,
            "human_approval_required": self.human_approval_required,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ScopeGuardSnapshot:
    """Snapshot M71 para exponer alcance seguro al pipeline cognitivo."""

    signals: tuple[ScopeGuardSignal | str, ...]
    status: ScopeGuardStatus | str
    decision: ScopeGuardDecision
    audit_trail: tuple[str, ...]
    scope_contract: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("scope guard signals must not be empty")
        for signal in self.signals:
            ScopeGuardSignal(signal)
        ScopeGuardStatus(self.status)
        if any(not item.strip() for item in self.audit_trail):
            raise ValueError("scope guard audit items must not be blank")
        if any(not item.strip() for item in self.scope_contract):
            raise ValueError("scope guard contract lines must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("scope guard snapshot timestamp must be aware")
        if not self.snapshot_id.strip():
            raise ValueError("scope guard snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[ScopeGuardSignal, ...]:
        return tuple(ScopeGuardSignal(signal) for signal in self.signals)

    @property
    def normalized_status(self) -> ScopeGuardStatus:
        return ScopeGuardStatus(self.status)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Scope Guard M71:",
            f"- Estado: {self.normalized_status.value}",
            f"- Señales: {signals}",
            "- Regla: ROBY no opera bancos, billeteras, pagos ni compras.",
            "- Regla: ROBY puede organizar información personal permitida.",
            "- Regla: acciones externas o decisiones sensibles "
            "requieren revisión humana.",
        ]
        for line in self.scope_contract:
            lines.append(f"- Contrato: {line}")
        for domain in self.decision.allowed_domains:
            lines.append(f"- Dominio permitido: {ScopeDomain(domain).value}")
        for domain in self.decision.review_required_domains:
            lines.append(f"- Revisión requerida: {ScopeDomain(domain).value}")
        for domain in self.decision.blocked_domains:
            lines.append(f"- Dominio bloqueado: {ScopeDomain(domain).value}")
        lines.append(f"- Racional: {self.decision.rationale}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "status": self.normalized_status.value,
            "decision": self.decision.to_dict(),
            "audit_trail": list(self.audit_trail),
            "scope_contract": list(self.scope_contract),
            "created_at": self.created_at.isoformat(),
        }


class ScopeGuardManager:
    """M71: delimita ROBY Personal Operations antes de incorporar capacidades."""

    _TERMS_BY_DOMAIN: dict[ScopeDomain, tuple[str, ...]] = {
        ScopeDomain.BANKING: (
            "banco",
            "bancos",
            "cuenta bancaria",
            "home banking",
            "transferencia bancaria",
            "cbu",
            "alias bancario",
        ),
        ScopeDomain.WALLET: (
            "billetera",
            "mercado pago",
            "uala",
            "naranja x",
            "paypal",
            "cripto",
            "wallet",
        ),
        ScopeDomain.PURCHASE: (
            "comprá",
            "compra",
            "comprar",
            "pedido",
            "carrito",
            "pagá",
            "paga",
            "pagar",
            "mercadolibre",
            "amazon",
        ),
        ScopeDomain.FINANCE: (
            "invertí",
            "invertir",
            "acciones",
            "bonos",
            "plazo fijo",
            "dólares",
            "dolares",
            "finanzas",
            "préstamo",
            "prestamo",
        ),
        ScopeDomain.MEDICAL_DECISION: (
            "diagnóstico",
            "diagnostico",
            "medicación",
            "medicacion",
            "tratamiento",
            "dosis",
            "receta",
        ),
        ScopeDomain.LEGAL_DECISION: (
            "demanda",
            "juicio",
            "abogado",
            "legal",
            "contrato legal",
            "denuncia",
        ),
        ScopeDomain.EXTERNAL_ACTION: (
            "enviá",
            "envia",
            "mandá",
            "manda",
            "publicá",
            "publica",
            "reservá",
            "reserva",
            "cancelá",
            "cancela",
        ),
        ScopeDomain.HOUSEHOLD_MEMORY: (
            "recordá",
            "recorda",
            "anotá",
            "anota",
            "garantía",
            "garantia",
            "servicio",
            "reparación",
            "reparacion",
            "trámite",
            "tramite",
        ),
        ScopeDomain.DOCUMENTS: (
            "documento",
            "pdf",
            "archivo",
            "contrato",
            "resumen",
            "resumí",
            "resumi",
            "leé",
            "lee",
        ),
        ScopeDomain.CALENDAR: (
            "agenda",
            "calendario",
            "turno",
            "evento",
            "reunión",
            "reunion",
            "vencimiento",
        ),
        ScopeDomain.KNOWLEDGE: (
            "investigá",
            "investiga",
            "biblioteca",
            "apunte",
            "lectura",
            "idea",
            "estudio",
        ),
        ScopeDomain.TASKS: (
            "tarea",
            "pendiente",
            "prioridad",
            "priorizá",
            "prioriza",
            "hacer hoy",
            "seguimiento",
        ),
        ScopeDomain.CONVERSATION: (
            "conversemos",
            "hablemos",
            "opinión",
            "opinion",
            "pensás",
            "pensas",
        ),
        ScopeDomain.PERSONAL_OPERATIONS: (
            "organizar",
            "organización",
            "organizacion",
            "rutina",
            "vida diaria",
            "casa",
            "personal",
        ),
    }

    def __init__(self, policy: ScopeGuardPolicy | None = None) -> None:
        self.policy = policy or ScopeGuardPolicy()
        self._history: list[ScopeGuardSnapshot] = []

    @property
    def history(self) -> tuple[ScopeGuardSnapshot, ...]:
        return tuple(self._history)

    @property
    def last_snapshot(self) -> ScopeGuardSnapshot | None:
        return self._history[-1] if self._history else None

    def observe_turn(
        self,
        text: str,
        *,
        proposed_domains: tuple[ScopeDomain | str, ...] = (),
        now: datetime | None = None,
    ) -> ScopeGuardSnapshot:
        if not text.strip():
            raise ValueError("scope guard text must not be empty")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("scope guard timestamp must be timezone-aware")

        detected = self._detected_domains(text, proposed_domains)
        blocked = self._blocked_domains(detected)
        review = self._review_domains(detected, blocked)
        allowed = self._allowed_domains(detected, blocked, review)
        status = self._status_for(blocked, review)
        human_approval_required = (
            status is ScopeGuardStatus.REVIEW_REQUIRED
            and self.policy.require_human_approval_for_review
        )
        decision = ScopeGuardDecision(
            status=status,
            detected_domains=detected,
            allowed_domains=allowed,
            review_required_domains=review,
            blocked_domains=blocked,
            rationale=self._rationale_for(status, detected, blocked, review),
            can_continue=status is not ScopeGuardStatus.OUT_OF_SCOPE,
            human_approval_required=human_approval_required,
            created_at=timestamp,
        )
        snapshot = ScopeGuardSnapshot(
            signals=self._signals_for(decision),
            status=status,
            decision=decision,
            audit_trail=self._audit_trail_for(decision),
            scope_contract=self._contract_lines(),
            created_at=timestamp,
        )
        self._history.append(snapshot)
        if len(self._history) > self.policy.max_audit_records:
            self._history = self._history[-self.policy.max_audit_records :]
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return (
                "Scope Guard M71:",
                "- Estado: in_scope",
                "- Regla: no operar bancos, billeteras, pagos ni compras.",
                "- Regla: priorizar autonomía personal supervisada.",
            )
        return self.last_snapshot.system_prompt_lines()

    def _detected_domains(
        self,
        text: str,
        proposed_domains: tuple[ScopeDomain | str, ...],
    ) -> tuple[ScopeDomain, ...]:
        detected: set[ScopeDomain] = set()
        normalized = text.casefold()
        for domain in proposed_domains:
            detected.add(ScopeDomain(domain))
        for domain, terms in self._TERMS_BY_DOMAIN.items():
            if any(term.casefold() in normalized for term in terms):
                detected.add(domain)
        if not detected:
            detected.add(ScopeDomain.CONVERSATION)
        return tuple(sorted(detected, key=lambda item: item.value))

    def _blocked_domains(
        self,
        detected: tuple[ScopeDomain, ...],
    ) -> tuple[ScopeDomain, ...]:
        forbidden = set(self.policy.normalized_forbidden_domains)
        return tuple(domain for domain in detected if domain in forbidden)

    def _review_domains(
        self,
        detected: tuple[ScopeDomain, ...],
        blocked: tuple[ScopeDomain, ...],
    ) -> tuple[ScopeDomain, ...]:
        review = set(self.policy.normalized_review_domains)
        blocked_set = set(blocked)
        return tuple(
            domain
            for domain in detected
            if domain in review and domain not in blocked_set
        )

    def _allowed_domains(
        self,
        detected: tuple[ScopeDomain, ...],
        blocked: tuple[ScopeDomain, ...],
        review: tuple[ScopeDomain, ...],
    ) -> tuple[ScopeDomain, ...]:
        allowed = set(self.policy.normalized_allowed_domains)
        blocked_set = set(blocked)
        review_set = set(review)
        return tuple(
            domain
            for domain in detected
            if domain in allowed
            and domain not in blocked_set
            and domain not in review_set
        )

    def _status_for(
        self,
        blocked: tuple[ScopeDomain, ...],
        review: tuple[ScopeDomain, ...],
    ) -> ScopeGuardStatus:
        if blocked and self.policy.most_restrictive_policy_wins:
            return ScopeGuardStatus.OUT_OF_SCOPE
        if review:
            return ScopeGuardStatus.REVIEW_REQUIRED
        return ScopeGuardStatus.IN_SCOPE

    def _rationale_for(
        self,
        status: ScopeGuardStatus,
        detected: tuple[ScopeDomain, ...],
        blocked: tuple[ScopeDomain, ...],
        review: tuple[ScopeDomain, ...],
    ) -> str:
        if status is ScopeGuardStatus.OUT_OF_SCOPE:
            domains = ", ".join(domain.value for domain in blocked)
            return f"La solicitud toca dominios excluidos de ROBY: {domains}."
        if status is ScopeGuardStatus.REVIEW_REQUIRED:
            domains = ", ".join(domain.value for domain in review)
            return f"La solicitud requiere revisión humana previa: {domains}."
        domains = ", ".join(domain.value for domain in detected)
        return f"La solicitud permanece dentro del alcance permitido: {domains}."

    def _signals_for(
        self,
        decision: ScopeGuardDecision,
    ) -> tuple[ScopeGuardSignal, ...]:
        signals = [
            ScopeGuardSignal.SCOPE_GUARD_READY,
            ScopeGuardSignal.SCOPE_EVALUATED,
            ScopeGuardSignal.CONTRACT_PRESERVED,
        ]
        if decision.blocked_domains:
            signals.append(ScopeGuardSignal.FORBIDDEN_DOMAIN_DETECTED)
        if decision.review_required_domains:
            signals.append(ScopeGuardSignal.REVIEW_DOMAIN_DETECTED)
        if decision.allowed_domains:
            signals.append(ScopeGuardSignal.SAFE_DOMAIN_DETECTED)
        if decision.human_approval_required:
            signals.append(ScopeGuardSignal.HUMAN_APPROVAL_REQUIRED)
        return tuple(signals)

    def _audit_trail_for(
        self,
        decision: ScopeGuardDecision,
    ) -> tuple[str, ...]:
        return (
            f"decision:{decision.decision_id}",
            f"status:{decision.normalized_status.value}",
            "detected:"
            + ",".join(
                ScopeDomain(domain).value for domain in decision.detected_domains
            ),
            "blocked:"
            + (
                ",".join(
                    ScopeDomain(domain).value for domain in decision.blocked_domains
                )
                or "none"
            ),
            f"can_continue:{str(decision.can_continue).lower()}",
        )

    def _contract_lines(self) -> tuple[str, ...]:
        return (
            "ROBY no opera cuentas bancarias, billeteras, pagos, "
            "inversiones ni compras.",
            "ROBY puede organizar memoria doméstica, documentos, agenda y tareas.",
            "Toda acción externa o decisión sensible debe pasar por revisión humana.",
            "Ante conflicto prevalece la interpretación más restrictiva del alcance.",
        )
