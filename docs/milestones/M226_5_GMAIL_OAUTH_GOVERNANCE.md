# ROBY M226.5 — Gmail OAuth Governance

M226.5 adds a provider-neutral, secret-free OAuth lifecycle boundary to the
existing governed Gmail architecture.

## Pipeline position

```text
External credential store
          ↓
GmailCredentialProvider
          ↓
Gmail OAuth Governance
          ↓
Secret-free lifecycle snapshot
          ↓
Gmail governed integration status
```

The execution path from M226.4 remains unchanged. This milestone governs whether
credential material is absent, ready, expired, revoked, or missing required
scopes; it does not perform Gmail API calls.

## Security properties

- Access tokens, refresh tokens, client secrets, and raw scopes are never exposed
  by snapshots or status.
- Scope identifiers are represented by bounded SHA-256 fingerprints.
- Credential loading is abstracted behind a protocol.
- Refresh and revocation are independently controlled by local policy.
- Credential expiry timestamps must be timezone-aware.
- Real credential files are not committed or packaged.

## Deliberate exclusions

- No `google-auth` dependency.
- No OAuth browser or device authorization flow.
- No token persistence implementation.
- No Gmail API transport.
- No network calls in tests.
- No Runtime Composition Root mutation.
