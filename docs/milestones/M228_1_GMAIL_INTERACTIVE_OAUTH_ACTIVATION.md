# ROBY M228.1 — Gmail Interactive OAuth Activation

M228.1 activates the proven Google installed-application OAuth flow behind ROBY's
existing deployment and governance boundaries. It also restores the intended legacy
startup behavior in a privacy-minimal form: count unread messages and announce only
their subjects.

## OAuth runtime flow

```text
External client configuration
          ↓
Explicit interactive authorization policy
          ↓
InstalledAppFlow.run_local_server(port=0)
          ↓
Google authorized-user credentials
          ↓
SecureCredentialStore (preferred)
          ↓
External atomic JSON fallback
          ↓
GmailOAuthGovernance / Runtime Composition
```

## Startup subject announcement

```text
Desktop startup
      ↓
Optional GmailStartupSubjectAnnouncer
      ↓
Gmail query: is:unread
      ↓
messages.get(format="metadata", metadataHeaders=["Subject"])
      ↓
"Tenés N correos nuevos. Asuntos: ..."
```

The startup path does not request message bodies or snippets, does not mutate labels,
and does not mark mail as read. Failure is non-blocking, so the desktop still opens.

## Deployment requirements

Install the optional Google packages in the local virtual environment:

```powershell
python -m pip install google-auth google-auth-oauthlib google-api-python-client
```

Keep the Google OAuth client file outside the ROBY directory and configure:

```dotenv
ROBY_GMAIL_TOKEN_PATH=C:\secure\roby\gmail-token.json
ROBY_GMAIL_CLIENT_SECRETS_PATH=C:\secure\roby\credentials.json
ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH=true
```

A production deployment should inject a `SecureCredentialStore`; the external token
path is retained for compatibility and migration only. The subject announcer is an
optional dependency of `ROBYDesktopApp` and must be composed only after OAuth and the
Gmail API client are ready.

## Safety properties

- Interactive authorization is disabled by default.
- Startup subject announcement is disabled unless explicitly composed.
- No browser is opened by the normal test suite.
- No network call is made by the normal test suite.
- No token, refresh token, client secret, path, or account value appears in status.
- Credentials are written atomically; POSIX fallback files use mode `0600`.
- Startup lookup uses metadata-only Gmail requests.
- Message bodies are never requested by the subject-announcement flow.
- Gmail is not modified and messages remain unread.
- Pickle persistence and the legacy modules are not included.
- Existing OAuth Governance, Provider Transport, Retry Governance, Runtime
  Composition, acceptance, and readiness certification remain unchanged.

## Certification

- Ruff: all checks passed.
- Focused OAuth + subject announcement + desktop integration: 31 passed.
- Full suite: 5906 passed, 1 skipped in the construction environment.
- Regression failures: zero.
