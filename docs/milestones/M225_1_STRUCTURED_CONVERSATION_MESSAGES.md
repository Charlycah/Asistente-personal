# M225.1 — Structured Conversation Messages

## Objective

Preserve conversational roles from ROBY's governed runtime through provider execution without removing compatibility with legacy text prompts.

## Delivered

- Immutable `ConversationMessage` model.
- Structured `messages` collection on `LLMRequest`.
- Role-preserving construction after recent-context curation.
- Direct OpenAI-compatible chat payloads.
- Final-boundary serialization for text-only Ollama generation.
- Compatibility tests for first-turn and historical-context requests.

## Acceptance

- Existing callers may continue to provide only `prompt`.
- A first turn carries exactly one conversational `user` message without changing its fallback prompt. Governed `system` guidance may precede that message under the later Post-M409.1 contract.
- Historical user and assistant turns retain their roles and order.
- Provider routing copies structured messages without mutation.
- Text-only providers receive deterministic serialization.
