# RP.20.2 Environment compatibility

## Mail switches

ROBY exposes three independent Gmail/mail switches:

- `ROBY_MAIL_READER_ENABLED`: canonical switch for the conversational `mail.read_runtime` capability.
- `ROBY_GMAIL_ENABLED`: enables the Gmail runtime composition and OAuth-backed integration.
- `ROBY_GMAIL_STARTUP_ANNOUNCEMENT_ENABLED`: enables the startup subject announcement when Gmail is available.

`ROBY_MAIL_ENABLED` remains a legacy fallback only when `ROBY_MAIL_READER_ENABLED` is absent.
An exact capability-inventory test must set every optional capability switch explicitly so a developer `.env` cannot alter the expected tuple.

Variables loaded from `.env` are process configuration; they do not have to appear in the parent PowerShell environment.
