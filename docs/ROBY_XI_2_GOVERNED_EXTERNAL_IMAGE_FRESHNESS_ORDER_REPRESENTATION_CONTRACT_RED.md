# ROBY XI.2 — Governed External Image Freshness Order Representation
## CONTRACT RED

### Owner-certified input
Contract Design baseline:
- 13,584 PASS / 0 FAIL;
- Ruff clean;
- M361 reproducible.

### RED scope
Added exactly one architecture contract:
`tests/architecture/test_governed_external_image_freshness_order_representation_contract_red.py`

No productive Python changed.

### Contract coverage
The RED requires:
1. `GovernedSourceQueryOrder.NEWEST_FIRST == "newest_first"`;
2. optional `order=None` on selection request and source query;
3. fail-closed rejection of string/non-enum order;
4. unchanged selector projection of typed order;
5. newest-first capability gating for topic-constrained requests;
6. both independent capabilities for open-visual newest-first;
7. query-contract capability defense in depth;
8. coexistence of explicit date bounds and newest-first;
9. execution identity sensitivity to governed order;
10. no executor sorting, Wikimedia `gsrsort`, freshness-language admission, or
    parallel freshness authority.

### Local RED evidence
Focal:
`9 FAILED / 1 PASSED`

Failures converge on absent representation:
- missing `GovernedSourceQueryOrder`;
- absent `order` constructor field.

The negative boundary test already passes.

Related existing architecture contracts:
`50 PASSED / 0 FAILED`.

### Expected GREEN
Authorized productive modules remain exactly:
- `app/governed_source_query.py`;
- `app/governed_conversational_source_selection.py`;
- `app/governed_source_query_executor.py`.

No other productive Python is authorized.

### Formal state
`CONTRACT_RED: COMPLETE / PENDING OWNER CERTIFICATION`
`FOCAL_RED: 9 FAIL / 1 PASS`
`FAILURE_CONVERGENCE: ABSENT TYPED ORDER REPRESENTATION`
`RELATED_CONTRACTS: 50 PASS / 0 FAIL`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ONE ARCHITECTURE CONTRACT`
`EXECUTOR_SORTING: FORBIDDEN`
`PROVIDER_PROJECTION: DEFERRED`
`NATURAL_LANGUAGE_ADMISSION: DEFERRED`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: SURGICAL GREEN`
