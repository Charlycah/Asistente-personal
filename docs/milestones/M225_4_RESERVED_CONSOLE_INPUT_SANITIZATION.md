# M225.4 — Reserved Console Commands & Input Sanitization

M225.4 hardens the M221 development console by classifying terminal input before
it can cross the conversation-runtime boundary.

## Acceptance criteria

- Reserved operational prefixes are rejected locally.
- Rejected input is not sent to the provider and is not persisted.
- Normal conversation and governed `/tool` requests remain unchanged.
- Exit, EOF, and keyboard-interrupt shutdown behavior remains unchanged.
- Prefix matching is case-insensitive and tolerates surrounding whitespace.
- Focused tests cover classification, runtime isolation, journal isolation, and
  recovery to the next valid user turn.
