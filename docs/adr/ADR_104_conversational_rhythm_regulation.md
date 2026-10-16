# ADR-104 — Conversational Rhythm Regulation

## Status
Accepted.

## Context
M93–M101 govern whether ROBY should enter a conversation, when an opportunity is appropriate, what reflective and intellectual contribution to form, how to realize it, what presence to adopt, and how to assess the subsequent feedback. The architecture still needs an explicit, auditable decision about conversational cadence after feedback without turning that decision into scheduling or delivery.

## Decision
Introduce M102 as a channel-neutral conversational rhythm regulator. It consumes an immutable M101 feedback assessment plus local exchange observations and returns an immutable decision containing:

- a governed rhythm: brisk, steady, measured, paused, or closing;
- a minimum conversational interval;
- a maximum number of consecutive ROBY turns;
- whether a follow-up prompt remains permissible;
- whether the user floor must be explicitly preserved;
- rationale and deterministic identity.

## Boundaries
M102 does not sleep, wait, schedule, deliver, rewrite content, select a channel, synthesize voice, update memory, learn preferences, or alter upstream M93–M101 records. Intervals are advisory metadata for later orchestration layers.

## Consequences
Conversational pacing becomes explicit, testable, conservative, and reusable by future text, mobile, driving, voice, and ambient companions without coupling FASE X to any delivery medium.
