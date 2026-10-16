# M225.5 — Conversation History Sanitization

M225.5 removes previously persisted runtime-observation and synthetic-role turns from the inference-only recent-history view.

## Acceptance criteria

- Reserved historical turns never appear in the final prompt or structured message list.
- Matching is trimmed and case-insensitive.
- A turn is removed when either side is reserved.
- The journal remains complete and immutable.
- Owner/session isolation and context bounds remain unchanged.
- `--observe` reports sanitizer and curator removal counts separately.
