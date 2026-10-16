# ROBY XI.2 — Governed General Open Visual Provider
## Provider / Integration Reconciliation

### Certified input
`OPEN_VISUAL_SUBJECT_CAPABLE_SOURCE_AVAILABILITY_PRE_RED_RECONCILIATION`
is Owner-certified at 13,531 PASS / 0 FAIL, Ruff clean, M361 reproducible.

Closed seams are not reopened:
- natural-language visual reachability;
- open-visual request representation;
- source capability declaration.

### Existing ROBY integration path
The current architecture already supplies every authority needed for a new
governed source:
- `GovernedInformationSources`;
- `GovernedConversationalSourceSelector`;
- `GovernedSourceQueryContract`;
- `GovernedSourceQueryExecutor`;
- `OfficialConversationGateway`;
- non-default adapter `source_declaration` admission precedent;
- external-image presentation projection based on raw result fields.

A compatible adapter only needs to normalize provider results to the existing
raw visual-result contract (`source_id`, `external_id`, `title`, `media_type`,
HTTPS `preview_url`, plus optional description/published_at/verification).
No new presentation authority is justified.

### Provider research
Official provider documentation was compared for Wikimedia Commons, Pexels,
Unsplash, and Pixabay.

#### Wikimedia Commons
MediaWiki/Wikimedia official APIs provide:
- general search;
- file/image information;
- original/description URLs and thumbnail URLs;
- uploader/timestamp/media type;
- extended metadata including credit/artist/license information.

Read access can operate without a provider API key, but requests must identify
the client with a meaningful User-Agent and obey current Wikimedia API rate
limits, Retry-After behavior, content-license attribution, and robot/API policy.

This maps well to ROBY's existing no-automatic-fetch, bounded on-demand source
adapter pattern and to the existing external-image presentation raw fields.

#### Pexels
Official API supports arbitrary-topic photo search and rich photo results.
It requires an API key in the Authorization header and has attribution/link
guidelines and rate limits. It is technically compatible but adds credential
provisioning and provider-specific display obligations.

#### Unsplash
Official API supports photo search and rich image URLs. It requires API
credentials and mandates hotlinking returned image URLs plus Unsplash/
photographer attribution and related integration rules. It is technically
compatible but imposes a stronger provider-specific presentation contract.

#### Pixabay
Official API supports general image search and image filters. It requires an
API key and asks API consumers to identify Pixabay as the source when showing
search results. It is technically compatible but adds credential/provider
policy obligations.

### Selection
`WIKIMEDIA_COMMONS` is selected as the preferred first governed provider
candidate for this residual.

Rationale:
1. genuinely general/open visual subject coverage;
2. official read APIs expose search, HTTPS image/thumbnail URLs and provenance
   metadata needed by the existing result pipeline;
3. no commercial API key is required for ordinary read access;
4. source identity, uploader, timestamps and license/credit metadata are
   inspectable;
5. it can be integrated through the already existing non-default
   `source_declaration` + executor registration path;
6. it does not require generalizing NASA or weakening topic-constrained sources;
7. it does not require a new selector, executor, registry, router, gateway, or
   presentation authority.

Selection does not mean productive integration is authorized yet.

### Necessary bounded source contract
A future Wikimedia Commons adapter must:
- declare one non-default governed source with
  `OPEN_VISUAL_SUBJECT_QUERY`;
- remain `automatic_fetch_enabled=False`;
- execute only explicit selected queries;
- search Commons file/image content for `query.query_text`;
- return only image results with HTTPS preview URLs;
- preserve stable external identity and provider/source identity;
- retain enough attribution/license/source-page metadata in normalized raw
  results for future compliant exposure without changing source authority;
- use a meaningful governed User-Agent;
- enforce bounded result count/response size/timeouts;
- treat HTTP/rate-limit/provider failures as bounded source failure/unavailability;
- never infer eligibility from empty topics or adapter technical ability.

### Architectural issue discovered
`GovernedInformationSource` currently requires a non-empty `topics` set even
for a source whose intended authorization is `OPEN_VISUAL_SUBJECT_QUERY`.
That legacy invariant is appropriate for topic-constrained sources, but a
general open-visual source cannot honestly invent an `InterestTopic` merely to
satisfy it.

Therefore provider integration contains a prerequisite contract seam:

`OPEN_VISUAL_CAPABLE_SOURCE_DECLARATION_WITHOUT_FAKE_TOPIC`

This must be solved narrowly: empty source topics may be permitted only when
the source explicitly declares `OPEN_VISUAL_SUBJECT_QUERY`. It must not create
an empty-topic wildcard, and selector/query-contract capability enforcement
must remain authoritative.

This prerequisite is an existing source-model deepening, not a new authority.

### Decision and sequencing
Preferred provider candidate:
`WIKIMEDIA_COMMONS`

Immediate next seam:
`OPEN_VISUAL_CAPABLE_SOURCE_DECLARATION_WITHOUT_FAKE_TOPIC`

Only after that seam is contractually closed should ROBY add the bounded
Wikimedia Commons source declaration/adapter/registration.

`EXTERNAL_IMAGE_FRESHNESS_ORDERING` remains later and is not part of provider
integration.

### Authorization state
`PROVIDER_INTEGRATION_RECONCILIATION: COMPLETE`
`PREFERRED_PROVIDER_CANDIDATE: WIKIMEDIA_COMMONS`
`NASA_GENERALIZATION: REJECTED`
`PEXELS: COMPATIBLE / NOT PREFERRED FIRST`
`UNSPLASH: COMPATIBLE / NOT PREFERRED FIRST`
`PIXABAY: COMPATIBLE / NOT PREFERRED FIRST`
`EXACT_PREREQUISITE_SEAM: OPEN_VISUAL_CAPABLE_SOURCE_DECLARATION_WITHOUT_FAKE_TOPIC`
`CONTRACT_DESIGN_AUTHORIZATION: YES / PREREQUISITE SEAM ONLY`
`CONTRACT_RED_AUTHORIZATION: NO`
`WIKIMEDIA_ADAPTER_GREEN_AUTHORIZATION: NO`
`FRESHNESS: EXCLUDED / LATER`
`NEW_AUTHORITY: NONE`


## No-fake-topic contract design outcome
Declaration predicate: topics non-empty OR explicit OPEN_VISUAL_SUBJECT_QUERY.
Empty topics remain forbidden as topic wildcard.
CONTRACT RED authorized for this prerequisite seam only.


## No-fake-topic prerequisite seam closure
Owner-certified GREEN: 13,542 PASS / 0 FAIL; Ruff clean.\nInternal residual: NONE.\nNext residual: GOVERNED_WIKIMEDIA_COMMONS_OPEN_VISUAL_PROVIDER_INTEGRATION.\nNext step: provider-specific PRE-RED reconciliation; no RED/GREEN authorization yet.\n