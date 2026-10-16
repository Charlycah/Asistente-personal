# M166 - Provider Health Evaluation

M166 opens PM3 by giving ROBY a provider-independent health snapshot for local
and remote intelligence providers.

## Delivered

- Immutable provider observations and deterministic IDs.
- Local and remote provider classification.
- Health states for available, degraded, unavailable, misconfigured, offline,
  disabled, and unknown providers.
- Model, endpoint, version, capability, latency, configuration, and service
  reachability metadata.
- Healthy, degraded, unavailable, configuration-required, and not-applicable
  outcomes.
- Exact M162 readiness lineage.
- Append-only in-memory repository.
- Strict prohibition of provider calls, network access, and platform mutation.

## Boundary

M166 diagnoses observations supplied by adapters. It does not probe endpoints,
call Ollama, Gemini, Mistral, choose a provider, or authorize inference.
