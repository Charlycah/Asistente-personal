# ROBY XI.2 — Higher Cognitive Evolution
## Canonical Productive Reasoning Episode Unification Wave

**Baseline de entrada:** 13.404 tests PASS + Ruff limpio.  
**Estado:** CLOSED / PROMOTED — full local promotion gate satisfied at **13.439 PASS + Ruff limpio**.

## Purpose

Unify ordinary productive Reasoning so End-to-End/Adaptive Cognition and the existing
`ReasoningRuntimeContributor` refer to one governed Reasoning episode per canonical turn.

The wave does not create stronger epistemic assessments and does not claim Metacognitive Closure.

## Canonical turn identity

The existing reliability identity algorithm is promoted to the canonical conversation-turn helper:

`build_governed_conversation_turn_identity(request, now)`.

It preserves:

- conversation id;
- request id;
- turn id;
- trace id.

Reliability observability now consumes this shared helper instead of duplicating the calculation.

## Canonical productive Reasoning episode

`CanonicalProductiveReasoningEpisode` is a read-only, non-persistent value under
`governed_reasoning` authority. It contains:

- owner;
- session;
- exact turn id;
- input fingerprint of the canonical Reasoning evaluation;
- one `GovernedReasoningResult`;
- deterministic source fingerprint.

The `OfficialGovernedReasoningRuntimeGateway` keeps at most the current episode for each
owner/session handoff. A later turn replaces it; it is not durable history.

## Single-evaluation contract

`OfficialAdaptiveCognitionRuntimeGateway` can receive the canonical productive turn id.

When the End-to-End entry path routes a turn to Reasoning, it creates/reuses the episode through the
existing `OfficialGovernedReasoningRuntimeGateway`.

`CanonicalProductiveReasoningSource`, wired into the existing `ReasoningRuntimeContributor`, derives
the same canonical turn id from the original request identity. If the episode already exists, it
projects that exact result and does not rerun Reasoning. If no episode exists, it evaluates the
official gateway exactly once for that turn.

Thus:

`E2E / Adaptive Cognition`
→ `one OfficialGovernedReasoningRuntimeGateway episode`
→ `ReasoningRuntimeContributor projection`.

## Runtime preparation timestamp

The ordinary conversation pipeline now uses the optional `prepare_at(request, now=created_at)` hook
when available. Legacy preparation ports continue using their original `prepare(request)` contract.

This preserves the exact turn timestamp between conversation evaluation and canonical runtime
preparation without breaking existing preparation ports.

## Runtime-root authority

`runtime_root_factory.py` now wires:

`CanonicalProductiveReasoningSource(governed_reasoning_runtime)`

instead of treating `OperationalCognitiveSource.reasoning` as the canonical Reasoning source.

Planning, Reflection and Executive operational sources remain unchanged.

The same `OfficialGovernedReasoningRuntimeGateway` instance is still shared by:

- Adaptive Cognition;
- End-to-End Conversation Runtime;
- canonical ReasoningRuntimeContributor source.

No second gateway or Reasoning manager is introduced.

## Truthful abstention

The canonical gateway remains abstention-first. If governed evidence is insufficient, the shared
episode may be `ABSTAINED`; `ReasoningRuntimeContributor` projects that as explicit caution rather
than converting it to synthetic `COMPLETED` reasoning.

This is a deliberate truthfulness improvement and does not equate abstention with failure.

## Boundaries

The episode:

- is read-only;
- is turn-scoped;
- is not Memory;
- is not Learning;
- grants no authority;
- executes no tools;
- does not modify planner needs;
- does not create epistemic quality/sufficiency artifacts.

Operational `Reasoning COMPLETED` is no longer the canonical substitute for governed Reasoning in
the official runtime root.

## Certification

Initial RED exposed the missing episode APIs.

New wave contract: **9 PASS**.

Focused regression matrices across Reasoning Runtime, Governed Reasoning, Adaptive Cognition,
End-to-End Conversation, Reliability Observability, Operational Acceptance, Productive Strategy
Wiring, Strategy Outcome/Metacognition and Future Influence remained green.

M396.3 authority preservation is intentionally updated because the authorized runtime-root wiring
changed.

Full local promotion gate satisfied at **13.439 PASS + Ruff limpio**.

## Remaining causal boundary

This wave proves:

`ordinary turn`
→ `one canonical governed Reasoning episode`
→ `same episode projected into cognitive runtime`.

It still does not prove:

`canonical Reasoning episode`
→ `Hypothesis Deepening`
→ `Epistemic Sufficiency`
→ `Reasoning Quality`
→ `Method Provenance / Outcome`.

Therefore Productive Strategy Metacognitive Closure remains blocked only by the final strong
epistemic-assessment bridge, not by duplicate Reasoning source identity.
