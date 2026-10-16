# ADR 227.1 — Google OAuth Deployment Adapter

## Status
Accepted.

## Context
M226.5 defined provider-neutral OAuth governance and M226.9 certified the full
in-memory Gmail architecture. Deployment still required a concrete boundary for
loading Google authorized-user credentials without importing deployment secrets
or Google SDK dependencies into the domain.

## Decision
Add `GoogleOAuthDeploymentAdapter` behind `GmailCredentialProvider`.

The adapter:

- reads an authorized-user JSON document only from an explicit external path;
- imports Google OAuth libraries lazily;
- keeps interactive authorization disabled by default;
- exposes secret-free availability and counters only;
- normalizes dependency, parsing, and authorization failures;
- never persists, logs, audits, or packages credential values.

The repository does not include a token document, client secret document, pickle,
or Google SDK dependency. Deployment operators install the SDK and provide paths
outside the repository.

## Consequences
ROBY remains runnable and testable without Google dependencies. A real deployment
can supply `google-auth` and `google-auth-oauthlib` while preserving M226 OAuth
governance and runtime degradation behavior.
