# ADR-143 — Presence Context Integration

## Status
Accepted

## Context
M140 produces governed anonymous presence-situation assessments. ROBY needs a final
ambient-presence boundary that can expose those assessments together with explicitly
declared device, conversation, spatial, and temporal context without inferring missing
facts or authorizing behavior.

## Decision
Introduce M141 as a pure integration layer. It consumes only valid M140 results,
preserves the selected assessment and ambient lineage, attaches only declared external
context dimensions, and classifies the output as integrated or partial according to a
policy threshold.

M141 does not reinterpret presence, infer identity, activity, or intent, track people,
decide responses, adapt behavior, access sensors, call providers, or automate actions.

## Consequences
The Ambient Context chain gains a stable output boundary suitable for future governed
consumers while keeping observation, understanding, temporal reasoning, semantic
interpretation, situation assessment, and context integration independently testable.
