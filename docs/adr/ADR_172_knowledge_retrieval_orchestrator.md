# ADR-172: Knowledge Retrieval Orchestrator

## Status

Accepted.

## Context

M169 declares which source classes are required but intentionally forbids
retrieval. ROBY needs a deterministic boundary that converts that policy into an
ordered and inspectable retrieval plan before any adapter performs I/O.

## Decision

Introduce M170 downstream from M169. It creates immutable retrieval steps with
source, query, priority, requirement, and strategy. Verification may be planned
in parallel; ordinary multi-source retrieval is sequential.

M170 prepares plans only. It does not open documents, access the network, call
providers or APIs, execute retrieval, or mutate the platform.

## Consequences

- Retrieval intent is explicit before side effects.
- Source ordering and verification strategy are testable.
- Exact M169 lineage is preserved.
- Actual retrieval remains delegated to a later governed boundary.
