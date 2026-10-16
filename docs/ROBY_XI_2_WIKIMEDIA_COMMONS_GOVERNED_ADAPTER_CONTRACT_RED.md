# ROBY XI.2 — Wikimedia Commons Governed Adapter Contract
## Contract RED

### Certified design input
The Owner-certified Contract Design authorizes RED for the provider adapter
contract only. Productive adapter implementation, executor registration,
presentation changes, and freshness remain unauthorized.

### RED delta
Exactly one test Python file is introduced:

`tests/architecture/test_wikimedia_commons_governed_adapter_contract_red.py`

Productive Python delta: zero.

### RED obligations represented
The RED covers the provider seam through:
- canonical `wikimedia_commons` adapter/source declaration;
- explicit `OPEN_VISUAL_SUBJECT_QUERY` capability with empty topics;
- HTTPS Commons Action API request;
- File namespace restriction;
- bounded result limit of 20;
- 640px thumbnail request;
- imageinfo/extmetadata request;
- prevention of user parameter override of provider policy;
- required governed non-blank User-Agent before network I/O;
- timeout propagation;
- stable provider identity and bounded visual metadata projection;
- attribution/license metadata preservation;
- rejection of non-HTTPS/non-image preview results;
- malformed provider payload fail-closed behavior;
- explicit absence of provider-specific registry, executor, selector,
  presenter, or retry-manager authorities.

Registration/reachability and freshness are intentionally not tested here.

### Expected RED
Focused result:
`7 FAILED / 1 PASSED`.

All seven failures converge on:
`ModuleNotFoundError: No module named 'app.wikimedia_commons_governed_source'`.

The passing test proves the forbidden parallel provider authorities remain
absent.

There is no demonstrated fixture/API mismatch and no productive Python change.

### GREEN authorization boundary
A future surgical GREEN may introduce only the provider adapter module needed
to satisfy this contract. It must not register that adapter into productive
executor composition in this seam.

### State
`CONTRACT_RED: COMPLETE`
`FOCAL_RED: 7 INTENTIONAL FAIL / 1 PASS`
`FAILURE_CAUSE: SINGLE / MISSING_CANONICAL_ADAPTER_MODULE`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_PYTHON_DELTA: EXACTLY_1_FILE`
`EXECUTOR_REGISTRATION: ZERO`
`PRESENTATION_CHANGE: ZERO`
`FRESHNESS: ZERO`
`NEW_AUTHORITY: NONE`
`SURGICAL_GREEN_AUTHORIZATION: ADAPTER_MODULE_ONLY / AFTER OWNER RED CERTIFICATION`


## Surgical GREEN outcome
Canonical user-corrected RED test integrated.\nOne productive adapter module introduced.\nHistorical no-provider assertion semantically migrated; parallel-authority guards retained.\nExecutor registration/reachability remains a later seam.\n