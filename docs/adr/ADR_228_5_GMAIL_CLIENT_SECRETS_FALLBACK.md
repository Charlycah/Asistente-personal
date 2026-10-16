# ADR 228.5 — Gmail Client Secrets Local Fallback

## Status
Accepted.

## Context
ROBY M228.4 required `ROBY_GMAIL_CLIENT_SECRETS_PATH` even when a valid
`credentials.json` was already present in the execution directory. This was safe
but unnecessarily inconvenient for the official desktop development workflow.

## Decision
Resolve Google OAuth Client Secrets in this strict order:

1. `ROBY_GMAIL_CLIENT_SECRETS_PATH`, when non-empty.
2. `credentials.json` in the current execution directory, only when the variable
   is absent and the file exists.
3. No Client Secrets configuration.

An explicitly configured path always has absolute precedence, even if it is
invalid. ROBY must not silently mask a deployment error by falling back.

The same resolver is used by the deployment adapter and diagnostic runtime.
No preflight gate, Gmail capability, scope, mailbox mutation, or network call is
added.

## Consequences
- Local desktop startup matches the established `credentials.json` workflow.
- Production deployment remains explicitly configurable.
- Diagnostics remain deterministic and actionable.
- Paths and credential contents remain absent from serialized diagnostics.
