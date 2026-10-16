# M121 — Driving Safety Coordination

## Objective
Provide the final declarative safety boundary for the Driving domain by coordinating the exact outputs of M118, M119, and M120.

## Architectural fit
`M117 Eligibility → M118 Context → M119 Interaction Policy → M120 Conversation Adaptation → M121 Safety Coordination`

M121 consumes prior decisions without replacing or recalculating them. It applies the most restrictive result and determines whether a future interaction may leave the Driving domain.

## Added contracts
- `DrivingSafetyLevel`
- `DrivingSafetyStatus`
- `DrivingSafetyAction`
- `DrivingSafetyPolicy`
- `DrivingSafetyCoordinationRequest`
- `DrivingSafetyDecision`
- `DrivingSafetyRepository`
- `InMemoryDrivingSafetyRepository`
- `DrivingSafetyCoordinationEngine`

## Final safety dimensions
- Conversation permission.
- Voice suitability.
- Initiative permission.
- Complex-dialog permission.
- Interruption permission.
- Notification permission.
- Deferral requirement.
- Confirmation requirement.
- Explicit emergency override.
- Clear, guarded, restricted, critical, and emergency safety levels.

## Invariants
- Owner and full M118→M119→M120 identifier lineage must match.
- No upstream prohibition can be upgraded.
- Critical load blocks non-emergency interaction.
- Emergency override is restricted to emergency system alerts and remains minimal.
- Non-authorized decisions expose no active permissions.
- Decisions are immutable, deterministic, auditable, and repository-backed.

## Non-responsibilities
M121 does not generate language, realize prompts, manage turns, execute voice, deliver notifications, schedule resumption, access maps, navigate, read cameras or sensors, control vehicle systems, or integrate Android Auto or CarPlay.

## Future compatibility
Maps, Visual Understanding, Ambient Context, and Unified Companion may consume the final M121 contract through adapters without depending on the internal structure of the Driving domain.
