from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

from app.productive_organization_advisory_wiring import (
    ProductiveOrganizationAdvisoryWiring,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.explicit_human_decision_deliberation import (
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)
from core.explicit_organization_reference_acquisition import (
    ExplicitOrganizationReference,
)
from core.intelligent_personal_organization import (
    IntelligentPersonalOrganizationView,
    PersonalOrganizationItem,
)
from core.partial_canonical_organization_snapshot import (
    OrganizationSourceAvailability,
    OrganizationSourceKind,
    PartialCanonicalOrganizationSnapshotBuilder,
)
from core.partial_organization_m391_5_consumption import (
    PartialOrganizationM3915Consumer,
)
from core.personal_knowledge_base import (
    InMemoryPersonalKnowledgeRepository,
    KnowledgeKind,
    KnowledgeOwner,
    KnowledgeSource,
    PersonalKnowledgeBaseManager,
)
from core.personal_organization import PersonalOrganizationCapability
from core.productive_organization_evidence_projection import (
    ProductiveOrganizationEvidenceProjection,
)

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)


def _manager() -> PersonalKnowledgeBaseManager:
    return PersonalKnowledgeBaseManager(
        repository=InMemoryPersonalKnowledgeRepository()
    )


def _note(
    *,
    owner: KnowledgeOwner = KnowledgeOwner.CARLOS,
    title: str = "Idea ROBY",
    content: str = "Revisar integración de notas con organización personal.",
):
    return _manager().remember(
        title=title,
        content=content,
        kind=KnowledgeKind.NOTE,
        source=KnowledgeSource.MANUAL_ENTRY,
        owner=owner,
        now=NOW,
    )


def test_nps1_m74_has_explicit_note_semantics_and_owner() -> None:
    item = _note()

    assert item.normalized_kind is KnowledgeKind.NOTE
    assert item.normalized_owner is KnowledgeOwner.CARLOS
    assert item.normalized_source is KnowledgeSource.MANUAL_ENTRY
    assert item.content.startswith("Revisar integración")


def test_nps2_m74_candidate_approval_preserves_note_semantics() -> None:
    manager = _manager()
    candidate = manager.create_candidate(
        title="Llamar a Juan",
        content="Preguntarle por el presupuesto.",
        kind=KnowledgeKind.NOTE,
        source=KnowledgeSource.MANUAL_ENTRY,
        owner=KnowledgeOwner.CARLOS,
        now=NOW,
    )

    item = manager.approve(candidate, now=NOW)

    assert item.normalized_kind is KnowledgeKind.NOTE
    assert item.normalized_owner is KnowledgeOwner.CARLOS
    assert item.title == "Llamar a Juan"


def test_nps3_m74_recall_filters_note_owner_fail_closed() -> None:
    manager = _manager()
    manager.remember(
        title="Carlos note",
        content="Privada de Carlos",
        kind=KnowledgeKind.NOTE,
        owner=KnowledgeOwner.CARLOS,
        now=NOW,
    )
    manager.remember(
        title="Partner note",
        content="Privada de partner",
        kind=KnowledgeKind.NOTE,
        owner=KnowledgeOwner.PARTNER,
        now=NOW,
    )

    carlos = manager.recall(
        kind=KnowledgeKind.NOTE,
        owner=KnowledgeOwner.CARLOS,
    )

    assert tuple(item.title for item in carlos) == ("Carlos note",)
    assert all(item.normalized_owner is KnowledgeOwner.CARLOS for item in carlos)


def test_nps4_existing_m391_5_accepts_notes_capability_items() -> None:
    item = _note()
    projected = PersonalOrganizationItem(
        item_id=item.item_id,
        capability=PersonalOrganizationCapability.NOTES,
        title=item.title,
        source_reference=f"knowledge:note:{item.item_id}",
    )

    report = IntelligentPersonalOrganizationView().organize((projected,))

    assert report.canonical_authority == "PersonalOrganizationAuthority"
    assert report.recommendations[0].item_id == item.item_id
    assert report.recommendations[0].capability is PersonalOrganizationCapability.NOTES
    assert report.modifies_items is False
    assert report.executes_actions is False


def test_nps5_persistent_personal_knowledge_repository_exists() -> None:
    from infrastructure.repositories.sqlite_personal_knowledge_repository import (
        SQLitePersonalKnowledgeRepository,
    )

    repository = SQLitePersonalKnowledgeRepository(":memory:")
    manager = PersonalKnowledgeBaseManager(repository=repository)
    item = manager.remember(
        title="Persisted note",
        content="Debe sobrevivir al repository productivo.",
        kind=KnowledgeKind.NOTE,
        owner=KnowledgeOwner.CARLOS,
        now=NOW,
    )

    assert repository.get_item(item.item_id) == item


def test_nps6_official_runtime_exposes_existing_m74_authority() -> None:
    from app.runtime_root_factory import build_runtime_root

    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    registration = registry.registration_for("resident.personal_knowledge")

    assert registration is not None
    assert isinstance(
        registration.interceptor.manager,
        PersonalKnowledgeBaseManager,
    )


def test_nps7_existing_projection_exposes_m74_note_as_notes() -> None:
    item = _note()
    projection = ProductiveOrganizationEvidenceProjection()

    projected = projection.project_knowledge_note(item)

    assert projected.item_id == item.item_id
    assert projected.normalized_capability is PersonalOrganizationCapability.NOTES
    assert projected.source_reference == f"knowledge:note:{item.item_id}"


class NotesPort:
    def list_notes(self):
        return (_note(),)


def test_nps8_snapshot_builder_accepts_read_only_notes_port() -> None:
    notes_kind = OrganizationSourceKind("notes")
    builder = PartialCanonicalOrganizationSnapshotBuilder(
        notes_port=NotesPort(),
    )

    snapshot = builder.build()

    notes = snapshot.source_for(notes_kind)
    assert notes.availability is OrganizationSourceAvailability.AVAILABLE
    assert len(notes.item_ids) == 1


@dataclass(frozen=True)
class Registration:
    interceptor: object


class KnowledgeService:
    def __init__(self) -> None:
        self.owner = KnowledgeOwner.CARLOS
        self.manager = _manager()
        self.manager.remember(
            title="Runtime note",
            content="Nota productiva para M391.5.",
            kind=KnowledgeKind.NOTE,
            owner=KnowledgeOwner.CARLOS,
            now=NOW,
        )
        self.service = self


class Registry:
    def __init__(self) -> None:
        self.registration = Registration(KnowledgeService())

    def registration_for(self, name: str):
        if name == "resident.personal_knowledge":
            return self.registration
        return None


class Runtime:
    def __init__(self) -> None:
        self.registry = Registry()
        self.bootstrap = SimpleNamespace(
            root=SimpleNamespace(
                dependencies=SimpleNamespace(official_capability_registry=self.registry)
            )
        )


def test_nps9_productive_wiring_consumes_notes_into_m391_5() -> None:
    wiring = ProductiveOrganizationAdvisoryWiring(Runtime())

    snapshot = wiring._snapshot_builder().build()
    result = PartialOrganizationM3915Consumer().consume(snapshot)

    assert result.notes_available is True
    assert (
        result.organization.recommendations[0].capability
        is PersonalOrganizationCapability.NOTES
    )


def _adaptation():
    evidence = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "¿Revisar esta nota o seguir con la tarea?"
    )
    return ExplicitDeliberationDecisionOptionAdapter().adapt(evidence)


def test_nps10_exact_note_reference_reaches_existing_m391_6() -> None:
    runtime = Runtime()
    wiring = ProductiveOrganizationAdvisoryWiring(runtime)
    note = runtime.registry.registration.interceptor.manager.recall(
        kind=KnowledgeKind.NOTE,
        owner=KnowledgeOwner.CARLOS,
    )[0]
    references = (
        ExplicitOrganizationReference(
            0,
            organization_source_reference=f"knowledge:note:{note.item_id}",
        ),
    )

    result = wiring.assemble(_adaptation(), references)

    assert result is not None
    assert result.notes_available is True
    assert result.advisory.schema_version == "m391.6"
    assert result.advisory.canonical_facade == "CanonicalDecisionFacade"
