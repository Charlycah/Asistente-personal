# ADR 224.3 — LLM Request Trace & Context Injection Verification

## Status
Accepted.

## Context
M224.2 reconstructs recent session-scoped turns and injects them into the neutral `LLMRequest`. A real Ollama conversation still produced an answer inconsistent with the prior turn. Persistence and provider execution remained healthy, so the next required step is exact observability at the inference boundary rather than another behavioral change.

## Decision
The development-console observer reads the immutable pipeline result retained by the in-memory repository and exposes:

- count and size of recent conversational turns;
- current-message and final-prompt sizes;
- system-prompt size;
- context-source flags;
- selected provider and model;
- the exact prompt present in the provider execution request.

The full prompt is rendered only during automatic `python main.py --observe` output. Existing ordinary observation rendering remains redacted to preserve the M182 privacy contract. No trace content is added to the persistent journal or operational trace store.

## Consequences
M224.3 can prove whether the journal context reached the final provider boundary without changing provider behavior. The output may contain domestic conversation text when `--observe` is explicitly enabled, so that mode remains a development diagnostic and should not be shared unredacted.
