# ROBY XI.2 — Governed Contextual Memory Neural Reranking — Contract RED

## 1. Certified entry state

Owner-certified input: `GOVERNED CONTEXTUAL MEMORY NEURAL RERANKING — CONTRACT
DESIGN`, Ruff CLEAN and full suite 13,617 PASS / 0 FAIL.

This block adds contractual tests only. Productive Python remains unchanged. No
neural model, provider, embedding generation, vector store or external private
content transmission is introduced.

## 2. RED seam

The missing seam is optional advisory orchestration at
`core.cognitive_memory_recall:CognitiveMemoryRecall`.

The RED freezes a minimal representation named:

- `MemoryNeuralRerankEvidence`;
- `MemoryNeuralRerankResponse`;
- dependency injection through `neural_reranker`.

These names represent bounded contract data and an injected collaborator. They do
not create a new Memory authority.

## 3. Contractual behavior under RED

The new contract requires:

1. valid advisory evidence can reorder already-eligible candidates;
2. absent, abstaining or failing specialist preserves deterministic ordering;
3. neural evidence cannot admit a memory below `minimum_score`;
4. partial coverage preserves uncovered eligible candidates;
5. unknown or invalid evidence fails closed;
6. existing `limit` and deterministic tie-break behavior remain authoritative;
7. the productive source contains no neural manager, vector store, background
   indexing, provider lookup, direct Memory/Learning write or network client.

The fake specialist is deterministic and local to the tests. It is not a real
neural implementation.

## 4. Observed RED

Focused execution of the new contract produced:

`8 FAILED / 1 PASSED`

Seven failures demonstrate that `CognitiveMemoryRecall` does not yet accept the
`neural_reranker` dependency. One failure demonstrates that the frozen advisory
evidence representation does not yet exist. The architecture guard passes.

This is the intended contractual RED: the governed seam is absent while the
forbidden parallel architecture is also absent.

## 5. Preserved boundaries

`CANONICAL_MEMORY_AUTHORITY: memory_gateway`

`NEURAL_ROLE: OPTIONAL_ADVISORY_RERANKER`

`DETERMINISTIC_ELIGIBILITY_BEFORE_NEURAL_RERANK: REQUIRED`

`NEURAL_ADMISSION_ACROSS_MINIMUM_SCORE: FORBIDDEN`

`ARBITRARY_WEIGHTED_SCORE_BLEND: NOT_SELECTED`

`DETERMINISTIC_FALLBACK: REQUIRED`

`EXTERNAL_PRIVATE_CONTENT_TRANSMISSION: NOT_AUTHORIZED`

`REAL_NEURAL_PROVIDER_REQUIRED: NO`

`EMBEDDING_PERSISTENCE: FORBIDDEN`

`VECTOR_STORE: FORBIDDEN`

`BACKGROUND_INDEXING: FORBIDDEN`

`NEW_AUTHORITY: NONE`

## 6. Change accounting

`PRODUCTIVE_PYTHON_DELTA: ZERO`

`NEW_CONTRACT_TEST_FILE: 1`

`FOCUSED_RED: 8 FAILED / 1 PASSED`

`NEXT_AFTER_OWNER_RED_CERTIFICATION:`
`GOVERNED CONTEXTUAL MEMORY NEURAL RERANKING — SURGICAL GREEN`

`STOP_BEFORE_PRODUCTIVE_GREEN: YES`
