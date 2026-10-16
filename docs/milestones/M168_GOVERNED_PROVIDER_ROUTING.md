# M168 - Governed Provider Routing

M168 turns the provider-class preference from M167 into one concrete,
deterministic provider route without executing it.

## Delivered

- Immutable route requests and route results.
- Local, remote, no-provider, withheld, and not-applicable outcomes.
- Deterministic provider selection by configured preference, latency, and name.
- Default local preference for Ollama.
- Default remote preference for Gemini followed by Mistral.
- Ordered fallback provider observations.
- Exact M167 policy lineage.
- Append-only in-memory repository.
- Strict prohibition of provider calls, inference, network access, and platform
  mutation.

## Boundary

M168 selects and declares a route. It does not execute that route. Provider
invocation remains outside this milestone.
