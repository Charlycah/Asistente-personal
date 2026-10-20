# ADR 225.1 — Structured Conversation Messages

## Status

Accepted.

## Context

ROBY transported recent conversation context as one concatenated prompt. This preserved continuity but erased the semantic distinction between system instructions, user turns, and assistant turns before reaching chat-capable providers.

## Decision

Introduce the immutable `ConversationMessage` value object with the roles `system`, `user`, and `assistant`. `LLMRequest` now carries an ordered tuple of these messages while retaining `prompt` as a backwards-compatible fallback.

The governed context-continuity boundary constructs structured messages after curation. OpenAI-compatible providers send them directly in the `messages` payload. Providers that only accept text serialize them at their final adapter boundary.

## Post-M409.1 compatibility reconciliation

The original role-preservation contract remains valid. Governed system
guidance may precede conversational turns as a structured `system`
message. The first turn still contains exactly one conversational
`user` message, and its legacy `prompt` fallback remains unchanged.

`LLMRequest.messages` preserves the ordered structured conversation.
The canonical `LocalProviderRuntimeAdapter` composes configured system
style and governed request guidance without repeating an identical
instruction already present in the structured messages.

Reserved historical turns remain subject to the existing M225.5
sanitization contract. This reconciliation introduces no new provider,
authority, routing path, or conversation-history mutation.

## Consequences

- Conversation roles remain explicit across ROBY's provider-neutral runtime.
- Existing request builders and text-only providers remain compatible.
- Context curation still operates on journal turns before message construction.
- Persistent memory, retrieval, tools, and conversation replay remain distinct sources.
- Provider-specific formatting is delayed until the provider boundary.
