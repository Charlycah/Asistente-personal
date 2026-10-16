# M167 - Local-First Provider Policy

M167 gives ROBY a deterministic policy for deciding whether a workload needs a
provider and whether local or remote intelligence should be preferred.

## Delivered

- Immutable workload declarations and deterministic policy decisions.
- Local-preferred, remote-fallback, no-provider-required, withheld, and
  not-applicable outcomes.
- Capability-aware provider eligibility.
- Local preference for normal and sensitive workloads.
- Explicit remote handling for current-information workloads.
- Configurable remote fallback and degraded-provider eligibility.
- Exact M166 provider-health lineage.
- Append-only in-memory repository.
- Strict prohibition of provider selection, inference, network access, routing,
  and platform mutation.

## Boundary

M167 declares a provider class preference. It does not select Ollama, Gemini,
Mistral, or any other concrete provider and does not execute a request.
