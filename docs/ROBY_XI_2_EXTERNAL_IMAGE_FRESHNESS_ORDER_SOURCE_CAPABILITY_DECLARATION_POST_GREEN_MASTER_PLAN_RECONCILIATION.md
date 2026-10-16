# ROBY XI.2 — External Image Freshness Order Source Capability Declaration
## POST-GREEN MASTER PLAN RECONCILIATION

### Owner-certified input
Surgical GREEN owner certification:
- 13,584 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated / reproducible;
- user-corrected contract test canonical.

### Reconciliation result
The capability-declaration block is internally complete.

Canonical capability authority remains:
`InformationSourceCapability` +
`GovernedInformationSource.capabilities`.

Productive occurrences of the new semantic are exactly:
1. enum declaration in `app/governed_information_sources.py`;
2. explicit Wikimedia declaration in
   `app/wikimedia_commons_governed_source.py`.

No other productive occurrence exists.

### Preserved boundaries
No productive occurrence of:
- `freshness_order`;
- `newest_first=`;
- `gsrsort`.

Therefore this block has not prematurely implemented:
- freshness-order request representation;
- selector eligibility for freshness;
- query-contract freshness validation;
- provider newest-first projection;
- executor-side sorting;
- presentation-side sorting;
- natural-language freshness admission.

NASA/default-source semantics remain outside this capability declaration and the
certified contract protects their lack of the new capability.

The empty-topic exception remains governed by
`OPEN_VISUAL_SUBJECT_QUERY`; newest-first capability does not become wildcard
admission authority.

### Local reconciliation evidence
Related architecture contracts:
`46 PASS / 0 FAIL`.

Hashes remain:
- `app/governed_information_sources.py`:
  `c5494ff42ab31b9a3c8cb25a3ce7702224cc4f22057b15f2675cee49ff25a965`
- `app/wikimedia_commons_governed_source.py`:
  `2a77daf2fa7e6cf2036233617a488741c5934872e04a2f40ca575ff0949b1aa3`
- canonical corrected RED contract:
  `386ddce477710b39c7f73c23410666cc0738c490577350271f57f76c56389fc7`

No Python or test file changed during this reconciliation.

### Residual analysis
Internal residual for
`EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`:
`NONE`.

The parent horizon remains open:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`.

The next demonstrated dependency is the already identified separate residual:
`GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`.

This is not a continuation of the capability declaration itself. It requires
its own PRE-RED reconciliation before any contract or productive change.

### Formal closure
`POST_GREEN_MASTER_PLAN_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`CAPABILITY_DECLARATION_INTERNAL_RESIDUAL: NONE`
`STOP_CAPABILITY_DECLARATION: CERTIFIED LOCALLY / OWNER CERTIFICATION PENDING`
`PARENT_RESIDUAL: EXTERNAL_IMAGE_FRESHNESS_ORDERING`
`NEXT_DEMONSTRATED_RESIDUAL: GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ZERO`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: GOVERNED EXTERNAL IMAGE FRESHNESS ORDER REPRESENTATION — PRE-RED RECONCILIATION`
