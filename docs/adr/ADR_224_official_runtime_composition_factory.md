# ADR 224 — Official Runtime Composition Factory

## Status
Accepted.

## Context
M221 introduced the development console and M222 introduced guided setup, but both required users to provide an external `module:function` factory. ROBY therefore could be fully validated yet still fail its first interactive startup.

## Decision
Provide `app.runtime_root_factory:build_runtime_root` as the official local development composition factory. It builds the certified `RuntimeCompositionRoot` with the configured OpenAI-compatible local provider, deterministic conversation workload and inference ports, internal knowledge policy, and retrieval disabled until a governed retriever is explicitly configured.

The CLI setup flow selects this factory automatically. The lower-level `SetupOptions` contract remains backward compatible and can still accept a custom factory.

## Boundaries
The factory does not deploy services, start workers, mutate infrastructure, invent credentials, or enable unconfigured retrieval. Provider health is observed through the existing local adapter.

## Consequences
A new installation only needs a valid local model and endpoint before `python main.py --doctor` can pass. Advanced users retain the ability to replace the factory explicitly.
