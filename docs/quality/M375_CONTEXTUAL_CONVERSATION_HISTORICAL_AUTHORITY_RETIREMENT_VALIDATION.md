# ROBY XI.2 — M375 contextual conversation historical authority retirement

## Scope

Governed retirement of the disconnected M375 `ConversationContextAuthority`
foundation and reconciliation with the current productive context-continuity
boundary.

## Retired

- `core/contextual_conversation.py`
- `tests/test_m375_contextual_conversation.py` (8 tests)

## Preserved current architecture

- `core.conversation_strategy:ConversationContext`
- `app.context_continuity_runtime:OfficialContextContinuityRuntimeGateway`
- `core.conversational_context_continuity`
- context curation and conversation-history sanitization
- official runtime construction/registration of the context-continuity gateway

## Historical preservation

The original M375 document is archived unchanged at:

`docs/history/legacy-conversation/M375_CONTEXTUAL_CONVERSATION.md`

Historical M375 changelog/decision entries remain historical; a current
supersession decision is appended instead of rewriting them.

## Expected test delta

Certified input baseline: **12,530 PASS**.

- 8 direct historical M375 tests retired.
- 1 architectural retirement/current-successor guardrail added.
- M390.4 test count unchanged; only an obsolete forbidden-name token is removed.

Collection after surgery: **12,523 tests collected**.

Local focused validation: **25 PASS** across the retirement guardrail,
M390.4 relational boundary and current context-continuity/curation/sanitization
contracts. M361 baseline reproducibility: **5 PASS**.

Expected owner baseline: **12,523 PASS · 0 FAIL · Ruff clean**.

## Certification state

**IMPLEMENTED / PENDING OWNER CERTIFICATION**
