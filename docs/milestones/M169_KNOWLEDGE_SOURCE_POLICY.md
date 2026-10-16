# M169 - Knowledge Source Policy

## Purpose

Decide which class of knowledge source ROBY needs after M168 has declared a
governed provider route.

## Outcomes

- `internal_sufficient`
- `local_source_preferred`
- `external_source_required`
- `verification_required`
- `withheld`
- `not_applicable`

## Source classes

- internal knowledge
- local documents
- official documentation
- web
- news
- APIs

## Governance boundary

M169 does not retrieve sources, call providers, access the network, or mutate the
platform. It only publishes a deterministic, inspectable source policy.

## Validation

- 30 focused tests.
- Exact M168 lineage.
- Immutable deterministic decisions.
- Append-only in-memory repository.
- No retrieval or execution authorization.
