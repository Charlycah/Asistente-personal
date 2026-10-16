# ADR-169: Local-First Provider Policy

## Status

Accepted.

## Context

M166 gives ROBY a provider-independent health snapshot, but it does not express
which provider class should be preferred for a workload. ROBY needs a stable
policy that favors local intelligence when it is sufficient, preserves privacy,
and avoids unnecessary remote calls.

## Decision

M167 introduces a declarative local-first provider policy downstream from M166.
It consumes a provider health result and a typed workload declaration. The
policy can declare local preference, remote fallback, no-provider-required,
withheld, or not-applicable outcomes.

Local providers are preferred when they are healthy and satisfy all required
capabilities. Remote providers are declared only when the workload explicitly
requires remote or current information, when no eligible local provider exists,
or when policy permits fallback. Sensitive workloads prefer local providers.

M167 does not select a concrete provider, invoke a model, authorize network
access, or route execution. Those responsibilities remain outside this module
and are reserved for M168 and later runtime adapters.

## Consequences

ROBY can avoid waking a model for simple greetings, prefer Ollama or another
local provider for ordinary work, and declare a governed remote fallback when
required. Provider identity remains separate from ROBY's voice and personality.
