# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_event_bus import (
    CognitiveEvent,
    CognitiveEventBus,
    CognitiveEventType,
)
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.global_cognitive_state import (
    GlobalCognitiveReadiness,
    GlobalCognitiveStateEngine,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class CrossDomainCoordinationStatus(str, Enum):
    IDLE = "idle"
    COORDINATED = "coordinated"
    ATTENTION_REQUIRED = "attention_required"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class CrossDomainCoordinationDirective:
    owner: str
    session_id: str
    status: CrossDomainCoordinationStatus | str
    participating_domains: tuple[CognitiveBlackboardDomain | str, ...]
    priorities: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    directive_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        status = CrossDomainCoordinationStatus(self.status)
        domains = tuple(
            CognitiveBlackboardDomain(item) for item in self.participating_domains
        )
        priorities = tuple(item.strip() for item in self.priorities if item.strip())
        conflicts = tuple(item.strip() for item in self.conflicts if item.strip())
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("cross-domain coordination identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("cross-domain coordination time must be timezone-aware")
        if len(set(domains)) != len(domains):
            raise ValueError("cross-domain coordination domains must be unique")
        if len(set(priorities)) != len(priorities):
            raise ValueError("cross-domain coordination priorities must be unique")
        if len(set(conflicts)) != len(conflicts):
            raise ValueError("cross-domain coordination conflicts must be unique")
        if len(set(references)) != len(references):
            raise ValueError("cross-domain coordination references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    *(item.value for item in domains),
                    *priorities,
                    *conflicts,
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.directive_id and self.directive_id != expected:
            raise ValueError("cross-domain coordination id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "participating_domains", domains)
        object.__setattr__(self, "priorities", priorities)
        object.__setattr__(self, "conflicts", conflicts)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "directive_id", expected)


class CrossDomainCoordinator:
    """Derive consultative coordination directives from shared cognitive signals."""

    def __init__(
        self,
        *,
        blackboard: UnifiedCognitiveBlackboard | None = None,
        event_bus: CognitiveEventBus | None = None,
        state_engine: GlobalCognitiveStateEngine | None = None,
    ) -> None:
        self.blackboard = blackboard
        self.event_bus = event_bus
        self.state_engine = state_engine
        self.last_directive: CrossDomainCoordinationDirective | None = None

    def bind(
        self,
        *,
        blackboard: UnifiedCognitiveBlackboard,
        event_bus: CognitiveEventBus,
        state_engine: GlobalCognitiveStateEngine,
    ) -> None:
        self.blackboard = blackboard
        self.event_bus = event_bus
        self.state_engine = state_engine

    def coordinate(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> CrossDomainCoordinationDirective:
        timestamp = now or datetime.now(timezone.utc)
        if (
            self.blackboard is None
            or self.event_bus is None
            or self.state_engine is None
        ):
            raise RuntimeError("cross-domain coordinator dependencies are not bound")
        state = self.state_engine.last_state
        if (
            state is None
            or state.owner != owner.strip()
            or state.session_id != session_id.strip()
        ):
            self.state_engine.bind_blackboard(self.blackboard)
            state = self.state_engine.assess(
                owner=owner, session_id=session_id, now=timestamp
            )
        events = self.event_bus.events(owner=owner, session_id=session_id)
        domains = tuple(
            dict.fromkeys(
                (*state.active_domains, *(event.source_domain for event in events))
            )
        )
        conflicts = self._detect_conflicts(events)
        priorities = self._priorities(state.readiness, events, conflicts)
        if not domains and not events:
            status = CrossDomainCoordinationStatus.IDLE
        elif state.readiness is GlobalCognitiveReadiness.BLOCKED:
            status = CrossDomainCoordinationStatus.BLOCKED
        elif conflicts or state.constraints:
            status = CrossDomainCoordinationStatus.ATTENTION_REQUIRED
        else:
            status = CrossDomainCoordinationStatus.COORDINATED
        references = tuple(
            dict.fromkeys(
                (
                    state.state_id,
                    *state.source_reference_ids,
                    *(event.event_id for event in events),
                )
            )
        )
        directive = CrossDomainCoordinationDirective(
            owner=owner,
            session_id=session_id,
            status=status,
            participating_domains=domains,
            priorities=priorities,
            conflicts=conflicts,
            source_reference_ids=references,
            created_at=timestamp,
        )
        self.last_directive = directive
        return directive

    @staticmethod
    def _detect_conflicts(events: tuple[CognitiveEvent, ...]) -> tuple[str, ...]:
        values: dict[str, set[str]] = {}
        for event in events:
            values.setdefault(event.topic.casefold(), set()).add(event.value.casefold())
        return tuple(sorted(topic for topic, items in values.items() if len(items) > 1))

    @staticmethod
    def _priorities(
        readiness: GlobalCognitiveReadiness,
        events: tuple[CognitiveEvent, ...],
        conflicts: tuple[str, ...],
    ) -> tuple[str, ...]:
        priorities: list[str] = []
        if any(
            event.event_type is CognitiveEventType.CONSTRAINT_RAISED for event in events
        ):
            priorities.append("resolve_constraints")
        if conflicts:
            priorities.append("reconcile_conflicting_signals")
        if readiness is GlobalCognitiveReadiness.DEGRADED:
            priorities.append("restore_signal_quality")
        if readiness is GlobalCognitiveReadiness.BLOCKED:
            priorities.append("preserve_blocking_boundary")
        if not priorities:
            priorities.append("maintain_cross_domain_alignment")
        return tuple(priorities)


@dataclass
class CrossDomainCoordinationRuntimeContributor:
    coordinator: CrossDomainCoordinator
    blackboard: UnifiedCognitiveBlackboard
    event_bus: CognitiveEventBus
    state_engine: GlobalCognitiveStateEngine
    name: str = "cross_domain_coordination"

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
        self.coordinator.bind(
            blackboard=self.blackboard,
            event_bus=self.event_bus,
            state_engine=self.state_engine,
        )
        directive = self.coordinator.coordinate(
            owner=owner, session_id=session_id, now=now
        )
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CANDIDATE,
                key="cross_domain_coordination_status",
                value=directive.status.value,
                confidence=1.0 if not directive.conflicts else 0.7,
                source_reference_ids=(
                    directive.directive_id,
                    *directive.source_reference_ids,
                ),
                created_at=now,
            )
        )
        domains = (
            ", ".join(item.value for item in directive.participating_domains)
            or "ninguno"
        )
        priorities = ", ".join(directive.priorities)
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                f"Coordinación transversal: {directive.status.value}; dominios {domains}; prioridades {priorities}.",
            ),
            reference_ids=(
                entry.entry_id,
                directive.directive_id,
                *directive.source_reference_ids,
            ),
            rationale=(
                "m201_blackboard_consulted",
                "m202_global_state_consulted",
                "m203_events_correlated",
                "cross_domain_directive_published",
            ),
        )
