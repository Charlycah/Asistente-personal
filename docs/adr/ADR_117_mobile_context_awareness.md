# ADR-117 — Mobile Context Awareness

## Status
Accepted.

## Context
M110–M114 establish mobile eligibility, runtime, presence, notification intelligence, and background continuity. ROBY now needs a governed representation of mobile context without coupling the core to operating-system sensors or device APIs.

## Decision
Introduce `core.mobile_context` as an immutable, repository-backed decision layer. It consumes M112 presence and M114 continuity decisions plus an explicitly supplied declarative signal. It assembles an auditable context snapshot describing activity, attention, connectivity, power, orientation, lock state, user presence, confidence, and interaction suitability.

## Invariants
- M112 remains authoritative for mobile presence.
- M114 remains authoritative for background continuity.
- All timestamps are timezone-aware and freshness is policy-governed.
- Low-confidence, stale, or future observations require review.
- Upstream blocked, review, and not-applicable states propagate conservatively.
- Snapshot identifiers are deterministic and integrity-checked.
- Models and repository outputs are immutable.

## Boundaries
M115 does not read GPS, Bluetooth, accelerometer, camera, microphone, or operating-system state. It does not activate sensors, infer precise location, initiate interaction, send notifications, mutate runtime/presence/continuity, or persist raw sensor payloads.
