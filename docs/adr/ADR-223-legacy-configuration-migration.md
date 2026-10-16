# ADR-223 — Legacy Configuration Migration

## Status
Accepted.

## Context
Older ROBY installations stored operational preferences and secrets together in
`config/config.json`, plus OAuth material in `credentials.json` and
`token.pickle`. M222 introduced `.env` setup but did not provide a governed
migration path.

## Decision
M223 adds an explicit migration command that maps supported legacy preferences
into the official `.env` schema, creates a backup, and skips secrets by default.
Secrets can only be copied with an explicit unsafe opt-in. OAuth credential and
token files are never imported automatically.

## Consequences
Useful preferences are preserved, plaintext secret propagation is prevented by
default, and legacy phrase lists are retired in favor of ROBY's semantic intent
and governed tool authorization layers.
