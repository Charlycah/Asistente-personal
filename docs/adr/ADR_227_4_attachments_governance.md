# ADR 227.4 — Attachments Governance

## Status

Accepted.

## Context

The Gmail API backend can now create drafts and send messages, but attachment data
must not cross the provider boundary without deterministic local validation. Gmail
provider limits alone are insufficient because ROBY must reject unsafe names, blocked
file types, excessive payloads, and unknown inbound media before execution or use.

## Decision

Introduce `GmailAttachmentsGovernance` as a provider-independent policy authority.
It normalizes filenames, computes SHA-256 digests, enforces per-item, aggregate, and
count limits, blocks executable extensions, permits an explicit MIME allowlist, and
quarantines unknown inbound MIME types by default. Outbound violations fail before
the Gmail API request is executed.

The Google Gmail API backend composes governed outbound attachments into standard
MIME multipart messages. Attachment bytes, filenames, digests, and message values
are excluded from observable status.

## Consequences

- Attachments are denied by default outside the configured MIME allowlist.
- Inbound unknown types are represented as quarantined decisions, not downloaded or
  opened automatically.
- Deployment-specific malware scanning can be added later behind the same decision
  boundary.
- No antivirus engine, network call, or new mandatory dependency is introduced.
