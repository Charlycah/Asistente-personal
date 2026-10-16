# M228.2 — Gmail Startup Announcement Runtime Wiring

M228.2 connects the governed Gmail subject announcer to the official development console entrypoint.

## Runtime sequence

```text
python main.py --observe
        ↓
Development console banner
        ↓
Google OAuth load / refresh / explicit activation
        ↓
Gmail API metadata-only query: is:unread
        ↓
Subject-only startup announcement
        ↓
Carlos> prompt
```

## Environment

```dotenv
ROBY_GMAIL_ENABLED=true
ROBY_GMAIL_ACCOUNT_ADDRESS=your-account@example.com
ROBY_GMAIL_TOKEN_PATH=C:\external\secure\gmail-token.json
ROBY_GMAIL_CLIENT_SECRETS_PATH=C:\external\secure\gmail-oauth-client.json
ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH=true
ROBY_GMAIL_STARTUP_ANNOUNCEMENT_ENABLED=true
ROBY_GMAIL_STARTUP_ANNOUNCEMENT_MAX_RESULTS=5
ROBY_GMAIL_STARTUP_ANNOUNCEMENT_TIMEOUT_SECONDS=10
```

`ROBY_GMAIL_EMAIL`, `GMAIL_ADDRESS`, and `EMAIL_USER` are accepted as compatibility aliases for the account address. Password variables are not used.

## Privacy contract

- Query: `is:unread`.
- Message retrieval format: `metadata`.
- Requested header: `Subject` only.
- Message bodies and snippets are not requested.
- Messages are not marked read.
- Labels are not modified.
- Gmail failure does not prevent ROBY startup.

## Certification

- Ruff: All checks passed.
- Focused wiring/OAuth/announcement/console tests: 53 passed.
- Full suite: 5918 passed, 1 skipped.
- Regression delta: zero failures; 12 additive tests.
