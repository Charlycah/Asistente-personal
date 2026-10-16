# ROBY XI.2 — Explicit External Image Freshness Intent Admission
## CONTRACT DESIGN RECONCILIATION

### Owner-certified starting state
Input is the Owner-certified:
`EXPLICIT EXTERNAL IMAGE FRESHNESS INTENT ADMISSION — PRE-RED RECONCILIATION`.

Owner certification supplied for that state:
- Ruff: CLEAN;
- full suite: 13,602 PASS / 0 FAIL;
- PRE-RED residual and authority boundary: CLOSED / OWNER-CERTIFIED.

This increment freezes contract design only. No productive Python or test change
is authorized or made.

## 1. Exact contract seam
Parent:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

Current residual:
`EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`

Exact seam:
`EXPLICIT_FRESHNESS_LANGUAGE_TO_EXISTING_GOVERNED_NEWEST_FIRST_ORDER`

Canonical owner:
`AppliedConversationalIntelligence.interpret()`.

The contract must deepen that existing authority only. It must not introduce a
freshness parser, manager, router, selector, provider authority, executor,
planner, agent, or loop.

## 2. Frozen primary semantic
Explicit user language requesting the latest/most-recent external images is an
ORDER intent, not a date-window intent.

Binding mapping:
`EXPLICIT_IMAGE_FRESHNESS_INTENT -> GovernedSourceQueryOrder.NEWEST_FIRST`

Permanent distinctions:
`LATEST_INTENT != ARBITRARY_DATE_WINDOW`
`TIME_FILTER != RESULT_ORDER`

The admission layer must not synthesize `published_after`, `published_before`,
or a 7/30/365-day window.

## 3. Minimal positive lexical contract
Contract RED shall require, at minimum, these bounded Spanish forms:

1. `Roby, mostrame las últimas fotos de Saturno.`
2. `Roby, mostrame las ultimas fotos de Saturno.`
3. `Roby, mostrame las imágenes más recientes de Saturno.`
4. `Roby, mostrame las imagenes mas recientes de Saturno.`

The accepted freshness constructions are intentionally narrow:
- `las últimas|ultimas` immediately modifying a supported visual noun;
- `las <visual noun> más|mas recientes` as the equivalent bounded form.

Supported visual nouns remain the existing visual vocabulary:
`foto`, `fotos`, `imagen`, `imágenes`, `imagenes`.

This design does not globally admit isolated words such as `último`, `ultima`,
`reciente`, `nuevo`, `latest`, or `newest` wherever they occur in a sentence.
English freshness admission is not part of this residual.

## 4. Required request representation
For an admitted open-visual freshness request, Contract RED shall require:
- status: `RECOGNIZED`;
- existing mode: `OPEN_VISUAL_SUBJECT`;
- existing bounded subject extraction;
- existing `GLOBAL` region;
- existing limit behavior;
- `order=GovernedSourceQueryOrder.NEWEST_FIRST`;
- no `published_after`;
- no `published_before`.

Example:
`mostrame las últimas fotos de Saturno`
must preserve `query_text="Saturno"`; freshness words are control language and
must not contaminate the visual subject.

For known-topic visual requests, the existing topic authority remains binding.
Example:
`mostrame las últimas fotos de James Webb`
must remain `TOPIC_CONSTRAINED`, preserve the James Webb topic/query semantics,
and add only `order=NEWEST_FIRST`.

Freshness must not migrate request mode, topic ownership, region, subject, or
provider selection.

## 5. Subject extraction design
The existing `_open_visual_subject()` is the bounded subject extraction
mechanism for open visual requests. Contract RED may require its surgical
extension so the freshness modifier is consumed before the existing `de
<subject>` boundary.

A second extractor/parser authority is forbidden.

The subject contract remains:
- non-empty;
- contains meaningful alphanumeric content;
- trailing sentence punctuation may be removed;
- freshness control words are not part of `query_text`.

## 6. Negative and fail-closed contract
Contract RED shall include negatives proving that freshness wording does not
broaden ACI into generic temporal NLP.

At minimum:
- `Roby, mostrame las últimas fotos.` -> `NOT_RECOGNIZED`;
- `Roby, mostrame las imágenes más recientes.` -> `NOT_RECOGNIZED`;
- punctuation-only subject remains `NOT_RECOGNIZED`;
- non-visual freshness language remains outside this contract;
- ordinary `Roby, mostrame fotos de Saturno.` remains recognized with
  `order=None`;
- unsupported/global occurrences of `último`, `reciente`, `nuevo`, `latest`,
  or `newest` do not independently trigger `NEWEST_FIRST`.

No wildcard query may be manufactured from a subjectless freshness request.

## 7. Downstream capability behavior to reuse
No downstream contract is redesigned.

The existing selector already requires
`EXTERNAL_IMAGE_NEWEST_FIRST_QUERY` when `request.order` is `NEWEST_FIRST`.
Therefore Contract RED shall verify reuse of that behavior:
- capable source may be selected by the existing selector;
- absence of a capable source remains `UNAVAILABLE`;
- no fallback to relevance/default ordering is allowed;
- ACI never names or selects Wikimedia.

Provider projection remains closed:
`NEWEST_FIRST -> Wikimedia gsrsort=create_timestamp_desc`.

## 8. Historical-contract semantic reconciliation required in RED
`test_general_open_visual_natural_language_admission_contract_red.py` contains
an older guard named `test_red_does_not_pull_freshness_into_admission` whose
source-text assertion forbids `"newest"` in ACI.

That assertion encoded the correct pre-residual boundary when freshness
admission was intentionally deferred. After this Contract Design, it conflicts
with the now-authorized reuse of `GovernedSourceQueryOrder.NEWEST_FIRST` inside
the canonical ACI request-construction authority.

Contract RED must reconcile that historical assertion surgically rather than:
- preserving it through aliases or indirection;
- deleting unrelated anti-sorting/date-window guards;
- weakening the prohibition on executor/presentation sorting;
- changing downstream authorities.

The semantic replacement must distinguish:
`ACI MAY REPRESENT EXPLICIT ORDER INTENT`
from
`ACI MUST NOT SORT, DATE-FILTER, SELECT A PROVIDER, OR EXECUTE`.

## 9. RED scope frozen
The next RED is authorized to change tests/documentation only.

Expected RED coverage:
1. positive accented latest-photo admission;
2. positive unaccented normalization-compatible form;
3. positive `más recientes` form;
4. exact `query_text` without freshness contamination;
5. `order is NEWEST_FIRST`;
6. no implicit date bounds;
7. ordinary visual compatibility with `order=None`;
8. subjectless/punctuation-only fail-closed behavior;
9. known-topic compatibility;
10. downstream capable-source gate reuse;
11. no provider choice in ACI;
12. no parallel freshness authority;
13. historical freshness guard semantic reconciliation.

The RED must fail only because the existing ACI does not yet admit the frozen
freshness grammar/project `NEWEST_FIRST`, not because a new downstream
capability is demanded.

## 10. Explicit exclusions
Contract RED/GREEN must not redesign or create:
- `GovernedConversationalSourceSelectionRequest.order`;
- `GovernedSourceQueryOrder`;
- source capability declarations;
- selector ranking or capability gating;
- query executor ordering;
- Wikimedia provider projection;
- NASA semantics;
- presentation sorting;
- generic temporal NLP;
- Memory, Learning, Planning, Authorization, Execution, or Reasoning.

## 11. Contract Design conclusion
The lexical and semantic contract is sufficiently bounded for a surgical RED.
The future productive seam remains one existing authority: ACI recognizes the
contracted freshness modifier on an otherwise valid visual request and places
`NEWEST_FIRST` in the already-existing governed request field.

No productive implementation is authorized in this increment.

Next legal step after Owner certification:
`EXPLICIT EXTERNAL IMAGE FRESHNESS INTENT ADMISSION — RED CONTRACTUAL`

STOP before RED.

## 12. Formal state
`CONTRACT_DESIGN_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`PARENT_RESIDUAL: EXTERNAL_IMAGE_FRESHNESS_ORDERING`
`CURRENT_RESIDUAL: EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`CANONICAL_ADMISSION_AUTHORITY: APPLIED_CONVERSATIONAL_INTELLIGENCE`
`PRIMARY_SEMANTIC: NEWEST_FIRST_ORDER`
`BOUNDED_SPANISH_FRESHNESS_GRAMMAR: FROZEN`
`OPEN_VISUAL_SUBJECT_EXTRACTION: REUSE / SURGICAL_EXTENSION_ALLOWED`
`KNOWN_TOPIC_AUTHORITY: PRESERVE`
`IMPLICIT_FIXED_TIME_WINDOW: REJECTED`
`GENERIC_TEMPORAL_NLP: NOT_AUTHORIZED`
`ENGLISH_FRESHNESS_ADMISSION: OUT_OF_SCOPE`
`HISTORICAL_CONTRACT_RECONCILIATION_REQUIRED_IN_RED: YES`
`NEW_AUTHORITY: NONE`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ZERO`
`CONTRACT_RED_AUTHORIZATION: AFTER_OWNER_CERTIFICATION`
`NEXT_AFTER_OWNER_CERTIFICATION: RED CONTRACTUAL`
`STOP_BEFORE_RED: YES`
