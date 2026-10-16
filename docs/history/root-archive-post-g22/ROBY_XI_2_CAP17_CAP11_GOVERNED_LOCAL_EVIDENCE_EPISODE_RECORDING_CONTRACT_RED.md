# CAP-17/CAP-11 — Governed Local Evidence Episode Recording — RED contractual

## Purpose
Close only the residual between an already-completed CAP-17 local evidence reasoning re-entry and the existing CAP-11 investigation episode boundary.

## Contract
- The canonical episode owner remains `GovernedMultiStepInvestigationEpisodeBoundaryV1`.
- Add one explicit local recording port: `record_local_evidence_reentry`.
- The port consumes an already-completed `GovernedLocalEvidenceReasoningReentryResult`; it never acquires evidence and never invokes reasoning.
- Local Unified Retrieval execution lineage is recorded separately from historical Level-2 execution lineage; no fake plan or authorization IDs are permitted.
- `consumed_acquisitions` is the global episode budget across Level-2 and local-library acquisitions.
- Successful local re-entry transitions to `AWAITING_REQUIREMENT` while budget remains, or `CLOSED / BUDGET_EXHAUSTED` when exhausted.
- Original reasoning, requirement, episode, source and world-snapshot lineage must be preserved.
- Existing Level-2 `record_acquisition` and `record_reentry` contracts remain intact.
- Productive CAP-17 invokes episode recording only after the existing local reasoning re-entry has completed.
- No second search, read, retrieval, authorization, planning, reasoning, Memory, Learning, question generation or background work.
- `KnowledgeRetrievalStep` remains unchanged.
- `.roby/config.json` remains untouched.

## Expected RED
The new architectural tests fail only because the generalized local episode recording port and productive chaining do not yet exist. Existing guardrails remain green.
