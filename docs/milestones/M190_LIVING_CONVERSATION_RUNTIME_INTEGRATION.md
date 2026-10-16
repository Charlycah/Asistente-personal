# M190 — Living Conversation Runtime Integration

M190 connects the governed living-conversation chain built in M93–M105 to the
operational cognitive orchestration introduced in M189.

## Runtime position

The integration is evaluated after memory and inside the cognitive runtime,
before tools and provider execution. It cannot send messages, schedule future
interventions, invoke tools, or mutate memory.

## Operational contribution

An eligible `LivingConversationIntegration` can contribute:

- conversational rhythm;
- the governed next move;
- preservation of the user's conversational floor;
- the selected governed conversational orientation;
- exact lineage references from the M93–M105 chain.

Paused, non-applicable, review-required, missing, and non-eligible decisions are
represented as skipped cognitive stages and do not alter the provider prompt.

## Composition

`RuntimeCompositionDependencies` accepts an optional
`living_conversation_source`. The official composition root turns that source
into `LivingConversationRuntimeContributor` and installs it in the M189
orchestrator. Existing official contributors are preserved in deterministic
order.

## Safety boundary

M190 shapes only the current user-initiated turn. It does not activate
proactive conversation and does not grant delivery or execution authority to
the living-conversation modules.
