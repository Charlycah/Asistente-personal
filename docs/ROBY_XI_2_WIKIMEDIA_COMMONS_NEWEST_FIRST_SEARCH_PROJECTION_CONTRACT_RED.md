# ROBY XI.2 — Wikimedia Commons Newest-First Search Projection
## CONTRACT RED

### Certified input
CONTRACT DESIGN RECONCILIATION Owner-certified:
- 13,594 PASS / 0 FAIL;
- Ruff clean;
- M361 reproducible;
- productive Python/test delta at design stage: ZERO.

### Contract introduced
One architecture contract file only:
`tests/architecture/test_wikimedia_commons_newest_first_search_projection_contract_red.py`

No productive Python module was changed.

### Frozen positive obligation
For:
`query.order is GovernedSourceQueryOrder.NEWEST_FIRST`

`WikimediaCommonsGovernedSourceAdapter._build_url(query)` must project:
`gsrsort=create_timestamp_desc`.

The current product intentionally does not yet do so.

### Preserved boundaries proved GREEN in RED
The contract also establishes that:
- `order=None` omits `gsrsort`;
- generator remains `search`;
- query text remains provider search text;
- namespace remains file namespace `6`;
- `gsrlimit` remains bounded to `20`;
- thumbnail width remains `640`;
- `last_edit_desc` is absent;
- the adapter contains no local `sorted(...)` / `.sort(...)` authority;
- provider item order is preserved even when timestamps would suggest the
  opposite chronological order;
- NEWEST_FIRST creates no implicit date window;
- the adapter does not introduce natural-language freshness admission.

### Intentional RED result
New contract:
`1 FAILED / 7 PASSED`.

Exact intentional failure:
`test_newest_first_projects_exact_provider_create_order`

Failure cause:
`KeyError: 'gsrsort'`

This is the precise missing provider projection frozen by the design.

Related existing architecture contracts:
`39 PASSED / 0 FAILED`.

### Full-suite note
A full-suite attempt in the assistant environment could not complete collection
because the supplied ZIP does not contain modules imported by unrelated tests,
including `app.personal_document_ingestion_runtime`.

This is not classified as a RED regression. No global pass/fail count is
claimed from this environment. Owner certification remains authoritative for
the full suite, Ruff, and M361.

### Delta discipline
Productive Python delta:
`ZERO`.

Test delta:
exactly one architecture contract file.

Maximum line length of the new contract:
`73`.

No import-order or line-too-long debt was introduced by the contract file.

### Expected surgical GREEN
Modify only:
`app/wikimedia_commons_governed_source.py`.

Expected shape:
1. import `GovernedSourceQueryOrder` alongside `GovernedSourceQuery`;
2. after constructing the existing parameter mapping, if
   `query.order is GovernedSourceQueryOrder.NEWEST_FIRST`, add
   `parameters["gsrsort"] = "create_timestamp_desc"`;
3. preserve the existing `urlencode(parameters)` path.

No other productive module is authorized by this RED.

### Formal state
`CONTRACT_RED: COMPLETE / PENDING OWNER CERTIFICATION`
`INTENTIONAL_CONTRACT_FAILURES: 1`
`NEW_CONTRACT_PASSES: 7`
`RELATED_CONTRACTS: 39 PASS / 0 FAIL`
`EXACT_MISSING_BEHAVIOR: gsrsort=create_timestamp_desc`
`ORDER_NONE_PRESERVED: YES`
`PROVIDER_ORDER_PRESERVED: YES`
`LAST_EDIT_DESC: ABSENT / FORBIDDEN`
`LOCAL_SORTING: ABSENT / FORBIDDEN`
`IMPLICIT_DATE_WINDOW: ABSENT / FORBIDDEN`
`ACI_CHANGE: NONE / DEFERRED`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ONE CONTRACT FILE`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: SURGICAL GREEN`
