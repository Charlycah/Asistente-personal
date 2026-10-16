# ROBY XI.2 — General Open Visual Natural Language Admission
## PRE-RED Reconciliation

### Owner-certified starting state
Input is the Owner-certified Wikimedia registration/reachability Post-GREEN:
- 13,562 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated / reproducible;
- Wikimedia runtime configuration/registration closed;
- Wikimedia open-visual selection/execution reachability closed.

This PRE-RED changes documentation only.

### Governance classification
Candidate classification:
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

No new conversational router, selector, executor, source registry, gateway,
presenter, manager, planner, agent, loop, or authority is justified.

Canonical admission logic already exists in
`app.applied_conversational_intelligence.py`.

### Current admission behavior
`AppliedConversationalIntelligence.interpret()` currently:
1. normalizes the text;
2. derives known `InterestTopic` values from `_TOPIC_TERMS`;
3. detects explicit query vocabulary;
4. detects explicit visual language using `mostrame` plus a visual noun;
5. rejects when `not topics` OR when neither explicit nor visual language is
   present;
6. otherwise constructs a topic-constrained
   `GovernedConversationalSourceSelectionRequest`.

Therefore an explicit request such as:
`Roby, mostrame fotos de Saturno.`
is visually explicit but is rejected solely because Saturn is not represented
by the finite `InterestTopic` vocabulary.

The same applies to arbitrary subjects such as:
`Roby, mostrame imágenes de las pistas de Nazca.`

This is the demonstrated admission gap.

### Existing reusable open-visual representation
The already-certified request model supports:
- `GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT`;
- empty `topics`;
- mandatory non-empty `query_text`.

The already-certified selector treats this mode specially and requires
`InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY` on a registered,
declared source.

Thus:
`EMPTY_TOPICS_IN_OPEN_VISUAL_MODE != WILDCARD`

and:
`QUERY_TEXT != SOURCE_ELIGIBILITY_AUTHORITY`.

Wikimedia Commons is now a configured capable source through the existing
executor/contract/selector path.

### Exact missing seam
The missing seam is not request representation, source capability, provider
availability, registration, selection, execution, or presentation.

It is:

`EXPLICIT_GENERAL_VISUAL_LANGUAGE_TO_OPEN_VISUAL_REQUEST_ADMISSION`

Specifically, the existing ACI admission authority does not branch explicit
visual requests with no known topic into the already-certified
`OPEN_VISUAL_SUBJECT` request mode.

### Smallest legal future behavior
A future Contract Design should specify an internal branch inside the existing
`AppliedConversationalIntelligence.interpret()` authority:

- recognized known-topic behavior remains unchanged;
- an explicit visual request with a meaningful subject but no known topic may
  produce an `OPEN_VISUAL_SUBJECT` request;
- that request uses `topics=frozenset()`;
- `query_text` carries the extracted/normalized arbitrary visual subject;
- region remains compatible with general/global source selection;
- limit/timeout continue through existing request defaults/contracts;
- source eligibility remains entirely with the existing selector/capability
  checks;
- absence of a capable registered source remains typed `UNAVAILABLE`.

No source id may be chosen in ACI.

### Critical subject-extraction prerequisite
Current `_query_text()` is topic-oriented. For unknown subjects it falls back
to the entire input text.

That transport is technically non-empty, but PRE-RED does not establish that
sending the full conversational imperative (`Roby, mostrame fotos de ...`) is
the correct canonical search payload.

Therefore Contract Design must fix a bounded subject-extraction contract for
explicit open-visual language before Contract RED.

It should preserve the meaningful subject without inventing an
`InterestTopic`, and must fail closed when no meaningful subject exists.

Examples that must remain distinguishable:
- `mostrame fotos de Saturno` -> meaningful subject exists;
- `mostrame imágenes de las pistas de Nazca` -> meaningful subject exists;
- `mostrame fotos` -> no meaningful subject; must not become a general/wildcard
  external search.

This is extraction inside the existing ACI request-construction authority, not
a new NLP/router authority.

### Existing known-topic compatibility
The already-certified external-image natural-language behavior for James Webb
and NASA must remain compatible.

Contract Design must decide explicitly whether known-topic visual requests
remain `TOPIC_CONSTRAINED` (preserving current behavior) while only unknown
subjects use `OPEN_VISUAL_SUBJECT`, or whether a broader semantic migration is
actually necessary.

PRE-RED evidence does not justify migrating known-topic behavior.

Default surgical direction:
`KNOWN_TOPIC_VISUAL_BEHAVIOR: PRESERVE`

### Explicit exclusions
This block must not:
- alter Wikimedia adapter behavior;
- alter runtime environment wiring;
- alter official runtime composition;
- alter source declarations/capabilities;
- alter selector ranking;
- alter executor/query contract;
- alter OfficialConversationGateway authority;
- alter visual presentation;
- implement freshness/latest/newest ordering;
- create background/autonomous fetch;
- turn empty topics into wildcard eligibility;
- invent new `InterestTopic` values for arbitrary subjects.

### Residual decomposition
Parent:
`GENERAL_OPEN_VISUAL_NATURAL_LANGUAGE_ADMISSION`

Refined seams:
1. `EXPLICIT_GENERAL_VISUAL_LANGUAGE_TO_OPEN_VISUAL_REQUEST_ADMISSION`
2. `BOUNDED_OPEN_VISUAL_SUBJECT_EXTRACTION`

These belong to one existing ACI admission/request-construction authority and
should be designed together before RED.

Separate/later:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

### PRE-RED evidence
Assistant baseline probes:
- arbitrary explicit visual subjects are currently `NOT_RECOGNIZED`;
- subjectless `mostrame fotos` is also `NOT_RECOGNIZED`;
- existing external-image NL + Wikimedia registration/reachability contracts
  remain green.

No productive Python or tests are changed.

### Next authorization
The next authorized block is:
`GENERAL OPEN VISUAL NATURAL LANGUAGE ADMISSION — CONTRACT DESIGN RECONCILIATION`

Contract RED is not authorized yet because the exact subject-extraction and
known-topic compatibility contracts must first be fixed.

### Formal state
`PRE_RED_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ZERO`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`CANONICAL_ADMISSION_AUTHORITY: APPLIED_CONVERSATIONAL_INTELLIGENCE`
`OPEN_VISUAL_REQUEST_REPRESENTATION: REUSE / CLOSED`
`WIKIMEDIA_PROVIDER_PATH: REUSE / CLOSED`
`SELECTOR / EXECUTOR / QUERY_CONTRACT: REUSE / CLOSED`
`EXACT_MISSING_SEAM: EXPLICIT_GENERAL_VISUAL_LANGUAGE_TO_OPEN_VISUAL_REQUEST_ADMISSION`
`SUBJECT_EXTRACTION_PREREQUISITE: BOUNDED_OPEN_VISUAL_SUBJECT_EXTRACTION`
`KNOWN_TOPIC_VISUAL_BEHAVIOR: PRESERVE`
`FRESHNESS: OUT_OF_SCOPE / LATER`
`NEW_AUTHORITY: NONE`
`CONTRACT_RED_AUTHORIZATION: NO`
`NEXT: CONTRACT_DESIGN_RECONCILIATION`
