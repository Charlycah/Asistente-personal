# ADR-173: Knowledge Retrieval Execution Gateway

## Status

Accepted

## Context

M170 produces a complete, deterministic retrieval plan but deliberately cannot
open documents, query internal stores or access external sources. Operational
integration requires a boundary that can execute those plans without coupling
the domain core to concrete infrastructure.

## Decision

Introduce `core.knowledge_retrieval_execution` as an application-facing gateway.
It consumes the exact M170 plan, applies explicit execution permissions and
invokes source-specific `KnowledgeRetriever` ports supplied by composition code.

The gateway records one immutable result for every planned step. It validates
that returned artifacts preserve the planned source and query, limits content
size, captures adapter failures, and reports completed, partial, failed,
withheld or not-applicable outcomes.

External retrieval requires explicit `allow_network=True`. Internal and local
document retrieval have separate controls. Logical parallel plans attempt all
steps but retain plan order in the result; this milestone does not mandate a
threading or async implementation.

## Consequences

ROBY gains its first governed knowledge retrieval execution boundary while the
core remains independent of HTTP clients, filesystems, search engines and model
providers. Concrete adapters can now be integrated progressively outside this
module. Provider inference, response generation and platform mutation remain
future boundaries.
