# ROBY XI.2 — External Image Freshness Order Source Capability Declaration
## CONTRACT RED

### Certified input
Owner-certified CONTRACT DESIGN baseline:
- 13,575 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated / reproducible.

### RED scope
One architecture contract was added:
`tests/architecture/test_external_image_freshness_order_source_capability_declaration_contract_red.py`

No productive Python was changed.

### Contract obligations
The RED proves:
1. exact enum member/value:
   `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY = "external_image_newest_first_query"`;
2. all default/legacy sources remain capability-empty;
3. NASA does not claim newest-first capability;
4. Wikimedia explicitly declares both visual capabilities;
5. newest-first capability is independent from open-visual capability for a
   topical source;
6. newest-first capability alone does not authorize empty topics;
7. open-visual capability continues to authorize empty topics;
8. timestamp metadata does not infer source capability;
9. no freshness wiring/provider ordering parameter/parallel authority is added.

### Local focal evidence
Focal contract:
`6 FAILED / 3 PASSED`

All six failures converge on the missing enum member
`InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`.

This is the expected pre-GREEN failure root. Some downstream assertions cannot
evaluate until that enum exists; the GREEN must not respond by weakening those
assertions.

Related existing contracts:
`28 PASSED / 0 FAILED`

### Expected surgical GREEN
Authorized productive files remain exactly:
- `app/governed_information_sources.py`
- `app/wikimedia_commons_governed_source.py`

Expected changes:
- add the enum member;
- add that member to Wikimedia's existing immutable capability set.

No other productive change is authorized.

### Formal state
`CONTRACT_RED: COMPLETE / PENDING OWNER CERTIFICATION`
`FOCAL_RED: 6 FAIL / 3 PASS`
`FAILURE_CONVERGENCE: MISSING EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`
`RELATED_CONTRACTS: 28 PASS / 0 FAIL`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ONE ARCHITECTURE CONTRACT`
`NEW_AUTHORITY: NONE`
`PROVIDER_QUERY_CHANGE: NONE`
`SELECTOR_CHANGE: NONE`
`QUERY_CONTRACT_CHANGE: NONE`
`EXECUTOR_CHANGE: NONE`
`NATURAL_LANGUAGE_CHANGE: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: SURGICAL GREEN`
