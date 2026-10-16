# Post-M409.1 — Governed Level 2B Productive Entry / Real-World Reachability Foundation v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Provide the missing canonical admission edge from an already-governed R1 product into the
existing bounded Level 2B episode lifecycle without adding an investigation orchestrator.

## Productive path
existing governed `DiscriminatingEvidenceRequirement` R1
→ explicit `originating_reasoning_id`
→ `GovernedLevel2BProductiveEntryFoundationV1.admit(...)`
→ existing `GovernedMultiStepInvestigationEpisodeBoundaryV1.start(...)`
→ episode OPEN with `max_acquisitions=2`, `consumed_acquisitions=0`
→ `eligible_for_existing_planning=True`
→ STOP.

## Authority
The entry surface does not create R1 and does not decide whether R1 is epistemically valid.
It only admits an already-governed requirement to the existing episode lifecycle. The
Episode Boundary remains lifecycle authority and Planning remains `planning_foundation`.

## Idempotence
The v1 surface keeps in-process admission lineage keyed by originating reasoning id,
requirement id, source reference and world snapshot. Repeating the same admission returns
`ALREADY_ADMITTED` and the existing episode id instead of restarting another episode.
This is intentionally not persisted and does not introduce Memory writes.

## Hard boundaries
No Planning invocation, Authorization, Execution, Reasoning re-entry, Curiosity,
Conversation, Memory mutation, networking, Android, state-changing action, retry, scheduler,
background loop or autonomous research orchestrator is introduced.

## Validation
Architecture/semantic tests cover valid admission, exact R1/reasoning/source/snapshot
lineage, fixed clean budget, idempotence, fail-closed eligibility, Episode Boundary failure,
contract mismatch, and absence of downstream authority or loop calls. Official certification
remains `ruff check .` plus complete `pytest -q`.
