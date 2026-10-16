# ADR 224.2 — Conversational Context Continuity Hotfix

## Status
Accepted for local certification.

## Context
ROBY M224.1 persists operational conversation turns in the local JSONL journal, but each new governed inference request contains only the current user text. The local provider therefore receives no recent dialogue even when the same owner and session already have persisted turns.

## Decision
The end-to-end local conversation runtime reconstructs a bounded sequence of completed recent turns from the active journal scope and transports it as immutable conversational context on `GovernedConversationPipelineRequest`.

`GovernedRuntimePreparation` is the single common boundary that enriches the provider-neutral `LLMRequest`. It prepends the recent transcript before the current prompt while preserving the request's system prompt, model, token limits, temperature, and metadata.

The context is constrained by both a maximum turn count and a maximum character count. Defaults are eight turns and 12,000 characters. Context selection is strictly scoped by normalized owner and exact session identifier.

## Separation from persistent memory
Conversational context is short-term replay of recent dialogue. It is not promoted into persistent semantic memory, identity, preferences, or profile facts. Existing memory runtime enrichment remains a separate later stage.

## Consequences
- Multi-turn local conversations can reference immediately preceding dialogue.
- Context survives process/runtime recreation because it is reconstructed from the journal.
- Profiles and sessions remain isolated.
- Prompt growth is bounded and configurable.
- First-turn and disabled-context behavior remain backward compatible.
