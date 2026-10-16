# ROBY XI.2 — Governed External Image Freshness Order Representation
## SURGICAL GREEN

### Owner-certified RED input
- 9 intentional contract failures;
- 13,585 pass;
- Ruff clean;
- M361 regenerated;
- unexpected failures: zero.

### Productive delta
Exactly three authorized existing modules changed:
1. `app/governed_source_query.py`
2. `app/governed_conversational_source_selection.py`
3. `app/governed_source_query_executor.py`

The canonical RED contract is unchanged.

### Implemented representation
`GovernedSourceQueryOrder.NEWEST_FIRST = "newest_first"` now belongs to the
existing governed query authority.

Both:
- `GovernedConversationalSourceSelectionRequest`
- `GovernedSourceQuery`

carry:
`order: GovernedSourceQueryOrder | None = None`.

Non-enum values fail closed; no string coercion is introduced.

### Projection and admission
The existing selector projects `request.order` unchanged into the existing
query.

A NEWEST_FIRST request requires:
`InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`.

The existing query contract independently enforces the same capability.

For OPEN_VISUAL_SUBJECT + NEWEST_FIRST, both independent capabilities remain
required.

Date bounds remain orthogonal and unchanged.

### Execution identity
The existing executor includes the governed order value in execution identity.

It does not sort raw items or inspect timestamps to impose freshness.

`EXECUTION_ID_INCLUDES_ORDER != EXECUTOR_ORDERING_AUTHORITY`

### Preserved boundaries
No:
- `gsrsort`;
- Wikimedia provider projection;
- NASA change;
- generic executor sorting;
- presentation sorting;
- ACI freshness-language admission;
- runtime/gateway/composition change;
- new authority.

### Local surgical evidence
Focal + related architecture contracts:
`60 PASS / 0 FAIL`.

All changed Python and the canonical RED test parse successfully.

Maximum line lengths:
- governed source query: 87;
- governed conversational source selection: 83;
- governed source query executor: 86;
- canonical RED contract: 88.

The local runner could not execute its Ruff binary because of an environment
permission error. This is not recorded as a Ruff failure or success. Owner
certification must run canonical `ruff check .`.

### Expected Owner certification
Because RED added 10 tests (9 RED + 1 already-green boundary test), successful
GREEN full-suite count is expected to be:
`13,594 PASS / 0 FAIL`.

Owner commands:
- `python scripts/clean_project_caches.py`
- `python scripts/generate_quality_baseline.py`
- `ruff check .`
- `pytest -q`

### Formal state
`SURGICAL_GREEN: COMPLETE / PENDING OWNER CERTIFICATION`
`FOCAL_PLUS_RELATED: 60 PASS / 0 FAIL`
`EXPECTED_FULL_SUITE: 13,594 PASS / 0 FAIL`
`PRODUCTIVE_DELTA: THREE AUTHORIZED EXISTING MODULES`
`CONTRACT_TEST_CHANGED: NO`
`DATE_BOUNDS: PRESERVED`
`EXECUTOR_SORTING: NONE`
`PROVIDER_PROJECTION: NONE`
`NATURAL_LANGUAGE_ADMISSION: NONE`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: POST-GREEN MASTER PLAN RECONCILIATION`
