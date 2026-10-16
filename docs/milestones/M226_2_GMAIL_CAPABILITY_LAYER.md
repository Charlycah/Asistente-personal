# M226.2 — Gmail Capability Layer

M226.2 adds a deterministic semantic capability layer to the governed Gmail
integration delivered in M226.1.

## Delivered

- Five semantic Gmail capabilities: read, compose, draft, reply, and send.
- Immutable capability decisions with policy, permission scope, mutation, and
  confirmation metadata.
- Deterministic mapping onto the existing `mail.read` and `mail.send` gateway
  capabilities.
- Secret-free capability catalog.
- Preservation of Tool Gateway routing and Permission & Consent authority.
- Send disabled by default and explicitly classified as externally mutating.

## Verification

- Focused M226.1 + M226.2 tests.
- Ruff over the complete repository.
- Complete pytest suite.
- No network calls and no runtime composition changes.
