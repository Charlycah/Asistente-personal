# M226.6 — Gmail Provider Transport

M226.6 introduces the governed provider-call boundary for Gmail.

## Pipeline

```text
Gmail Intent Resolution
        ↓
Semantic Capability Resolution
        ↓
Execution Planning
        ↓
OAuth Governance
        ↓
Gmail Provider Transport
        ↓
Provider-specific Backend
```

## Included

- Canonical transport operations for recent listing, search, read, draft and send.
- OAuth-ready preflight before backend invocation.
- Immutable request mapping at the backend boundary.
- Local timeout and result-count policy.
- Secret-free normalized provider error taxonomy.
- Immutable transport results with payload-free status metadata.
- Optional transport status in `GmailGovernedIntegration`.

## Preserved

- M61 Tool Gateway routing.
- M62 Capability Registry authority.
- M63 Permissions & Consent authority.
- Existing `mail.read` and `mail.send` contracts.
- M226.1 through M226.5 behavior.
- Send disabled by default.

## Deferred

- Google API client dependency.
- Interactive OAuth authorization.
- Live Gmail network calls.
- Retry scheduling and backoff.
- Idempotent send keys.
- Runtime Composition Root activation.
