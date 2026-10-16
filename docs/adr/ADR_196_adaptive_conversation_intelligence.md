# ADR 196 — Adaptive Conversation Intelligence

## Decision

ROBY will derive bounded, deterministic conversation-state and response-adaptation
signals for each active session. The capability is advisory and participates in
the official cognitive runtime before reasoning, planning, reflection, and
executive coordination.

## Rationale

After M195 validated the complete operational runtime, ROBY needs a coherent way
to adapt response strategy, depth, and continuity as user intent evolves across
turns. Existing living-conversation capabilities govern timing and opportunity;
M196 complements them by modeling the active conversational state of the current
session.

## Consequences

- state is isolated by owner and session and remains process-local by default;
- intent evolution distinguishes initial, continuation, refinement, correction,
  and topic-shift transitions;
- adaptation selects direct, explanatory, collaborative, technical, or concise
  response strategies;
- prompt contributions are advisory and grant no tool, provider, memory,
  planning, or mutation authority;
- bounded state prevents unbounded accumulation;
- deterministic state identifiers preserve traceability without exposing raw
  conversation content as references.
