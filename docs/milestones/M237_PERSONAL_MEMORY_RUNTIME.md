# M237 — Personal Memory Runtime

## Objective

Connect ROBY's existing governed cognitive-memory runtime to the official household composition root. Carlos and Cristina share the single `Familia` runtime identity, so learned memories and recalled context live in one persistent household store.

## Operational behavior

- Relevant durable statements are learned after a completed conversation turn.
- Later turns recall matching memories and add a bounded memory context to the provider request.
- Storage is SQLite under `.roby/memory`.
- Recall and learning are independently governed from the single `.env`.
- The desktop and console entrypoints use the same memory runtime through the official composition root.
- No new RAG, vector database, or parallel bootstrap is introduced.

## Configuration

```env
ROBY_PERSONAL_MEMORY_ENABLED=true
ROBY_PERSONAL_MEMORY_PATH=.roby/memory
ROBY_PERSONAL_MEMORY_RECALL_ENABLED=true
ROBY_PERSONAL_MEMORY_LEARNING_ENABLED=true
ROBY_PERSONAL_MEMORY_RECALL_LIMIT=5
```

## Certification

- Focused: 31 passed.
- Ruff: all checks passed.
- Full suite: 6002 passed, 0 skipped.
- Zero observed regressions.

