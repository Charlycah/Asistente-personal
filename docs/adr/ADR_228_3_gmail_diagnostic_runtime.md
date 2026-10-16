# ADR 228.3 — Gmail Diagnostic Runtime

## Status

Accepted.

## Context

M228.2 connected the governed Gmail startup announcement to the official ROBY
entrypoint and deliberately contained all provider and deployment failures. That
containment preserved runtime availability, but collapsed every operational fault
into one generic degraded message. Operators could not distinguish missing
configuration, unavailable Google dependencies, invalid credentials, filesystem
permissions, OAuth policy, scopes, provider backend, or announcement failures.

## Decision

Introduce a read-only, secret-free `GmailDiagnosticRuntime` at the application
boundary.

The runtime:

- inspects Gmail enablement, startup-announcement policy, account configuration,
  OAuth token configuration, token document shape, required read-only scope,
  interactive OAuth Client Secrets, and lazy Google SDK dependencies;
- classifies contained exception chains into stable component/code pairs;
- emits one actionable primary diagnostic at startup while retaining the full
  immutable finding set for structured observation;
- never serializes account addresses, paths, token values, Client Secrets,
  provider exception text, or credential payloads;
- remains non-blocking and introduces no new Gmail capability, network call, or
  mailbox mutation.

The startup hook performs diagnostic preflight before provider construction. A
preflight degradation prevents a futile OAuth/API attempt and reports the first
blocking cause. Failures after preflight are classified from their governed
exception chain.

## Consequences

ROBY now distinguishes operational causes such as `account_missing`,
`token_path_missing`, `token_missing`, `token_invalid_json`,
`readonly_scope_missing`, `dependency_missing`, `permission_denied`,
`token_refresh_failed`, `secure_store_read_failed`, and
`subject_lookup_failed`.

Diagnostics are intentionally bounded. They report a safe category and
remediation, not raw provider details. The Gmail startup behavior remains
optional, read-only, and degradable.
