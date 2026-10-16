from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_event_bus import CognitiveEventBus
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.executive_arbitration import (
    ExecutiveArbitrationDecision,
    ExecutiveArbitrator,
    ExecutiveTaskDisposition,
)
from core.global_cognitive_state import GlobalCognitiveStateEngine
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class GlobalContextFusionStatus(str, Enum):
    EMPTY = "empty"
    COHERENT = "coherent"
    CONSTRAINED = "constrained"
    CONFLICTED = "conflicted"


@dataclass(frozen=True)
class FusedContextDomain:
    domain: CognitiveBlackboardDomain | str
    facts: tuple[str, ...] = ()
    confidence: float = 1.0

    def __post_init__(self) -> None:
        domain = CognitiveBlackboardDomain(self.domain)
        facts = tuple(item.strip() for item in self.facts if item.strip())
        if len(set(facts)) != len(facts):
            raise ValueError("fused context facts must be unique")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("fused context confidence must be between zero and one")
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "facts", facts)


@dataclass(frozen=True)
class GlobalContextView:
    owner: str
    session_id: str
    status: GlobalContextFusionStatus | str
    domains: tuple[FusedContextDomain, ...]
    authorized_actions: tuple[str, ...] = ()
    deferred_actions: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        status = GlobalContextFusionStatus(self.status)
        authorized = tuple(
            item.strip() for item in self.authorized_actions if item.strip()
        )
        deferred = tuple(item.strip() for item in self.deferred_actions if item.strip())
        constraints = tuple(item.strip() for item in self.constraints if item.strip())
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("global context identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("global context time must be timezone-aware")
        if len({item.domain for item in self.domains}) != len(self.domains):
            raise ValueError("global context domains must be unique")
        for values, label in (
            (authorized, "authorized actions"),
            (deferred, "deferred actions"),
            (constraints, "constraints"),
            (references, "references"),
        ):
            if len(set(values)) != len(values):
                raise ValueError(f"global context {label} must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    *(
                        f"{item.domain.value}:{','.join(item.facts)}:{item.confidence:.3f}"
                        for item in self.domains
                    ),
                    *authorized,
                    *deferred,
                    *constraints,
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.context_id and self.context_id != expected:
            raise ValueError("global context id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "authorized_actions", authorized)
        object.__setattr__(self, "deferred_actions", deferred)
        object.__setattr__(self, "constraints", constraints)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "context_id", expected)


class GlobalContextFusionEngine:
    """Fuse governed cognitive sources into one advisory context view."""

    def __init__(
        self,
        *,
        blackboard: UnifiedCognitiveBlackboard,
        state_engine: GlobalCognitiveStateEngine,
        event_bus: CognitiveEventBus,
        arbitrator: ExecutiveArbitrator,
    ) -> None:
        self.blackboard = blackboard
        self.state_engine = state_engine
        self.event_bus = event_bus
        self.arbitrator = arbitrator
        self.last_context: GlobalContextView | None = None

    def fuse(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> GlobalContextView:
        timestamp = now or datetime.now(timezone.utc)
        snapshot = self.blackboard.snapshot(
            owner=owner, session_id=session_id, now=timestamp
        )
        state = self.state_engine.last_state
        if (
            state is None
            or state.owner != owner.strip()
            or state.session_id != session_id.strip()
        ):
            state = self.state_engine.assess(
                owner=owner, session_id=session_id, now=timestamp
            )
        decision = self.arbitrator.last_decision
        if (
            decision is None
            or decision.owner != owner.strip()
            or decision.session_id != session_id.strip()
        ):
            decision = self.arbitrator.arbitrate(
                owner=owner, session_id=session_id, now=timestamp
            )
        events = self.event_bus.events(owner=owner, session_id=session_id)
        domains = self._domains(snapshot.entries)
        authorized, deferred = self._actions(decision)
        constraints = tuple(dict.fromkeys((*state.constraints, *decision.constraints)))
        event_values: dict[tuple[str, str], set[str]] = {}
        for event in events:
            event_values.setdefault(
                (event.source_domain.value, event.topic), set()
            ).add(event.value)
        conflicted = any(len(values) > 1 for values in event_values.values())
        if not domains and not events and not decision.task_decisions:
            status = GlobalContextFusionStatus.EMPTY
        elif conflicted:
            status = GlobalContextFusionStatus.CONFLICTED
        elif constraints or deferred:
            status = GlobalContextFusionStatus.CONSTRAINED
        else:
            status = GlobalContextFusionStatus.COHERENT
        references = tuple(
            dict.fromkeys(
                (
                    snapshot.snapshot_id,
                    state.state_id,
                    decision.decision_id,
                    *(event.event_id for event in events),
                )
            )
        )
        context = GlobalContextView(
            owner=owner,
            session_id=session_id,
            status=status,
            domains=domains,
            authorized_actions=authorized,
            deferred_actions=deferred,
            constraints=constraints,
            source_reference_ids=references,
            created_at=timestamp,
        )
        self.last_context = context
        return context

    @staticmethod
    def _domains(
        entries: tuple[CognitiveBlackboardEntry, ...],
    ) -> tuple[FusedContextDomain, ...]:
        grouped: dict[CognitiveBlackboardDomain, list[CognitiveBlackboardEntry]] = {}
        for entry in entries:
            if entry.key == "global_context_fusion_status":
                continue
            grouped.setdefault(entry.domain, []).append(entry)
        result = []
        for domain in sorted(grouped, key=lambda item: item.value):
            values = grouped[domain]
            facts = tuple(dict.fromkeys(f"{item.key}={item.value}" for item in values))
            confidence = sum(item.confidence for item in values) / len(values)
            result.append(
                FusedContextDomain(domain=domain, facts=facts, confidence=confidence)
            )
        return tuple(result)

    @staticmethod
    def _actions(
        decision: ExecutiveArbitrationDecision,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        authorized = tuple(
            item.action
            for item in decision.task_decisions
            if item.disposition is ExecutiveTaskDisposition.AUTHORIZE
        )
        deferred = tuple(
            item.action
            for item in decision.task_decisions
            if item.disposition is not ExecutiveTaskDisposition.AUTHORIZE
        )
        return authorized, deferred


@dataclass
class GlobalContextFusionRuntimeContributor:
    fusion: GlobalContextFusionEngine
    blackboard: UnifiedCognitiveBlackboard
    name: str = "global_context_fusion"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del text, request
        context = self.fusion.fuse(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONTEXT,
                key="global_context_fusion_status",
                value=context.status.value,
                confidence=1.0
                if context.status
                in {GlobalContextFusionStatus.EMPTY, GlobalContextFusionStatus.COHERENT}
                else 0.8,
                source_reference_ids=(
                    context.context_id,
                    *context.source_reference_ids,
                ),
                created_at=now,
            )
        )
        domain_names = (
            ", ".join(item.domain.value for item in context.domains) or "sin dominios"
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                f"Contexto global: {context.status.value}; dominios {domain_names}.",
            ),
            reference_ids=(
                entry.entry_id,
                context.context_id,
                *context.source_reference_ids,
            ),
            rationale=(
                "m201_m206_sources_fused",
                "conflicts_and_constraints_preserved",
                "global_context_published",
                "execution_authority_not_acquired",
            ),
        )
