# ADR-178 — Desktop Runtime Integration

## Status
Accepted

## Context
ROBY already exposes a historical desktop UI, a governed console conversation boundary (M172), local and external execution boundaries (M173–M174), and immutable operational responses (M175). The desktop surface must consume these capabilities without constructing providers, authorizing network access, synthesizing new answers, or coupling Tkinter to core execution details.

## Decision
Introduce `DesktopRuntimeIntegration` as an application-facing orchestration boundary.

- Desktop input is normalized into an immutable request carrying owner, session, and exact M162 readiness lineage.
- Blocked readiness prevents both greeting and operational execution.
- Greeting-compatible input is processed through M172, preserving M163–M165 lineage.
- Other input is delegated through an injected `OperationalDesktopPipeline` that returns an M175 response.
- M175 deliverable responses are mapped to desktop delivery; withheld and failed responses are declared with stable local text.
- Provider and network flags are copied only as lineage from M175.
- Platform mutation is forbidden.
- A thin adapter maps the integration result to the existing `UIResponse` contract.

## Consequences
The desktop UI can now run against the governed operational architecture while remaining independent from concrete providers, retrievers, network clients, and Tkinter lifecycle concerns. Composition remains the responsibility of bootstrap code.
