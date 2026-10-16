# ROBY M227.4 — Attachments Governance

M227.4 adds deterministic attachment policy before Gmail provider execution.

## Governed controls

- safe basename normalization;
- SHA-256 content fingerprinting;
- per-attachment size limit;
- aggregate message attachment limit;
- attachment count limit;
- explicit allowed MIME types;
- blocked executable/script extensions;
- inbound quarantine decisions for unknown MIME types;
- secret-free counters and policy status.

## Default limits

- maximum attachment: 10 MiB;
- maximum aggregate attachments: 20 MiB;
- maximum count: 10.

The defaults are intentionally conservative and can be replaced through an injected
`AttachmentPolicy`.

## Gmail API integration

Draft and send operations build MIME multipart messages only after every outbound
attachment has passed governance. A rejected attachment prevents request execution.
No attachment is automatically opened, executed, downloaded, or scanned over the
network during tests.
