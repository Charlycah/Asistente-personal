# ROBY XI.2 — External Image Freshness Ordering
## PRE-RED RECONCILIATION

### Certified input
Owner-certified global reselection baseline:
- 13,575 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated / reproducible;
- selected demonstrated residual:
  `EXTERNAL_IMAGE_FRESHNESS_ORDERING`.

This PRE-RED is reconciliation only. No productive Python or test change is
authorized or made.

## 1. Current authority chain
The current external-image path already has one authority per responsibility:

1. `AppliedConversationalIntelligence`
   - bounded explicit natural-language admission;
   - known-topic and open-visual request construction.
2. `GovernedConversationalSourceSelectionRequest`
   - already carries `published_after` and `published_before`.
3. `GovernedConversationalSourceSelector`
   - projects those date bounds unchanged into `GovernedSourceQuery`.
4. `GovernedSourceQueryContract`
   - validates the query and its temporal bounds.
5. `GovernedSourceQueryExecutor`
   - executes the selected adapter and bounds raw result count;
   - it does not impose external-image chronological ordering.
6. Provider adapters
   - NASA maps date bounds to year_start/year_end and exposes date_created as
     `published_at`;
   - Wikimedia currently performs relevance/default search and exposes
     imageinfo timestamp as `published_at`.
7. Presentation
   - consumes raw governed result order and metadata;
   - it is not an ordering authority.

No new manager/router/executor is justified.

## 2. Exact current gaps
### A. Freshness intent admission
ACI does not currently give "últimas", "más recientes", or equivalent bounded
freshness language a governed semantic representation.

Exact seam:
`EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`

### B. Freshness ordering representation
The existing request/query model represents temporal filtering bounds but has
no explicit request-level/result-order semantic such as newest-first.

Exact seam:
`GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`

These are distinct:
`TIME_FILTER != RESULT_ORDER`
`LATEST_INTENT != ARBITRARY_DATE_WINDOW`

## 3. Existing date fields
`published_after` / `published_before` are reusable and must not be duplicated.

However, "latest" does not itself define a truthful fixed cutoff. Therefore the
PRE-RED rejects manufacturing a window such as 7/30/365 days without an
independent product contract.

For latest/newest semantics, ordering is the primary demonstrated need.
Filtering may remain absent unless explicit bounded date language is later
demonstrated and separately contracted.

Decision:
`FRESHNESS_PRIMARY_SEMANTIC: NEWEST_FIRST_ORDER`
`IMPLICIT_FIXED_TIME_WINDOW: REJECTED`
`EXISTING_DATE_BOUNDS: REUSE WHEN EXPLICITLY AVAILABLE`

## 4. Provider semantics
### NASA
The existing NASA adapter can project date bounds as year_start/year_end and
maps NASA `date_created` to `published_at`.

This demonstrates filtering capability, not a general newest-first guarantee.
NASA ordering must not be generalized without provider-specific evidence.

### Wikimedia Commons
Current adapter:
- uses generator search with default relevance;
- requests imageinfo timestamp;
- returns pages in provider/raw order;
- labels the imageinfo timestamp as `published_at`.

Official MediaWiki documentation establishes:
- search supports explicit `create_timestamp_desc` and `last_edit_desc`;
- imageinfo timestamp is the timestamp of the file version / last image
  modification, not necessarily creation/publication time.

Therefore:
`WIKIMEDIA_IMAGEINFO_TIMESTAMP != SAFE_CREATION_TIMESTAMP`
`LAST_EDIT_DESC != CREATE_TIMESTAMP_DESC`

For a user meaning "latest/newest images", the technically closest documented
search semantic is `create_timestamp_desc`, but this PRE-RED does not yet
authorize a productive adapter change. A contract must bind the intended
semantic and prove the generated request.

## 5. Ordering authority
The generic executor must not silently sort all governed source results by a
provider-specific `published_at` field:
- not every provider has equivalent timestamp semantics;
- missing/unparseable timestamps would create hidden policy;
- executor is source-agnostic execution authority.

Presentation must also remain passive and must not redefine intent.

The correct direction is:
- represent freshness order explicitly in the existing governed request/query
  path;
- only an explicitly capable provider may honor it according to its declared
  semantics;
- preserve provider result order after that governed provider query.

This is existing-capability deepening, not a new authority.

## 6. Capability governance prerequisite
Current source capability governance distinguishes open-visual subject query,
but does not yet declare a source capability for truthful freshness ordering.

A source must not become freshness-eligible merely because it happens to emit
a timestamp.

Exact prerequisite seam:
`EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`

Permanent:
`TIMESTAMP_METADATA != FRESHNESS_CAPABILITY`
`FRESHNESS_CAPABILITY != INFERRED_FROM_PROVIDER`
`EMPTY/MISSING_TIMESTAMP != LICENSE_TO_REORDER`

This prerequisite should be resolved before productive freshness reachability.

## 7. Refined residual decomposition
The selected parent residual decomposes into:

1. `EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`
2. `GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`
3. `WIKIMEDIA_COMMONS_NEWEST_FIRST_SEARCH_PROJECTION`
4. `EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`

The order above is governance/dependency order, not necessarily four separate
productive modules. Reconciliation must prefer deepening existing models and
authorities.

No separate presentation-ordering residual is demonstrated.

## 8. Natural-language boundary
The already-certified visual language must remain the base admission boundary.
A later contract may add a bounded freshness modifier to an otherwise valid
visual request.

This PRE-RED does not authorize broad generic temporal NLP.

Examples to contract later only after representation/capability prerequisites:
- `Roby, mostrame las últimas fotos de Saturno.`
- `Roby, mostrame las imágenes más recientes de Saturno.`

The exact accepted Spanish forms require CONTRACT DESIGN before RED.

## 9. Fail-closed requirements
Future contracts must prove:
- freshness request with no freshness-capable source -> UNAVAILABLE, not
  relevance fallback;
- no inferred capability from `published_at`;
- provider unable to honor requested order -> fail closed;
- no UI-side sorting;
- no generic executor-side provider-semantic sorting;
- ordinary non-fresh visual requests preserve current behavior;
- known-topic NASA behavior remains unchanged unless separately contracted.

## 10. Classification
Parent:
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

No evidence supports a new authority.

## 11. PRE-RED conclusion
The parent residual remains demonstrated, but it is not a single safe GREEN
edit. The first prerequisite is source capability governance for freshness
ordering, followed by explicit order representation, provider projection, and
only then natural-language reachability.

Selected next seam:
`EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`

The next legal step is:
`EXTERNAL IMAGE FRESHNESS ORDER SOURCE CAPABILITY DECLARATION — CONTRACT DESIGN RECONCILIATION`

No CONTRACT RED is authorized before that design reconciliation.

## 12. Formal state
`EXTERNAL_IMAGE_FRESHNESS_ORDERING_PRE_RED: COMPLETE / PENDING OWNER CERTIFICATION`
`OWNER_BASELINE: 13,575 PASS / 0 FAIL`
`RELATED_CONTRACTS: 60 PASS / 0 FAIL`
`PARENT_RESIDUAL: EXTERNAL_IMAGE_FRESHNESS_ORDERING`
`FRESHNESS_PRIMARY_SEMANTIC: NEWEST_FIRST_ORDER`
`IMPLICIT_FIXED_TIME_WINDOW: REJECTED`
`EXISTING_DATE_BOUNDS: REUSE / NOT DUPLICATED`
`EXECUTOR_SIDE_GENERIC_SORT: REJECTED`
`PRESENTATION_SIDE_SORT: REJECTED`
`TIMESTAMP_METADATA_IS_CAPABILITY: FALSE`
`EXACT_PREREQUISITE: EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ZERO`
`NEW_AUTHORITY: NONE`
`CONTRACT_RED_AUTHORIZATION: NO`
`NEXT: EXTERNAL IMAGE FRESHNESS ORDER SOURCE CAPABILITY DECLARATION — CONTRACT DESIGN RECONCILIATION`
