from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum

from app.cognitive_hypothesis_workspace import (
    CognitiveHypothesisStatus,
    CognitiveHypothesisWorkspaceSnapshot,
)
from app.cognitive_thought_stream import CognitiveThoughtStreamSnapshot


class CognitiveWorldEntityKind(str, Enum):
    FOCUS = "focus"
    HYPOTHESIS = "hypothesis"


class CognitiveWorldFactStatus(str, Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    UNCERTAIN = "uncertain"
    RETIRED = "retired"


class CognitiveWorldModelTransition(str, Enum):
    NO_CHANGE = "no_change"
    CREATED = "created"
    UPDATED = "updated"
    REFRAMED = "reframed"
    SUSPENDED = "suspended"


@dataclass(frozen=True)
class CognitiveWorldModelPolicy:
    max_entities: int = 12
    max_relations: int = 16
    uncertainty_threshold: float = 0.5

    def __post_init__(self) -> None:
        if self.max_entities <= 0 or self.max_relations <= 0:
            raise ValueError("world model limits must be positive")
        if not 0 <= self.uncertainty_threshold <= 1:
            raise ValueError(
                "world model uncertainty threshold must be between zero and one"
            )


@dataclass(frozen=True)
class CognitiveWorldEntity:
    key: str
    kind: CognitiveWorldEntityKind
    label: str
    status: CognitiveWorldFactStatus
    confidence: float
    sources: tuple[str, ...]
    first_seen_at: datetime
    last_seen_at: datetime
    revisions: int


@dataclass(frozen=True)
class CognitiveWorldRelation:
    key: str
    subject_key: str
    predicate: str
    object_key: str
    status: CognitiveWorldFactStatus
    confidence: float
    sources: tuple[str, ...]
    updated_at: datetime


@dataclass(frozen=True)
class CognitiveWorldModelSnapshot:
    generated_at: datetime
    active_focus_key: str | None
    leading_hypothesis_key: str | None
    transition: CognitiveWorldModelTransition
    entities: tuple[CognitiveWorldEntity, ...]
    relations: tuple[CognitiveWorldRelation, ...]
    summary: str
    rationale: str
    requires_user_authorization: bool = False


class CognitiveWorldModel:
    """Maintain a concise, provenance-aware internal model of current reality."""

    def __init__(self, *, policy: CognitiveWorldModelPolicy | None = None) -> None:
        self.policy = policy or CognitiveWorldModelPolicy()
        self._entities: dict[str, CognitiveWorldEntity] = {}
        self._relations: dict[str, CognitiveWorldRelation] = {}
        self._active_focus_key: str | None = None
        self._leading_hypothesis_key: str | None = None

    def update(
        self,
        thought_stream: CognitiveThoughtStreamSnapshot | None,
        workspace: CognitiveHypothesisWorkspaceSnapshot | None,
        *,
        now: datetime | None = None,
    ) -> CognitiveWorldModelSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        previous_leader = self._leading_hypothesis_key
        focus = self._active_thread(thought_stream)
        if focus is None or workspace is None:
            transition = self._suspend(timestamp)
        else:
            created = focus.key not in self._entities
            self._active_focus_key = focus.key
            self._upsert_entity(
                key=focus.key,
                kind=CognitiveWorldEntityKind.FOCUS,
                label=focus.title,
                status=CognitiveWorldFactStatus.OBSERVED,
                confidence=focus.confidence,
                sources=focus.evidence_sources,
                now=timestamp,
            )
            self._sync_hypotheses(workspace, focus.key, timestamp)
            self._leading_hypothesis_key = workspace.leading_key
            self._retire_other_foci(focus.key, timestamp)
            if created:
                transition = CognitiveWorldModelTransition.CREATED
            elif previous_leader != self._leading_hypothesis_key:
                transition = CognitiveWorldModelTransition.REFRAMED
            else:
                transition = CognitiveWorldModelTransition.UPDATED
        self._trim()
        return self._snapshot(timestamp, transition)

    @staticmethod
    def _active_thread(thought_stream):
        if thought_stream is None or thought_stream.active_key is None:
            return None
        return next(
            (
                thread
                for thread in thought_stream.threads
                if thread.key == thought_stream.active_key
            ),
            None,
        )

    def _sync_hypotheses(self, workspace, focus_key: str, now: datetime) -> None:
        active_keys: set[str] = set()
        for hypothesis in workspace.hypotheses:
            if hypothesis.thread_key != focus_key:
                continue
            active_keys.add(hypothesis.key)
            status = self._hypothesis_status(hypothesis.status, hypothesis.confidence)
            self._upsert_entity(
                key=hypothesis.key,
                kind=CognitiveWorldEntityKind.HYPOTHESIS,
                label=hypothesis.proposition,
                status=status,
                confidence=hypothesis.confidence,
                sources=hypothesis.evidence_sources,
                now=now,
            )
            relation_key = f"{focus_key}:interpreted_by:{hypothesis.key}"
            self._relations[relation_key] = CognitiveWorldRelation(
                key=relation_key,
                subject_key=focus_key,
                predicate="interpreted_by",
                object_key=hypothesis.key,
                status=status,
                confidence=hypothesis.confidence,
                sources=hypothesis.evidence_sources,
                updated_at=now,
            )
        for key, entity in tuple(self._entities.items()):
            if (
                entity.kind is CognitiveWorldEntityKind.HYPOTHESIS
                and key not in active_keys
            ):
                self._entities[key] = replace(
                    entity,
                    status=CognitiveWorldFactStatus.RETIRED,
                    last_seen_at=now,
                )

    def _hypothesis_status(self, status, confidence: float) -> CognitiveWorldFactStatus:
        if status in {
            CognitiveHypothesisStatus.SUSPENDED,
            CognitiveHypothesisStatus.REJECTED,
        }:
            return CognitiveWorldFactStatus.RETIRED
        if confidence < self.policy.uncertainty_threshold:
            return CognitiveWorldFactStatus.UNCERTAIN
        return CognitiveWorldFactStatus.INFERRED

    def _upsert_entity(self, *, key, kind, label, status, confidence, sources, now):
        existing = self._entities.get(key)
        self._entities[key] = CognitiveWorldEntity(
            key=key,
            kind=kind,
            label=label,
            status=status,
            confidence=max(0.0, min(1.0, round(confidence, 6))),
            sources=tuple(dict.fromkeys(sources)),
            first_seen_at=existing.first_seen_at if existing else now,
            last_seen_at=now,
            revisions=(existing.revisions + 1) if existing else 1,
        )

    def _retire_other_foci(self, active_key: str, now: datetime) -> None:
        for key, entity in tuple(self._entities.items()):
            if entity.kind is CognitiveWorldEntityKind.FOCUS and key != active_key:
                self._entities[key] = replace(
                    entity,
                    status=CognitiveWorldFactStatus.RETIRED,
                    last_seen_at=now,
                )

    def _suspend(self, now: datetime) -> CognitiveWorldModelTransition:
        if self._active_focus_key is None:
            return CognitiveWorldModelTransition.NO_CHANGE
        for key, entity in tuple(self._entities.items()):
            if entity.status is not CognitiveWorldFactStatus.RETIRED:
                self._entities[key] = replace(
                    entity,
                    status=CognitiveWorldFactStatus.RETIRED,
                    last_seen_at=now,
                )
        self._active_focus_key = None
        self._leading_hypothesis_key = None
        return CognitiveWorldModelTransition.SUSPENDED

    def _trim(self) -> None:
        entities = sorted(
            self._entities.values(),
            key=lambda item: (
                item.status is not CognitiveWorldFactStatus.RETIRED,
                item.last_seen_at,
            ),
            reverse=True,
        )[: self.policy.max_entities]
        allowed = {entity.key for entity in entities}
        self._entities = {entity.key: entity for entity in entities}
        relations = [
            relation
            for relation in self._relations.values()
            if relation.subject_key in allowed and relation.object_key in allowed
        ]
        relations.sort(key=lambda item: item.updated_at, reverse=True)
        selected_relations = relations[: self.policy.max_relations]
        self._relations = {relation.key: relation for relation in selected_relations}

    def _snapshot(self, now, transition):
        entities = tuple(sorted(self._entities.values(), key=lambda item: item.key))
        relations = tuple(sorted(self._relations.values(), key=lambda item: item.key))
        summary = (
            f"Modelo activo sobre {self._active_focus_key} con "
            f"{len(relations)} relaciones"
            if self._active_focus_key is not None
            else "No hay un modelo cognitivo activo"
        )
        return CognitiveWorldModelSnapshot(
            generated_at=now,
            active_focus_key=self._active_focus_key,
            leading_hypothesis_key=self._leading_hypothesis_key,
            transition=transition,
            entities=entities,
            relations=relations,
            summary=summary,
            rationale=(
                f"world_model:{transition.value}:{self._active_focus_key or 'none'}"
            ),
        )
