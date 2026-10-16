# ROBY XI.2 — D:\Roby Governed Development History Source

## CONTRACT RED

### Starting state

- PRE-RED reconciliation: CLOSED / OWNER-CERTIFIED.
- Starting suite: 13,401 PASS / 0 FAIL / Ruff clean.
- Product implementation: intentionally absent.
- Scope: source/trust seam only.

### Contract target

The RED contracts one subordinate application-side mechanical seam:

`ROBY_DEVELOPMENT_HISTORY_ROOT -> bounded read-only discovery ->`
`development-history provenance + HISTORICAL_DEVELOPMENT_MATERIAL trust ->`
`explicit selection/revalidation -> existing DocumentReadingService ->`
`existing DocumentInboxManager`

It does not create a cognitive authority and does not authorize downstream automatic
Reasoning, diagnostics, Memory, Learning, Proposal, Planning or Execution.

### Required source behavior

The contract requires:

1. `DevelopmentHistoryRootDiscoveryAdapter` and its environment builder;
2. no source when `ROBY_DEVELOPMENT_HISTORY_ROOT` is absent;
3. deterministic bounded discovery under exactly one configured root;
4. stable candidate identity, relative path and `development-history:` provenance;
5. explicit `HISTORICAL_DEVELOPMENT_MATERIAL` trust classification;
6. read-only discovery with no content reads or Inbox ingestion;
7. root containment and external-symlink exclusion;
8. revalidation of candidate identity at explicit selection time;
9. reuse of `DocumentReadingService` and `DocumentInboxManager` only after selection;
10. rejection of unknown/unselected candidates;
11. no ZIP/archive extraction or arbitrary binary ingestion;
12. no cognitive, mutation, Memory, Learning, diagnostics or Proposal authority.

### Initial readable formats

The source may expose only formats already owned by `DocumentReadingService`:

`.txt`, `.md`, `.csv`, `.json`, `.log`, `.py`, `.html`, `.htm`, `.docx`, `.pdf`, `.epub`.

This RED creates no parser and no archive extraction authority.

### Permanent trust boundary

`HISTORICAL_DEVELOPMENT_MATERIAL != CURRENT_EXECUTABLE_PROJECT_EVIDENCE`

`HISTORICAL_FINDING != CURRENT_DEFECT`

`HISTORICAL_SUGGESTION != CHANGE_AUTHORIZATION`

A historical candidate can tell ROBY where to investigate. It cannot manufacture
current-project diagnostic evidence, reproduced proof, hash verification or change
authorization.

### Explicit STOP

This CONTRACT RED stops after source discovery/trust and explicit handoff to the
existing document lifecycle. It does not contract automatic Reasoning admission or any
new self-improvement behavior.

### Expected RED

The new architecture contract must fail only because
`app.development_history_source` does not yet exist. Existing unrelated tests and lint
must remain green.

`D_ROBY_DEVELOPMENT_HISTORY_CONTRACT_RED: AUTHORIZED`

`PRODUCTIVE_GREEN: NOT YET AUTHORIZED`
