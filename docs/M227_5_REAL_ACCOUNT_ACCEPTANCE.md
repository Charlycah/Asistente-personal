# ROBY M227.5 — Real Account Acceptance Tests

M227.5 adds an opt-in acceptance harness for validating a deployment-owned Gmail account against the fully governed runtime.

## Environment

```dotenv
ROBY_GMAIL_ACCEPTANCE_ENABLED=false
ROBY_GMAIL_ACCEPTANCE_ALLOW_WRITE=false
ROBY_GMAIL_ACCEPTANCE_SEARCH_QUERY=in:inbox
ROBY_GMAIL_ACCEPTANCE_RECIPIENT=
ROBY_GMAIL_ACCEPTANCE_MAX_RESULTS=3
ROBY_GMAIL_ACCEPTANCE_FIXTURE_READY=false
```

The default mode is disabled. When enabled without write permission, the harness performs list, search and conditional read operations. Write mode additionally requires an explicit recipient and validates draft creation and sending with idempotency.

## Running the live gate

The deployment must compose the real Gmail runtime and replace or extend the fixture guard in `tests/acceptance/test_m227_5_live_gmail_account.py`. Credentials remain external and must be provided through M227.1 and M227.3.

No live network request is made by the normal suite.
