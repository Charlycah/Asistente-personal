# ADR-118 — Hands-Free Interaction Foundation

## Status
Accepted

## Context
M115 provides a declarative mobile context snapshot, but ROBY still requires a governed boundary that determines whether a hands-free interaction is eligible before any audio, speech, wake-word, or platform integration exists.

## Decision
Introduce `core.hands_free` as an immutable decision layer over M110, M111, M112, and M115. It evaluates mobile mode, runtime, presence, context, consent, microphone permission, audio route, speaker availability, confidence, freshness, lock state, attention, and transit policy.

The layer emits `ready`, `review_required`, `blocked`, or `not_applicable`, with declarative actions and modalities. It does not activate hardware or execute speech I/O.

## Consequences
- Hands-free eligibility is auditable and deterministic.
- Continuous listening remains opt-in and policy-controlled.
- Driving Companion can consume a stable contract in M117.
- Audio capture, STT, TTS, wake words, Bluetooth, and operating-system integration remain outside M116.
