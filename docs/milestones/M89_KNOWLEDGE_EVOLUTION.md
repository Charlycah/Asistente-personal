# M89 — Knowledge Evolution

M89 introduces the governed boundary through which ROBY may propose changes to
long-lived knowledge.

## Responsibilities

- derive traceable proposals from M88 reflection records;
- classify create, reinforce, supersede and retire actions;
- preserve references to M86 mental models and M74 knowledge items;
- record explicit approval, rejection or blocking decisions;
- keep approval separate from application.

## Non-responsibilities

M89 does not infer new facts, edit the PKB, authorize tools, change cognitive
policies or execute recommendations. It never treats a reflection as evidence
sufficient by itself.

## Core invariants

1. Every proposal references at least one reflection.
2. Non-create actions reference existing knowledge targets.
3. Auto-approval is forbidden.
4. Low confidence escalates risk.
5. High-risk approval attempts are blocked.
6. Approval is not application.
7. Inputs remain immutable.
8. Every proposal and decision has a stable SHA-256 identity.

## Integration

The manager is an optional `CognitivePipeline` dependency and contributes only
governance instructions to the system prompt. No proposal is created during a
normal turn without an explicit caller supplying reflection evidence and the
candidate content.
