# ADR 228.2 — Gmail Startup Announcement Runtime Wiring

## Status
Accepted.

## Context
M228.1 introduced governed interactive OAuth activation and a metadata-only unread-subject announcer, but the official `python main.py --observe` entrypoint did not compose or invoke them. The development console therefore started without OAuth activation or the historical read-only startup announcement.

## Decision
Add a thin deployment wiring module invoked after the console banner and before the first user prompt. The wiring:

- remains disabled unless Gmail and the startup announcement are enabled;
- identifies the account only to derive a SHA-256 fingerprint;
- activates or refreshes OAuth through `GoogleOAuthDeploymentAdapter`;
- builds the Gmail API client lazily;
- queries `is:unread` and requests only `Subject` metadata;
- never requests message bodies or mutates mailbox state;
- degrades safely and never blocks the main ROBY console.

No password authentication, pickle persistence, or architectural bypass is introduced.

## Consequences
The official development console can now reproduce the historical behavior: announce the unread count and subjects before displaying the prompt. Deployment failures remain isolated from the conversational runtime.
