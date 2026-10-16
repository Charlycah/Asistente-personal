from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable
from uuid import uuid4

from core.adaptive_cognition.episodic_memory import Episode, EpisodeReference
from core.scope_guard import ScopeDomain


class MentalModelKind(str, Enum):
    PERSON = "person"
    PROJECT = "project"
    TASK = "task"
    SYSTEM = "system"
    ENVIRONMENT = "environment"
    CONCEPT = "concept"
    SELF = "self"


class MentalModelStatus(str, Enum):
    ACTIVE = "active"
    REVIEW_REQUIRED = "review_required"
    RETIRED = "retired"


class ModelAssertionStatus(str, Enum):
    TENTATIVE = "tentative"
    ACCEPTED = "accepted"
    DISPUTED = "disputed"
    RETIRED = "retired"


@dataclass(frozen=True)
class ModelAssertion:
    predicate: str
    value: str
    confidence: float
    status: ModelAssertionStatus | str = ModelAssertionStatus.TENTATIVE
    references: tuple[EpisodeReference, ...] = ()
    asserted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assertion_id: str = ""

    def __post_init__(self) -> None:
        status = ModelAssertionStatus(self.status)
        if not self.predicate.strip() or not self.value.strip():
            raise ValueError("model assertion fields must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("model assertion confidence must be between zero and one")
        if self.asserted_at.tzinfo is None:
            raise ValueError("model assertion timestamp must be timezone-aware")
        keys = {(item.reference_type, item.reference_id) for item in self.references}
        if len(keys) != len(self.references):
            raise ValueError("model assertion references must be unique")
        expected = sha256(
            "|".join(
                (
                    self.predicate.strip().lower(),
                    self.value.strip(),
                    str(self.confidence),
                    status.value,
                    self.asserted_at.isoformat(),
                    ";".join(
                        f"{item.reference_type}:{item.reference_id}"
                        for item in self.references
                    ),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assertion_id and self.assertion_id != expected:
            raise ValueError("model assertion id is inconsistent")
        object.__setattr__(self, "assertion_id", expected)

    @property
    def normalized_status(self) -> ModelAssertionStatus:
        return ModelAssertionStatus(self.status)

    def to_dict(self) -> dict[str, object]:
        return {
            "assertion_id": self.assertion_id,
            "predicate": self.predicate,
            "value": self.value,
            "confidence": self.confidence,
            "status": self.normalized_status.value,
            "references": [item.to_dict() for item in self.references],
            "asserted_at": self.asserted_at.isoformat(),
        }


@dataclass(frozen=True)
class MentalModel:
    subject: str
    kind: MentalModelKind | str
    owner: str
    domains: tuple[ScopeDomain | str, ...]
    assertions: tuple[ModelAssertion, ...] = ()
    status: MentalModelStatus | str = MentalModelStatus.ACTIVE
    labels: tuple[str, ...] = ()
    model_id: str = field(default_factory=lambda: uuid4().hex)
    revision: int = 1
    supersedes_revision: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        MentalModelKind(self.kind)
        MentalModelStatus(self.status)
        domains = tuple(ScopeDomain(item) for item in self.domains)
        identity = (self.subject, self.owner, self.model_id)
        if any(not item.strip() for item in identity):
            raise ValueError("mental model identity fields must not be empty")
        if not domains or len(set(domains)) != len(domains):
            raise ValueError("mental model domains must be non-empty and unique")
        invalid_labels = len(set(self.labels)) != len(self.labels) or any(
            not item.strip() for item in self.labels
        )
        if invalid_labels:
            raise ValueError("mental model labels must be unique and non-empty")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("mental model timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("mental model update cannot precede creation")
        if self.revision < 1:
            raise ValueError("mental model revision must be positive")
        if self.revision == 1 and self.supersedes_revision is not None:
            raise ValueError("first mental model revision cannot supersede another")
        if self.revision > 1 and self.supersedes_revision != self.revision - 1:
            raise ValueError("mental model revisions must be contiguous")
        ids = {item.assertion_id for item in self.assertions}
        if len(ids) != len(self.assertions):
            raise ValueError("mental model assertions must be unique")

    @property
    def normalized_kind(self) -> MentalModelKind:
        return MentalModelKind(self.kind)

    @property
    def normalized_status(self) -> MentalModelStatus:
        return MentalModelStatus(self.status)

    @property
    def normalized_domains(self) -> tuple[ScopeDomain, ...]:
        return tuple(ScopeDomain(item) for item in self.domains)

    @property
    def fingerprint(self) -> str:
        return sha256(
            "|".join(
                (
                    self.model_id,
                    str(self.revision),
                    self.subject,
                    self.normalized_kind.value,
                    self.normalized_status.value,
                    ";".join(item.assertion_id for item in self.assertions),
                )
            ).encode("utf-8")
        ).hexdigest()

    def revise(
        self,
        *,
        assertions: tuple[ModelAssertion, ...] | None = None,
        status: MentalModelStatus | str | None = None,
        updated_at: datetime | None = None,
    ) -> MentalModel:
        return replace(
            self,
            assertions=self.assertions if assertions is None else assertions,
            status=self.status if status is None else status,
            revision=self.revision + 1,
            supersedes_revision=self.revision,
            updated_at=updated_at or datetime.now(timezone.utc),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "revision": self.revision,
            "subject": self.subject,
            "kind": self.normalized_kind.value,
            "owner": self.owner,
            "domains": [item.value for item in self.normalized_domains],
            "status": self.normalized_status.value,
            "labels": list(self.labels),
            "assertions": [item.to_dict() for item in self.assertions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True)
class ModelUpdateProposal:
    model_id: str
    additions: tuple[ModelAssertion, ...] = ()
    retire_assertion_ids: tuple[str, ...] = ()
    rationale: str = ""
    requires_review: bool = False
    proposal_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.model_id.strip() or not self.proposal_id.strip():
            raise ValueError("model proposal identity must not be empty")
        if not self.rationale.strip():
            raise ValueError("model proposal rationale must not be empty")
        if len(set(self.retire_assertion_ids)) != len(self.retire_assertion_ids):
            raise ValueError("retired assertion ids must be unique")
        if not self.additions and not self.retire_assertion_ids:
            raise ValueError("model proposal must contain a change")


@runtime_checkable
class MentalModelRepository(Protocol):
    def save(self, model: MentalModel) -> MentalModel: ...
    def get(self, model_id: str) -> MentalModel | None: ...
    def list_all(self) -> tuple[MentalModel, ...]: ...
    def history(self, model_id: str) -> tuple[MentalModel, ...]: ...


class InMemoryMentalModelRepository:
    def __init__(self) -> None:
        self._current: dict[str, MentalModel] = {}
        self._history: dict[str, list[MentalModel]] = {}

    def save(self, model: MentalModel) -> MentalModel:
        current = self._current.get(model.model_id)
        expected = 1 if current is None else current.revision + 1
        if model.revision != expected:
            raise ValueError("mental model repository requires contiguous revisions")
        self._history.setdefault(model.model_id, []).append(model)
        self._current[model.model_id] = model
        return model

    def get(self, model_id: str) -> MentalModel | None:
        return self._current.get(model_id)

    def list_all(self) -> tuple[MentalModel, ...]:
        return tuple(
            sorted(
                self._current.values(),
                key=lambda item: (item.subject, item.model_id),
            )
        )

    def history(self, model_id: str) -> tuple[MentalModel, ...]:
        return tuple(self._history.get(model_id, ()))


@dataclass(frozen=True)
class MentalModelQuery:
    text: str = ""
    owner: str = "shared"
    kinds: tuple[MentalModelKind | str, ...] = ()
    domains: tuple[ScopeDomain | str, ...] = ()
    statuses: tuple[MentalModelStatus | str, ...] = (MentalModelStatus.ACTIVE,)
    limit: int = 10

    def __post_init__(self) -> None:
        if not self.owner.strip() or self.limit <= 0:
            raise ValueError("mental model query is invalid")
        tuple(MentalModelKind(item) for item in self.kinds)
        tuple(ScopeDomain(item) for item in self.domains)
        tuple(MentalModelStatus(item) for item in self.statuses)


@dataclass(frozen=True)
class MentalModelQueryResult:
    query: MentalModelQuery
    models: tuple[MentalModel, ...]
    considered: int


@dataclass(frozen=True)
class MentalModelPolicy:
    automatic_acceptance_threshold: float = 0.85
    conflict_tolerance: float = 0.05
    max_assertions_per_model: int = 100

    def __post_init__(self) -> None:
        if not 0.0 <= self.automatic_acceptance_threshold <= 1.0:
            raise ValueError("acceptance threshold must be between zero and one")
        if not 0.0 <= self.conflict_tolerance <= 1.0:
            raise ValueError("conflict tolerance must be between zero and one")
        if self.max_assertions_per_model <= 0:
            raise ValueError("maximum assertions must be positive")


class MentalModelManager:
    def __init__(
        self,
        repository: MentalModelRepository | None = None,
        *,
        policy: MentalModelPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryMentalModelRepository()
        self.policy = policy or MentalModelPolicy()
        self.last_model: MentalModel | None = None

    def create(
        self,
        subject: str,
        *,
        kind: MentalModelKind | str,
        owner: str = "shared",
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
        labels: tuple[str, ...] = (),
    ) -> MentalModel:
        self.last_model = self.repository.save(
            MentalModel(
                subject=subject,
                kind=kind,
                owner=owner,
                domains=domains,
                labels=labels,
            )
        )
        return self.last_model

    def propose_from_episode(
        self,
        model_id: str,
        episode: Episode,
        *,
        predicate: str,
        value: str,
        confidence: float | None = None,
        rationale: str = "Derived from governed episode",
    ) -> ModelUpdateProposal:
        self._require(model_id)
        assertion = ModelAssertion(
            predicate=predicate,
            value=value,
            confidence=episode.confidence if confidence is None else confidence,
            references=(
                EpisodeReference("episode", episode.episode_id, episode.fingerprint),
            ),
        )
        return ModelUpdateProposal(
            model_id=model_id,
            additions=(assertion,),
            rationale=rationale,
            requires_review=(
                assertion.confidence < self.policy.automatic_acceptance_threshold
            ),
        )

    def apply(
        self,
        proposal: ModelUpdateProposal,
        *,
        approved: bool = False,
    ) -> MentalModel:
        model = self._require(proposal.model_id)
        if proposal.requires_review and not approved:
            raise PermissionError("mental model proposal requires explicit approval")
        remaining = [
            item
            for item in model.assertions
            if item.assertion_id not in set(proposal.retire_assertion_ids)
        ]
        additions: list[ModelAssertion] = []
        for candidate in proposal.additions:
            conflicts = [
                item
                for item in remaining
                if item.predicate.casefold() == candidate.predicate.casefold()
                and item.value.casefold() != candidate.value.casefold()
                and item.normalized_status
                not in {
                    ModelAssertionStatus.RETIRED,
                    ModelAssertionStatus.DISPUTED,
                }
            ]
            if conflicts:
                candidate = replace(
                    candidate,
                    status=ModelAssertionStatus.DISPUTED,
                    assertion_id="",
                )
                remaining = [
                    replace(
                        item,
                        status=ModelAssertionStatus.DISPUTED,
                        assertion_id="",
                    )
                    if item in conflicts
                    else item
                    for item in remaining
                ]
            elif candidate.confidence >= self.policy.automatic_acceptance_threshold:
                candidate = replace(
                    candidate,
                    status=ModelAssertionStatus.ACCEPTED,
                    assertion_id="",
                )
            additions.append(candidate)
        assertions = tuple(remaining + additions)
        if len(assertions) > self.policy.max_assertions_per_model:
            raise ValueError("mental model assertion capacity exceeded")
        status = (
            MentalModelStatus.REVIEW_REQUIRED
            if any(
                item.normalized_status is ModelAssertionStatus.DISPUTED
                for item in assertions
            )
            else MentalModelStatus.ACTIVE
        )
        self.last_model = self.repository.save(
            model.revise(assertions=assertions, status=status)
        )
        return self.last_model

    def query(self, query: MentalModelQuery) -> MentalModelQueryResult:
        models = self.repository.list_all()
        terms = {item for item in query.text.casefold().split() if item}
        allowed_kinds = {MentalModelKind(item) for item in query.kinds}
        allowed_domains = {ScopeDomain(item) for item in query.domains}
        allowed_statuses = {MentalModelStatus(item) for item in query.statuses}
        eligible = []
        for model in models:
            if model.owner not in {query.owner, "shared"}:
                continue
            if model.normalized_status not in allowed_statuses:
                continue
            if allowed_kinds and model.normalized_kind not in allowed_kinds:
                continue
            if allowed_domains and not allowed_domains.intersection(
                model.normalized_domains
            ):
                continue
            haystack = " ".join(
                [model.subject, *model.labels]
                + [f"{item.predicate} {item.value}" for item in model.assertions]
            ).casefold()
            score = sum(term in haystack for term in terms)
            eligible.append((score, model.updated_at, model.model_id, model))
        ranked = tuple(
            item[3] for item in sorted(eligible, reverse=True)[: query.limit]
        )
        return MentalModelQueryResult(
            query=query,
            models=ranked,
            considered=len(models),
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = (
            "Modelos mentales gobernados: son representaciones revisables, no hechos.",
            "Las contradicciones deben conservarse y marcarse para revisión.",
        )
        if self.last_model is None:
            return lines + ("Último modelo mental: ninguno.",)
        return lines + (
            f"Último modelo mental: {self.last_model.subject}.",
            f"Estado del modelo: {self.last_model.normalized_status.value}.",
        )

    def _require(self, model_id: str) -> MentalModel:
        model = self.repository.get(model_id)
        if model is None:
            raise KeyError(f"unknown mental model: {model_id}")
        return model
