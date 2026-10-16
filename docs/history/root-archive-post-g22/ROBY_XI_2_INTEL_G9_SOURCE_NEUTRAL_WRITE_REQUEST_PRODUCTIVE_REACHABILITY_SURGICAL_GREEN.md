# ROBY XI.2 — INTEL-G9 — SOURCE-NEUTRAL CERTIFIED GOVERNED MEMORY WRITE REQUEST → EXISTING PRODUCTIVE WIRING → OFFICIAL MEMORY GATEWAY — SURGICAL GREEN

## Scope

Closes only the productive reachability seam certified by the preceding architectural reconciliation and CONTRACT RED.

## Surgical change

`ProductiveGovernedLearningWiring` now exposes `execute_certified_write_request(request)` for an already-certified `GovernedMemoryWriteRequest`.

The historical `execute(...)` path and the source-neutral entry both converge on the same private persistence routine. That routine preserves the existing `OfficialMemoryGateway` writer contract and the existing result semantics:

- `STORED`
- `ALREADY_STORED`
- `MEMORY_UNAVAILABLE`
- `WRITE_FAILED`

No new authorization, materialization authority, write adapter, writer, gateway, persistence runtime, planner, manager, or parallel productive wiring was introduced.

## Preserved invariants

- APPROVED != MATERIALIZED
- MATERIALIZATION PROPOSAL != WRITE REQUEST
- WRITE REQUEST != PERSISTED MEMORY
- source-neutral lineage does not fabricate Preference/Curiosity provenance
- `OfficialMemoryGateway` remains the only Memory write authority
- `GovernedMemoryWriteAdapterFoundation` remains the existing write adapter
- historical Curiosity/Preference productive behavior remains supported

## Tests integrated

The corrected G9 contract test supplied after RED validation is integrated, including normalized imports and Ruff-compliant line lengths.

Focused validation in the delivery environment:

- G9 contract: `4 passed`
- historical productive wiring + G9 contract: `14 passed`

Ruff is not installed in the delivery environment, so final certification remains local and must use the project-mandated sequence:

1. `python scripts/generate_quality_baseline.py`
2. `ruff check .`
3. `pytest -q`

The local certification result is authoritative for gate closure.
