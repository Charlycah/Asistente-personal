# ROBY M253 — Conversation Runtime

M253 connects ROBY's existing governed living-conversation contributor to the
official runtime composition root.

## Operational capability

`conversation.living_runtime` is the thirteenth official capability. It reuses:

- `LivingConversationRuntimeContributor`
- `StablePersonalityEngine`
- `OfficialRuntimeCapabilityRegistry`
- the official cognitive runtime orchestration path

The capability is activated only by explicit requests such as adapting or
evaluating the conversation. Ordinary turns do not activate it.

## Governance

- No autonomous conversation starts.
- No passive observation or sensors are enabled.
- No tools, providers, or mutations are executed by the capability.
- The user floor is always preserved.
- The existing twelve capability positions remain unchanged.

## Certification

- Focused tests: 26 passed.
- Ruff: all checks passed.
- Full suite: 6084 passed, 0 skipped.
- Zero observed regressions.
