# M224.3 — LLM Request Trace & Context Injection Verification

## Objective
Verify, from the development console, the exact conversational context and prompt delivered to the governed local-provider boundary.

## Observable output
After each turn under `python main.py --observe`, ROBY reports:

- `context turns`, context characters, and current-message characters;
- `context_sources` for journal, memory, retrieval, and tools;
- final `llm_request` character counts;
- selected provider/model payload identity;
- `llm_prompt_begin` / `llm_prompt_end` containing the exact inference prompt.

## Non-goals
This milestone does not alter routing, persistence, memory promotion, provider selection, or inference behavior. It does not decide whether a domestic response can bypass Ollama; that remains a later orchestration milestone.

## Validation scenario

1. Run `python main.py --observe`.
2. Say `Mi nombre es Carlos.`
3. Say `¿Cómo me llamo?`
4. Confirm the second observation reports `context turns=1` and the prompt includes both the first user/assistant turn and the current question.
