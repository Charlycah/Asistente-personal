# ROBY M254 — Voice Style Runtime

M254 integrates the existing deterministic M165 ROBY voice style policy into the
official operational runtime and capability registry.

## Operational capability

`voice.style_runtime`

Supported explicit commands include:

- `Evaluá el estilo de voz: <texto>`
- `Revisá el estilo de voz: <texto>`
- `Aplicá el estilo de ROBY: <texto>`
- `Estado del estilo de voz`

The runtime normalizes whitespace and configured diacritics, detects forbidden
bureaucratic phrases, and exposes the result without provider calls, network
access, storage changes, or platform mutation.

## Architectural constraints

- Reuses `ROBYVoiceStylePolicy` from M165.
- Does not create a second style engine.
- Does not automatically rewrite every ROBY response.
- Requires an explicit conversational request.
- Is registered after `conversation.living_runtime`, preserving all previous
  capability positions.
- Does not modify `.env`.

## Certification

- Focused tests: 42 passed.
- Ruff: All checks passed.
- Full suite: 6089 passed.
- Skipped: 0.
- Observed regressions: 0.
