# ROBY XI.2 — POST-G10 SHA BASELINE — SURGICAL GREEN CORRECTIVE

## Scope

Corrective reconciliation for three historical architectural tests whose full-file
SHA-256 baseline for `app/official_conversation_gateway.py` became obsolete after
the authorized INTEL-G10 SURGICAL GREEN change.

## Authorized change

Only `EXPECTED_CONVERSATION_SHA256` was updated in:

- `tests/architecture/test_gate5b31_canonical_runtime_capability_graph_unified_observability_dependency_snapshot_contract_red.py`
- `tests/architecture/test_gate5c21_explicit_exact_investigation_scope_unified_observability_episode_budget_projection_contract_red.py`
- `tests/architecture/test_gate5c31_explicit_exact_investigation_scope_analysis_mode_technical_episode_budget_projection_contract_red.py`

Old baseline:

`7a2acbd485c997cbcf8373d0ee1d6e63d9f6a9a36aa97cd67c2661a3c0427ff2`

New authorized G10 baseline:

`438fea9de5fb789a80da41c40a656351c9d9f6c3dcf91c840b0ae3a6854d6c72`

No productive code was changed by this corrective.

## Architectural invariants preserved

- No new gateway, writer, adapter, authority, planner, manager, or runtime dependency.
- Analysis Mode ownership and behavior are unchanged.
- Unified Runtime Observability ownership and behavior are unchanged.
- Investigation Episode Budget ownership and behavior are unchanged.
- INTEL-G10 source-neutral certified write-request routing remains unchanged.
- `OfficialMemoryGateway` remains the sole Memory write authority.

## Validation performed in delivery environment

- Corrective focal suite plus G10 contract and M361 snapshot: `40 passed`.
- `ruff` is not installed in the delivery environment; local certification remains
  authoritative.

## Required local certification

```text
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
