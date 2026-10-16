# RP.13 — Cognitive Reflection Engine

RP.13 adds a governed reflective pass over RP.11 agenda state and RP.12 executive
deliberation. Its purpose is not to produce another action plan. It evaluates
whether the current focus remains justified before ROBY carries that focus forward.

The engine can affirm a supported focus, request more evidence, wait for a blocked
condition to change, identify a stale focus, or recommend priority reassessment
when agenda candidates are too close or a low-escalation focus persists.

Reflection is deliberately bounded:

- it does not mutate `CognitiveAgendaSnapshot`;
- it does not execute capabilities or external actions;
- it does not replace RP.12 deliberation;
- it never requests user authorization;
- it exposes an immutable `CognitiveReflection` in resident cognitive state;
- its persistence counter is ephemeral and process-local.

The resident flow is now:

`runtime signals -> RP.11 agenda -> RP.12 deliberation -> RP.13 reflection -> RP.10 state`

Compatibility is preserved. `ContinuousCognitiveState.rationale` remains
`agenda:<key>` whenever an agenda focus exists. Detailed reflection is available
separately through `ContinuousCognitiveState.reflection`.
