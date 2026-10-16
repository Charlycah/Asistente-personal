# ROBY XI.2 — Governed External Image Freshness Order Representation
## PRE-RED RECONCILIATION

### Owner-certified baseline
Input is the Owner-certified closure of
`EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`:
- 13,584 PASS / 0 FAIL;
- Ruff clean;
- M361 reproducible;
- capability-declaration internal residual: NONE.

Parent horizon:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`.

Selected residual:
`GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`.

### Existing canonical transport
`GovernedConversationalSourceSelectionRequest` already carries typed query intent:
- topics;
- query_text;
- limit;
- region;
- published_after;
- published_before;
- timeout_seconds;
- parameters;
- conversational request mode.

`GovernedConversationalSourceSelector.select()` explicitly projects those fields
into `GovernedSourceQuery`.

`GovernedSourceQuery` already validates its own structural invariants and
normalizes date bounds.

`GovernedSourceQueryContract.prepare()` is the existing capability/source
admission boundary.

No separate freshness request/query authority is needed.

### Date bounds are not ordering
`published_after` and `published_before` are temporal filters.

They do not encode result ordering and must not be overloaded to mean newest
first.

Permanent distinctions:
`DATE_WINDOW != RESULT_ORDER`
`TIMESTAMP_METADATA != RESULT_ORDER`
`NEWEST_FIRST_ORDER != IMPLICIT_TIME_WINDOW`

No fixed 7/30/365-day window is authorized for "latest".

### Representation seam
The minimal representation is one explicit typed result-order semantic carried
by both existing request and query objects and projected unchanged through the
existing selector.

Recommended canonical type:
`GovernedSourceQueryOrder`

Initial bounded value:
`NEWEST_FIRST = "newest_first"`

Recommended fields:
- `GovernedConversationalSourceSelectionRequest.order:
  GovernedSourceQueryOrder | None = None`
- `GovernedSourceQuery.order:
  GovernedSourceQueryOrder | None = None`

The selector must project `request.order` unchanged into `query.order`.

This is a query-result-order semantic, not a conversational mode. Therefore
`GovernedConversationalRequestMode` must remain unchanged.

It must not be encoded inside free-form `parameters`, because that would bypass
typed governance and permit provider-specific strings to become semantic
authority.

### Capability-gated admission
If `order is NEWEST_FIRST`, source eligibility/admission must require:
`InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`.

The already certified capability is the authority for that promise.

Fail-closed behavior:
- selector: freshness-order request with no registered capable source =>
  `UNAVAILABLE`;
- query contract: direct newest-first query against a non-capable source =>
  reject with `ValueError`.

Ordinary queries with `order is None` preserve existing source eligibility.

For an OPEN_VISUAL_SUBJECT newest-first request, both independent capabilities
are required:
- `OPEN_VISUAL_SUBJECT_QUERY`;
- `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`.

`NEWEST_FIRST` must not imply open-visual eligibility, and open-visual
capability must not imply newest-first eligibility.

### Executor boundary
The executor is not ordering authority.

It may transport/hash the governed order once representation exists so
execution identity remains semantically complete, but it must not sort raw
items by timestamp or invent provider semantics.

Provider result order remains authoritative only after a capable adapter
explicitly projects the governed order into its provider-supported query.

Whether execution-id inclusion belongs in the representation GREEN or in the
provider-projection block must be decided at CONTRACT DESIGN; no change is
authorized here.

### Provider boundary
This PRE-RED does not add `gsrsort` or any Wikimedia request parameter.

Provider projection remains the separate later residual:
`WIKIMEDIA_COMMONS_NEWEST_FIRST_SEARCH_PROJECTION`.

### Natural-language boundary
This PRE-RED does not recognize "latest", "newest", "últimas", "más recientes",
or related language.

Natural-language admission remains the separate later residual:
`EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`.

### Exact dependency result
The representation residual decomposes into one bounded contract surface:
1. typed order enum/value;
2. optional order field on existing selection request;
3. optional order field on existing source query;
4. exact request-to-query projection;
5. capability-gated selector eligibility;
6. capability-gated query-contract admission;
7. preservation of ordinary/date-bound/open-visual behavior.

No new manager, selector, executor, router, planner, gateway, or source
authority is justified.

### CONTRACT DESIGN questions
Before RED, CONTRACT DESIGN must freeze:
- exact module location/name for `GovernedSourceQueryOrder`;
- exact field name (`order`);
- whether executor execution identity includes order in this block or later;
- validation behavior for invalid/non-enum order values;
- exact preservation matrix for topic-constrained and open-visual requests.

### Expected future productive envelope
Likely existing files only:
- `app/governed_conversational_source_selection.py`;
- `app/governed_source_query.py`;
- optionally one minimal shared enum module only if import direction proves
  necessary.

No productive change is authorized yet.

Not authorized in this residual:
- ACI/natural-language changes;
- Wikimedia `gsrsort`;
- NASA changes;
- generic executor sorting;
- presentation sorting;
- new freshness authority.

### Local evidence
Relevant architecture contracts:
`50 PASS / 0 FAIL`.

PRE-RED Python/test delta:
`ZERO`.

### Formal state
`PRE_RED_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`CANONICAL_TRANSPORT: EXISTING SELECTION REQUEST -> EXISTING SOURCE QUERY`
`REPRESENTATION_DIRECTION: TYPED OPTIONAL NEWEST_FIRST ORDER`
`DATE_BOUNDS: PRESERVED AS FILTERS / NOT ORDER`
`CAPABILITY_AUTHORITY: EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`
`EXECUTOR_SORTING: REJECTED`
`PRESENTATION_SORTING: REJECTED`
`PROVIDER_PROJECTION: DEFERRED`
`NATURAL_LANGUAGE_ADMISSION: DEFERRED`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ZERO`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: CONTRACT DESIGN RECONCILIATION`
