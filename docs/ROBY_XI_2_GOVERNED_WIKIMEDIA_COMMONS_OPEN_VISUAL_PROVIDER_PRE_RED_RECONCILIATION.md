# ROBY XI.2 — Governed Wikimedia Commons Open Visual Provider
## PRE-RED Reconciliation

### Certified input
The prerequisite
`OPEN_VISUAL_CAPABLE_SOURCE_DECLARATION_WITHOUT_FAKE_TOPIC`
is closed / Owner-certified at 13,542 PASS / 0 FAIL and Ruff clean.

### Existing ROBY authorities to reuse
The integration must reuse:
- `GovernedInformationSource` with explicit
  `OPEN_VISUAL_SUBJECT_QUERY` capability and empty topics;
- `GovernedInformationSources.admit_non_default()`;
- `GovernedSourceQueryContract.admit_non_default_source()`;
- `GovernedSourceQueryExecutor` adapter registration/admission path;
- the existing bounded adapter/network pattern;
- existing raw external-image presentation fields and authority.

No new selector, source registry, query executor, router, gateway, planner, agent,
or presentation authority is justified.

### Existing implementation precedents
`foursquare_governed_source.py` demonstrates a non-default
`source_declaration` and bounded HTTP transport.

`nasa_governed_source.py` demonstrates governed external-media query transport
and raw visual result projection including `media_type` and `preview_url`.

`external_image_presentation.py` already consumes HTTPS image results and
preserves provenance. The provider adapter must feed this existing contract;
it must not create a second presentation model.

### Wikimedia Commons provider facts
The provider target is Wikimedia Commons through the MediaWiki Action API.

The integration must use read-only GET operations. Search results must be
resolved to file information sufficient to produce bounded image results.

MediaWiki `imageinfo` supports URL/thumbnail URL, media type, timestamp, user,
and `extmetadata`. Commons documents `extmetadata` as the current
machine-readable route for license/author information.

Wikimedia requires a descriptive User-Agent for automated API clients and
expects operator/contact identification. API consumers must honor throttling
and rate-limit instructions and content-license requirements.

### Required result projection
The adapter should project only fields needed by ROBY's existing governed
external-image result/presentation path, including:
- stable external/file identity;
- title/label;
- `media_type = image`;
- HTTPS `preview_url`;
- canonical/source URL where available;
- provider/source provenance;
- bounded attribution/license metadata required for responsible reuse.

Provider-native payload must not become a new authority.

### Attribution/licensing boundary
Attribution/license metadata is a provider integration obligation, not a reason
to weaken `GovernedInformationItem`.

The PRE-RED evidence does not justify changing
`GovernedInformationItem` or `GovernedInformationSources.accept()`.

The exact final raw-result keys for attribution/license must be fixed by the
provider Contract Design before RED, against the existing presentation/raw
result contract. They must not be invented opportunistically in GREEN.

### Network/policy boundary
The provider adapter must:
- use HTTPS;
- use a descriptive Wikimedia-compliant User-Agent supplied through governed
  configuration rather than a fake browser identity;
- remain read-only;
- use bounded result counts/timeouts;
- honor API continuation/throttling semantics as required;
- avoid uncontrolled concurrency or bulk crawling;
- fail closed/unavailable on malformed or unusable provider results.

No credentials/API key are required as an architectural premise for ordinary
read-only Commons Action API access.

### Exact residual decomposition
The parent residual
`GOVERNED_WIKIMEDIA_COMMONS_OPEN_VISUAL_PROVIDER_INTEGRATION`
is real, but PRE-RED shows it contains two ordered seams:

1. `WIKIMEDIA_COMMONS_GOVERNED_ADAPTER_CONTRACT`
   Provider-specific declaration, query mapping, bounded read transport,
   Wikimedia policy identity, result filtering/projection, and
   attribution/license preservation.

2. `WIKIMEDIA_COMMONS_EXISTING_EXECUTOR_REGISTRATION_AND_REACHABILITY`
   Registration of that adapter through the existing
   `GovernedSourceQueryExecutor` path so an `OPEN_VISUAL_SUBJECT` request can
   actually reach it.

The second seam must not be implemented before the adapter contract is proven.

### Contract-design requirements before RED
A dedicated provider Contract Design Reconciliation must define:
- exact `source_id`, kind/provenance/coverage declaration;
- explicit empty topics + `OPEN_VISUAL_SUBJECT_QUERY`;
- exact MediaWiki search/imageinfo request shape;
- image-only filtering;
- result limit and timeout bounds;
- exact User-Agent configuration contract;
- exact raw-result schema, including attribution/license keys;
- malformed/unsafe URL rejection;
- API error/throttle behavior;
- deterministic identity/provenance behavior;
- proof that no new authority is introduced.

### PRE-RED decision
`PRE_RED_RECONCILIATION: COMPLETE`
`PREFERRED_PROVIDER: WIKIMEDIA_COMMONS`
`PROVIDER_ENDPOINT_FAMILY: MEDIAWIKI_ACTION_API`
`SOURCE_DECLARATION_PATH: EXISTING_NON_DEFAULT`
`QUERY_EXECUTOR: EXISTING`
`PRESENTATION_AUTHORITY: EXISTING`
`GOVERNED_INFORMATION_ITEM_CHANGE: NOT_JUSTIFIED`
`NEW_AUTHORITY: NONE`
`EXACT_NEXT_SEAM: WIKIMEDIA_COMMONS_GOVERNED_ADAPTER_CONTRACT`
`CONTRACT_RED_AUTHORIZATION: NO`
`PRODUCTIVE_GREEN_AUTHORIZATION: NO`
`FRESHNESS: EXCLUDED / LATER`
`NEXT_STEP: WIKIMEDIA_COMMONS_GOVERNED_ADAPTER_CONTRACT_DESIGN_RECONCILIATION`


## Adapter contract design outcome
Adapter contract design completed without productive Python delta.\nContract RED authorized for WIKIMEDIA_COMMONS_GOVERNED_ADAPTER_CONTRACT only.\nExecutor registration/reachability, presentation, and freshness remain later seams.\n