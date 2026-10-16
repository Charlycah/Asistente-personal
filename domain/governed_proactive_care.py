from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping, Sequence

from .exceptions import DomainError
from .governed_cognitive_judgment import (
    GovernedCognitiveJudgment,
    GovernedJudgmentOutcome,
)


class GovernedCareKind(StrEnum):
    INFORM = "inform"
    REMIND = "remind"
    WARN = "warn"
    SUGGEST = "suggest"


class GovernedCareUrgency(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass(frozen=True)
class GovernedCareProposal:
    proposal_id: str
    judgment_id: str
    objective_ids: tuple[str, ...]
    beneficiaries: tuple[str, ...]
    kind: GovernedCareKind
    urgency: GovernedCareUrgency
    situation: str
    rationale: str
    proposed_message: str
    suggested_response: str
    evidence: tuple[str, ...]
    risks: tuple[str, ...]
    authorization_required: bool = True
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "proposal_id",
            "judgment_id",
            "situation",
            "rationale",
            "proposed_message",
            "suggested_response",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        for field_name in (
            "objective_ids",
            "beneficiaries",
            "evidence",
            "risks",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalized_strings(field_name, getattr(self, field_name)),
            )
        if not self.objective_ids:
            raise DomainError("care proposal requires governed objectives")
        if not self.beneficiaries:
            raise DomainError("care proposal requires explicit beneficiaries")
        if not isinstance(self.kind, GovernedCareKind):
            raise DomainError("kind must be a GovernedCareKind")
        if not isinstance(self.urgency, GovernedCareUrgency):
            raise DomainError("urgency must be a GovernedCareUrgency")
        if self.authorization_required is not True:
            raise DomainError("care proposals must require authorization")
        object.__setattr__(self, "metadata", _immutable_mapping(self.metadata))


@dataclass(frozen=True)
class GovernedProactiveCareSnapshot:
    schema_version: str
    authority: str
    persistence_enabled: bool
    autonomous_monitoring_enabled: bool
    autonomous_notification_enabled: bool
    authorization_authority: bool
    execution_authority: bool
    conversation_authority: bool
    recorded_proposals: int
    kinds: tuple[GovernedCareKind, ...]
    urgencies: tuple[GovernedCareUrgency, ...]


class GovernedProactiveCare:
    """Gateway-owned authority for explicit, advisory household care proposals."""

    SCHEMA_VERSION = "m347.2"
    AUTHORITY = "domain.governed_proactive_care:GovernedProactiveCare"

    def __init__(self) -> None:
        self._proposals: dict[str, GovernedCareProposal] = {}

    @property
    def snapshot(self) -> GovernedProactiveCareSnapshot:
        return GovernedProactiveCareSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            persistence_enabled=False,
            autonomous_monitoring_enabled=False,
            autonomous_notification_enabled=False,
            authorization_authority=False,
            execution_authority=False,
            conversation_authority=False,
            recorded_proposals=len(self._proposals),
            kinds=tuple(GovernedCareKind),
            urgencies=tuple(GovernedCareUrgency),
        )

    def propose(
        self,
        judgment: GovernedCognitiveJudgment,
        **proposal_fields,
    ) -> GovernedCareProposal:
        proposal_id = proposal_fields.get("proposal_id")
        if proposal_id in self._proposals:
            raise DomainError(f"proposal_id already exists: {proposal_id}")
        if judgment.outcome is not GovernedJudgmentOutcome.READY:
            raise DomainError("care proposal requires a ready cognitive judgment")
        supplied_judgment_id = proposal_fields.pop("judgment_id", None)
        supplied_objective_ids = tuple(proposal_fields.pop("objective_ids", ()))
        if supplied_judgment_id and supplied_judgment_id != judgment.judgment_id:
            raise DomainError("judgment_id must match governed judgment")
        if supplied_objective_ids and supplied_objective_ids != judgment.objective_ids:
            raise DomainError("objective_ids must match governed judgment")
        proposal = GovernedCareProposal(
            judgment_id=judgment.judgment_id,
            objective_ids=judgment.objective_ids,
            **proposal_fields,
        )
        self._proposals[proposal.proposal_id] = proposal
        return proposal

    def find(self, proposal_id: str) -> GovernedCareProposal | None:
        return self._proposals.get(proposal_id)

    def for_objective(self, objective_id: str) -> tuple[GovernedCareProposal, ...]:
        return tuple(
            proposal
            for proposal in self._proposals.values()
            if objective_id in proposal.objective_ids
        )

    def for_beneficiary(self, beneficiary: str) -> tuple[GovernedCareProposal, ...]:
        return tuple(
            proposal
            for proposal in self._proposals.values()
            if beneficiary in proposal.beneficiaries
        )


def _normalized_strings(
    field_name: str, values: Sequence[str]
) -> tuple[str, ...]:
    normalized = tuple(values)
    if not all(isinstance(value, str) and value.strip() for value in normalized):
        raise DomainError(f"{field_name} must contain only non-empty strings")
    if len(normalized) != len(set(normalized)):
        raise DomainError(f"{field_name} cannot contain duplicates")
    return normalized


def _immutable_mapping(values: Mapping[str, str] | None) -> Mapping[str, str]:
    normalized = dict(values or {})
    if not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in normalized.items()
    ):
        raise DomainError("metadata must contain non-empty string keys and values")
    return MappingProxyType(normalized)
