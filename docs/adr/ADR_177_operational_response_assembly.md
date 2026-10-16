# ADR-177: Operational Response Assembly

## Status
Accepted

## Context
M171 executes governed knowledge retrieval, M173 executes governed local inference, and M174 supplies external retrieval adapters. ROBY still needs a deterministic application boundary that can turn those completed execution records into one deliverable response without performing new inference or retrieval.

## Decision
Introduce `core.operational_response_assembly` as a pure assembly boundary. It accepts optional M171 and M173 execution records, preserves their exact identity, publishes accepted provider text, converts successful retrieval artifacts into evidence, and records explicit limitations. It never calls providers, retrievers, network clients, fallback routes, or platform mutation ports.

A valid provider response is required by default. Retrieval alone is evidence, not prose generation. Failed or bounded evidence may produce a partial response only when accepted provider text already exists.

## Consequences
- Final operational responses are immutable and auditable.
- Side-effect ownership remains in earlier execution milestones.
- Evidence and limitations are explicit rather than hidden in presentation logic.
- Future applications can consume a stable response contract.
