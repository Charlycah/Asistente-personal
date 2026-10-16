# ADR 224.1 — Runtime Identity Compatibility Hotfix

## Status
Accepted.

## Context
M224 introduced the official runtime composition factory while the development environment continued to expose the historical `ROBY_RUNTIME_STATE_PATH=.roby/runtime_state.json` setting. When loaded globally, that legacy placeholder overrode M188's profile- and session-scoped runtime state paths. Local personal profile names loaded from `.env` also leaked into tests that were intended to verify default identity contracts.

## Decision
Treat `.roby/runtime_state.json` as a legacy global placeholder rather than an explicit override. When it is absent or equals that placeholder, derive state from the selected profile and session. Continue to honor any other explicit path as a deliberate override. Isolate default-contract tests from local personal-name environment variables.

## Consequences
Private and shared profiles regain isolated state paths, explicit custom paths remain supported, and the test suite becomes portable across machines with personalized `.env` files. No runtime authority, provider, tool, or deployment behavior is added.
