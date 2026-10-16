# ADR 228.4 — Gmail Diagnostic Trace

## Status

Accepted.

## Context

M228.3 introduced safe, actionable Gmail diagnostic codes. A degraded startup still
needed a deterministic view of the execution stage that failed and of the stages that
were not reached. The trace must not reintroduce the preflight regression corrected in
M228.3, expose secrets, perform network calls, or alter Gmail behavior.

## Decision

Add an immutable nine-stage trace to `GmailDiagnosticReport`:

1. Runtime
2. Configuration
3. google-auth
4. OAuth
5. Secure Credential Store
6. Token & Scopes
7. Gmail API Backend
8. Startup Announcement
9. Runtime Completion

Each stage has a stable key and one of four states: `OK`, `FAILED`, `NOT_EXECUTED`, or
`DISABLED`. The existing compact degraded diagnostic remains the first console line;
trace lines follow it. Disabled Gmail remains silent. The startup wiring continues to
build and execute the announcer first and only creates a diagnostic report after a
failure.

## Consequences

- Operational failures identify the exact causal stage.
- Later stages are explicitly marked as not executed.
- Existing callers retain the primary diagnostic line and report fields.
- Structured serialization now includes a secret-free trace.
- No Gmail capability, OAuth policy, mailbox mutation, or network behavior is added.
