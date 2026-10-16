# M181 — Operational Trace Model

## Objective
Add the formal, local-first trace model required to inspect each operational
conversation turn while preserving governance, privacy, and exact lineage.

## Delivered
- Immutable operational event and turn-trace models.
- Deterministic trace and event identifiers.
- Contiguous event ordering and explicit causal parent validation.
- Start, pipeline-finished, persisted, and failed event vocabulary.
- Exact M180 turn, M177 pipeline, and M175 response lineage.
- Provider, retrieval, network, and platform-mutation execution flags.
- Private append-only JSONL trace persistence.
- Owner/session-scoped listing and exact `trace_id` lookup.
- Automatic M180 integration with independently configurable tracing.
- No prompt or response duplication in traces.

## Explicitly deferred
- Development console visualization and filtering (M182).
- Memory runtime integration (M183).
- Tool runtime integration (M184).
- Long-lived retention, rotation, and process coordination (M185).

## Validation
- 20 focused M181 tests passed.
- 40 combined M180-M181 tests passed.
- 5051 full-suite tests passed.
- Ruff clean.
