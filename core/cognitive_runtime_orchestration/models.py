from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.llm_provider import LLMRequest


class CognitiveRuntimeStageStatus(str, Enum):
    APPLIED = "applied"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class CognitiveRuntimeContribution:
    stage: str
    status: CognitiveRuntimeStageStatus | str
    prompt_lines: tuple[str, ...] = ()
    reference_ids: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        stage = self.stage.strip()
        status = CognitiveRuntimeStageStatus(self.status)
        lines = tuple(item.strip() for item in self.prompt_lines if item.strip())
        refs = tuple(item.strip() for item in self.reference_ids if item.strip())
        rationale = tuple(item.strip() for item in self.rationale if item.strip())
        if not stage:
            raise ValueError("cognitive runtime stage must not be blank")
        if len(set(refs)) != len(refs):
            raise ValueError("cognitive runtime references must be unique")
        if status is CognitiveRuntimeStageStatus.APPLIED and not lines:
            raise ValueError("applied cognitive contribution requires prompt lines")
        if not rationale:
            raise ValueError("cognitive runtime rationale must not be empty")
        object.__setattr__(self, "stage", stage)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "prompt_lines", lines)
        object.__setattr__(self, "reference_ids", refs)
        object.__setattr__(self, "rationale", rationale)




class CognitiveStrategyApplicationStatus(str, Enum):
    READY = "ready"
    BLOCKED = "blocked"


class CognitiveStrategyApplicationOutcomeStatus(str, Enum):
    APPLIED = "applied"
    PARTIALLY_APPLIED = "partially_applied"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class GovernedCognitiveStrategyApplication:
    """Read-only projection of a strategy onto existing cognitive runtime stages."""

    strategy_fingerprint: str
    owner: str
    scope: str
    status: CognitiveStrategyApplicationStatus | str
    requested_stage_sequence: tuple[str, ...]
    evidence_requirements: tuple[str, ...]
    decision_required: bool
    requested_capabilities: tuple[str, ...]
    provenance: tuple[str, ...]
    source_fingerprint: str
    read_only: bool = True
    executes_tools: bool = False
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    grants_authority: bool = False

    _ALLOWED_STAGES = frozenset(
        {"reasoning", "planning", "reflection", "executive"}
    )

    def __post_init__(self) -> None:
        status = CognitiveStrategyApplicationStatus(self.status)
        owner = self.owner.strip()
        scope = self.scope.strip()
        fingerprint = self.strategy_fingerprint.strip()
        source = self.source_fingerprint.strip()
        stages = tuple(
            item.strip().casefold() for item in self.requested_stage_sequence
        )
        evidence = tuple(item.strip().casefold() for item in self.evidence_requirements)
        capabilities = tuple(
            item.strip().casefold() for item in self.requested_capabilities
        )
        provenance = tuple(item.strip() for item in self.provenance if item.strip())
        if not owner or not scope or not fingerprint or not source:
            raise ValueError("strategy application requires identity and lineage")
        if len(stages) != len(set(stages)):
            raise ValueError("strategy application stages must be unique")
        if any(item not in self._ALLOWED_STAGES for item in stages):
            raise ValueError("strategy application contains unsupported runtime stage")
        if len(evidence) != len(set(evidence)):
            raise ValueError("strategy evidence requirements must be unique")
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("strategy requested capabilities must be unique")
        if not provenance:
            raise ValueError("strategy application requires provenance")
        expected_source = sha256(
            repr(
                (
                    fingerprint,
                    owner,
                    scope,
                    status.value,
                    stages,
                    evidence,
                    self.decision_required,
                    capabilities,
                    provenance,
                )
            ).encode("utf-8")
        ).hexdigest()
        if source != expected_source:
            raise ValueError("strategy application fingerprint is inconsistent")
        if any(
            (
                not self.read_only,
                self.executes_tools,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.grants_authority,
            )
        ):
            raise ValueError("strategy application violates governed limits")
        if status is CognitiveStrategyApplicationStatus.BLOCKED and stages:
            raise ValueError(
                "blocked strategy application cannot request runtime stages"
            )
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "requested_stage_sequence", stages)
        object.__setattr__(self, "evidence_requirements", evidence)
        object.__setattr__(self, "requested_capabilities", capabilities)
        object.__setattr__(self, "provenance", provenance)
        object.__setattr__(self, "source_fingerprint", source)


@dataclass(frozen=True)
class CognitiveStrategyApplicationEvidence:
    """Truthful, read-only evidence of how a strategy touched the cognitive runtime."""

    strategy_fingerprint: str
    owner: str
    scope: str
    status: CognitiveStrategyApplicationOutcomeStatus | str
    requested_stage_sequence: tuple[str, ...]
    applied_stage_sequence: tuple[str, ...]
    skipped_stages: tuple[str, ...]
    failed_stages: tuple[str, ...]
    unmet_requirements: tuple[str, ...]
    contribution_reference_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    read_only: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        status = CognitiveStrategyApplicationOutcomeStatus(self.status)
        owner = self.owner.strip()
        scope = self.scope.strip()
        fingerprint = self.strategy_fingerprint.strip()
        source = self.source_fingerprint.strip()
        if not owner or not scope or not fingerprint or not source:
            raise ValueError(
                "strategy application evidence requires identity and lineage"
            )
        if not self.rationale_codes:
            raise ValueError("strategy application evidence requires rationale")
        if any(
            (
                not self.read_only,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("strategy application evidence violates governed limits")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "status", status)


@runtime_checkable
class CognitiveRuntimeContributor(Protocol):
    name: str

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution: ...


@dataclass(frozen=True)
class CognitiveRuntimeOrchestrationResult:
    owner: str
    session_id: str
    request: LLMRequest
    contributions: tuple[CognitiveRuntimeContribution, ...]
    strategy_application_evidence: CognitiveStrategyApplicationEvidence | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    orchestration_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        if not owner or not session_id:
            raise ValueError("cognitive orchestration identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("cognitive orchestration time must be timezone-aware")
        stages = tuple(item.stage.casefold() for item in self.contributions)
        if len(set(stages)) != len(stages):
            raise ValueError("cognitive orchestration stages must be unique")
        contribution_states = tuple(
            f"{item.stage}:{item.status.value}" for item in self.contributions
        )
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    self.request.prompt,
                    self.created_at.isoformat(),
                    *contribution_states,
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.orchestration_id and self.orchestration_id != expected:
            raise ValueError("cognitive orchestration id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "orchestration_id", expected)

    @property
    def activated_stages(self) -> tuple[str, ...]:
        return tuple(
            item.stage
            for item in self.contributions
            if item.status is CognitiveRuntimeStageStatus.APPLIED
        )
