# PM2 / M164 — Natural Greeting Response

M164 realizes a short, natural reply for greeting entries produced by M163.
It removes command acknowledgement language such as `Recibido. Hola ROBY.` and
replaces it with deterministic conversational alternatives.

## Scope

- Preserve exact M163 lineage.
- Generate only for `ConversationEntryKind.GREETING`.
- Support morning, afternoon, evening, night, and neutral variants.
- Avoid recently used responses when another variant is available.
- Keep visible response text without accents.
- Remain local and deterministic.

## Explicit non-goals

- General dialogue generation.
- Provider selection or model calls.
- Internet access.
- Full ROBY voice governance.
- Platform mutation.
