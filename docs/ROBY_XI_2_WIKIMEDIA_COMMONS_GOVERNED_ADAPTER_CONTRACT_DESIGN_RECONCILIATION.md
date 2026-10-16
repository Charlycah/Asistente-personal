# ROBY XI.2 — Wikimedia Commons Governed Adapter Contract
## Contract Design Reconciliation

### Certified input
`GOVERNED WIKIMEDIA COMMONS OPEN VISUAL PROVIDER — PRE-RED RECONCILIATION`
is the governing input. Its productive Python delta is zero and its Owner
baseline is 13,542 PASS / 0 FAIL, Ruff clean.

### Classification
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

This seam adds one provider adapter behind existing governed source/query
authorities. It does not create a source-selection, query-execution,
presentation, routing, planning, or conversational authority.

### Adapter identity and declaration
Future adapter:
`WikimediaCommonsGovernedSourceAdapter`

Canonical source id:
`wikimedia_commons`

The adapter must expose `source_declaration` as a
`GovernedInformationSource` with:
- `source_id="wikimedia_commons"`;
- empty `topics`;
- explicit capability
  `InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY`;
- global coverage/region;
- a classification/provenance combination representing Wikimedia Commons as
  an external community-curated media repository, using existing enums only.
  Contract RED must not add a new classification enum merely for Wikimedia.
- inactive declaration flags required by the existing source model.

The exact existing enum values must be chosen by semantic fit in RED fixtures;
no new source-model authority is authorized.

### Endpoint and operation
Canonical endpoint:
`https://commons.wikimedia.org/w/api.php`

Read-only HTTPS GET only.

The adapter must use MediaWiki Action API `action=query` and JSON output.

### Query mapping
The governed `query.query_text` is the only user subject/search text.
It must be non-empty after existing query validation.

Contract request shape:
- `action=query`
- `format=json`
- `generator=search`
- `gsrsearch=<query.query_text>`
- `gsrnamespace=6` (File namespace)
- `gsrlimit=<bounded query.limit>`
- `prop=imageinfo`
- `iiprop=url|mime|mediatype|timestamp|user|extmetadata`
- `iilimit=1`
- bounded thumbnail width through `iiurlwidth`
- `iiextmetadatalanguage=en`
- `iiextmetadatafilter` restricted to attribution/license fields actually used
  by ROBY.

No arbitrary user-provided query parameter may override endpoint, namespace,
action, format, prop, imageinfo properties, result bound, or transport policy.

### Result bound
The adapter must preserve the existing governed query limit and additionally
apply a provider-local hard maximum.

Contract value:
`MAX_RESULTS = 20`

Effective provider request/result limit:
`min(query.limit, 20)`.

The executor remains the final bounding authority for returned items.

### Thumbnail contract
Contract thumbnail width:
`640` pixels.

The adapter should prefer the HTTPS thumbnail URL returned for that width.
If a usable thumbnail URL is unavailable, it may use the original HTTPS file
URL only when the result is otherwise a supported raster image.

### Image-only eligibility
Only results representing displayable raster images are eligible.

Required accepted MIME family:
`image/*`

Provider `mediatype` and MIME must not indicate audio, video, document,
archive, or other non-image media.

SVG and other formats whose direct rendering/support is ambiguous must be
accepted only through a provider-generated raster thumbnail URL; the adapter
must not expose a non-raster original as `preview_url`.

### Raw result schema
Each accepted item must project a bounded mapping containing exactly the
provider facts required downstream. Required keys:
- `source_id`: `"wikimedia_commons"`
- `external_id`: stable Commons page/file identity
- `title`: normalized file title/label
- `media_type`: `"image"`
- `preview_url`: HTTPS renderable preview
- `source_url`: HTTPS Commons description/canonical page URL when available
- `published_at`: provider timestamp when valid
- `uploader`: provider user/uploader when present
- `artist`: attribution author/artist text when present
- `credit`: attribution/source text when present
- `license_short_name`: machine-readable short license label when present
- `license_url`: HTTPS license URL when present
- `attribution_required`: boolean derived only from provider metadata when
  determinable; otherwise conservative/unknown representation must not invent
  a legal conclusion.

No HTML from `extmetadata` may be rendered as trusted UI markup. Metadata text
must be treated as untrusted provider text.

### Metadata filter
Contract RED must require a narrow `iiextmetadatafilter` sufficient for:
`Artist`, `Credit`, `LicenseShortName`, `LicenseUrl`, and any exact field
needed to determine attribution without requesting unrestricted extmetadata.

### Stable identity
`external_id` must come from a stable provider page/file identifier (page id
when available, otherwise canonical file title). It must not be derived from
result order, preview URL, timestamp, or local random state.

### HTTPS and URL safety
`preview_url`, `source_url`, and `license_url` are accepted only when they are
absolute HTTPS URLs.

Missing/invalid `preview_url` rejects that item.
Invalid optional source/license URL is omitted rather than repaired or
guessed.

### User-Agent contract
Every Wikimedia HTTP request must carry:
- `Accept: application/json`;
- a meaningful, non-browser `User-Agent` identifying ROBY and containing
  operator/contact information as required by Wikimedia policy.

The contact-bearing User-Agent must enter through governed configuration or
adapter construction. It must not hardcode a personal email/address and must
not silently fall back to a generic browser User-Agent.

An empty/blank configured User-Agent is a contract error before network I/O.

### Timeout and transport
The adapter must pass `query.timeout_seconds` to the existing bounded HTTP
transport. Existing `GovernedSourceQuery` already restricts this to `(0, 60]`.

No adapter-specific background loop, retry worker, concurrency manager, or
unbounded pagination is authorized.

### Throttling/error behavior
The adapter performs a single bounded Action API query per execution unless
future evidence demonstrates a necessary continuation seam.

HTTP/API failure, malformed JSON, missing query/pages structure, unusable
image information, or malformed URLs must fail closed according to the
existing executor/adapter error contract.

HTTP 429 / `Retry-After` must not trigger an internal sleep/retry loop in this
seam. The request fails/returns unavailable through the existing executor
boundary; retry scheduling is not adapter authority.

### Attribution/licensing boundary
The adapter preserves provider metadata; it does not decide that a work is
legally reusable, does not rewrite licenses, and does not synthesize missing
attribution.

`PROVIDER_METADATA_PRESERVATION != LEGAL_REUSE_AUTHORIZATION`.

No change to `GovernedInformationItem` is authorized.

### Presentation boundary
Existing external-image presentation remains authoritative.
This seam does not add attribution UI or alter desktop presentation.

If later product requirements demand visible attribution/license rendering,
that is a separate presentation residual and must be reconciled separately.

### Registration/reachability boundary
This contract does not register the future adapter in productive composition.

`WIKIMEDIA_COMMONS_EXISTING_EXECUTOR_REGISTRATION_AND_REACHABILITY`
remains a later seam.

### Contract RED obligations
The future RED should prove at minimum:
1. canonical source id and explicit open-visual capability;
2. empty topics without wildcard semantics;
3. canonical Commons HTTPS endpoint and GET-only query;
4. File namespace restriction;
5. query text mapping;
6. provider hard result bound of 20;
7. thumbnail width bound;
8. exact narrow imageinfo/extmetadata request;
9. descriptive configured User-Agent required before network I/O;
10. query timeout propagation;
11. image-only/raster-preview eligibility;
12. malformed/non-HTTPS preview rejection;
13. stable provider identity;
14. bounded raw result schema;
15. attribution/license metadata preservation without legal inference;
16. untrusted HTML metadata not treated as trusted markup;
17. malformed/API-error fail-closed behavior;
18. no internal retry/background/concurrency authority;
19. no `GovernedInformationItem` change;
20. no executor/selector/presentation authority duplication;
21. no productive registration/reachability in this seam;
22. no freshness ordering in this seam.

### Authorization
`CONTRACT_DESIGN_RECONCILIATION: COMPLETE`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`SOURCE_ID: wikimedia_commons`
`ENDPOINT: COMMONS MEDIAWIKI ACTION API`
`MAX_RESULTS: 20`
`THUMBNAIL_WIDTH: 640`
`EMPTY_TOPICS: AUTHORIZED ONLY BY EXISTING OPEN_VISUAL CAPABILITY`
`USER_AGENT: GOVERNED CONTACT-BEARING CONFIGURATION REQUIRED`
`ATTRIBUTION_LICENSE: PRESERVE / DO NOT LEGALLY INFER`
`GOVERNED_INFORMATION_ITEM_CHANGE: FORBIDDEN / OUT OF SCOPE`
`EXECUTOR_REGISTRATION: FORBIDDEN / LATER SEAM`
`PRESENTATION_CHANGE: FORBIDDEN / OUT OF SCOPE`
`FRESHNESS: FORBIDDEN / LATER`
`NEW_AUTHORITY: NONE`
`CONTRACT_RED_AUTHORIZATION: YES / ADAPTER CONTRACT ONLY`
`PRODUCTIVE_GREEN_AUTHORIZATION: NO`


## Contract RED outcome
Focused RED: 7 intentional FAIL / 1 PASS.\nAll failures converge on missing canonical adapter module.\nProductive Python delta: zero; test Python delta: exactly one file.\n