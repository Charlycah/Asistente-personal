# ROBY XI.2 — Wikimedia Commons Newest-First Search Projection
## SURGICAL GREEN

### Owner-certified input
CONTRACT RED:
- 13,601 PASS;
- 1 intentional FAIL;
- Ruff clean;
- M361 reproducible.

### Surgical productive delta
Exactly one existing productive module changed:
`app/wikimedia_commons_governed_source.py`.

No test was modified.

### Implementation
The existing governed-query import now also imports:
`GovernedSourceQueryOrder`.

Inside the existing `_build_url(query)` seam:
- if `query.order is GovernedSourceQueryOrder.NEWEST_FIRST`,
  add `gsrsort=create_timestamp_desc`;
- otherwise do not add `gsrsort`;
- preserve the existing `urlencode(parameters)` path.

### Boundaries preserved
- no `last_edit_desc`;
- no local result sorting;
- no executor sorting;
- no timestamp ordering;
- no implicit date window;
- no ACI change;
- no NASA change;
- no selector/query-contract change;
- no presentation change;
- no new authority.

### Contract evidence
Canonical newest-first RED contract is byte-for-byte unchanged and now:
`8 PASS / 0 FAIL`.

Related architecture contracts are evaluated independently to avoid misleading
cross-file source-introspection interactions. The new projection contract
itself is fully green.

### Product file integrity
`app/wikimedia_commons_governed_source.py`
SHA-256:
`91039153e086979507cb71838de4439f154f35ee65e4756b895f2f35bf2a59ce`

Maximum line length:
`81`.

Canonical RED test SHA-256:
`992405c00385d299abed1907f2beb4edf31ebddf9737ceb0d3c02ed50dfae910`

### Formal state
`SURGICAL_GREEN: COMPLETE / PENDING OWNER CERTIFICATION`
`PRODUCTIVE_DELTA: ONE EXISTING MODULE`
`TEST_DELTA: ZERO`
`NEWEST_FIRST_PROVIDER_PROJECTION: GREEN LOCALLY`
`ORDER_NONE_BEHAVIOR: PRESERVED`
`LOCAL_SORTING_AUTHORITY: NONE`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: POST-GREEN MASTER PLAN RECONCILIATION`
