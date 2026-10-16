# ADR-085 — Explainable Answers

## Status

Accepted.

## Context

M82 persists governed reasoning outcomes as immutable Decision Records. ROBY now needs a public explanation boundary that can communicate conclusions, abstentions, blocks, uncertainty, sources and review requirements without reconstructing unrestricted internal reasoning or weakening the distinction between facts and rule-derived claims.

## Decision

Introduce `core.governed_reasoning.explanations` with deterministic rendering from a single immutable `DecisionRecord`.

The subsystem provides:

- `ExplanationLevel`: concise, standard and audit.
- `SourceCitation` with evidence fingerprints, claim revisions, rule versions and conflict identifiers.
- typed `ExplanationSection` values.
- immutable `ExplainableAnswer` with stable SHA-256 identity.
- `ExplainableAnswerRenderer`.
- `ReasoningExplanationManager`.

Explanations must be derived only from public audit data already present in the Decision Record. They must never invent citations, infer unrecorded reasons, expose unrestricted chain-of-thought, or treat a rule result as a confirmed fact.

## Consequences

- The same Decision Record and rendering request produce the same answer identity.
- Conclusions, abstentions, blocked requests and human-review requirements remain semantically distinct.
- Confidence is presented as both a semantic band and a bounded score.
- Audit explanations expose identifiers and versions, not copied source documents.
- M84 can consume a stable explanation object without coupling the pipeline to rendering details.

## Deferred

- Full M77–M83 orchestration and Cognitive Pipeline integration: M84.
- Localization and alternative presentation surfaces.
- Retrieval of human-readable source excerpts from external repositories.
