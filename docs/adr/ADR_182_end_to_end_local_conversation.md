# ADR-182 — End-to-End Local Conversation

## Status
Accepted

## Context
M179 makes ROBY's governed local runtime startable and durable, but it intentionally performs no conversation. The operational development runtime now needs one official path from local user input to the M177 governed pipeline and back to a visible response, while preserving M178 composition, M179 lifecycle, exact lineage, local privacy, and the future boundaries reserved for formal tracing, memory, and tools.

## Decision
Introduce `core.end_to_end_local_conversation` as the official local conversation use case.

- A turn can execute only while the M179 bootstrap is running.
- Owner and session identity come exclusively from the bootstrap configuration.
- Every turn is converted into the exact M177 request and executed through the already composed M178 pipeline.
- The returned turn preserves the M177 result id, M175 response id, execution flags, status, rationale, and timestamp.
- A local JSON Lines journal persists ordered session turns with private file permissions.
- Conversation history is scoped by owner and session and survives process restarts.
- The journal is operational session continuity, not cognitive memory; M183 remains responsible for memory integration.
- The console adapter performs input, exit handling, and rendering only. It contains no routing, policy, inference, retrieval, memory, or response-assembly logic.
- Provider failures remain contained by the governed pipeline and become explicit non-deliverable turn outcomes.
- M180 never authorizes platform mutation.

## Consequences
ROBY can now be started locally and used for real governed conversation from `main.py`. Sessions continue across restarts through a local auditable journal, while formal per-turn trace modeling remains reserved for M181 and development observability remains reserved for M182.
