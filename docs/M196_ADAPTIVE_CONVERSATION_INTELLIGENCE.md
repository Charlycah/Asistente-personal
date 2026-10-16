# M196 — Adaptive Conversation Intelligence

M196 opens ROBY's next operational stage by adding deterministic adaptation to
the active conversation. It models the current topic, user goal, intent
evolution, response strategy, response depth, continuity, and coherence for each
owner/session boundary.

The capability is deliberately advisory. It does not call providers, execute
tools, persist private memory, modify plans, or initiate actions. Its signals are
projected through the official cognitive runtime as governed prompt context.

Acceptance criteria:

- active conversation state is isolated by owner and session;
- intent transitions distinguish continuation, refinement, correction, and
  topic shifts;
- response strategy and depth adapt deterministically to the current turn;
- state accumulation is bounded;
- official composition inserts M196 before later cognitive contributors;
- prompt enrichment preserves request settings and remains non-authoritative;
- failures continue to be contained by the cognitive runtime orchestrator.
