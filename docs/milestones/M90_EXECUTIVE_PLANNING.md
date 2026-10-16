# M90 — Executive Planning

M90 introduces a governed framework for strategic, multi-horizon planning.

## Responsibilities

- represent near-, mid- and long-horizon plans;
- define objectives with explicit success criteria and priorities;
- organize milestones with ordered dependencies;
- preserve constraints and provenance from M86, M88 and M89;
- maintain immutable, contiguous plan revisions;
- govern lifecycle transitions from draft to completion or cancellation.

## Non-responsibilities

M90 does not schedule work, create tasks automatically, invoke tools, approve
permissions, execute milestones, change knowledge or replace M46, M69, M70 or
M75.

## Core invariants

1. Every plan has an owner, purpose, objectives and milestones.
2. Milestone sequences are contiguous and dependencies are explicit.
3. References must be unique, non-blank and internally valid.
4. Every change creates a new immutable revision.
5. First revisions start at one and repository history is contiguous.
6. Long-horizon and critical plans require review.
7. Lifecycle transitions follow an explicit state machine.
8. An active plan is not an executing plan.
9. M90 never authorizes direct execution.
10. Plan identities are deterministic SHA-256 fingerprints.

## Integration

`ExecutivePlanningManager` is an optional `CognitivePipeline` dependency. It
contributes governance instructions to the system prompt only. Plans are
created by explicit callers that provide objectives, milestones, constraints
and any selected cognitive references.
