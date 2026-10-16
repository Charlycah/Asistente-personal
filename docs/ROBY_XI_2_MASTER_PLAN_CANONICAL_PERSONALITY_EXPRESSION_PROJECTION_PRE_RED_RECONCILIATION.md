# ROBY XI.2 — MASTER PLAN — CANONICAL PERSONALITY EXPRESSION PROJECTION
# PRE-RED RECONCILIATION

**Classification:** PRE-RED RECONCILIATION / DOCUMENTARY ONLY  
**PRODUCT_CHANGE: NONE**  
**TEST_CHANGE: NONE**  
**NEW_CAPABILITY: NONE**  
**AUTHORITY_CHANGE: NONE**  
**B2: STOP**  
**B3: STOP**  
**B4: STOP**

## 1. Purpose

Close the exact authority, signal, producer and projection questions for the
selected humanization residual before any CONTRACT RED is authorized.

Selected residual:

`CANONICAL_PERSONALITY_EXPRESSION_PROJECTION`

Target seam:

`Stable Personality → Adaptive Personality → ordinary provider preparation`

This block does not implement that seam.

## 2. Existing canonical authorities

The repository already contains both required decision authorities.

### Stable personality

`StablePersonalityEngine.evaluate_turn()` is the canonical pure M55 evaluator.

It produces `StablePersonalitySnapshot` from:

- current text;
- optional Presence snapshot;
- optional Relationship Memory snapshot;
- optional Social Regulation snapshot;
- an explicit or current timestamp.

The snapshot already exposes stable traits, expression, consistency, rationale
and bounded guidance.

No new stable-personality owner is required.

### Adaptive personality

`AdaptivePersonalityAuthority.adapt()` is explicitly the unique M377 expressive
authority.

It consumes one `StablePersonalitySnapshot` plus an optional
`AdaptivePersonalityRequest` and produces one `AdaptivePersonalityProfile`.

The profile already carries:

- the stable snapshot identifier;
- stable traits;
- stable expression;
- delivery tone;
- response detail;
- response structure;
- auditable rationale.

It rejects identity mutation and parallel-brain creation.

Therefore:

`STABLE_PERSONALITY_AUTHORITY: EXISTING`

`ADAPTIVE_PERSONALITY_AUTHORITY: EXISTING`

`NEW_PERSONALITY_AUTHORITY_REQUIRED: NO`

## 3. Existing stable producer evidence

`app/conversation_runtime.py` already constructs one `StablePersonalityEngine`
inside the existing Living Conversation source and calls `evaluate_turn()`.

That path is not the ordinary-turn producer required by this residual.

M253 explicitly bounds Living Conversation activation to explicit requests to
adapt or evaluate conversation.

Therefore it proves reuse and semantics, but it must not be widened silently
into an always-on second conversation path.

Classification:

`LIVING_CONVERSATION_STABLE_PRODUCER: EXISTING / EXPLICIT_PATH_ONLY`

## 4. Adaptive profile productive producer

Repository-wide productive inspection finds no current `app/`, `core/` or
`application/` construction of `AdaptivePersonalityAuthority`.

It also finds no productive call to its `adapt()` method.

The current official runtime composition exposes no demonstrated producer of
`adaptive_personality_profile`.

Desktop and relational-affective evidence contain read-only consumers for such
a profile when one is available.

Therefore:

`ADAPTIVE_PERSONALITY_PROFILE_PRODUCTIVE_PRODUCER: MISSING`

This is the first causal gap.

## 5. Reconciliation with H4 Voice S2

The historical H4 Voice S2 contract states that the official conversation
runtime already owns the canonical adaptive profile behind the protected
Gateway.

Current executable evidence does not demonstrate that producer.

H4 S2 did certify a narrower invariant:

an already-decided canonical `delivery_tone`, when available, may traverse the
existing Desktop seam into the existing Voice Reader.

H4 also permanently protects these boundaries:

- Desktop and Voice do not own `AdaptivePersonalityAuthority`;
- tone is transported, not re-decided downstream;
- absence of canonical tone preserves historical no-tone behavior;
- provider remains below the voice-expression boundary;
- thought is not expression;
- expressive prosody is not subjective emotion.

This reconciliation does not rewrite, reanchor or invalidate H4.

It classifies the historical producer premise as:

`H4_S2_PROFILE_PRODUCER_PREMISE: NOT_DEMONSTRATED_BY_CURRENT_EXECUTABLE_STATE`

and preserves the certified downstream transport contract.

## 6. Signals authorized by M377

`AdaptivePersonalityRequest` already defines the complete admitted signal
surface:

- `task_complexity`;
- `urgency`;
- `sensitive`;
- explicit requested detail;
- explicit requested structure;
- bounded simulated-affective delivery tone;
- explicit affective source reference;
- explicit functional-regulation reference.

M377 does not authorize hidden psychological inference or personality learning.

M390.5 may only contribute a subordinate bounded affective signal through
`GovernedExpressiveModulation`.

It does not construct the adaptive profile.

## 7. Signals authorized for the first productive seam

The first seam must be smaller than the full M377 signal surface.

No current ordinary-turn authority has been proven to derive task complexity,
urgency, sensitivity, requested detail or requested structure specifically for
M377 on every turn.

Likewise, simulated inner-state modulation is not yet proven as an ordinary
productive input.

Therefore the first productive seam must fail closed to:

`AdaptivePersonalityRequest()`

with no inferred per-turn extras.

This means the first seam may derive adaptive delivery from the canonical stable
snapshot using M377 defaults, but it may not invent urgency, sensitivity,
preferences, affect or inner-state evidence.

Classification:

`FIRST_SEAM_ADAPTIVE_SIGNALS: DEFAULT_ONLY`

`HIDDEN_SIGNAL_INFERENCE: NOT_AUTHORIZED`

`INNER_STATE_MODULATION_IN_FIRST_SEAM: NOT_AUTHORIZED`

`RELATIONSHIP_PERSONALIZATION_IN_FIRST_SEAM: NOT_AUTHORIZED`

Those richer inputs require later evidence-specific residuals.

## 8. Stable snapshot inputs for the first seam

`StablePersonalityEngine.evaluate_turn()` already supports missing Presence,
Relationship Memory and Social Regulation.

The first seam therefore does not need to solve those integrations.

It may evaluate the current text with the canonical engine and no unproven
optional contextual snapshots.

This preserves the M55 baseline traits and expression logic without creating a
relationship or social inference shortcut.

Classification:

`FIRST_SEAM_STABLE_INPUT: CURRENT_TEXT_ONLY`

Optional Presence, Relationship and Social Regulation remain future integration
questions.

## 9. Exact ordinary-turn projection point

The canonical provider path constructs the initial `LLMRequest` through the
existing `InferenceRequestPort`.

`GovernedRuntimePreparation` then enriches that same request with recent
conversation context, governed Memory and other certified cognitive context
before returning one `GovernedConversationPreparation`.

This class is already the canonical composition boundary for read-only context
transport into ordinary provider inference.

Therefore the smallest authorized target for a future contract is:

`GovernedRuntimePreparation`

not:

- `OfficialConversationGateway`;
- Desktop;
- Voice;
- the provider implementation;
- `UIResponse`;
- Living Conversation;
- a new Humanization or Personality runtime.

The projection must enrich the existing `LLMRequest.system_prompt`.

It must not mutate user text, provider routing, Memory, planning, authorization,
execution or response content after generation.

Classification:

`CANONICAL_PROJECTION_POINT: GOVERNED_RUNTIME_PREPARATION`

`PROJECTION_SURFACE: LLMREQUEST_SYSTEM_PROMPT`

## 10. Dependency ownership

`RuntimeCompositionDependencies` is the existing dependency boundary consumed by
`GovernedRuntimePreparation`.

A future GREEN may expose the existing M55/M377 authorities through that
composition boundary.

It must not introduce a new manager, agent, planner, runtime loop, personality
store, profile cache or alternate conversation pipeline.

The runtime factory may compose the existing authorities once and supply them to
the existing preparation boundary.

This is dependency wiring, not a new capability.

## 11. Bounded projection semantics

A future projection may transport only already-decided canonical expressive
facts from the M55 snapshot and M377 profile.

At minimum, the provider may be informed of:

- stable personality guidance;
- canonical delivery tone;
- canonical response-detail guidance;
- canonical response-structure guidance.

The projection is advisory expression context.

It must explicitly preserve:

`PERSONALITY_EXPRESSION != FACTUAL_AUTHORITY`

`PERSONALITY_EXPRESSION != REASONING_AUTHORITY`

`PERSONALITY_EXPRESSION != AUTHORIZATION`

`PERSONALITY_EXPRESSION != MEMORY`

`PERSONALITY_EXPRESSION != SUBJECTIVE_EMOTION`

It may shape how an answer is expressed, never what facts become true or what
actions become authorized.

## 12. Fail-closed behavior

If stable evaluation or adaptive projection is unavailable, the ordinary
provider path must remain compatible with its historical behavior.

No fallback personality engine may be created downstream.

Desktop and Voice continue to accept absence of adaptive profile/tone evidence.

## 13. Protected surfaces

The first contract must preserve:

- one integrated cognitive brain;
- one M55 stable-personality authority;
- one M377 adaptive-personality authority;
- the protected `OfficialConversationGateway`;
- existing Desktop tone-only behavior;
- existing Voice projection boundaries;
- existing provider routing;
- Memory and identity privacy gates;
- current Planning / Authorization / Execution separation;
- B2 / B3 / B4 STOP.

It must not reactivate the legacy rich `CognitivePipeline` as a second ordinary
conversation path.

## 14. Exact proven residual

The pre-RED reconciliation reduces the broader humanization finding to:

`MISSING_PRODUCTIVE_M377_PROFILE_PRODUCTION_AND_BOUNDED_PROVIDER_PROJECTION`

The causal chain is:

`current ordinary text`

→ existing `StablePersonalityEngine.evaluate_turn()`

→ existing `StablePersonalitySnapshot`

→ existing `AdaptivePersonalityAuthority.adapt()`

→ existing `AdaptivePersonalityProfile`

→ missing bounded projection into
`GovernedRuntimePreparation` / `LLMRequest.system_prompt`

The missing element is integration, not cognition.

## 15. RED authorization decision

Evidence is now sufficient to authorize one narrow CONTRACT RED.

Recommended next block:

`MASTER PLAN — CANONICAL PERSONALITY EXPRESSION PROJECTION — CONTRACT RED`

The RED must prove only that the ordinary productive preparation path can reuse
the existing M55 and M377 authorities and project their already-decided bounded
expression context into the existing provider request.

The RED must not require:

- Relationship Memory integration;
- Presence integration;
- Social Regulation integration;
- simulated inner-state modulation;
- new signal inference;
- personality persistence or learning;
- Gateway modification;
- Desktop expansion;
- Voice Identity;
- a new capability or authority.

## 16. Closure

`PRODUCT_CHANGE: NONE`

`TEST_CHANGE: NONE`

`NEW_CAPABILITY: NONE`

`STABLE_PERSONALITY_AUTHORITY: EXISTING`

`ADAPTIVE_PERSONALITY_AUTHORITY: EXISTING`

`ADAPTIVE_PERSONALITY_PROFILE_PRODUCTIVE_PRODUCER: MISSING`

`FIRST_SEAM_STABLE_INPUT: CURRENT_TEXT_ONLY`

`FIRST_SEAM_ADAPTIVE_SIGNALS: DEFAULT_ONLY`

`CANONICAL_PROJECTION_POINT: GOVERNED_RUNTIME_PREPARATION`

`PROJECTION_SURFACE: LLMREQUEST_SYSTEM_PROMPT`

`RED_AUTHORIZED: YES`

`NEXT_ACTION: CANONICAL_PERSONALITY_EXPRESSION_PROJECTION_CONTRACT_RED`

`B2: STOP`

`B3: STOP`

`B4: STOP`
