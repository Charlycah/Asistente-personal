# M197 — Conversational Repair and Clarification Intelligence

M197 extends M196 with deterministic detection of dialogue conditions that can
cause ROBY to answer against an incomplete or unstable conversational target. It
classifies missing references, underspecified requests, uncertain intent,
correction transitions, and abrupt topic shifts, then emits a bounded advisory
repair action.

The capability never blocks the runtime, calls providers, executes tools,
rewrites memory, or changes plans. It contributes only governed prompt guidance
through the official cognitive runtime and is ordered immediately after M196.

Acceptance criteria:

- grounded requests proceed without unnecessary clarification;
- missing references and underspecified requests produce one targeted repair
  recommendation;
- corrections are confirmed before the new scope is applied;
- abrupt topic shifts are acknowledged without resisting the new objective;
- assessment identifiers are deterministic and contain no raw prompt content;
- M197 consumes M196 state when available but remains independently optional;
- provider request settings and metadata are preserved;
- failures remain contained by the cognitive runtime orchestrator.
