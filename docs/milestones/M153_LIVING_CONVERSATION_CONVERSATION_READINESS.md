# M153 — Living Conversation Conversation Readiness

M153 consumes governed M152 selection results and declares whether the selected presence opportunity is ready for later conversational decision layers.

- Full selection becomes `READY`.
- Partial selection becomes `READY_PARTIAL` when policy allows it.
- Deferred selection becomes `NOT_READY`.
- Confidence, recency, ownership, deduplication, and result limits remain governed.
- Exact M152 selection and M150 opportunity objects are preserved.
- No conversation decision, activation, timing selection, prompt generation, response realization, automation, or platform mutation is allowed.
