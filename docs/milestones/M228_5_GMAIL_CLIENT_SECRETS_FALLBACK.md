# ROBY M228.5 — Gmail Client Secrets Governed Fallback

M228.5 improves local OAuth deployment ergonomics without changing Gmail runtime
capabilities.

## Resolution policy

- Prefer `ROBY_GMAIL_CLIENT_SECRETS_PATH`.
- Otherwise use `credentials.json` from the process working directory when present.
- Otherwise preserve the existing degraded diagnostic.

The fallback is deliberately non-recursive and does not search user folders or the
repository tree. An invalid explicit path never falls back.

## Compatibility

- M228.4 diagnostic trace is unchanged.
- M228.3 post-failure-only diagnosis is unchanged.
- M228.2 startup announcement behavior is unchanged.
- OAuth scopes, token persistence, and backend behavior are unchanged.
