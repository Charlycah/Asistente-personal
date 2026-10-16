# ROBY XI.2 — Wikimedia Commons Newest-First Search Projection
## PRE-RED RECONCILIATION

### Owner-certified baseline
Input:
`GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`
POST-GREEN Owner-certified:
- 13,594 PASS / 0 FAIL;
- Ruff clean;
- M361 reproducible;
- representation internal residual: NONE.

Parent:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`.

Selected independent residual:
`WIKIMEDIA_COMMONS_NEWEST_FIRST_SEARCH_PROJECTION`.

### Existing canonical authority
No new provider/query/executor authority is needed.

Existing adapter:
`WikimediaCommonsGovernedSourceAdapter`

Existing governed intent:
`GovernedSourceQueryOrder.NEWEST_FIRST`

Existing explicit source capability:
`InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`

Wikimedia already declares that capability.

### Existing adapter request
The adapter already uses MediaWiki Action API:
- `action=query`;
- `generator=search`;
- `gsrsearch=<query text>`;
- `gsrnamespace=6`;
- bounded `gsrlimit`;
- `prop=imageinfo`;
- bounded thumbnail/image metadata retrieval.

It currently does not inspect/project `query.order`.

No productive `gsrsort` exists.

### Official provider semantics
MediaWiki's official Search API documents:
- the search module can be used as a generator;
- search exposes a sort-order parameter;
- `create_timestamp_desc` is an allowed search sort value;
- default search order is relevance.

Because the adapter invokes search as `generator=search`, search-module
parameters use the generator prefix `gsr`.

Therefore the provider-side projection corresponding to governed
`NEWEST_FIRST` is:

`gsrsort=create_timestamp_desc`

This is provider-supported search ordering, not ROBY timestamp sorting.

### Semantic boundary
`create_timestamp_desc` is selected rather than `last_edit_desc`.

Reason:
the governed intent is newest-first image search; last-edit ordering would rank
old files with recent edits as newer, which is a different semantic.

Permanent:
`NEWEST_FIRST != LAST_EDIT_DESC`
`PROVIDER_CREATE_ORDER != IMAGEINFO_TIMESTAMP_SORT`

The adapter's returned `imageinfo.timestamp` remains metadata. It must not be
used by ROBY to re-sort results.

### Exact projection seam
The minimal seam is inside the existing
`WikimediaCommonsGovernedSourceAdapter._build_url(query)`.

If:
`query.order is GovernedSourceQueryOrder.NEWEST_FIRST`

then add exactly:
`gsrsort=create_timestamp_desc`

If:
`query.order is None`

do not add `gsrsort`; preserve existing relevance/default behavior.

No other order value currently exists.

### Fail-closed relationship
Capability admission is already enforced upstream by the selector and query
contract.

The Wikimedia adapter declares the capability and may therefore project the
certified order.

The adapter must not infer NEWEST_FIRST from:
- query text;
- timestamps;
- date bounds;
- provider response order.

`query.order` is the sole governed trigger.

### Date-bound boundary
`published_after` / `published_before` remain independent governed filters.

This provider-projection block must not invent a time window.

Whether Wikimedia currently projects those bounds is outside this residual
unless an existing contract already requires it.

### Result-order boundary
After Wikimedia receives the explicit provider sort, the adapter and executor
must preserve provider result order.

No local `sorted(...)` call is authorized.

No timestamp completeness requirement is authorized for ordering, because
provider-side search semantics supply the order.

### Scope classification
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

Expected productive GREEN:
`app/wikimedia_commons_governed_source.py` only.

No new adapter, manager, selector, executor, router, planner, gateway, source,
or presentation authority.

### CONTRACT DESIGN questions
Before RED, freeze:
1. exact import of `GovernedSourceQueryOrder` into the adapter;
2. exact conditional insertion point for `gsrsort`;
3. contract that ordinary `order=None` omits `gsrsort`;
4. contract that NEWEST_FIRST emits exactly
   `gsrsort=create_timestamp_desc`;
5. preservation of existing bounded query parameters;
6. preservation of raw/provider result order;
7. no use of `last_edit_desc`;
8. no timestamp sorting;
9. no ACI freshness-language change.

### Separate later residual
`EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`

This block must not modify natural-language recognition.

### Local evidence
Related architecture contracts:
`39 PASS / 0 FAIL`.

PRE-RED Python/test delta:
`ZERO`.

### Formal state
`PRE_RED_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`CANONICAL_ADAPTER: WikimediaCommonsGovernedSourceAdapter`
`GOVERNED_TRIGGER: GovernedSourceQueryOrder.NEWEST_FIRST`
`PROVIDER_PROJECTION: gsrsort=create_timestamp_desc`
`ORDINARY_ORDER_NONE: PROVIDER DEFAULT / NO gsrsort`
`LAST_EDIT_DESC: REJECTED`
`LOCAL_TIMESTAMP_SORTING: REJECTED`
`EXECUTOR_SORTING: REJECTED`
`IMPLICIT_TIME_WINDOW: REJECTED`
`EXPECTED_PRODUCTIVE_GREEN_DELTA: ONE EXISTING ADAPTER MODULE`
`PRODUCTIVE_PYTHON_DELTA_NOW: ZERO`
`TEST_DELTA_NOW: ZERO`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: CONTRACT DESIGN RECONCILIATION`
