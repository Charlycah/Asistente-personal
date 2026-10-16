# M206 — Executive Arbitration

M206 introduces ROBY's governed executive arbitration boundary.

It converts M205 cognitive schedules into immutable decisions that authorize, defer, or reject each task while preserving constraints, dependencies, source lineage, and session isolation. Blocked schedules are rejected, attention-required schedules authorize repair work before dependent tasks, and ordinary schedules are authorized for downstream execution.

M206 does not itself execute tools or cognitive contributors. It publishes a governed executive decision to the M201 Blackboard for later integration milestones.
