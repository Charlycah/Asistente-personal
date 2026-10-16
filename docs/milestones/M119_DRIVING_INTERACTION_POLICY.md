# M119 — Driving Interaction Policy

## Objective
Convert the immutable M118 driving-context snapshot into a governed interaction envelope that declares whether ROBY may listen, respond, initiate, interrupt, acknowledge, defer, or withhold an interaction while driving.

## Architectural fit
M117 remains responsible for Driving Companion eligibility. M118 remains responsible for describing contextual load. M119 consumes those contracts and selects interaction constraints without realizing conversation or executing any modality.

`Driving Eligibility → Driving Context → Interaction Policy → Future Conversation Adaptation`

This milestone creates the stable policy boundary required by later Driving Conversation Adaptation, safety coordination, Maps, Visual Understanding, Ambient Context, and Unified Companion layers.

## Added contracts
- `DrivingInteractionDirection`
- `DrivingInteractionUrgency`
- `DrivingInteractionMode`
- `DrivingInteractionStatus`
- `DrivingInteractionAction`
- `DrivingInteractionPolicy`
- `DrivingInteractionSignal`
- `DrivingInteractionRequest`
- `DrivingInteractionDecision`
- `DrivingInteractionRepository`
- `InMemoryDrivingInteractionRepository`
- `DrivingInteractionPolicyEngine`

## Policy dimensions
- User-initiated, ROBY-initiated, and system-alert direction.
- Routine, important, urgent, and emergency urgency.
- Deferrability and acknowledgement need.
- Signal confidence and freshness.
- M118 parked, low, elevated, high, and critical load.
- Normal, brief, minimal, silent, and emergency-only envelopes.

## Invariants
- Ownership must match the full M117–M118 lineage.
- M118 remains authoritative for contextual load and upstream status.
- Non-ready decisions cannot permit any interaction capability.
- Critical load defers ordinary interaction.
- Emergency policy is explicit and independently configurable.
- A response time budget exists only when response is allowed.
- Decisions are immutable, deterministic, auditable, and repository-backed.

## Non-responsibilities
M119 does not generate wording, summarize content, choose a voice, perform speech recognition or synthesis, control microphones or speakers, manage turn-taking, deliver alerts, mutate conversation state, access maps, route guidance, cameras, sensors, vehicle systems, Android Auto, or CarPlay.

## Future compatibility
M120 can translate the policy envelope into conversational adaptation without changing M119. Maps, navigation, visual, and ambient domains may supply governed interaction intents through adapters, while M119 remains independent of acquisition source and delivery platform.
