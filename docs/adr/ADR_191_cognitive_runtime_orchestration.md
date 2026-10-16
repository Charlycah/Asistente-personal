# ADR-191 — Cognitive Runtime Orchestration

## Status

Accepted.

## Context

ROBY has mature cognitive modules, but the official operational conversation path
needs a single governed mechanism to coordinate them without coupling the
composition root or console to their internal models.

## Decision

Introduce an optional `CognitiveRuntimePort` in runtime composition. Its concrete
orchestrator invokes ordered contributors and returns an enriched immutable
`LLMRequest` plus stage-level lineage.

The boundary is placed after memory enrichment and before tool enrichment. Stage
failures are contained and do not abort later contributors. Applied context is
clearly delimited in the provider prompt.

## Consequences

Future cognitive integrations share one operational contract. M189 itself adds
no reasoning policy, planning authority, reflection behavior, tool execution, or
platform mutation.
