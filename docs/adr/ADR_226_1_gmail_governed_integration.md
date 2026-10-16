# ADR 226.1 — Gmail Governed Integration

## Status

Accepted

## Context

ROBY already has a read-only mail adapter (M66) and a governed mail action adapter
(M67). Those adapters intentionally separate provider transport from the core, but
there is no single Gmail-specific composition boundary that binds one account,
local action policy, Tool Gateway routing, consent decisions, and secret-free audit
records.

Directly replacing M66/M67 or wiring Gmail into the cognitive runtime would create
regression risk and duplicate established governance.

## Decision

Add `GmailGovernedIntegration` as an incremental infrastructure composition layer.

The integration:

- composes the existing `MailReaderAdapter` and `MailActionAdapter`;
- registers both only through the existing Tool Gateway;
- binds the integration to one normalized, hashed account fingerprint;
- applies an explicit local allow/deny policy per action;
- keeps send disabled by default;
- preserves the existing `mail.read` and `mail.send` permission semantics;
- records bounded, immutable audit entries without addresses, passwords, message
  bodies, subjects, recipients, or provider credentials;
- delegates all provider operations to the existing IMAP/SMTP adapters;
- exposes a secret-free status snapshot.

## Boundaries

M226.1 does not:

- add Gmail OAuth or Google API dependencies;
- bypass M61 Tool Gateway or M63 consent;
- infer permission or consent;
- persist credentials or raw account identifiers;
- automatically register itself in the official runtime composition root;
- execute network calls during tests;
- alter conversation, provider, memory, or shutdown behavior.

## Consequences

ROBY gains one governed Gmail integration seam suitable for later OAuth transport and
runtime composition milestones. Existing M66/M67 contracts remain valid and no
existing capability names change.
