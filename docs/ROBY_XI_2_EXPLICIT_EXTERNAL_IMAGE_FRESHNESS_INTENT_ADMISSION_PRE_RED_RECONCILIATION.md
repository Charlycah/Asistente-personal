# ROBY XI.2 — Explicit External Image Freshness Intent Admission
## PRE-RED RECONCILIATION

### Owner-certified starting state
Input is the Owner-certified:
`WIKIMEDIA COMMONS NEWEST-FIRST SEARCH PROJECTION — POST-GREEN MASTER PLAN RECONCILIATION`.

Owner certification supplied after that reconciliation:
- Ruff clean;
- full suite: 13,602 PASS / 0 FAIL;
- productive Wikimedia GREEN remains closed;
- no internal residual remains in the Wikimedia newest-first projection block.

This PRE-RED is reconciliation only. No productive Python or test change is
authorized or made.

## 1. Parent and exact residual
Parent:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

Current residual:
`EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`

All prerequisites are already closed:
1. `EXTERNAL_IMAGE_FRESHNESS_ORDER_SOURCE_CAPABILITY_DECLARATION`;
2. `GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`;
3. `WIKIMEDIA_COMMONS_NEWEST_FIRST_SEARCH_PROJECTION`.

Therefore this block must not reopen capability declaration, governed order
representation, provider projection, selection, execution, or presentation.

## 2. Existing canonical authority chain
The current chain already contains every required downstream semantic:

1. `AppliedConversationalIntelligence.interpret()` owns bounded explicit
   conversational admission and request construction.
2. `GovernedConversationalSourceSelectionRequest` already carries
   `order: GovernedSourceQueryOrder | None`.
3. `GovernedConversationalSourceSelector` projects `request.order` unchanged
   into `GovernedSourceQuery` and capability-gates `NEWEST_FIRST`.
4. `GovernedSourceQueryContract` rejects `NEWEST_FIRST` for a source lacking
   `EXTERNAL_IMAGE_NEWEST_FIRST_QUERY`.
5. The existing executor preserves provider/raw order.
6. `WikimediaCommonsGovernedSourceAdapter` already projects only
   `NEWEST_FIRST` as `gsrsort=create_timestamp_desc`.
7. Presentation remains passive and is not an ordering authority.

No new router, parser, intent manager, freshness manager, selector, executor,
provider, planner, agent, loop, or authority is justified.

## 3. Demonstrated current gap
Current ACI visual admission recognizes bounded forms such as:
`Roby, mostrame fotos de Saturno.`

and constructs an open-visual request with:
- `query_text=Saturno`;
- `mode=OPEN_VISUAL_SUBJECT`;
- `order=None`.

Current probes demonstrate that explicit freshness forms remain
`NOT_RECOGNIZED`, including:
- `Roby, mostrame las últimas fotos de Saturno.`;
- `Roby, mostrame las imágenes más recientes de Saturno.`.

Thus the missing seam is not downstream order representation. It is the
existing ACI authority failing to admit a bounded freshness modifier on an
otherwise valid external-image request and failing to project that explicit
intent as:
`order=GovernedSourceQueryOrder.NEWEST_FIRST`.

Exact seam:
`EXPLICIT_FRESHNESS_LANGUAGE_TO_EXISTING_GOVERNED_NEWEST_FIRST_ORDER`

## 4. Semantic boundary
The parent PRE-RED already established:
`FRESHNESS_PRIMARY_SEMANTIC: NEWEST_FIRST_ORDER`
`LATEST_INTENT != ARBITRARY_DATE_WINDOW`
`TIME_FILTER != RESULT_ORDER`

Those decisions remain binding.

Therefore explicit latest/newest image language must not manufacture
`published_after` or `published_before`, and must not invent a fixed 7/30/365
day freshness window.

The existing date-bound fields remain orthogonal and unchanged.

## 5. Admission ownership
The future behavior belongs inside the existing
`AppliedConversationalIntelligence` admission/request-construction authority.

ACI may recognize only an explicitly contracted freshness modifier attached
to an otherwise valid visual request. It may then construct the existing
request representation with `order=NEWEST_FIRST`.

ACI must not:
- select Wikimedia or any provider;
- infer capability from timestamps;
- execute a query;
- sort results;
- change provider parameters directly;
- bypass selector/query-contract capability gates.

Permanent:
`LANGUAGE_ADMISSION != SOURCE_SELECTION`
`LANGUAGE_ADMISSION != PROVIDER_PROJECTION`
`LANGUAGE_ADMISSION != RESULT_SORTING`

## 6. Existing visual admission compatibility
Ordinary visual requests must preserve current behavior:
`mostrame fotos de Saturno` -> existing visual admission with `order=None`.

Known-topic visual behavior must also remain compatible. Freshness language
may add the governed order requirement, but must not silently migrate source
authority, topic authority, request mode, region semantics, or query subject.

The already-certified bounded open-visual subject extraction must be reused or
surgically extended inside ACI; a second extractor/parser authority is not
authorized.

## 7. Fail-closed requirements
Future Contract Design/RED must preserve these boundaries:
- freshness wording without a meaningful visual subject must not become a
  wildcard external search;
- freshness wording without an otherwise valid visual request must not become
  generic temporal NLP;
- `NEWEST_FIRST` with no registered capable source must remain `UNAVAILABLE`;
- no relevance/default fallback may silently satisfy explicit newest-first
  intent;
- no provider may become eligible merely because it exposes timestamp
  metadata;
- no executor-side or presentation-side chronological sort is allowed;
- ordinary non-fresh visual requests remain unchanged.

## 8. Contract-design prerequisite
PRE-RED proves the authority and semantic target, but it does not yet freeze
the exact Spanish lexical/grammatical contract.

Contract Design must define the smallest bounded accepted forms and subject
extraction behavior. At minimum it must adjudicate the already-demonstrated
examples:
- `mostrame las últimas fotos de Saturno`;
- `mostrame las imágenes más recientes de Saturno`.

It must also define negative/compatibility cases before RED, including
subjectless freshness language and ordinary visual language without freshness.

Broad generic words such as `último`, `reciente`, `nuevo`, `latest`, or
`newest` must not be admitted globally merely because they occur in text.

Therefore Contract RED is not authorized directly from this PRE-RED.

## 9. Classification
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

Reason:
- existing conversational authority;
- existing request field;
- existing governed order enum;
- existing capability gates;
- existing provider projection;
- no new authority required.

## 10. Explicit exclusions
This block must not change:
- `app/governed_source_query.py`;
- `app/governed_conversational_source_selection.py`;
- `app/governed_source_query_executor.py`;
- `app/wikimedia_commons_governed_source.py`;
- source capability declarations;
- selector ranking;
- provider registration/runtime composition;
- presentation;
- NASA semantics;
- Memory, Learning, Planning, Authorization, Execution, or Reasoning
  authorities.

No productive Python or test change is made in PRE-RED.

## 11. PRE-RED conclusion
The residual is demonstrated and narrowly located inside the existing ACI
admission/request-construction authority. All downstream newest-first
semantics are already represented, capability-gated, executable, and projected
by the existing canonical chain.

The next legal step is:
`EXPLICIT EXTERNAL IMAGE FRESHNESS INTENT ADMISSION — CONTRACT DESIGN RECONCILIATION`

STOP before Contract Design implementation/RED.

## 12. Formal state
`PRE_RED_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`PARENT_RESIDUAL: EXTERNAL_IMAGE_FRESHNESS_ORDERING`
`CURRENT_RESIDUAL: EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`CANONICAL_ADMISSION_AUTHORITY: APPLIED_CONVERSATIONAL_INTELLIGENCE`
`EXACT_MISSING_SEAM: EXPLICIT_FRESHNESS_LANGUAGE_TO_EXISTING_GOVERNED_NEWEST_FIRST_ORDER`
`GOVERNED_ORDER_REPRESENTATION: REUSE / CLOSED`
`SOURCE_CAPABILITY_GATE: REUSE / CLOSED`
`WIKIMEDIA_PROVIDER_PROJECTION: REUSE / CLOSED`
`IMPLICIT_FIXED_TIME_WINDOW: REJECTED`
`GENERIC_TEMPORAL_NLP: NOT_AUTHORIZED`
`NEW_AUTHORITY: NONE`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ZERO`
`CONTRACT_RED_AUTHORIZATION: NO`
`NEXT_AFTER_OWNER_CERTIFICATION: CONTRACT DESIGN RECONCILIATION`
`STOP_BEFORE_CONTRACT_DESIGN: YES`
