# ADR-164 — PM1 / M162 Runtime Readiness Gate

## Status

Accepted.

## Context

M161 closes the declarative unified companion pipeline, but it does not establish whether the concrete runtime dependencies needed for startup are present. ROBY needs a deterministic boundary between architectural readiness and actual startup. That boundary must diagnose configuration, memory, providers, services, permissions, storage, network, and other declared components without starting services or producing side effects.

## Decision

Introduce `core.runtime_readiness_gate` downstream from M161.

The milestone:

- consumes one immutable M161 integration result;
- consumes immutable component checks supplied by adapters or bootstrap code;
- distinguishes required and optional components;
- classifies configuration, provider, memory, service, permission, storage, network, capability, and generic dependencies;
- produces `READY`, `DEGRADED`, `BLOCKED`, `CONFIGURATION_REQUIRED`, `PROVIDER_UNAVAILABLE`, or `NOT_APPLICABLE`;
- preserves exact M161 lineage;
- exposes available and unavailable providers without selecting or calling one;
- calculates conservative confidence from M161 and component states;
- uses deterministic immutable identifiers and an append-only repository contract;
- remains declarative, deterministic, and side-effect free.

## Boundaries

M162 does not:

- start ROBY, schedulers, services, devices, or background workers;
- call Ollama, Llama 3, Gemini, Mistral, Internet services, or any provider;
- read secrets, files, environment variables, sockets, or operating-system state directly;
- mutate configuration or request credentials;
- authorize conversation start, provider calls, network access, activation, or platform mutation;
- replace M161 companion integration;
- perform recovery, fallback, routing, or provider selection.

Concrete probes remain adapter responsibilities. M162 evaluates their immutable results.

## Consequences

ROBY gains an auditable startup gate that can explain why the runtime is ready, degraded, blocked, missing configuration, or lacking a provider. The actual startup operation remains a separate future responsibility, preventing readiness evaluation from becoming execution.
