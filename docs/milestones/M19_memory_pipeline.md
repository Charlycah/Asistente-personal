# M19 — Memory Pipeline

## Objective

Activate ROBY memory through a small pipeline layer without introducing semantic memory, persistence, embeddings, or recall-driven behavior.

M19 makes memory capture explicit and testable while keeping memory non-critical for the main `ROBY.process()` contract.

## Scope

Added:

- `core.memory_pipeline.MemoryPipeline` protocol.
- `core.memory_pipeline.StoreBackedMemoryPipeline`.
- `ROBY.__init__(memory_pipeline=...)` optional dependency.
- Default store-backed pipeline using `ROBY.memory_store`.
- User input capture during `ROBY.process()`.
- Final user response capture during `ROBY.process()`.

Out of scope:

- semantic recall;
- embeddings;
- persistent storage;
- memory-based planning;
- memory search;
- UI or voice integration.

## Pipeline contract

For every successful ROBY turn, the memory pipeline captures:

```text
user_input
↓
conversation / execution / response
↓
user_response
```

### User input item

```text
content: original user text
metadata:
  kind: user_input
  component: ROBY
  session_id: <session id | None>
```

### User response item

```text
content: final response text
metadata:
  kind: user_response
  component: ROBY
  session_id: <session id | None>
  status: <response status>
```

## Failure contract

Memory is non-critical in M19.

If a `MemoryStore` fails while capturing a memory item:

- the exception is not propagated;
- `ROBY.process()` continues normally;
- the public response contract remains unchanged.

This keeps memory as an auxiliary capability rather than a hard dependency of the core interaction flow.

## Architectural decision

ROBY does not construct `MemoryItem` objects directly. It delegates memory capture to `MemoryPipeline`.

```text
ROBY.process()
    ↓
MemoryPipeline
    ↓
MemoryStore
```

This keeps `ROBY.process()` focused on orchestration and lets future milestones evolve memory rules independently.

## Tests added

Validated:

- the pipeline captures user input as a `MemoryItem`;
- the pipeline captures user responses as a `MemoryItem`;
- `ROBY.process()` captures successful turns through the memory pipeline;
- failed conversation resolution captures only user input, not a response;
- memory store failures do not propagate from the pipeline;
- `ROBY.process()` does not fail when memory capture fails.

## Current state

M19 activates write-only memory capture.

Memory recall remains intentionally inactive and should be introduced in a later milestone only after its architecture and tests are defined.
