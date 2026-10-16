# ROBY XI.2 — Governed External Image Freshness Order Representation
## CONTRACT DESIGN RECONCILIATION

### Certified design basis
Parent:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

Current residual:
`GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`

Prerequisite already closed:
`EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`

Canonical capability:
`InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`

This block is:
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`.

No new query, selector, executor, router, gateway, planner, source, or
presentation authority is authorized.

### Decision 1 — canonical order type location
`GovernedSourceQueryOrder` belongs in:
`app/governed_source_query.py`

Exact initial contract:
`class GovernedSourceQueryOrder(StrEnum):`
`    NEWEST_FIRST = "newest_first"`

Rationale:
- the semantic describes governed result order;
- it is not conversational language/mode;
- `governed_source_query.py` already owns typed query semantics and validation;
- source selection already imports `GovernedSourceQuery`, so importing the
  adjacent enum from the same module does not introduce a new dependency cycle;
- a separate module would be unnecessary authority/surface for one bounded
  query semantic.

### Decision 2 — exact field
Both existing transport objects gain:
`order: GovernedSourceQueryOrder | None = None`

Objects:
1. `GovernedConversationalSourceSelectionRequest`
2. `GovernedSourceQuery`

`None` means no governed result-order requirement and preserves all current
behavior.

The selector must project:
`order=request.order`

without transformation or inference.

### Decision 3 — validation
The public contract is typed, but Python runtime construction must fail closed
for non-enum values.

`GovernedConversationalSourceSelectionRequest.__post_init__`:
- accepts `None` or `GovernedSourceQueryOrder`;
- otherwise raises `ValueError`.

`GovernedSourceQuery.__post_init__`:
- accepts `None` or `GovernedSourceQueryOrder`;
- otherwise raises `ValueError`.

No coercion from strings such as `"newest_first"` is authorized.

Permanent:
`STRING_VALUE != GOVERNED_ORDER_ENUM`

### Decision 4 — date bounds remain orthogonal
`published_after` / `published_before` remain unchanged.

The following combinations are structurally valid:
- date bounds with `order=None`;
- `NEWEST_FIRST` with no date bounds;
- `NEWEST_FIRST` with explicit date bounds.

No implicit date window is manufactured from `NEWEST_FIRST`.

Permanent:
`DATE_FILTER != ORDER`
`ORDER != DATE_FILTER`

### Decision 5 — capability-gated selector eligibility
For any request with:
`order is GovernedSourceQueryOrder.NEWEST_FIRST`

the selected source must explicitly declare:
`InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`.

This check composes with all existing eligibility checks.

Therefore:
- topic-constrained + no order: existing behavior;
- topic-constrained + NEWEST_FIRST: topic/region/registration rules plus
  newest-first capability;
- open-visual + no order: existing OPEN_VISUAL capability behavior;
- open-visual + NEWEST_FIRST: requires BOTH
  `OPEN_VISUAL_SUBJECT_QUERY` and `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`.

No capability implies the other.

If no eligible capable registered source exists:
`UNAVAILABLE`.

### Decision 6 — query-contract admission
`GovernedSourceQueryContract.prepare()` must independently enforce the same
newest-first capability.

A direct query with `order=NEWEST_FIRST` against a source lacking
`EXTERNAL_IMAGE_NEWEST_FIRST_QUERY` raises `ValueError`.

This is defense in depth and does not replace selector eligibility.

Existing topic/open-visual/region validation remains authoritative and
composes with this check.

### Decision 7 — execution identity belongs in this representation block
`GovernedSourceQueryExecutor._execution_id()` must include the governed
`query.order` value (or empty string for `None`).

Reason:
once `order` is part of the canonical query representation, two otherwise
identical queries with different governed order semantics are not the same
execution intent. Omitting order would make execution identity semantically
incomplete.

This is transport/identity completeness only.

The executor MUST NOT:
- sort results;
- inspect result timestamps to enforce order;
- infer provider semantics;
- reject/accept capability on its own.

Permanent:
`EXECUTION_ID_INCLUDES_ORDER != EXECUTOR_ORDERING_AUTHORITY`

### Decision 8 — provider projection remains deferred
Wikimedia already declares
`EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`, but this representation block does not
project the order to provider parameters.

No `gsrsort` is authorized here.

Separate residual:
`WIKIMEDIA_COMMONS_NEWEST_FIRST_SEARCH_PROJECTION`.

Until that residual is implemented, this block establishes governed
representation/admission only; it does not claim end-to-end productive
freshness behavior.

### Decision 9 — natural-language admission remains deferred
No change to `AppliedConversationalIntelligence`.

Words such as:
- latest;
- newest;
- últimas;
- más recientes;

are not admitted by this block.

Separate residual:
`EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`.

### CONTRACT RED obligations
A focused RED must prove at minimum:

1. `GovernedSourceQueryOrder.NEWEST_FIRST.value == "newest_first"`.
2. selection request defaults `order` to `None`.
3. source query defaults `order` to `None`.
4. invalid string/non-enum order fails closed in both objects.
5. selector projects NEWEST_FIRST unchanged into the query.
6. ordinary topic-constrained request behavior remains unchanged.
7. topic-constrained NEWEST_FIRST excludes a source without the capability.
8. topic-constrained NEWEST_FIRST accepts an explicitly capable source.
9. open-visual NEWEST_FIRST requires both independent capabilities.
10. newest-first with no capable source returns UNAVAILABLE.
11. query contract rejects NEWEST_FIRST for non-capable source.
12. query contract accepts NEWEST_FIRST for capable source.
13. explicit date bounds coexist with NEWEST_FIRST unchanged.
14. execution identity differs when governed order differs.
15. executor still preserves raw adapter order; no timestamp sorting.
16. no `gsrsort`/provider projection is introduced.
17. no natural-language freshness admission is introduced.
18. no parallel freshness authority module is introduced.

### Expected RED failure shape
Before productive GREEN, failures should converge on absent representation:
- missing `GovernedSourceQueryOrder`;
- absent `order` fields/projection;
- absent capability gating;
- execution identity not including order.

Preservation/negative tests that do not depend on the absent enum should remain
green.

RED must not require Wikimedia `gsrsort` or natural-language freshness.

### Expected surgical GREEN envelope
Authorized productive files:
1. `app/governed_source_query.py`
2. `app/governed_conversational_source_selection.py`
3. `app/governed_source_query_executor.py`

Expected changes only:
- define `GovernedSourceQueryOrder`;
- add/validate optional `order` on existing query;
- add/validate optional `order` on existing selection request;
- project request order unchanged;
- capability-gate selector eligibility;
- capability-gate query-contract admission;
- include order in execution identity.

No new productive module is authorized.

Not authorized:
- `app/applied_conversational_intelligence.py`;
- Wikimedia adapter/provider query changes;
- NASA changes;
- generic sorting;
- presentation changes;
- runtime wiring/composition;
- gateway changes.

### Compatibility
Existing productive request constructors remain compatible because
`order=None` is the default.

Existing `GovernedSourceQuery` construction is centralized through the
selector in productive code, so the optional field does not require parallel
productive call-site migration.

### Local evidence
Relevant architecture contracts remain:
`50 PASS / 0 FAIL`.

Current CONTRACT DESIGN Python/test delta:
`ZERO`.

### Formal state
`CONTRACT_DESIGN_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`ORDER_TYPE: GovernedSourceQueryOrder`
`ORDER_TYPE_MODULE: app.governed_source_query`
`ORDER_VALUE: NEWEST_FIRST = newest_first`
`FIELD: order`
`DEFAULT: None`
`STRING_COERCION: REJECTED`
`DATE_BOUNDS: ORTHOGONAL / PRESERVED`
`SELECTOR_CAPABILITY_GATE: REQUIRED`
`QUERY_CONTRACT_CAPABILITY_GATE: REQUIRED`
`OPEN_VISUAL_NEWEST_FIRST: REQUIRES BOTH CAPABILITIES`
`EXECUTION_ID: MUST INCLUDE ORDER`
`EXECUTOR_SORTING: FORBIDDEN`
`PROVIDER_PROJECTION: DEFERRED`
`NATURAL_LANGUAGE_ADMISSION: DEFERRED`
`EXPECTED_GREEN_PRODUCTIVE_DELTA: THREE EXISTING MODULES ONLY`
`PRODUCTIVE_PYTHON_DELTA_NOW: ZERO`
`TEST_DELTA_NOW: ZERO`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: CONTRACT RED`
