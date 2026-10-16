# M382 - Unified Brain Stabilization

## Outcome

M382 establishes `UnifiedBrain` as the single application integration boundary
for ROBY's certified desktop conversation path. It delegates to the official
conversation gateway and does not replace the existing cognitive or domain
authorities.

## Unified diagnostic view

`UnifiedBrainDiagnosticSnapshot` combines two existing immutable views:

- conversation processing state from `OfficialConversationGateway`;
- post-turn reflection metadata from `PostTurnReflectionObserver`.

The diagnostic view reports the exact difference between processed and observed
turns. A zero difference means that every successfully submitted turn was
observed. It does not assign a health grade or trigger behavior.

## Observable metadata

The view includes response paths, consecutive degradation, explicit degradation
causes and recoveries. It never includes user or assistant message text.

## Preserved authorities

Memory, decision, agenda, reminders, notes, permissions, credentials,
persistence and capability execution retain their existing canonical owners.
`UnifiedBrain` coordinates the conversation boundary; it does not absorb those
responsibilities.

## Explicit exclusions

M382.14 adds no decisions, alerts, retries, persistence, memory writes,
automation, provider selection or platform mutation. Further cognitive
integration must continue incrementally through existing governed contracts.
