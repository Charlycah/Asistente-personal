# ROBY XI.2 — External Image Freshness Order Source Capability Declaration
## SURGICAL GREEN

### Certified input
Owner-validated CONTRACT RED:
- six intentional product-contract failures converging on the missing
  `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`;
- user-corrected RED test is canonical;
- Ruff clean after that correction.

### Canonical test correction
The user-supplied corrected contract test replaces the earlier generated copy.
It preserves contract semantics while fixing import order, line length, unused
local state, and repository-root-safe file inspection.

Do not revert this corrected test.

### Productive GREEN
Exactly two productive files changed.

1. `app/governed_information_sources.py`
   - adds:
     `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY = "external_image_newest_first_query"`
   - preserves the empty-topic exception as
     `OPEN_VISUAL_SUBJECT_QUERY` only.

2. `app/wikimedia_commons_governed_source.py`
   - existing Wikimedia source declaration now explicitly contains:
     - `OPEN_VISUAL_SUBJECT_QUERY`
     - `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`
   - no provider query parameter/order implementation is added.

### Preserved boundaries
Unchanged:
- NASA declaration;
- default/legacy source capability defaults;
- selector;
- query model/contract;
- executor;
- ACI/natural-language admission;
- runtime wiring/composition;
- gateway;
- presentation.

No `gsrsort`, freshness-order field, generic sort, or parallel freshness
authority is introduced.

### Local evidence
Focal corrected RED contract plus related regression contracts:
`37 PASS / 0 FAIL`

Maximum line length:
- corrected RED test: 88;
- governed_information_sources.py: 88;
- wikimedia_commons_governed_source.py: 81.

Productive Python delta against RED:
- `app/governed_information_sources.py`
- `app/wikimedia_commons_governed_source.py`

No other productive Python delta.

### Hashes
`app/governed_information_sources.py`
`c5494ff42ab31b9a3c8cb25a3ce7702224cc4f22057b15f2675cee49ff25a965`

`app/wikimedia_commons_governed_source.py`
`2a77daf2fa7e6cf2036233617a488741c5934872e04a2f40ca575ff0949b1aa3`

Canonical corrected RED test:
`386ddce477710b39c7f73c23410666cc0738c490577350271f57f76c56389fc7`

### Residual
This GREEN declares source capability only.

It does not yet make a freshness order request representable or reachable.

Parent remains:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

Next demonstrated child residual:
`GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`

### Formal state
`SURGICAL_GREEN: COMPLETE / PENDING OWNER CERTIFICATION`
`FOCAL_AND_RELATED: 37 PASS / 0 FAIL`
`NEW_CAPABILITY: EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`
`WIKIMEDIA_DECLARATION: OPEN_VISUAL_SUBJECT_QUERY + EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`
`NASA_NEW_CAPABILITY: NONE`
`EMPTY_TOPIC_EXCEPTION: UNCHANGED / OPEN_VISUAL_SUBJECT_QUERY ONLY`
`PRODUCTIVE_PYTHON_DELTA: TWO AUTHORIZED FILES ONLY`
`USER_CORRECTED_TEST: INCORPORATED / CANONICAL`
`PROVIDER_QUERY_CHANGE: NONE`
`SELECTOR_CHANGE: NONE`
`QUERY_CONTRACT_CHANGE: NONE`
`EXECUTOR_CHANGE: NONE`
`NATURAL_LANGUAGE_CHANGE: NONE`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: POST-GREEN MASTER PLAN RECONCILIATION`
