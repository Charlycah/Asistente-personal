# ROBY XI.2 — Governed Contextual Memory Neural Reranking — PRE-RED Reconciliation

## 1. Entry state

Owner-certified input: `GOVERNED NEURAL ASSISTIVE INTEGRATION — EXISTING
AUTHORITY & USE-CASE INVENTORY`, Ruff CLEAN and full suite 13,617 PASS / 0 FAIL.

This block is reconciliation only. It does not authorize CONTRACT RED, a neural
provider, embeddings, vector storage, persistence, or productive code changes.

## 2. Canonical authority and productive reachability

CAP-02 remains `CLOSED / PERSISTENT / GOVERNED` and its authority remains
`memory_gateway`. `core.cognitive_memory_recall:CognitiveMemoryRecall` is the
existing productive cognitive-recall specialist used by cognitive integration and
memory runtime paths.

`app.contextual_memory_retrieval_foundation:ContextualMemoryRetrievalFoundation`
is a governed read-only policy foundation and an important semantic precedent, but
it is not currently the productive consumer of `CognitiveMemoryRecall` candidates.
It is directly composed by autobiographical continuity and has its own candidate
DTO. Therefore PRE-RED MUST NOT invent a bridge and MUST NOT claim that inserting
a reranker there would improve productive conversational recall.

## 3. Exact bounded insertion seam

The productive seam demonstrated in `CognitiveMemoryRecall.recall()` is:

1. normalize request and context;
2. collect candidates through the existing store;
3. apply session-profile filtering;
4. exclude inactive (`archived` / `superseded`) memories;
5. **bounded advisory neural relevance evidence may be requested here**;
6. existing recall authority performs final governed ranking/selection;
7. existing threshold, limit, touch/access and continuity behavior remain owned by
   `CognitiveMemoryRecall`.

The future specialist MUST NOT run before profile/status filtering and MUST NOT
collect memories independently.

## 4. Minimal advisory contract shape for CONTRACT RED

CONTRACT RED, if Owner-certified after this PRE-RED, may require a minimal
read-only advisory representation with these semantics:

- input identity: existing memory identifier only for already-eligible candidates;
- input content: only the query/context and candidate content strictly necessary
  for relevance inference;
- output: bounded relevance evidence in `[0.0, 1.0]` per supplied candidate;
- confidence: bounded confidence in `[0.0, 1.0]`;
- abstention: explicit and non-exceptional;
- provenance: specialist/provider/model identity or deterministic local-specialist
  descriptor without private memory content in logs;
- coverage: output may refer only to supplied candidate identifiers;
- mutation: forbidden;
- persistence: forbidden;
- prompt injection: forbidden;
- Learning admission: forbidden.

This PRE-RED does not freeze a class name or implementation module. CONTRACT RED
must prefer an existing extension/injection seam if one is demonstrated before
creating any new interface.

## 5. Combination and fallback semantics

Neural evidence is advisory. It MUST NOT replace the existing deterministic score
as an independent authority.

The contract must prove one bounded combination rule that preserves deterministic
behavior when neural evidence is absent. The exact weighting is deliberately NOT
selected in PRE-RED; hard-coding an arbitrary neural weight now would be design by
speculation.

Required fallback states are:

- specialist absent -> current deterministic ranking exactly;
- specialist unavailable/error -> current deterministic ranking exactly;
- specialist abstains -> current deterministic ranking exactly;
- incomplete advisory coverage -> uncovered candidates retain deterministic
  treatment;
- unknown candidate id from specialist -> ignored/fail-closed, never admitted;
- invalid/non-finite/out-of-range score -> ignored/fail-closed;
- ties -> existing deterministic tie-break semantics remain authoritative.

## 6. Privacy, provenance and observability

No embedding persistence, vector store, background indexing or durable neural
feature cache is selected. Raw private memory content MUST NOT be emitted into
observability/provenance records.

Observable evidence should be limited to safe metadata such as whether the
specialist was available, used or abstained; candidate counts; covered counts;
provider/model descriptor when policy permits; and reason/fallback codes.

A future provider that requires external transmission of private memory content is
NOT authorized by this PRE-RED. Provider/privacy policy must be resolved explicitly
before such a backend can become selectable.

## 7. Historical contract reconciliation

The historical statements that M36/M37 use no embeddings are valid descriptions of
their certified milestones and MUST NOT be silently rewritten as if embeddings had
always existed. They do not prohibit a later, separately governed advisory seam,
provided that M36 storage and Memory write authority remain unchanged.

Historical prohibitions on semantic/embedding matching in unrelated identity,
epistemic selection, image, document, or capability-resolution contracts remain
fully binding in those scopes. This PRE-RED authorizes no global semantic matching.

The M366.7 read-only invariants are preserved as normative precedent: archived and
superseded memories remain excluded, conflicts remain review-governed, persistence
is not added, and automatic prompt injection/runtime mutation remain forbidden.

## 8. Measurable value requirement

A CONTRACT RED must demonstrate value on cases where lexical/contextual scoring is
insufficient but the correct memory is already inside the governed candidate set.
It must also prove no regression on exact lexical matches, profile isolation,
archived/superseded exclusion, threshold/limit behavior and deterministic fallback.

A model/provider benchmark alone is insufficient. The contract target is the
governed behavioral seam, not a particular neural technology.

## 9. PRE-RED decision

`PRE_RED_RECONCILIATION: COMPLETE`

`CANONICAL_MEMORY_AUTHORITY: memory_gateway`

`PRODUCTIVE_CONSUMER_BOUNDARY: CognitiveMemoryRecall`

`INSERTION_SEAM: AFTER_PROFILE_AND_INACTIVE_FILTER_BEFORE_FINAL_RANKING`

`CONTEXTUAL_RETRIEVAL_FOUNDATION_ROLE: READ_ONLY_NORMATIVE_PRECEDENT`

`NEURAL_ROLE: ADVISORY_ONLY`

`EMBEDDING_PERSISTENCE: FORBIDDEN`

`VECTOR_STORE: FORBIDDEN`

`BACKGROUND_INDEXING: FORBIDDEN`

`DIRECT_MEMORY_OR_LEARNING_WRITE: FORBIDDEN`

`AUTOMATIC_PROMPT_INJECTION: FORBIDDEN`

`DETERMINISTIC_FALLBACK: REQUIRED`

`EXTERNAL_PRIVATE_CONTENT_TRANSMISSION: NOT_AUTHORIZED`

`PRODUCTIVE_PYTHON_DELTA: ZERO`

`TEST_DELTA: ZERO`

`NEW_AUTHORITY: NONE`

`NEXT_ACTION_AFTER_OWNER_CERTIFICATION:`
`GOVERNED CONTEXTUAL MEMORY NEURAL RERANKING — CONTRACT DESIGN`

`CONTRACT_RED_AUTHORIZATION: NONE`

`PRODUCTIVE_GREEN_AUTHORIZATION: NONE`

`STOP_BEFORE_CONTRACT_DESIGN_OR_RED: YES`
