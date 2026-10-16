# ROBY M227.3 — Secure Credential Store

M227.3 adds encrypted, atomic credential persistence behind a provider-neutral
boundary.

## Delivered

- `CredentialProtector` deployment boundary.
- `SecureCredentialStore` provider-neutral contract.
- `EncryptedFileCredentialStore` versioned encrypted envelopes.
- SHA-256-derived record names.
- Atomic writes and restrictive POSIX permissions.
- Explicit credential deletion.
- Protector rotation with re-encryption.
- Secret-free status counters and protector fingerprint.
- Optional secure-store consumption by `GoogleOAuthDeploymentAdapter`.
- Compatibility fallback to the external token file from M227.1.

## Security boundary

The repository does not provide or package an encryption key. Deployments must
inject a protector backed by a trusted platform secret facility. Tests use a
small deterministic fake protector and never contain real credentials.

## Certification

- Ruff: All checks passed.
- Focused M227.3 tests: 12 passed.
- Full suite: 5844 passed.
- Regression delta: zero failures, 12 additive tests.
