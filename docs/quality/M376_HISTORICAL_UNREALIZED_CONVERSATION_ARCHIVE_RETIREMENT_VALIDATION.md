# M376 Historical Unrealized Conversation Archive Retirement Validation

Status: IMPLEMENTED / PENDING OWNER CERTIFICATION.

Retired: `core/long_term_conversation.py` and its eight direct historical tests. The original milestone document is preserved byte-identically under `docs/history/legacy-conversation/`. No productive runtime, store, writer or Memory authority was replaced or added.

Current boundary: the operational conversation journal is session/turn history; Living Conversation is longitudinal topic/thread continuity; Cognitive Memory remains governed by the existing memory authority / `OfficialMemoryGateway`. Conversation occurrence or summarization does not authorize automatic Memory admission.

Expected owner baseline from certified 12,520: -8 historical tests +1 architecture guardrail = **12,513 tests**, with Ruff clean and zero failures.
