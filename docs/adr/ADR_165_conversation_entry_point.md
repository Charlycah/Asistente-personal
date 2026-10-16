# ADR-165 — Conversation Entry Point

## Decision

Introduce M163 as a declarative conversation-entry classifier downstream of M162.
It recognizes the conversational shape of a user message without generating a reply,
calling a provider, accessing the network, or mutating the platform.

## Rationale

A greeting such as `Hola ROBY` must not enter the command-confirmation path. Separating
entry classification from response realization lets M164 and M165 produce natural,
varied language while preserving deterministic routing and testability.

## Consequences

- M163 consumes an M162 readiness result.
- Ready and degraded runtime states may be classified.
- Blocked runtime states withhold conversation entry.
- The assistant name alone is treated as an attention call.
- Reply generation remains outside this module.
