# ADR-186 — Integrate tools through the governed M61 gateway

## Status

Accepted for M184.

## Context

The operational runtime can now converse, trace, observe, and use cognitive memory. ROBY already has a governed tool gateway from M61, including capability registration, consent checks, handler isolation, and audit records. M184 must connect that existing boundary without creating a second tool system or granting the console execution authority.

## Decision

Add `ToolRuntimeIntegration` as an optional dependency of the official runtime composition. During turn preparation it recognizes only the explicit `/tool` command contract, normalizes a deterministic invocation, and delegates execution to `ToolGatewayManager`. Successful read-only output may enrich the provider prompt as structured evidence. Platform-mutating capabilities are blocked before gateway execution while M177 continues to require `platform_mutation_performed=False`.

## Consequences

- M61 remains the single gateway and audit authority for tools.
- Composition remains idempotent and side-effect free.
- Tool use is explicit and testable during development.
- Unknown, disabled, consent-gated, unavailable, and failing capabilities remain contained.
- M184 cannot execute platform mutations; a later governed contract must explicitly add that authority.
- Autonomous planning and natural-language tool selection remain outside this milestone.
