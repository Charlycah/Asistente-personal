# M226.3 — Gmail Intent Resolution

M226.3 adds deterministic intent normalization before the Gmail semantic capability
layer introduced in M226.2.

## Delivered

- Seven canonical Gmail intents: recent, search, read, compose, draft, reply, send.
- Immutable intent decisions with canonical action, semantic capability, and
  required payload-field metadata.
- Bounded, explicit aliases for user-facing action terminology.
- Secret-free intent catalog.
- Canonical gateway payloads and canonical audit actions.
- Preservation of Tool Gateway routing, local Gmail policy, and Permission &
  Consent authority.

## Verification

- Twelve focused M226.3 tests.
- Combined M226.1–M226.3 focused suite.
- Ruff over the complete repository.
- Complete pytest suite.
- No network calls and no runtime composition changes.
