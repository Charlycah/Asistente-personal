# ADR 224.5 — Graceful Runtime Shutdown

## Status

Accepted.

## Context

The development console recognized only `/exit` and `/quit`. Plain `exit` was routed as a conversational turn, while `KeyboardInterrupt` was not treated as a normal operator shutdown. On Windows this could leave the supervised runtime active long enough to appear frozen and force the user to close VS Code.

## Decision

The local conversation console recognizes `exit`, `quit`, and `salir`, both with and without a leading slash. EOF and `KeyboardInterrupt` are normal shutdown signals. Every exit path crosses the same `finally` boundary, which stops the heartbeat supervisor, stops the lifecycle or bootstrap, persists the stopped state, and releases the runtime lease.

The shutdown commands are handled locally and are never sent to the LLM or journaled as conversation.

## Consequences

- operator shutdown is deterministic and provider-independent;
- no conversational inference is used to interpret shutdown intent;
- lifecycle and lease cleanup remain centralized;
- unexpected exceptions still mark the runtime degraded before cleanup and propagation.
