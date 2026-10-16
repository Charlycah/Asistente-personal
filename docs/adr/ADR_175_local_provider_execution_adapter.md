# ADR-175: Local Provider Execution Adapter

## Status

Accepted for M173.

## Context

M168 declares a governed provider route but explicitly forbids provider calls and
inference. ROBY now needs a narrow execution boundary that can invoke a selected
local provider without silently widening permissions to remote providers,
network services, fallback routes, or platform mutation.

## Decision

Introduce `GovernedProviderExecutionAdapter` downstream from M168.

The adapter:

- accepts the exact `GovernedProviderRoute` produced by M168;
- executes only an active `ROUTED_LOCAL` route;
- resolves providers through injected `LLMProvider` ports;
- forces the routed model into the provider request;
- rejects provider and model lineage mismatches;
- contains provider exceptions and malformed responses;
- applies prompt and response size limits;
- never performs remote fallback;
- never authorizes external network access or platform mutation;
- publishes immutable, repository-backed execution records.

The existing `OllamaProvider` remains an infrastructure implementation of the
neutral `LLMProvider` protocol. M173 does not import HTTP clients or assume a
specific local runtime.

## Consequences

ROBY gains its first governed local inference execution boundary while retaining
strict route lineage and failure containment. Remote provider execution remains
outside this milestone.
