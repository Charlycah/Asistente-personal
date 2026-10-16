# ADR-162 — M160 Long-Term Experience Evaluation

## Status

Accepted.

## Context

M159 establishes whether the governed companion path is operationally reliable for a specific cross-context conversational candidate. A reliable current path does not establish whether the companion has provided a consistently good experience over time.

ROBY needs a longitudinal, declarative evaluation boundary that can combine multiple explicit experience observations linked to historical M159 results. The boundary must distinguish sustained positive experience, mixed experience, negative experience, and insufficient evidence without silently learning from behavior or mutating memory, personality, policy, or knowledge.

This concern is distinct from M57 long-term collaboration, M85 episodic memory, M88 reflection, and M89 knowledge evolution. Those layers represent collaboration, retained episodes, reflective records, and governed knowledge proposals. M160 only evaluates explicit longitudinal experience evidence.

## Decision

Introduce `core.long_term_experience_evaluation` downstream from M159.

The milestone:

- consumes immutable M159 reliability results;
- accepts immutable experience observations explicitly linked by `reliability_id`;
- evaluates ownership, source confidence, horizon, sample count, observation span, exclusions, optional explicit feedback, and reference integrity;
- scores satisfaction, continuity quality, consent alignment, reliability quality, and declared outcome;
- calculates an auditable longitudinal score and negative-outcome ratio;
- produces `POSITIVE`, `MIXED`, `NEGATIVE`, `INSUFFICIENT`, `REVIEW_REQUIRED`, `BLOCKED`, or `NOT_APPLICABLE`;
- preserves exact representative M159 → M158 → M157 → M156 → M155 → M150 lineage;
- uses deterministic immutable identifiers and an append-only repository contract;
- remains declarative and side-effect free.

A positive result requires both a score at or above the positive threshold and a negative-outcome ratio no higher than the configured limit. Evidence below the minimum sample count or minimum temporal span is explicitly classified as insufficient rather than inferred.

## Boundaries

M160 does not:

- collect implicit behavioral telemetry;
- infer satisfaction from silence or continued use;
- create, append, or mutate episodic memory;
- learn preferences or habits;
- change personality, policy, thresholds, or routing;
- create knowledge evolution proposals;
- authorize conversations, scheduling, prompts, responses, providers, automation, or platform mutation;
- replace M57, M85, M88, M89, or M159.

## Consequences

ROBY gains an auditable long-term experience declaration that can inform later governance and improvement layers without turning historical evaluation into autonomous learning or execution. Sparse or weak longitudinal evidence remains visible as insufficient or review-required rather than being overinterpreted.
