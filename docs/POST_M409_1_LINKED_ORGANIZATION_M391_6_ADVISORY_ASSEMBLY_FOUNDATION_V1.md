# Post-M409.1 — Linked Organization Evidence → M391.6 Advisory Assembly Foundation v1

## Purpose

Materialize the missing read-only bridge from already certified exact organization linkage and M391.5 partial organization consumption into the existing M391.6 advisory path.

## Canonical flow

`OrganizationDecisionLinkageResult` + `PartialOrganizationM3915Consumption` → `LinkedOrganizationM3916AdvisoryAssembler` → existing `CanonicalDecisionFacade.advise()` → existing M391.6 `GovernedDecisionAdvisoryReport`.

## Governing constraints

- No new decision, organization or conversation authority.
- M391.6 is not modified; `CanonicalDecisionFacade` remains the canonical façade.
- M391.5 remains the sole organization-consumption boundary.
- Goals / Projects / Reminders are the admitted productive Organization sources in v1.
- Tasks remains `UNAVAILABLE / DEFERRED`.
- Linkage and M391.5 consumption must originate from the same canonical partial snapshot.
- Every linked organization item must exist in the consumed M391.5 report.
- v1 carries organization evidence only; scenario, causal and preference signals stay outside this Foundation.
- Read-only, advisory-only, deterministic, no persistence, no organization mutation, no execution, no background process.
- No `OfficialConversationGateway`, runtime composition, M410, networking or Residential changes.

## Productive wiring gate

This Foundation does not itself activate the full Productive Organization Advisory Wiring. That gate remains pending until this Foundation is externally certified with Ruff and the complete pytest suite.

## Implementation state

**IMPLEMENTED / CERTIFICATION PENDING USER GATES**.
