# ROBY XI.2 — Authorized Productive Wiring Exact Validation
## Legacy Contract Preservation / New G7 Path Fail-Closed

Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**.

### Correction after owner gate

The first implementation correctly added exact authorization validation to
`execute_certified_write_request(request, authorization)` but also changed the historical
`execute(evaluation, response, current_turn_text=...)` contract to stop at
`GovernedMemoryWriteRequest`.

The owner full-suite gate demonstrated that this altered previously certified behavior:
legacy causal/recall/longitudinal tests expected the historical approved-learning path to
persist Memory and instead received `REVIEW_REQUIRED`.

That broad semantic change is reverted here.

### Preserved historical contract

`ProductiveGovernedLearningWiring.execute(...)` is restored exactly from the pre-wiring
authorization package. Historical approved-learning behavior is therefore not redefined by
the new G7 authorization seam.

### New G7 fail-closed seam

`ProductiveGovernedLearningWiring.execute_certified_write_request(...)` remains the
new bounded entry for an already-created `GovernedMemoryWriteRequest`.

It requires:
- the exact `GovernedMemoryWriteRequest`;
- `AuthorizedGovernedMemoryWriteExecutionEvidence`;
- exact request id;
- exact materialization proposal id;
- exact idempotency key;
- exact canonical writer authority/component/method;
- inert authorization evidence.

Missing or mismatched authorization returns `REVIEW_REQUIRED` before the writer.

### No bypass through legacy execute

The new G7 request cannot be supplied to legacy `execute(...)`: that method accepts only
the historical `(evaluation, response, current_turn_text=...)` contract and has no
`request` or `authorization` parameter.

Thus:
- legacy certified behavior remains intact;
- the new G7 request route remains fail-closed;
- no second writer or approval authority is introduced.

### STOP

`OfficialConversationGateway` is not changed in this correction.

Next residual after owner certification:

`OfficialConversationGateway`
→ exact `GovernedMemoryWriteRequest + AuthorizedGovernedMemoryWriteExecutionEvidence`
→ already-gated `execute_certified_write_request(...)`.

### Validation note

Pure authorization/wiring contract tests were run in the assistant environment.
SQLite-backed tests could not be meaningfully evaluated there because the environment
returned `sqlite3.OperationalError: disk I/O error`. The official owner gate remains the
certification authority.
