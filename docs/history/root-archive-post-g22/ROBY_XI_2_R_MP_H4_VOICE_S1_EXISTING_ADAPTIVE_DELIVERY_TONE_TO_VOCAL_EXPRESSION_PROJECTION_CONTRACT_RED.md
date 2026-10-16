# R-MP-H4-VOICE-S1 — Contract RED

Existing Adaptive Delivery Tone → Vocal Expression Projection

## Status

CONTRACT RED. STOP BEFORE GREEN.

## Proven residual

ROBY already has one canonical expressive modulation authority,
`AdaptivePersonalityAuthority`, whose immutable `AdaptivePersonalityProfile` exposes the
already-decided `delivery_tone`. ROBY also has a productive vocal path through
`VoiceResponseReader`, `VoiceProsodyFormatter`, and `VoiceOutput`.

The missing bounded seam is projection: the already-authorized delivery tone does not
currently reach vocal expression. `VoiceResponseReader` and `VoiceProsodyFormatter`
consume only response text.

## Existing owners preserved

- `AdaptivePersonalityAuthority` remains the only authority that decides adaptive
  expressive modulation.
- `AdaptiveDeliveryTone` remains the canonical delivery-tone vocabulary.
- `VoiceProsodyFormatter` remains the bounded preparation surface for spoken delivery.
- `VoiceResponseReader` remains the response-to-voice adapter.
- `VoiceOutput` and provider implementations remain synthesis/output concerns below
  the expression boundary.

No new personality, emotion, expression, voice-identity, reasoning, or provider
authority is authorized.

## Required S1 behavior

1. Vocal expression MAY receive an optional, already-decided canonical
   `AdaptiveDeliveryTone`.
2. Absence of a delivery tone MUST preserve the historical text-only vocal path.
3. `VoiceResponseReader` MUST be able to forward the optional canonical tone to the
   existing `VoiceProsodyFormatter`; it MUST NOT calculate or infer a tone.
4. `VoiceProsodyFormatter` MAY project the supplied tone into bounded spoken-delivery
   preparation while preserving the authorized semantic content.
5. The projection MUST remain deterministic and provider-independent.
6. Invalid/noncanonical tone input MUST fail safely; it MUST NOT create a new tone or
   infer cognitive/emotional state.
7. Existing callers using `read(response)` and `format(text)` MUST remain compatible.

## Permanent boundaries

**THOUGHT != EXPRESSION**

**EXPRESSIVE PROSODY != CLAIM OF SUBJECTIVE EMOTION**

**VOICE TIMBRE != COGNITIVE IDENTITY**

The vocal layer MUST NOT instantiate or call `AdaptivePersonalityAuthority`.
The vocal layer MUST NOT derive tone from response text, user state, affect, urgency,
provider capability, or acoustic output.
The vocal layer MUST NOT mutate beliefs, reasoning, memory, learning, planning,
initiative, authorization, execution, or the semantic claim being spoken.
The expression seam MUST NOT depend on Edge TTS or any concrete provider.

## Non-goals

This block does NOT authorize ROBY Voice Identity, timbre selection, voice cloning,
provider migration, SSML generalization, subjective emotion, new affect inference,
new communicative-intent authority, new speech engine, or changes to M377 tone
selection.

## RED expectation

The contract tests must fail only because the optional canonical delivery-tone
projection seam is not implemented yet. Protective ownership/provider/compatibility
checks should already pass.

STOP BEFORE GREEN.
