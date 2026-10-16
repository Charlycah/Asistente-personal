# ADR-084 — Decision Records

## Status

Accepted for M82.

## Context

M77–M81 provide normalized evidence, claims, governed context, deterministic inference and conflict-aware confidence. ROBY now needs an immutable audit boundary that records what was asked, what material was considered, which rules and conflicts affected the outcome, and whether the system concluded, abstained, blocked or required human review.

The record must remain useful without copying complete source documents or storing unrestricted private reasoning.

## Decision

Introduce `core.governed_reasoning.decisions` with immutable `DecisionRecord` entities, typed evidence/claim/rule links, explicit lifecycle and outcome enums, human-review events, a repository protocol, an in-memory repository and `DecisionRecordManager`.

A record stores stable references to:

- query and context identity;
- Scope Guard outcome;
- evidence identifiers and fingerprints;
- claim identifiers and revisions;
- inference rule identifiers and versions;
- conflict identifiers;
- confidence score and public rationale;
- limitations and declared assumptions;
- conclusion or abstention text;
- review state and supersession lineage.

Decision status and outcome are separate. A record may be completed, inconclusive, blocked, conflict-unresolved, review-required, rejected or superseded, while its public outcome is conclusion, abstention, blocked or human review.

Closed records are never mutated. Human review creates a new record that references the prior record through `supersedes`; the original remains available unchanged.

The initial repository is in memory. Durable persistence is deferred until contracts stabilize.

## Consequences

### Positive

- Every reasoning result has a reproducible audit envelope.
- Evidence, claims and rule versions remain traceable without content duplication.
- Abstention and blocked outcomes become first-class records.
- Human review preserves history instead of rewriting it.
- M83 can render explanations from a stable public record.

### Trade-offs

- Records depend on referenced source retention for full reconstruction.
- The initial repository does not survive process restart.
- M82 records public reasons and policy facts, not unrestricted chains of thought.
- End-to-end orchestration remains deferred to M84.
