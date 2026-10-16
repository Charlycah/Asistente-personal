# M80 — Governed Inference

## Objective

Add the first governed inference capability of FASE VIII over the normalized, filtered and auditable context produced by M79.

## Delivered components

- `ClaimCondition`
- `InferenceOperator`
- `InferenceRule`
- `InferencePolicy`
- `InferenceStatus`
- `InferenceResult`
- `InferenceRun`
- `InferenceRuleRegistry` protocol
- `InMemoryInferenceRuleRegistry`
- `GovernedInferenceEngine`

## Rule contract

Rules are immutable, versioned and declarative. They specify accepted claim conditions, allowed domains, a fixed conclusion, confidence ceiling and whether human review is mandatory.

Supported condition operators:

- `equals`
- `in`
- `before_as_of`
- `after_as_of`

Temporal comparisons use the `ReasoningQuery.as_of` timestamp rather than wall-clock time, preserving historical reproducibility.

## Governed output

A successful rule creates only a `ClaimType.RULE_RESULT` with:

- `ClaimOrigin.RULE`;
- explicit `rule_reference` in `rule_id@version` form;
- deterministic claim ID;
- input claim identifiers;
- confidence bounded by the rule and the weakest declared input confidence;
- status `proposed` or `review_required`.

The subsystem does not promote claims to facts, mutate M77–M79 state or execute external actions.

## Context behavior

- `blocked` context produces blocked inference results.
- `insufficient` context produces not-applicable results.
- review-required context can propagate review or be stopped by policy.
- rules outside the query domains are rejected.
- disabled rules are rejected explicitly.

## Explicit exclusions

M80 does not implement:

- recursive inference;
- rule learning;
- LLM-authored conclusions;
- conflict resolution;
- multifactor confidence scoring;
- decision records;
- explainable answer rendering;
- tool execution or external actions.

## Acceptance

- rules are versioned and fingerprinted;
- rule registration is deterministic and immutable per version;
- outputs are always rule-result claims;
- inference is reproducible for the same context and rules;
- temporal rules honor query time;
- Scope Guard domain boundaries are preserved;
- review requirements propagate;
- full regression suite remains green.
