from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.productive_organization_advisory_wiring import (
    ProductiveOrganizationAdvisoryWiring,
)
from core.agenda_evidence import AgendaEventEvidence
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
from core.personal_organization import (
    PersonalOrganizationAuthority,
    PersonalOrganizationCapability,
)
from core.productive_organization_evidence_projection import (
    ProductiveOrganizationEvidenceProjection,
)
from infrastructure.calendar.calendar_contract import (
    CalendarEvent,
    CalendarTimeRange,
)

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)
STARTS = NOW + timedelta(hours=2)
ENDS = STARTS + timedelta(hours=1)


def _event(event_id: str = "event-1") -> CalendarEvent:
    return CalendarEvent(
        event_id=event_id,
        title="Consulta médica",
        time_range=CalendarTimeRange(starts_at=STARTS, ends_at=ENDS),
        calendar_id="primary",
    )


def _agenda_event(event_id: str = "event-1") -> AgendaEventEvidence:
    return AgendaEventEvidence(
        agenda_id=event_id,
        title="Consulta médica",
        source_reference=f"calendar:event:{event_id}",
    )


def test_aps1_calendar_event_contract_is_provider_neutral_and_readable() -> None:
    event = _event()

    assert event.event_id == "event-1"
    assert event.title == "Consulta médica"
    assert event.time_range.starts_at == STARTS
    assert event.time_range.ends_at == ENDS


def test_aps2_cognitive_agenda_remains_distinct_existing_authority() -> None:
    binding = PersonalOrganizationAuthority().binding_for(
        PersonalOrganizationCapability.AGENDA
    )

    assert binding.authority_name == "CognitiveAgendaManager"
    assert "cognitive_agenda_manager" in binding.implementation_path
    assert "calendar providers remain external gateways" in binding.notes


def test_aps3_existing_m391_5_already_accepts_agenda_capability_items() -> None:
    item = PersonalOrganizationItem(
        item_id="event-1",
        capability=PersonalOrganizationCapability.AGENDA,
        title="Consulta médica",
        urgency=0.8,
        importance=0.7,
        source_reference="calendar:event:event-1",
    )

    report = IntelligentPersonalOrganizationView().organize((item,))

    assert report.canonical_authority == "PersonalOrganizationAuthority"
    assert report.recommendations[0].item_id == "event-1"
    assert report.recommendations[0].capability is PersonalOrganizationCapability.AGENDA
    assert report.modifies_items is False
    assert report.executes_actions is False


def test_aps4_existing_projection_exposes_neutral_agenda_evidence() -> None:
    projection = ProductiveOrganizationEvidenceProjection()

    item = projection.project_agenda_event(_agenda_event(), now=NOW)

    assert item.item_id == "event-1"
    assert item.normalized_capability is PersonalOrganizationCapability.AGENDA
    assert item.source_reference == "calendar:event:event-1"


class AgendaPort:
    def list_agenda_events(self) -> tuple[AgendaEventEvidence, ...]:
        return (_agenda_event(),)


def test_aps5_snapshot_builder_accepts_read_only_agenda_port() -> None:
    agenda_kind = OrganizationSourceKind("agenda")
    builder = PartialCanonicalOrganizationSnapshotBuilder(
        agenda_port=AgendaPort(),
    )

    snapshot = builder.build()

    assert snapshot.source_for(agenda_kind).availability is (
        OrganizationSourceAvailability.AVAILABLE
    )
    assert snapshot.source_for(agenda_kind).item_ids == ("event-1",)


def test_aps6_m391_5_consumption_exposes_agenda_availability() -> None:
    builder = PartialCanonicalOrganizationSnapshotBuilder(
        agenda_port=AgendaPort(),
    )
    snapshot = builder.build()

    result = PartialOrganizationM3915Consumer().consume(snapshot)

    assert result.agenda_available is True
    assert result.organization.recommendations[0].item_id == "event-1"


@dataclass(frozen=True)
class Registration:
    interceptor: object


class CalendarProvider:
    def list_events(self, time_range, *, calendar_id="primary"):
        del time_range, calendar_id
        return (_event(),)


class CalendarRuntime:
    provider = CalendarProvider()

    @staticmethod
    def snapshot():
        return SimpleNamespace(state=SimpleNamespace(value="ready"))

    def require_provider(self):
        return self.provider


class CalendarInterceptor:
    def __init__(self) -> None:
        self.runtime = CalendarRuntime()
        self.service = self


class Registry:
    def registration_for(self, name: str):
        if name == "calendar.read":
            return Registration(CalendarInterceptor())
        return None


class Runtime:
    bootstrap = SimpleNamespace(
        root=SimpleNamespace(
            dependencies=SimpleNamespace(official_capability_registry=Registry())
        )
    )


def test_aps7_productive_wiring_reads_existing_calendar_registration() -> None:
    wiring = ProductiveOrganizationAdvisoryWiring(Runtime())

    snapshot = wiring._snapshot_builder().build()

    agenda_kind = OrganizationSourceKind("agenda")
    agenda = snapshot.source_for(agenda_kind)
    assert agenda.availability is OrganizationSourceAvailability.AVAILABLE
    assert agenda.item_ids == ("event-1",)


def _adaptation():
    evidence = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "¿Consulta médica o tarea?"
    )
    return ExplicitDeliberationDecisionOptionAdapter().adapt(evidence)


def test_aps8_calendar_reference_reaches_existing_m391_6_advisory() -> None:
    wiring = ProductiveOrganizationAdvisoryWiring(Runtime())
    references = (
        ExplicitOrganizationReference(
            0,
            organization_source_reference="calendar:event:event-1",
        ),
    )

    result = wiring.assemble(_adaptation(), references)

    assert result is not None
    assert result.agenda_available is True
    assert result.advisory.schema_version == "m391.6"
    assert result.advisory.canonical_facade == "CanonicalDecisionFacade"
