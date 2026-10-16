# M180 — End-to-End Local Conversation

M180 establishes ROBY's first official operational conversation loop on the laptop.

## Delivered

- `EndToEndLocalConversation` use case over M179, M178, and M177.
- Exact owner/session identity and response lineage on every turn.
- Ordered local JSONL turn journal with owner/session isolation and `0600` permissions.
- Session sequence continuity after runtime recreation.
- Explicit completed, partial, withheld, and failed turn outcomes.
- Environment-configurable journal path and persistence switch.
- Thin terminal adapter and interactive root `main.py`.
- No cognitive decisions in the console.
- No memory semantics, tool integration, formal trace model, or platform mutation.

## Environment

- `ROBY_RUNTIME_ROOT_FACTORY=module:function`
- `ROBY_RUNTIME_OWNER=Carlos`
- `ROBY_RUNTIME_SESSION_ID=desktop-main`
- `ROBY_RUNTIME_STATE_PATH=.roby/runtime_state.json`
- `ROBY_CONVERSATION_JOURNAL_PATH=.roby/conversation_turns.jsonl`
- `ROBY_CONVERSATION_PERSIST=1`

Use `/exit`, `/quit`, EOF, or Ctrl+C to close the local console.
