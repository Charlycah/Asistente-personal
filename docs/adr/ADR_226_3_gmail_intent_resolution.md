# ADR 226.3 — Gmail Intent Resolution

## Status

Accepted

## Context

M226.2 introduced Gmail semantic capabilities while preserving the provider-neutral
`mail.read` and `mail.send` Tool Gateway contracts. Requests still entered the
integration as action strings, so aliases and user-facing wording had no explicit,
auditable normalization boundary before capability and policy resolution.

ROBY needs deterministic intent interpretation without introducing natural-language
classification, provider coupling, OAuth, network calls, or a bypass around M61,
M62, or M63.

## Decision

Add an immutable Gmail intent-resolution layer before semantic capability
resolution.

The layer introduces:

- `GmailIntent` canonical intent identifiers;
- `GmailIntentDecision` with requested action, canonical action, semantic
  capability, and required payload-field metadata;
- `GmailIntentResolver` with a bounded alias table;
- a secret-free intent catalog;
- canonical action routing and canonical audit recording.

The canonical intents are recent, search, read, compose, draft, reply, and send.
Controlled aliases normalize deterministically, including summary/list/inbox/latest,
find/open, write/new, save, answer/respond, and deliver.

Resolution order is:

1. intent normalization;
2. semantic capability resolution;
3. local Gmail policy evaluation;
4. M61 Tool Gateway routing;
5. M63 permission and consent enforcement;
6. existing mail adapter execution.

## Compatibility

M226.3 preserves:

- all M226.1 and M226.2 canonical actions;
- the historical `PermissionError` contract for unsupported actions;
- existing `mail.read` and `mail.send` handlers;
- local send-disabled-by-default policy;
- immutable, secret-free status and audit boundaries;
- runtime composition and transport behavior.

## Boundaries

M226.3 does not:

- perform probabilistic or LLM-based intent classification;
- validate or expose payload values in the intent catalog;
- bypass capability registration, policy, confirmation, or consent;
- introduce OAuth, Google API dependencies, attachment transport, or network tests;
- mutate the official Runtime Composition Root.

## Consequences

Gmail requests now have a deterministic interpretation boundary before governance
and execution. Future conversational parsing may target these canonical intents
without coupling language understanding to gateway handlers or provider transport.
