# ADR 228.1 — Gmail Interactive OAuth Activation

## Status

Accepted.

## Context

ROBY M227.6 contains governed OAuth state, secure credential persistence, Gmail API
transport, runtime composition, acceptance tests, and production-readiness
certification. A previous project proved that Google installed-application OAuth using
`InstalledAppFlow.run_local_server(port=0)` works for the deployment account, but it
persisted credentials with pickle and coupled authorization directly to Gmail calls.

The legacy user experience also announced unread mail when the desktop interface
opened. Its intended privacy contract was narrower than generic message reading:
announce the number of new messages and their `Subject` headers only, without reading
or speaking bodies and without marking messages as read.

ROBY must activate both proven behaviors without importing the legacy architecture,
weakening policy, or placing credentials in the repository.

## Decision

Extend `GoogleOAuthDeploymentAdapter` with an explicit `activate()` operation that:

1. loads credentials from `SecureCredentialStore` or the external authorized-user
   JSON fallback;
2. refreshes expired credentials when a refresh token is present;
3. starts `InstalledAppFlow` only when credentials are absent/invalid and deployment
   policy explicitly enables interactive authorization;
4. persists the resulting authorized-user document through the secure store when
   configured, otherwise through an atomic external JSON write;
5. publishes only a secret-free `GoogleOAuthActivationResult` and counters.

Add a separate read-only subject-announcement boundary that:

1. searches Gmail with `is:unread`;
2. retrieves each selected message using `format="metadata"` and
   `metadataHeaders=["Subject"]`;
3. never requests snippets or message bodies;
4. never modifies labels or marks messages as read;
5. exposes an optional desktop startup announcer that is non-blocking on failure.

Google SDK imports remain lazy. Interactive authorization and startup announcement
remain disabled by default. No pickle or legacy Gmail module is admitted into ROBY.

## Consequences

- The browser flow can be activated in a deployment without changing domain layers.
- Secure credential storage remains the preferred persistence mechanism.
- External `token.json` compatibility exists only as a deployment fallback and stays
  outside official packages.
- The desktop can reproduce the prior “new mail + subjects” behavior through an
  injected dependency, without coupling the UI to Gmail.
- Message bodies are not requested by the startup flow.
- Gmail remains read-only during the announcement and provider failure does not block
  interface startup.
- The normal test suite remains deterministic and network-free.
