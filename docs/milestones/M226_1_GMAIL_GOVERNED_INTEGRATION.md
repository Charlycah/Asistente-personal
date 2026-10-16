# M226.1 — Gmail Governed Integration

M226.1 introduces the first official Gmail-specific composition boundary while
preserving the mail adapters and governance contracts already certified in M61,
M63, M66, and M67.

## Scope

- `GmailGovernedIntegration` composes read and action adapters.
- Every request is routed through `ToolGatewayManager`.
- Gmail account identity is represented only by a normalized SHA-256 fingerprint.
- Local policy independently controls read, draft, reply, and send actions.
- Send remains disabled by default.
- Gateway consent remains mandatory for `mail.send` operations.
- Successful and blocked gateway results produce bounded, secret-free audit entries.
- The factory reuses centralized configuration and existing adapter factories.

## Supported actions

Read capability (`mail.read`):

- `summary`
- `recent`
- `list`
- `search`
- `read`

Action capability (`mail.send`):

- `draft`
- `reply`
- `send`

## Governance order

```text
User or governed caller
  -> GmailGovernedIntegration local policy
  -> Tool Gateway M61
  -> Capability Registry M62
  -> Permissions & Consent M63
  -> Mail adapters M66/M67
  -> Gmail IMAP/SMTP transport
```

## Security properties

- No credential is copied into status or audit output.
- No raw Gmail address is retained by the integration.
- Audit records exclude message content and recipients.
- Unknown and locally disabled actions fail before provider execution.
- One integration instance cannot be rebound to a different gateway.
- Tests use fake providers and perform no network calls.

## Acceptance criteria

- Existing M66 and M67 focused tests remain green.
- M226.1 focused tests cover identity, registration, policy, consent, routing,
  mutation classification, audit bounding, and gateway binding.
- Ruff passes.
- The complete pytest suite passes with zero regressions.
