# M195 — Operational Acceptance Suite

M195 validates ROBY as one operational cognitive runtime rather than as isolated
modules. The acceptance suite exercises the official composition root, local
bootstrap, conversation pipeline, memory, living conversation, governed
reasoning, executive planning, adaptive reflection, executive coordination,
tool runtime, provider execution, persistence, traces, shutdown, and restart.

The suite is observational. It grants no new authority, performs no hidden
network access, and does not weaken governance. Failures are normalized by
exception class without persisting private exception messages.

Acceptance criteria include:

- the official runtime starts and composes once;
- all official cognitive stages can contribute in declared order;
- a complete turn reaches the local provider and persists journal and trace;
- an explicit read-only tool executes through the governed gateway;
- platform mutation remains false;
- memory and turn sequence survive recreation;
- shutdown is clean and provider failures remain contained;
- observing reports, history, traces, or state does not repeat execution.
