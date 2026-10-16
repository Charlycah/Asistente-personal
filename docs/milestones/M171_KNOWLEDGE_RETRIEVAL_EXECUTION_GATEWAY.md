# M171 - Knowledge Retrieval Execution Gateway

## Purpose

Turn the deterministic M170 retrieval plan into a governed execution boundary
that dispatches each retrieval step through an injected source-specific port.

## Outcomes

- `completed`
- `partial`
- `failed`
- `withheld`
- `not_applicable`

## Execution model

- Internal, local-document and network retrieval permissions are independent.
- Network retrieval remains disabled by default.
- Direct and sequential plans stop after a required failure.
- Parallel verification plans attempt every planned source while preserving
  deterministic result order.
- Adapter exceptions, missing adapters and malformed artifacts become explicit
  governed outcomes instead of escaping the boundary.

## Governance boundary

M171 may retrieve knowledge only through caller-injected `KnowledgeRetriever`
ports. The core does not implement filesystem, HTTP, search-engine, API or model
provider adapters. Provider inference and platform mutation remain forbidden.

## Validation

- Exact M170 plan lineage.
- Immutable execution, step and artifact records.
- Every M170 step is accounted for in original order.
- Source/query identity validation and bounded artifact content.
- Append-only in-memory execution repository.
- Network disabled by default and explicitly authorized when required.
- No provider calls or platform mutation.
