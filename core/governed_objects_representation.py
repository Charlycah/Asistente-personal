from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.object_knowledge import ObjectKnowledgeProfile, ObjectKnowledgeStatus


class ObjectRepresentationStatus(StrEnum):
    COMPLETE = "complete"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedObject:
    object_id: str
    object_ref: str
    kind: str
    label: str
    attributes: tuple[str, ...]
    count: int
    confidence: float
    source_profile_id: str
    evidence_refs: tuple[str, ...]
    active: bool = True


@dataclass(frozen=True)
class GovernedObjectsRepresentation:
    representation_id: str
    status: ObjectRepresentationStatus
    objects: tuple[GovernedObject, ...]
    source_profile_ids: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m392.4"
    canonical_authority: str = "internal_world_model"
    source_authority: str = "object_knowledge"
    read_only: bool = True
    persistence_added: bool = False
    inventory_added: bool = False
    object_detection_added: bool = False
    object_tracking_added: bool = False
    location_inferred: bool = False
    ownership_inferred: bool = False
    modifies_source_data: bool = False
    grants_authority: bool = False
    runtime_behavior_changed: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "internal_world_model":
            raise ValueError("objects representation must preserve world authority")
        if self.source_authority != "object_knowledge":
            raise ValueError("objects representation source authority is invalid")
        if tuple(sorted(self.objects, key=_object_sort_key)) != self.objects:
            raise ValueError("objects must use canonical ordering")
        if tuple(sorted(set(self.source_profile_ids))) != self.source_profile_ids:
            raise ValueError("object profile ids must be unique and ordered")
        if any(
            (
                not self.read_only,
                self.persistence_added,
                self.inventory_added,
                self.object_detection_added,
                self.object_tracking_added,
                self.location_inferred,
                self.ownership_inferred,
                self.modifies_source_data,
                self.grants_authority,
                self.runtime_behavior_changed,
                self.starts_background_process,
            )
        ):
            raise ValueError("objects representation violates governed limits")

    def object(self, object_id: str) -> GovernedObject | None:
        return next(
            (item for item in self.objects if item.object_id == object_id),
            None,
        )


class GovernedObjectsRepresentationView:
    """Pure world-model projection over already consolidated object knowledge."""

    def build(
        self,
        profiles: tuple[ObjectKnowledgeProfile, ...] = (),
    ) -> GovernedObjectsRepresentation:
        self._validate_unique_profiles(profiles)
        objects: list[GovernedObject] = []
        risks: list[str] = []
        for profile in profiles:
            if profile.status is not ObjectKnowledgeStatus.AVAILABLE:
                risks.append(f"object_profile_not_available:{profile.profile_id}")
                continue
            if not profile.request.knowledge_declared:
                risks.append(f"object_knowledge_not_declared:{profile.profile_id}")
                continue
            for item in profile.objects:
                objects.append(
                    GovernedObject(
                        object_id=f"object:{profile.profile_id}:{item.object_ref}",
                        object_ref=item.object_ref,
                        kind=item.object_kind.value,
                        label=item.label,
                        attributes=tuple(sorted(item.attributes)),
                        count=item.count,
                        confidence=item.confidence,
                        source_profile_id=profile.profile_id,
                        evidence_refs=tuple(sorted(item.evidence_refs)),
                    )
                )
        canonical_objects = tuple(sorted(objects, key=_object_sort_key))
        canonical_risks = tuple(sorted(set(risks)))
        source_profile_ids = tuple(
            sorted({item.source_profile_id for item in canonical_objects})
        )
        evidence_codes = (
            "authority:internal_world_model",
            "source_authority:object_knowledge",
            "objects:declared_knowledge_only",
        )
        fingerprint = _fingerprint(canonical_objects, canonical_risks)
        return GovernedObjectsRepresentation(
            representation_id=f"objects-world-{fingerprint[:16]}",
            status=self._status(canonical_objects, canonical_risks),
            objects=canonical_objects,
            source_profile_ids=source_profile_ids,
            evidence_codes=evidence_codes,
            risk_codes=canonical_risks,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _validate_unique_profiles(
        profiles: tuple[ObjectKnowledgeProfile, ...],
    ) -> None:
        ids = tuple(item.profile_id for item in profiles)
        if len(ids) != len(set(ids)):
            raise ValueError("object knowledge profile ids must be unique")

    @staticmethod
    def _status(
        objects: tuple[GovernedObject, ...],
        risks: tuple[str, ...],
    ) -> ObjectRepresentationStatus:
        if risks:
            return ObjectRepresentationStatus.REVIEW_REQUIRED
        if not objects:
            return ObjectRepresentationStatus.EMPTY
        return ObjectRepresentationStatus.COMPLETE


def _object_sort_key(item: GovernedObject) -> tuple[str, str, str]:
    return item.kind, item.label.casefold(), item.object_id


def _fingerprint(
    objects: tuple[GovernedObject, ...],
    risks: tuple[str, ...],
) -> str:
    payload = "||".join(
        (
            *(
                "|".join(
                    (
                        item.object_id,
                        item.object_ref,
                        item.kind,
                        item.label,
                        ",".join(item.attributes),
                        str(item.count),
                        str(item.confidence),
                        item.source_profile_id,
                        ",".join(item.evidence_refs),
                    )
                )
                for item in objects
            ),
            *risks,
        )
    )
    return sha256(payload.encode("utf-8")).hexdigest()
