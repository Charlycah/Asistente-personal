# ADR-168: Provider Health Evaluation

## Status

Accepted.

## Context

ROBY can use local and remote model providers, including Ollama with Llama 3,
Gemini, and Mistral. Before provider selection or inference, ROBY needs a stable
and auditable view of provider health.

## Decision

M166 introduces a declarative provider health evaluator downstream from M162.
It consumes injected provider observations and publishes immutable health
results. It does not perform HTTP calls, invoke models, start services, access
the network, or select a provider.

The evaluator distinguishes available, degraded, unavailable, misconfigured,
offline, disabled, and unknown provider states. It also records provider kind,
model, endpoint, version, capabilities, latency, configuration presence, and
service reachability.

## Consequences

M167 and M168 can consume a deterministic health snapshot without coupling
routing policy to provider clients. Real probes may be implemented later by
adapters that produce M166 observations.
