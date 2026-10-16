# External Intelligence / Governed Source Query — Integration Residency Reconciliation

## Status

IMPLEMENTED / PENDING OWNER CERTIFICATION.

## Purpose

This post-M400 governed reconciliation corrects dependency direction without changing productive behavior or capability authority. The cross-capability adapter `GovernedExternalInformationSourceIntegration` is application-layer orchestration because it knows both the existing governed source-query result contract and the existing governed external-intelligence boundary.

## Current residency

- `app/governed_external_information_source_integration.py` owns the integration adapter.
- `core/governed_external_intelligence/` owns only External Intelligence domain/boundary, provider integration, verification, assessment and corroboration.
- `core/governed_external_intelligence` no longer imports or re-exports `app.governed_source_query`.

## Authority preservation

No authority is added or replaced.

- Source query execution remains owned by the existing `OfficialConversationGateway` / governed source-query path.
- `GovernedExternalIntelligenceBoundary` remains the admission boundary for external evidence.
- ROBY retains cognitive interpretation and decision authority.
- The integration adapter has `integration_id` and no `authority_id`; it does not execute, enable, select or poll sources.

## Historical M400.9 evidence

`docs/quality/M400_9_EXTERNAL_INTELLIGENCE_CLOSURE.json` is preserved unchanged as evidence of the topology and public API certified at M400.9. Its historical SHA-256 snapshot is not recalculated to govern the current repository. Current tests explicitly distinguish historical certification evidence from current topology.

## Expected productive delta

0. The class name, public behavior, validation rules, provenance semantics and M400.4–M400.7 functional contracts are preserved; only integration residency/import direction changes.

## Validation

Owner certification remains required with the official sequence:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

Expected test-count baseline: 12,534 PASS, unless the quality baseline generator itself produces a governed non-test artifact change.
