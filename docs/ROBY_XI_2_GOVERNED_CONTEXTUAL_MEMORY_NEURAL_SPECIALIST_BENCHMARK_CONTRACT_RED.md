# GOVERNED CONTEXTUAL MEMORY NEURAL SPECIALIST — BENCHMARK CONTRACT RED

## Certified input

Owner-certified contextual-memory neural reranking POST-GREEN baseline:
13,626 PASS / 0 FAIL and Ruff CLEAN.

## Purpose

Materialize the benchmark design as RED architecture contracts before any
real neural model, provider, runtime, network access, embedding framework,
or vector persistence is introduced.

The benchmark is subordinate to CAP-02 / `memory_gateway`. It evaluates
reranking only inside candidate membership already admitted by
`CognitiveMemoryRecall`.

## Frozen benchmark contract

The future benchmark authority must expose a synthetic, versionable,
non-private corpus covering at least:

- semantic paraphrase / weak lexical overlap;
- lexical-exact preservation;
- hard distractor;
- multiple relevant candidates;
- Spanish morphology / paraphrase;
- deterministic tie stability.

It must compare the deterministic baseline and advisory reranked order over
identical candidate membership. Primary quality evidence is MRR; secondary
quality evidence is NDCG. Latency evidence records p50, p95, and maximum on
the Owner hardware without inventing a universal millisecond budget.

`GO` is impossible if any governance invariant regresses, candidate
membership changes, or lexical-exact behavior regresses. Semantic quality
must improve rather than merely remain equal.

## RED boundary

The tests intentionally reference the missing bounded module:
`core.cognitive_memory_neural_benchmark`.

The RED must fail because this benchmark contract is absent. It must not fail
because Torch, Sentence Transformers, ONNX Runtime, a model checkpoint, a
provider, or network access is unavailable.

`REAL_NEURAL_MODEL: NONE`
`MODEL_PROVIDER: UNSELECTED`
`NETWORK_ACCESS: FORBIDDEN`
`PRIVATE_CORPUS: FORBIDDEN`
`CANDIDATE_MEMBERSHIP_MUTATION: FORBIDDEN`
`VECTOR_STORE: FORBIDDEN`
`EMBEDDING_PERSISTENCE: FORBIDDEN`
`NEW_MEMORY_AUTHORITY: NONE`

`BENCHMARK_CONTRACT_RED: COMPLETE / PENDING OWNER CERTIFICATION`
`STOP_BEFORE_BENCHMARK_GREEN_OR_REAL_MODEL: YES`
