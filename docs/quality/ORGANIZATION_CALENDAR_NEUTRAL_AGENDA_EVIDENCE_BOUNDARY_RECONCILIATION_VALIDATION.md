# ROBY XI.2 — Organization / Calendar neutral Agenda evidence boundary reconciliation

## Scope

Governed layering reconciliation with no authority, writer or productive
reachability change.

## Structural delta

- Added `core/agenda_evidence.py` with minimal `AgendaEventEvidence`.
- `core/partial_canonical_organization_snapshot.py` now consumes neutral Agenda
  evidence instead of `infrastructure.calendar.calendar_contract.CalendarEvent`.
- `core/productive_organization_evidence_projection.py` now projects neutral Agenda
  evidence.
- `app/productive_organization_advisory_wiring._AgendaReadAdapter` maps existing
  Calendar provider events into `AgendaEventEvidence`.
- Calendar provider contracts and adapters remain unchanged.

## Preserved authorities

- Calendar provider/read/create/availability authority: unchanged.
- `CognitiveAgendaManager`: unchanged.
- `PersonalOrganizationAuthority`: unchanged.
- M391.5/M391.6: unchanged.
- Calendar and Organization writers: unchanged.

## Guardrail

`tests/architecture/test_organization_calendar_neutral_agenda_boundary.py`
protects the neutral evidence contract and forbids Calendar infrastructure
imports in the two Organization core consumers.

## Certification state

**IMPLEMENTED / PENDING OWNER CERTIFICATION**

Expected owner baseline after the added guardrail: **12,536 PASS · 0 FAIL · Ruff clean**.

Owner gate:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
