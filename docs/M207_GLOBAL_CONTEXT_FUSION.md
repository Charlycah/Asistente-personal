# M207 — Global Context Fusion

M207 fuses the governed outputs of M201–M206 into one immutable, session-scoped
context view.

## Capabilities

- groups current Blackboard facts by cognitive domain;
- includes M202 global constraints and M206 task dispositions;
- detects incompatible event values without hiding disagreement;
- exposes authorized and deferred actions separately;
- preserves exact source lineage;
- publishes a governed context status back to M201.

## Boundaries

M207 is advisory. It does not execute tasks, invoke tools, modify memory,
rewrite plans, select providers, or override executive arbitration.
