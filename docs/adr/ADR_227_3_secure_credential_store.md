# ADR 227.3 — Secure Credential Store

## Status
Accepted.

## Context
M227.1 can load an external authorized-user token document and M227.2 can use
those credentials to build a Gmail API backend. Plain credential documents,
however, must not become the long-term persistence contract for ROBY.

ROBY needs a provider-neutral storage boundary that keeps credential material
outside source control, encrypts it before persistence, writes atomically,
restricts local permissions, supports key rotation, and never exposes secrets
or filesystem locations through operational status.

## Decision
Introduce `SecureCredentialStore`, `CredentialProtector`, and
`EncryptedFileCredentialStore` under `infrastructure.mail`.

The store:

- accepts provider-neutral JSON-like credential documents;
- delegates encryption and decryption to a deployment-specific protector;
- persists only a versioned encrypted envelope;
- derives filenames from SHA-256 rather than account identifiers;
- uses same-directory temporary files and atomic replacement;
- applies directory mode `0700` and file mode `0600` on POSIX;
- supports explicit deletion and protector rotation;
- publishes only bounded counters and a protector fingerprint;
- normalizes read/write/delete failures without including secret values.

`GoogleOAuthDeploymentAdapter` optionally reads from the secure store first and
falls back to the existing external token file for compatibility.

## Consequences
ROBY gains a stable secure-storage contract without choosing a universal key
management mechanism. Production deployments must provide a protector backed
by an operating-system keystore, HSM, cloud KMS, or equivalent trusted secret
facility. No plaintext token, encryption key, or real vault record is packaged.
