# M120 — Driving Conversation Adaptation

## Objective
Translate the governed M119 interaction envelope into a declarative conversational-form plan suitable for driving, without generating wording or executing speech.

## Architectural fit
`M117 Eligibility → M118 Context → M119 Interaction Policy → M120 Conversation Adaptation`

M120 consumes M119 and constrains the form of a future response. It does not reconsider driving context or permissions.

## Added contracts
- `DrivingConversationContentKind`
- `DrivingConversationComplexity`
- `DrivingConversationStyle`
- `DrivingConversationStatus`
- `DrivingConversationAction`
- `DrivingConversationAdaptationPolicy`
- `DrivingConversationSignal`
- `DrivingConversationAdaptationRequest`
- `DrivingConversationAdaptationPlan`
- `DrivingConversationAdaptationRepository`
- `InMemoryDrivingConversationAdaptationRepository`
- `DrivingConversationAdaptationEngine`

## Adaptation dimensions
- Standard, concise, essential, acknowledgement-only, silent, and emergency styles.
- Maximum word and sentence budgets.
- User-floor preservation.
- Question permission and confirmation need.
- Chunking and resumable remainder deferral.
- Content kind, complexity, confidence, and freshness.

## Invariants
- The complete M117–M119 ownership lineage must match.
- M119 permissions and modes are authoritative.
- Review, blocked, deferred, and non-applicable states propagate conservatively.
- M120 never upgrades a prohibited response into an allowed response.
- Complex or reflective content is deferred under restrictive modes.
- Plans are immutable, deterministic, auditable, and repository-backed.

## Non-responsibilities
M120 does not generate or rewrite text, summarize content, select exact wording, synthesize or recognize speech, control microphone or speaker state, schedule deferred work, mutate conversation state, manage turn-taking, access maps, navigation, cameras, sensors, vehicle systems, Android Auto, or CarPlay.

## Future compatibility
A later driving realization layer may use the M120 plan to shape actual language. Safety coordination may combine M118–M120 outputs without modifying their contracts. Maps, Visual Understanding, Ambient Context, and Unified Companion remain independent producers or consumers through adapters.
