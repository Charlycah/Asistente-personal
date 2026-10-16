# ADR 195 — Operational Acceptance Suite

## Decision

ROBY will maintain a deterministic operational acceptance suite that validates
its official local runtime as a complete system. Acceptance checks remain
observational and do not acquire execution, governance, memory, tool, or
provider authority.

## Rationale

The M177–M194 stage integrated many independently tested capabilities into one
runtime. Unit and focused integration tests alone do not prove that bootstrap,
cognition, tools, provider execution, persistence, traces, shutdown, and
restart continuity work together through the official path.

## Consequences

- acceptance failures are reported as structured checks;
- exception details are reduced to exception type;
- reports never repeat provider or tool execution;
- acceptance scenarios use local deterministic doubles where external services
  are not part of the behavior under test;
- future operational changes must preserve or intentionally update the suite.
