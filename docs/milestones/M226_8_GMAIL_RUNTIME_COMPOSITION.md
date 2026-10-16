# ROBY M226.8 — Gmail Runtime Composition

M226.8 integrates the governed Gmail architecture into ROBY's official Runtime
Composition Root without making Gmail mandatory for startup.

## Environment switch

`ROBY_GMAIL_ENABLED` accepts `1`, `true`, `yes`, or `on` (case-insensitive).

- unset/false: Gmail is omitted from the composed runtime;
- true without provider dependencies: Gmail is observable as `degraded` with
  `configuration_missing`;
- true with a complete graph and ready OAuth: Gmail is `ready`.

The milestone deliberately does not load credential files or construct a real Google
client. Those provider-specific factories belong to the end-to-end certification
milestone.
