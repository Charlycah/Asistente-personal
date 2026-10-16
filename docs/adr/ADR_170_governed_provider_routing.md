# ADR-170 - Governed Provider Routing

## Status

Accepted.

## Context

M166 publishes provider health and M167 declares whether a workload should use
local intelligence, remote fallback, or no provider. ROBY still needs a concrete,
deterministic route before an execution layer may invoke a provider.

## Decision

Introduce M168 as a pure governed routing boundary. It consumes the exact M167
policy decision, selects one eligible provider observation, publishes ordered
fallback observations, and records whether the route is local or remote.

Selection is deterministic. Configured provider-name preferences are considered
first, followed by latency and provider name. Default preferences favor Ollama
locally and Gemini then Mistral remotely.

M168 may declare a route but cannot call a provider, execute inference, access
the network, or mutate the platform.

## Consequences

- Provider choice is explicit, inspectable, and reproducible.
- Local-first policy remains separate from concrete routing.
- Future execution modules can consume a stable route contract.
- Provider failures can use an ordered fallback list without hidden selection.
