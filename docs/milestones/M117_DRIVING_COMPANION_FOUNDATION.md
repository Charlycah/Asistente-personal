# M117 — Driving Companion Foundation

M117 opens the Driving Companion domain with a governed, declarative foundation built on M115 and M116.

## Responsibilities
- Validate owner and upstream lineage.
- Evaluate freshness, confidence, consent, passenger policy, hands-free readiness, declared driving context, and stationary/transit conditions.
- Produce inactive, passenger, driver-ready, or driver-active decisions.
- Preserve deterministic identifiers, rationale, modalities, and repository history.

## Non-responsibilities
M117 does not access GPS, maps, routes, speed, acceleration, vehicle sensors, Bluetooth, Android Auto, CarPlay, microphone, STT, TTS, or audio output. It does not detect driving or activate any mode physically.

## Verification
- Ruff clean.
- 39 focused M117 tests.
- Full suite passing with no regressions.
