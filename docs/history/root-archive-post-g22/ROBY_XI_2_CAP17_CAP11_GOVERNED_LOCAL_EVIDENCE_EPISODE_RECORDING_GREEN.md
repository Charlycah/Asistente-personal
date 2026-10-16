# CAP-17/CAP-11 — Governed Local Evidence Episode Recording — GREEN

- `GovernedMultiStepInvestigationEpisodeBoundaryV1` remains the sole episode-state authority.
- `GovernedInvestigationEpisodeState` records local Unified Retrieval execution lineage separately in `local_execution_ids`; historical Level-2 `execution_ids`, `plan_ids` and `authorization_ids` remain intact.
- `consumed_acquisitions` is the global bounded acquisition budget across Level-2 and governed local-library evidence.
- `record_local_evidence_reentry(...)` consumes only an already-completed `GovernedLocalEvidenceReasoningReentryResult`; it performs no search, read, retrieval, planning, authorization or reasoning.
- Original episode/reasoning/requirement/source/world-snapshot lineage remains authoritative; no synthetic Level-2 lineage is created for Biblioteca.
- A successful local re-entry transitions to `AWAITING_REQUIREMENT` while budget remains or `CLOSED / BUDGET_EXHAUSTED` when the last acquisition is consumed.
- The productive CAP-17 contributor records the local re-entry only after the existing governed reasoning re-entry and exposes the resulting episode transition audibly through its invocation result.
- Existing Level-2 acquisition/re-entry contracts remain unchanged.
- Memory, Learning, questions, background work and `.roby/config.json` remain untouched.
