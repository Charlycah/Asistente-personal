# ROBY XI.2 — Governed Contextual Memory Neural Reranking — Surgical GREEN

## 1. Certified entry state

Owner-certified input: `GOVERNED CONTEXTUAL MEMORY NEURAL RERANKING — CONTRACT
RED`, Ruff CLEAN and full suite 13,618 PASS / 8 expected FAIL.

The eight RED failures were exactly the missing injected advisory seam and missing
contract representations. No unrelated historical failure was present.

## 2. Surgical productive change

Only `core/cognitive_memory_recall.py` changes productively.

`CognitiveMemoryRecall` now accepts an optional injected `neural_reranker`. The
new contract representations are:

- `MemoryNeuralRerankEvidence`;
- `MemoryNeuralRerankRequest`;
- `MemoryNeuralRerankResponse`;
- `MemoryNeuralReranker` protocol.

They are bounded advisory data/contracts. They do not create a Memory authority,
provider, manager, model, vector store or persistence path.

## 3. Preserved deterministic authority

The productive sequence is:

1. collect candidates through the existing Memory store;
2. apply existing profile and inactive-memory filtering;
3. compute the existing deterministic ranking;
4. apply the existing `minimum_score` eligibility boundary;
5. optionally rerank only that eligible tuple with advisory evidence;
6. apply the existing `limit`;
7. preserve existing touch and continuity behavior.

The neural collaborator therefore cannot admit a candidate across
`minimum_score`. Existing deterministic scores are unchanged and remain visible on
the selected items.

Absent dependency, specialist exception, explicit abstention, empty evidence,
unknown candidate identity, duplicate identity, invalid relevance/confidence or
unsafe empty evidence provenance all fail closed to the exact deterministic
eligible ordering.

Equal advisory evidence preserves the original deterministic order as the final
tie-break. Partial evidence never removes an eligible candidate.

## 4. Contract fixture reconciliation discovered during GREEN

The RED test named `neural_evidence_cannot_admit_below_threshold_memory` used
`minimum_score=0.75`. Once the constructor gap was closed, this exposed that both
fixture memories were actually deterministic-eligible:

- alpha score: `0.9525`;
- beta score: `0.9150`.

The test then required both exact baseline preservation and beta absence, which was
internally contradictory because beta was already in that baseline.

The fixture threshold is surgically corrected to `0.94`. This places alpha above
and beta below the real deterministic boundary while preserving the certified
contract semantics. No product behavior is distorted to satisfy the stale fixture
value.

## 5. Explicit non-goals preserved

`CANONICAL_MEMORY_AUTHORITY: memory_gateway`

`NEURAL_ROLE: OPTIONAL_ADVISORY_RERANKER`

`NEURAL_ADMISSION_ACROSS_MINIMUM_SCORE: FORBIDDEN`

`ARBITRARY_WEIGHTED_SCORE_BLEND: NOT_SELECTED`

`EMBEDDING_PERSISTENCE: FORBIDDEN`

`VECTOR_STORE: FORBIDDEN`

`BACKGROUND_INDEXING: FORBIDDEN`

`DIRECT_MEMORY_OR_LEARNING_WRITE: FORBIDDEN`

`AUTOMATIC_PROMPT_INJECTION: FORBIDDEN`

`EXTERNAL_PRIVATE_CONTENT_TRANSMISSION: NOT_AUTHORIZED`

`REAL_NEURAL_MODEL_OR_PROVIDER: NOT_INTRODUCED`

`NEW_AUTHORITY: NONE`

## 6. Local validation

Focused GREEN plus historical recall/continuity and M361 contracts:

`39 PASS / 0 FAIL`

M361 was regenerated after the productive change and reproduces cleanly.

Ruff is not installed in the execution environment, so no local Ruff claim is
made. A full suite attempt exceeded the environment execution limit before a
summary was produced; no full-suite local count is claimed.

Maximum line length in both changed Python files is 87 characters.

## 7. Certification boundary

`SURGICAL_GREEN: COMPLETE / PENDING OWNER CERTIFICATION`

`PRODUCTIVE_PYTHON_FILES_CHANGED: 1`

`CONTRACT_TEST_FILES_RECONCILED: 1`

`REAL_NEURAL_IMPLEMENTATION: NONE`

`STOP_BEFORE_POST_GREEN: YES`

Owner certification target: Ruff CLEAN and full suite 13,626 PASS / 0 FAIL.
