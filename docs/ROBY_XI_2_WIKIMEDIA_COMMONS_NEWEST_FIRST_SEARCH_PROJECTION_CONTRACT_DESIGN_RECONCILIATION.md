# ROBY XI.2 — Wikimedia Commons Newest-First Search Projection
## CONTRACT DESIGN RECONCILIATION

### Certified input
PRE-RED Owner-certified:
- 13,594 PASS / 0 FAIL;
- Ruff clean;
- M361 reproducible;
- Python/test delta: ZERO.

### Architectural classification
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

Canonical authority remains:
`WikimediaCommonsGovernedSourceAdapter`.

Exact seam:
`WikimediaCommonsGovernedSourceAdapter._build_url(query)`.

No new adapter, provider, executor, selector, manager, router, gateway,
presentation authority, or sorting authority is permitted.

### Contract D1 — typed governed trigger
The adapter imports the already-certified:
`GovernedSourceQueryOrder`

from:
`app.governed_source_query`.

Provider projection is triggered only by:
`query.order is GovernedSourceQueryOrder.NEWEST_FIRST`.

No string comparison or coercion is authorized.

### Contract D2 — exact provider projection
For NEWEST_FIRST, `_build_url(query)` adds exactly:

`gsrsort=create_timestamp_desc`

to the existing MediaWiki generator-search request.

The existing:
- `action=query`;
- `format=json`;
- `generator=search`;
- `gsrsearch`;
- `gsrnamespace=6`;
- bounded `gsrlimit`;
- imageinfo properties and thumbnail bounds

remain intact.

### Contract D3 — ordinary behavior preservation
For:
`query.order is None`

the request omits `gsrsort`.

Existing provider/default search ordering remains untouched.

No default NEWEST_FIRST behavior is introduced.

### Contract D4 — semantic exclusion
The projection must not use:
`last_edit_desc`.

Permanent:
`NEWEST_FIRST != LAST_EDIT_DESC`.

No fallback from create-order to last-edit order is authorized.

### Contract D5 — no local ordering authority
The adapter must not call `sorted(...)` or reorder parsed items.

The executor and presentation layers remain non-ordering authorities.

Permanent:
`PROVIDER_ORDER_PROJECTION != LOCAL_RESULT_SORTING`.

### Contract D6 — timestamp metadata remains metadata
`imageinfo.timestamp` must not be used to implement NEWEST_FIRST.

No timestamp completeness, parsing, comparison, or tie-breaking is required by
this block.

Permanent:
`IMAGEINFO_TIMESTAMP != NEWEST_FIRST_AUTHORITY`.

### Contract D7 — date bounds remain orthogonal
This block introduces no implicit `published_after` or `published_before`
window and does not reinterpret existing date bounds.

`NEWEST_FIRST_ORDER != DATE_FILTER`.

### Contract D8 — capability ownership remains upstream
The existing selector and `GovernedSourceQueryContract` remain the capability
admission authorities.

This adapter does not create a parallel capability gate.

Its declared
`EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`
capability remains unchanged.

### Contract D9 — URL encoding contract
The RED contract should parse the generated URL query string rather than rely
on parameter textual order.

For NEWEST_FIRST it must establish:
`parse_qs(...)["gsrsort"] == ["create_timestamp_desc"]`.

For order=None:
`"gsrsort" not in parse_qs(...)`.

This avoids coupling the contract to dictionary insertion order or URL
serialization details.

### Contract D10 — bounded request preservation
RED must prove that adding newest-first does not change the existing bounded
request semantics, especially:
- `gsrlimit == min(query.limit, 20)`;
- namespace remains file namespace `6`;
- generator remains `search`;
- thumbnail width remains `640`.

### Contract D11 — provider-order preservation
A transport fixture returning pages in a deliberate sequence must remain in
that sequence after adapter execution, subject only to existing bounded item
handling.

No test should require chronological interpretation of response timestamps.

### Contract D12 — deferred natural-language admission
No ACI/natural-language freshness term is added here.

Separate later residual:
`EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`.

### CONTRACT RED design
Create one architecture contract file only.

Minimum obligations:
1. NEWEST_FIRST URL contains exact `gsrsort=create_timestamp_desc`.
2. order=None omits `gsrsort`.
3. existing generator/search/query/namespace parameters are preserved.
4. existing result limit remains bounded.
5. existing thumbnail bound remains preserved.
6. no `last_edit_desc`.
7. no local `sorted(...)` ordering.
8. deliberate provider item order is preserved.
9. imageinfo timestamp is not required to enforce ordering.
10. no ACI change/new freshness-language admission.
11. no executor/presentation sorting.
12. no parallel provider/sorting authority.

Expected RED convergence:
the positive NEWEST_FIRST projection assertion fails because `gsrsort` is
currently absent; preservation/negative boundaries should remain green.

RED must not require a particular failure count beyond the intentional missing
projection, because multiple assertions may be grouped around that same absent
parameter.

### Expected surgical GREEN
Productive file:
`app/wikimedia_commons_governed_source.py` only.

Expected implementation shape:
- extend the existing governed-query import to include
  `GovernedSourceQueryOrder`;
- after constructing the existing `parameters` mapping, conditionally set:
  `parameters["gsrsort"] = "create_timestamp_desc"`
  only for typed NEWEST_FIRST;
- preserve existing `urlencode(parameters)` return path.

No other productive module is authorized by this design.

### Current reconciliation evidence
Related architecture contracts:
`39 PASS / 0 FAIL`.

Python/test delta during CONTRACT DESIGN:
`ZERO`.

### Formal state
`CONTRACT_DESIGN_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`CANONICAL_AUTHORITY: WikimediaCommonsGovernedSourceAdapter`
`EXACT_SEAM: _build_url(query)`
`TYPED_TRIGGER: GovernedSourceQueryOrder.NEWEST_FIRST`
`EXACT_PROJECTION: gsrsort=create_timestamp_desc`
`ORDER_NONE: OMIT gsrsort`
`LAST_EDIT_DESC: FORBIDDEN`
`LOCAL_SORTING: FORBIDDEN`
`TIMESTAMP_ORDERING: FORBIDDEN`
`IMPLICIT_DATE_WINDOW: FORBIDDEN`
`ACI_CHANGE: DEFERRED`
`EXPECTED_GREEN_PRODUCTIVE_DELTA: ONE EXISTING MODULE`
`PRODUCTIVE_PYTHON_DELTA_NOW: ZERO`
`TEST_DELTA_NOW: ZERO`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: CONTRACT RED`
