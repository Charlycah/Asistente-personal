# ROBY XI.2 — Same-Turn Authorized Memory Write → User-Visible Outcome

Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**.

Starting owner-certified baseline: **12,486 PASS · 0 FAIL · Ruff clean**.

The existing desktop ingress now binds one execution callback to the same
`OfficialROBYRuntime` already used for pending-request lookup and M369 response
evaluation.

When the existing M369 authority returns no exact execution evidence, the human
utterance continues through the normal conversational brain exactly once.

When exact M369 execution evidence exists, the adapter delegates
`session_id + authorization` to
`OfficialROBYRuntime.execute_pending_authorized_governed_memory_write(...)`,
receives the existing productive result, converts it to a deterministic
user-visible `UIResponse`, and returns immediately.

The same utterance is therefore not sent through `_brain.process(...)` after
productive execution.

The UI does not retrieve the governed write request, inspect authorization
phrases, call productive wiring directly, or call the Memory writer.

Protected gateway surfaces remain unchanged.

Invariant:

**ONE HUMAN TURN → ONE SEMANTIC PATH**
