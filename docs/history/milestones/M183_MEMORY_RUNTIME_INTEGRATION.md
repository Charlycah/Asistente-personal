# M183 — Memory Runtime Integration

## Objective

Integrate ROBY's existing cognitive memory capabilities into the official local operational runtime while preserving local-first governance, identity privacy, exact composition boundaries, and restart continuity.

## Scope

M183 adds:

- an explicit memory runtime integration port consumed by M178 preparation;
- governed recall before local provider inference;
- learning evaluation after an operational turn completes;
- reuse of M36–M39 cognitive memory, recall, and prompt-context contracts;
- physically separate SQLite stores for each private owner identity;
- optional shared-family recall, disabled by default;
- deterministic owner-safe database names and private local file permissions;
- memory continuity across process and runtime recreation.

## Runtime sequence

1. The composition root remains side-effect free.
2. Turn preparation builds the original inference request.
3. When configured, the memory runtime recalls relevant private memory and explicitly enabled shared memory.
4. Relevant memories are converted through the existing M39 prompt-context builder.
5. The governed M177 pipeline executes normally.
6. After the pipeline returns, the memory learning policy evaluates the user turn and stores only approved candidates in the owner's private store.

## Privacy and governance

Private memory is isolated by owner at the storage boundary. Owner names are not exposed in database filenames. Shared-family recall is opt-in and does not receive automatic writes in M183. Memory can be independently disabled for recall or learning. Composition itself never reads or writes memory.

## Exclusions

M183 does not add tool execution, automatic shared-memory writes, semantic embeddings, remote storage, memory administration UI, retention/forgetting policy changes, or new cognitive learning rules. Tool runtime integration remains M184.
