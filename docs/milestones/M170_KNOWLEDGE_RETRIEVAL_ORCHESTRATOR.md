# M170 - Knowledge Retrieval Orchestrator

## Purpose

Convert the M169 knowledge-source decision into an ordered, deterministic and
inspectable retrieval plan.

## Outcomes

- `internal_planned`
- `local_planned`
- `external_planned`
- `verification_planned`
- `withheld`
- `not_applicable`

## Strategies

- direct
- sequential
- parallel

## Governance boundary

M170 does not retrieve content, open local documents, access the network, call
providers or APIs, or mutate the platform. It only publishes a plan for a later
execution boundary.

## Validation

- Exact M169 lineage.
- Immutable deterministic plans and steps.
- Configurable source limit and verification strategy.
- Append-only in-memory repository.
- No retrieval or execution authorization.
