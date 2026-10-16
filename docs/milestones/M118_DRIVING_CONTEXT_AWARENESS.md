# M118 — Driving Context Awareness

## Objective
Provide a governed, declarative snapshot of the current driving situation so later Driving Companion layers can adapt interaction without acquiring sensor, map, route, vehicle, or platform data directly.

## Architectural fit
M117 remains the authority for whether Driving Companion operation is eligible. M118 consumes that immutable decision and adds a separate awareness layer describing contextual load. This preserves the global progression:

`Mobile Context → Hands-Free Eligibility → Driving Eligibility → Driving Context → Future Interaction Policy`

M118 does not duplicate M115 mobile context, M116 hands-free eligibility, or M117 driving activation. It creates the context contract that future driving interaction, navigation, ambient, and unified-companion layers may consume.

## Added contracts
- `VehicleMotionState`
- `DrivingDemandLevel`
- `DrivingContextLoad`
- `DrivingContextStatus`
- `DrivingContextAction`
- `DrivingContextPolicy`
- `DrivingContextSignal`
- `DrivingContextRequest`
- `DrivingContextSnapshot`
- `DrivingContextRepository`
- `InMemoryDrivingContextRepository`
- `DrivingContextAwarenessEngine`

## Context dimensions
- Declarative vehicle motion.
- Maneuver demand.
- Traffic complexity.
- Visibility demand.
- Driver attention availability.
- Passenger presence.
- Emergency declaration.
- Confidence and freshness.

## Invariants
- Ownership must match the M117 decision lineage.
- M117 remains authoritative for driving eligibility and mode.
- Upstream review, blocked, and not-applicable outcomes propagate conservatively.
- Only ready snapshots may allow speech or proactive interaction.
- Emergency and critical demand always suppress ordinary interaction suitability.
- Snapshots are immutable, deterministic, auditable, and repository-backed.

## Non-responsibilities
M118 performs no GPS, maps, routing, speed, acceleration, camera, microphone, Bluetooth, Android Auto, CarPlay, vehicle-bus, weather, traffic-service, or operating-system I/O. It does not detect driving, execute speech, choose content, deliver notifications, or mutate navigation state.

## Future compatibility
- Driving interaction policy can consume `load`, `speech_allowed`, and `proactive_interaction_allowed` without changing M118.
- Maps and navigation may later supply governed declarative signals without being owned by this domain.
- Visual Understanding may contribute observations through adapters while preserving the no-I/O core boundary.
- Ambient Context and Unified Companion can consume snapshots through integration layers rather than coupling directly to vehicle hardware.
