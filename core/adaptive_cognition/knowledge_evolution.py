from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.adaptive_cognition.mental_models import MentalModel
from core.adaptive_cognition.reflection_engine import ReflectionRecord
from core.personal_knowledge_base import KnowledgeItem


class KnowledgeEvolutionAction(str, Enum):
    CREATE = "create"
    REINFORCE = "reinforce"
    SUPERSEDE = "supersede"
    RETIRE = "retire"


class KnowledgeEvolutionStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    BLOCKED = "blocked"


class KnowledgeEvolutionRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class KnowledgeEvolutionProposal:
    action: KnowledgeEvolutionAction | str
    title: str
    content: str
    rationale: str
    reflection_ids: tuple[str, ...]
    mental_model_ids: tuple[str, ...] = ()
    target_knowledge_ids: tuple[str, ...] = ()
    confidence: float = 0.5
    risk: KnowledgeEvolutionRisk | str = KnowledgeEvolutionRisk.MEDIUM
    status: KnowledgeEvolutionStatus | str = KnowledgeEvolutionStatus.PROPOSED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    proposal_id: str = ""

    def __post_init__(self) -> None:
        action = KnowledgeEvolutionAction(self.action)
        risk = KnowledgeEvolutionRisk(self.risk)
        status = KnowledgeEvolutionStatus(self.status)
        if not self.title.strip() or not self.content.strip():
            raise ValueError("knowledge evolution requires title and content")
        if not self.rationale.strip() or not self.reflection_ids:
            raise ValueError("knowledge evolution requires rationale and reflections")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("knowledge evolution confidence must be valid")
        collections = (
            self.reflection_ids,
            self.mental_model_ids,
            self.target_knowledge_ids,
        )
        if any(len(set(items)) != len(items) for items in collections):
            raise ValueError("knowledge evolution references must be unique")
        if any(not item.strip() for items in collections for item in items):
            raise ValueError("knowledge evolution references must not be blank")
        if (
            action
            in {
                KnowledgeEvolutionAction.REINFORCE,
                KnowledgeEvolutionAction.SUPERSEDE,
                KnowledgeEvolutionAction.RETIRE,
            }
            and not self.target_knowledge_ids
        ):
            raise ValueError("knowledge evolution action requires a target")
        if self.created_at.tzinfo is None:
            raise ValueError("knowledge evolution timestamp must be timezone-aware")
        expected = sha256(
            "|".join(
                (
                    action.value,
                    self.title,
                    self.content,
                    self.rationale,
                    ";".join(self.reflection_ids),
                    ";".join(self.mental_model_ids),
                    ";".join(self.target_knowledge_ids),
                    f"{self.confidence:.8f}",
                    risk.value,
                    status.value,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.proposal_id and self.proposal_id != expected:
            raise ValueError("knowledge evolution proposal id is inconsistent")
        object.__setattr__(self, "proposal_id", expected)

    @property
    def normalized_action(self) -> KnowledgeEvolutionAction:
        return KnowledgeEvolutionAction(self.action)

    @property
    def normalized_status(self) -> KnowledgeEvolutionStatus:
        return KnowledgeEvolutionStatus(self.status)

    @property
    def normalized_risk(self) -> KnowledgeEvolutionRisk:
        return KnowledgeEvolutionRisk(self.risk)

    @property
    def requires_review(self) -> bool:
        return self.normalized_risk is not KnowledgeEvolutionRisk.LOW or (
            self.confidence < 0.8
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "action": self.normalized_action.value,
            "title": self.title,
            "content": self.content,
            "rationale": self.rationale,
            "reflection_ids": list(self.reflection_ids),
            "mental_model_ids": list(self.mental_model_ids),
            "target_knowledge_ids": list(self.target_knowledge_ids),
            "confidence": self.confidence,
            "risk": self.normalized_risk.value,
            "status": self.normalized_status.value,
            "requires_review": self.requires_review,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class KnowledgeEvolutionDecision:
    proposal_id: str
    status: KnowledgeEvolutionStatus | str
    reason: str
    reviewer: str
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = ""

    def __post_init__(self) -> None:
        status = KnowledgeEvolutionStatus(self.status)
        if status not in {
            KnowledgeEvolutionStatus.APPROVED,
            KnowledgeEvolutionStatus.REJECTED,
            KnowledgeEvolutionStatus.BLOCKED,
            KnowledgeEvolutionStatus.APPLIED,
        }:
            raise ValueError("knowledge evolution decision status is invalid")
        if not self.proposal_id.strip() or not self.reason.strip():
            raise ValueError(
                "knowledge evolution decision requires proposal and reason"
            )
        if not self.reviewer.strip():
            raise ValueError("knowledge evolution decision requires reviewer")
        if self.decided_at.tzinfo is None:
            raise ValueError("knowledge evolution decision timestamp must be aware")
        expected = sha256(
            "|".join(
                (
                    self.proposal_id,
                    status.value,
                    self.reason,
                    self.reviewer,
                    self.decided_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("knowledge evolution decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)

    @property
    def normalized_status(self) -> KnowledgeEvolutionStatus:
        return KnowledgeEvolutionStatus(self.status)


@dataclass(frozen=True)
class KnowledgeEvolutionPolicy:
    auto_approve_enabled: bool = False
    minimum_confidence: float = 0.65
    high_risk_requires_human: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_confidence <= 1.0:
            raise ValueError("knowledge evolution threshold must be valid")
        if self.auto_approve_enabled:
            raise ValueError("knowledge evolution cannot auto-approve in M89")


@runtime_checkable
class KnowledgeEvolutionRepository(Protocol):
    def add_proposal(self, proposal: KnowledgeEvolutionProposal) -> None: ...
    def get_proposal(self, proposal_id: str) -> KnowledgeEvolutionProposal | None: ...
    def add_decision(self, decision: KnowledgeEvolutionDecision) -> None: ...
    def list_proposals(self) -> tuple[KnowledgeEvolutionProposal, ...]: ...
    def list_decisions(self) -> tuple[KnowledgeEvolutionDecision, ...]: ...


class InMemoryKnowledgeEvolutionRepository:
    def __init__(self) -> None:
        self._proposals: dict[str, KnowledgeEvolutionProposal] = {}
        self._decisions: dict[str, KnowledgeEvolutionDecision] = {}

    def add_proposal(self, proposal: KnowledgeEvolutionProposal) -> None:
        if proposal.proposal_id in self._proposals:
            raise ValueError("knowledge evolution proposal already exists")
        self._proposals[proposal.proposal_id] = proposal

    def get_proposal(self, proposal_id: str) -> KnowledgeEvolutionProposal | None:
        return self._proposals.get(proposal_id)

    def add_decision(self, decision: KnowledgeEvolutionDecision) -> None:
        if decision.decision_id in self._decisions:
            raise ValueError("knowledge evolution decision already exists")
        self._decisions[decision.decision_id] = decision

    def list_proposals(self) -> tuple[KnowledgeEvolutionProposal, ...]:
        return tuple(sorted(self._proposals.values(), key=lambda item: item.created_at))

    def list_decisions(self) -> tuple[KnowledgeEvolutionDecision, ...]:
        return tuple(sorted(self._decisions.values(), key=lambda item: item.decided_at))


class KnowledgeEvolutionEngine:
    def __init__(self, policy: KnowledgeEvolutionPolicy | None = None) -> None:
        self.policy = policy or KnowledgeEvolutionPolicy()

    def propose_from_reflections(
        self,
        title: str,
        content: str,
        reflections: tuple[ReflectionRecord, ...],
        *,
        rationale: str,
        action: KnowledgeEvolutionAction | str = KnowledgeEvolutionAction.CREATE,
        mental_models: tuple[MentalModel, ...] = (),
        targets: tuple[KnowledgeItem, ...] = (),
        confidence: float = 0.5,
        risk: KnowledgeEvolutionRisk | str = KnowledgeEvolutionRisk.MEDIUM,
        now: datetime | None = None,
    ) -> KnowledgeEvolutionProposal:
        if not reflections:
            raise ValueError("knowledge evolution requires reflection evidence")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("knowledge evolution timestamp must be timezone-aware")
        if confidence < self.policy.minimum_confidence:
            risk = KnowledgeEvolutionRisk.HIGH
        return KnowledgeEvolutionProposal(
            action=action,
            title=title,
            content=content,
            rationale=rationale,
            reflection_ids=tuple(sorted(item.record_id for item in reflections)),
            mental_model_ids=tuple(sorted(item.model_id for item in mental_models)),
            target_knowledge_ids=tuple(sorted(item.item_id for item in targets)),
            confidence=confidence,
            risk=risk,
            created_at=timestamp,
        )

    def decide(
        self,
        proposal: KnowledgeEvolutionProposal,
        *,
        approve: bool,
        reason: str,
        reviewer: str,
        now: datetime | None = None,
    ) -> KnowledgeEvolutionDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("knowledge evolution timestamp must be timezone-aware")
        if approve and proposal.normalized_risk is KnowledgeEvolutionRisk.HIGH:
            status = KnowledgeEvolutionStatus.BLOCKED
        else:
            status = (
                KnowledgeEvolutionStatus.APPROVED
                if approve
                else KnowledgeEvolutionStatus.REJECTED
            )
        return KnowledgeEvolutionDecision(
            proposal_id=proposal.proposal_id,
            status=status,
            reason=reason,
            reviewer=reviewer,
            decided_at=timestamp,
        )


class KnowledgeEvolutionManager:
    def __init__(
        self,
        repository: KnowledgeEvolutionRepository | None = None,
        *,
        engine: KnowledgeEvolutionEngine | None = None,
    ) -> None:
        self.repository = repository or InMemoryKnowledgeEvolutionRepository()
        self.engine = engine or KnowledgeEvolutionEngine()
        self.last_proposal: KnowledgeEvolutionProposal | None = None
        self.last_decision: KnowledgeEvolutionDecision | None = None

    def propose_from_reflections(
        self,
        title: str,
        content: str,
        reflections: tuple[ReflectionRecord, ...],
        *,
        rationale: str,
        action: KnowledgeEvolutionAction | str = KnowledgeEvolutionAction.CREATE,
        mental_models: tuple[MentalModel, ...] = (),
        targets: tuple[KnowledgeItem, ...] = (),
        confidence: float = 0.5,
        risk: KnowledgeEvolutionRisk | str = KnowledgeEvolutionRisk.MEDIUM,
        now: datetime | None = None,
    ) -> KnowledgeEvolutionProposal:
        proposal = self.engine.propose_from_reflections(
            title,
            content,
            reflections,
            rationale=rationale,
            action=action,
            mental_models=mental_models,
            targets=targets,
            confidence=confidence,
            risk=risk,
            now=now,
        )
        self.repository.add_proposal(proposal)
        self.last_proposal = proposal
        return proposal

    def decide(
        self,
        proposal: KnowledgeEvolutionProposal,
        *,
        approve: bool,
        reason: str,
        reviewer: str,
        now: datetime | None = None,
    ) -> KnowledgeEvolutionDecision:
        decision = self.engine.decide(
            proposal,
            approve=approve,
            reason=reason,
            reviewer=reviewer,
            now=now,
        )
        self.repository.add_decision(decision)
        self.last_decision = decision
        return decision

    def system_prompt_lines(self) -> tuple[str, ...]:
        return (
            "Evolución de conocimiento: toda mutación empieza como propuesta.",
            "Las reflexiones no se convierten automáticamente en hechos.",
            "La aprobación explícita no equivale todavía a aplicar el cambio.",
            "Preserva procedencia, revisión, reversibilidad y trazabilidad.",
        )
