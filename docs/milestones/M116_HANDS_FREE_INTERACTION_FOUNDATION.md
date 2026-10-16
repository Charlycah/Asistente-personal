# M116 — Hands-Free Interaction Foundation

M116 adds a governed foundation for hands-free interaction on top of the Mobile Companion stack.

## Responsibilities

- Validate the complete M110/M111/M112/M115 derivation chain.
- Evaluate standby, push-to-talk, and continuous modes.
- Require explicit user consent and configurable audio prerequisites.
- Respect context confidence, freshness, attention, lock state, and transit policy.
- Produce immutable, deterministic, repository-backed decisions.

## Non-responsibilities

M116 does not activate microphones or speakers, capture audio, perform STT/TTS, listen for wake words, connect Bluetooth, send notifications, access sensors, mutate runtime or presence, or call mobile operating-system APIs.
