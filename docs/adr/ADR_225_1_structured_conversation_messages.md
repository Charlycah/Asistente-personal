# ADR 225.1 — Structured Conversation Messages

## Status

Accepted.

## Context

ROBY transported recent conversation context as one concatenated prompt. This preserved continuity but erased the semantic distinction between system instructions, user turns, and assistant turns before reaching chat-capable providers.

## Decision

Introduce the immutable `ConversationMessage` value object with the roles `system`, `user`, and `assistant`. `LLMRequest` now carries an ordered tuple of these messages while retaining `prompt` as a backwards-compatible fallback.

The governed context-continuity boundary constructs structured messages after curation. OpenAI-compatible providers send them directly in the `messages` payload. Providers that only accept text serialize them at their final adapter boundary.

## Consequences

- Conversation roles remain explicit across ROBY's provider-neutral runtime.
- Existing request builders and text-only providers remain compatible.
- Context curation still operates on journal turns before message construction.
- Persistent memory, retrieval, tools, and conversation replay remain distinct sources.
- Provider-specific formatting is delayed until the provider boundary.
