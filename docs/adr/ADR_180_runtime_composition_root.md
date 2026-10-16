# ADR-180 — Runtime Composition Root

## Status
Accepted

## Context
M177 established the official governed operational conversation pipeline while deliberately leaving construction of provider health, policy, routing, knowledge policy, retrieval planning, execution adapters, and response assembly outside the pipeline. ROBY now needs one local-first construction boundary that wires these existing capabilities without moving cognitive logic into interfaces or bootstrap code.

## Decision
Introduce `RuntimeCompositionRoot` as the single official constructor for ROBY's operational runtime graph.

- Turn-specific readiness, provider observations, workload, knowledge need, and LLM request construction enter through explicit ports.
- `GovernedRuntimePreparation` composes exact M166-M170 lineage for M177.
- The root constructs one instance of each existing policy, router, orchestrator, executor, and assembler.
- `compose()` is idempotent and exposes an immutable `RuntimeComposition` for observability and later bootstrap use.
- `build()` returns the official M177 pipeline consumed by later runtime milestones.
- Composition performs no provider call, retrieval, network access, or platform mutation.
- Retrieval can be disabled at the root without altering the pipeline contract.

## Consequences
ROBY has one inspectable and testable runtime graph. M179 can now bootstrap this graph from local configuration and concrete adapters without duplicating construction decisions. Cognitive and governance decisions remain in their original modules, while interfaces remain passive.
