# M224.2 — Conversational Context Continuity Hotfix

## Objective
Restore bounded recent-turn continuity for the official local ROBY runtime without conflating conversation replay with persistent memory.

## Implementation
- Added immutable `ConversationalContextTurn` transport data.
- Added configurable recent-context limits to `EndToEndLocalConversationConfig`.
- Reconstructed recent context from the owner/session-scoped local journal.
- Added common request enrichment in `GovernedRuntimePreparation` before memory, cognitive, tool, and provider execution stages.
- Preserved exact single-turn prompts when no context is available.

## Acceptance coverage
- Current message follows prior user/assistant transcript.
- Context survives runtime recreation.
- Session and owner journal scopes remain isolated.
- Maximum turn limit retains only the newest turns.
- Context can be disabled explicitly.
- Existing M180 and M224 official-factory contracts remain valid.
