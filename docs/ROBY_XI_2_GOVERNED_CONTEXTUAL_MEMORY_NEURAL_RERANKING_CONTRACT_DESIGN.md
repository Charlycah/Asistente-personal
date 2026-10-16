# ROBY XI.2 — Governed Contextual Memory Neural Reranking — Contract Design

## 1. Entry state

Owner-certified input: `GOVERNED CONTEXTUAL MEMORY NEURAL RERANKING — PRE-RED
RECONCILIATION`, Ruff CLEAN and full suite 13,617 PASS / 0 FAIL.

This block freezes contract semantics only. It does not authorize CONTRACT RED,
productive code, a neural model/provider, embeddings, vector storage, indexing,
or external transmission of private memory content.

## 2. Existing authority and consumer

CAP-02 remains owned by `memory_gateway`. The productive consumer boundary is
`core.cognitive_memory_recall:CognitiveMemoryRecall`.

The future neural component is a bounded advisory specialist. It is not a Memory
authority, selector, store, retriever, Learning authority, prompt builder, agent,
manager or second brain.

`ContextualMemoryRetrievalFoundation` remains a read-only normative precedent. It
is not inserted into the productive recall path by this design.

## 3. Refined insertion contract

PRE-RED located the bounded region after profile/status filtering and before final
selection. Contract Design refines that region to prevent neural admission of a
memory that deterministic recall would reject.

Required future flow:

1. collect candidates through the existing Memory path;
2. apply existing session-profile filtering;
3. exclude archived/superseded memories;
4. compute the existing deterministic score for every active candidate;
5. form deterministic eligibility using the existing `minimum_score`;
6. optionally request neural relevance evidence only for eligible candidates;
7. validate the advisory response fail-closed;
8. reorder only the eligible set when valid advisory evidence exists;
9. preserve deterministic score as fallback and authoritative tie-break evidence;
10. apply the existing `limit` and existing touch/continuity behavior.

Therefore neural evidence cannot promote a deterministically ineligible memory
across `minimum_score`.

## 4. Minimal request contract

A future advisory request may contain only data required for bounded relevance:

- normalized current recall query/context;
- stable identity of each already-eligible memory candidate;
- candidate text/content strictly required for inference;
- no Memory write handle;
- no store/gateway handle;
- no Learning handle;
- no prompt/runtime mutation handle.

The request MUST NOT authorize candidate discovery. The specialist receives a
closed candidate set and cannot add to it.

No durable embedding or neural feature representation is part of this contract.

## 5. Minimal response contract

For each covered supplied candidate, advisory evidence consists of:

- the supplied candidate identity;
- relevance in finite `[0.0, 1.0]`;
- confidence in finite `[0.0, 1.0]`;
- safe provenance descriptor that contains no private memory text.

The response also supports explicit abstention. Abstention is normal behavior, not
an exception.

Unknown IDs, duplicate IDs with contradictory evidence, non-finite values,
out-of-range values, malformed provenance or structurally invalid output MUST NOT
admit or mutate anything. Invalid evidence is ignored/fail-closed and deterministic
behavior remains available.

## 6. Influence rule: rerank, never admit

Contract Design deliberately rejects an arbitrary weighted blend such as
`deterministic + neural_weight * relevance`.

The neural specialist may influence only relative order inside the deterministic
eligible set. It cannot:

- change `minimum_score`;
- make an ineligible memory eligible;
- alter the stored memory confidence;
- alter matched deterministic signals;
- change profile/status/conflict eligibility;
- create or remove memories;
- choose a larger result limit.

When valid advisory evidence covers two or more eligible candidates, ordering may
prefer higher neural relevance, then higher neural confidence. Existing
deterministic ranking fields remain authoritative tie-break evidence.

Uncovered candidates retain deterministic treatment. CONTRACT RED must freeze a
stable mixed-coverage ordering rule before productive implementation; it must not
invent a provider-specific weighting scheme.

## 7. Fallback and failure contract

The exact current deterministic result ordering MUST be preserved when:

- no specialist is configured;
- the specialist is unavailable;
- the specialist raises an error;
- the specialist abstains;
- no valid advisory evidence remains after validation.

Partial valid coverage MUST NOT discard uncovered candidates. Invalid or unknown
advisory entries MUST NOT enlarge the candidate set.

The future integration must be optional and dependency-injected at the existing
`CognitiveMemoryRecall` consumer boundary or an equally narrow demonstrated seam.
A global singleton, manager, background loop or hidden provider lookup is forbidden.

## 8. Privacy and provenance contract

`EXTERNAL_PRIVATE_CONTENT_TRANSMISSION` remains `NOT_AUTHORIZED`.

CONTRACT RED may use a deterministic fake/stub advisory specialist to prove the
orchestration contract. It MUST NOT require a real external neural provider.

Safe observability may expose only metadata such as configured/used/abstained,
candidate and coverage counts, fallback reason, and non-sensitive specialist/model
descriptor. Raw private memory text, embeddings and neural feature vectors MUST NOT
be logged as provenance.

## 9. Historical-contract semantics

M36/M37 remain historically correct: those certified milestones introduced no
embeddings, vector DB or LLM dependency. A later optional advisory seam does not
rewrite their historical scope and does not alter M36 storage authority.

Unrelated prohibitions on semantic matching or embeddings in identity, epistemic,
capability, image and document contracts remain binding in their own scopes.

M366.7 remains precedent for read-only selection, inactive-memory exclusion,
review-governed conflicts, no automatic persistence and no automatic prompt
injection.

## 10. CONTRACT RED behavioral matrix

A future CONTRACT RED is authorized only to specify the missing orchestration seam.
At minimum it must prove:

1. no specialist -> exact current deterministic ordering;
2. unavailable/error/abstention -> exact deterministic ordering;
3. neural evidence cannot admit a candidate below `minimum_score`;
4. neural evidence cannot resurrect archived/superseded/profile-filtered memory;
5. unknown candidate IDs cannot enter recall;
6. invalid/non-finite/out-of-range evidence fails closed;
7. valid evidence can reorder two already-eligible candidates;
8. deterministic tie-break behavior remains stable when advisory evidence ties;
9. partial coverage preserves uncovered eligible candidates;
10. existing `limit`, touch/access and continuity semantics remain intact;
11. no Memory/Learning write or prompt injection is introduced;
12. no external provider, vector store or embedding persistence is required.

The RED must fail because the optional advisory orchestration seam does not yet
exist, not because a real neural model is unavailable.

## 11. Implementation boundary after a future RED

A later surgical GREEN, if separately Owner-authorized, may add only the minimal
advisory representation/injection seam and governed orchestration needed to satisfy
the RED. It MUST NOT silently add a concrete neural provider.

Concrete local or remote model selection, embedding generation, model lifecycle,
performance benchmarking and provider/privacy authorization require a later
separately reconciled block after the governed seam exists and is certified.

This ordering prevents technology selection from creating architectural authority.

## 12. Contract Design decision

`CONTRACT_DESIGN: COMPLETE`

`CANONICAL_MEMORY_AUTHORITY: memory_gateway`

`PRODUCTIVE_CONSUMER_BOUNDARY: CognitiveMemoryRecall`

`NEURAL_ROLE: OPTIONAL_ADVISORY_RERANKER`

`DETERMINISTIC_ELIGIBILITY_BEFORE_NEURAL_RERANK: REQUIRED`

`NEURAL_ADMISSION_ACROSS_MINIMUM_SCORE: FORBIDDEN`

`NEURAL_INFLUENCE: RELATIVE_ORDER_WITHIN_ELIGIBLE_SET_ONLY`

`ARBITRARY_WEIGHTED_SCORE_BLEND: NOT_SELECTED`

`DETERMINISTIC_FALLBACK: REQUIRED`

`DEPENDENCY_INJECTION: REQUIRED`

`GLOBAL_NEURAL_MANAGER_OR_SINGLETON: FORBIDDEN`

`EMBEDDING_PERSISTENCE: FORBIDDEN`

`VECTOR_STORE: FORBIDDEN`

`BACKGROUND_INDEXING: FORBIDDEN`

`DIRECT_MEMORY_OR_LEARNING_WRITE: FORBIDDEN`

`AUTOMATIC_PROMPT_INJECTION: FORBIDDEN`

`EXTERNAL_PRIVATE_CONTENT_TRANSMISSION: NOT_AUTHORIZED`

`REAL_NEURAL_PROVIDER_REQUIRED_FOR_CONTRACT_RED: NO`

`PRODUCTIVE_PYTHON_DELTA: ZERO`

`TEST_DELTA: ZERO`

`NEW_AUTHORITY: NONE`

`NEXT_AFTER_OWNER_CERTIFICATION:`
`GOVERNED CONTEXTUAL MEMORY NEURAL RERANKING — CONTRACT RED`

`PRODUCTIVE_GREEN_AUTHORIZATION: NONE`

`STOP_BEFORE_CONTRACT_RED_OR_PRODUCTIVE_IMPLEMENTATION: YES`
