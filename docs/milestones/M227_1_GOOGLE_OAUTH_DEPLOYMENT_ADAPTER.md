# ROBY M227.1 — Google OAuth Deployment Adapter

M227.1 introduces the concrete deployment boundary for Google authorized-user
credentials while preserving the secret-free OAuth governance established in
M226.5.

## Configuration

```dotenv
ROBY_GMAIL_TOKEN_PATH=C:/secure/roby/gmail-token.json
ROBY_GMAIL_CLIENT_SECRETS_PATH=C:/secure/roby/google-client.json
ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH=false
```

All paths must point outside the source tree in real deployments. Interactive
OAuth remains opt-in. The adapter imports Google libraries only when loading or
authorizing credentials.

## Certification

- Ruff: All checks passed
- Focused tests: 12 passed
- Full suite: 5820 passed
- Network calls in tests: none
- Credential files packaged: none
