# ROBY XI.2 — GOVERNED CONTEXTUAL MEMORY NEURAL SPECIALIST — BENCHMARK CONTRACT DESIGN

Status: RECONCILED / DOCUMENTED POST-FACTO

## Purpose

Freeze measurable admission criteria before any real neural model/provider is
selected or integrated. The benchmark measures delta over the existing
deterministic order and never changes candidate admission.

## Frozen benchmark design

- BENCHMARK_DATA: SYNTHETIC_NON_PRIVATE
- LANGUAGE_FOCUS: SPANISH
- CANDIDATE_MEMBERSHIP: DETERMINISTIC_ELIGIBLE_ONLY
- NEURAL_ADMISSION: FORBIDDEN
- BASELINE: EXISTING_DETERMINISTIC_ORDER
- PRIMARY_QUALITY_METRIC: MRR
- SECONDARY_QUALITY_METRIC: NDCG
- LEXICAL_EXACT_REGRESSION: ZERO
- GOVERNANCE_INVARIANTS: 100_PERCENT
- SEMANTIC_DELTA_MRR: POSITIVE_REQUIRED
- SEMANTIC_DELTA_NDCG: POSITIVE_REQUIRED
- SEMANTIC_CASE_IMPROVEMENT: STRICT_MAJORITY_REQUIRED
- LATENCY_METRICS: P50_P95_MAX
- UNIVERSAL_LATENCY_THRESHOLD: NONE
- NETWORK: FORBIDDEN
- PRIVATE_DATA: FORBIDDEN
- PERSISTENCE: FORBIDDEN
- REAL_MODEL: NONE
- PROVIDER: NONE

Mandatory families are semantic paraphrase with weak lexical overlap,
lexical-exact preservation, hard distractor, multi-relevant, Spanish
morphology/paraphrase, and tie stability.

Any candidate-membership mutation, governance violation, lexical-exact
regression, non-positive aggregate MRR/NDCG delta, or failure to improve a strict
majority of semantic challenge cases yields NO-GO.

This document records the design that was subsequently materialized by the
Owner-certified BENCHMARK CONTRACT RED and BENCHMARK SURGICAL GREEN.
