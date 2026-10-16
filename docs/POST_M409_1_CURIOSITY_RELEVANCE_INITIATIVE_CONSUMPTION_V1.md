# Post-M409.1 — Governed Epistemic Curiosity → Existing Relevance / Initiative Consumption Foundation v1

## Status

IMPLEMENTED / CERTIFICATION PENDING USER GATES.

## Purpose

Consume a certified Curiosity v1 `QUESTION_CANDIDATE` through the already
existing `RelevanceEvaluator` and `PersonalInitiativeEngine`.

This increment does not make ROBY ask productively. It proves that an epistemic
question can be admitted to the existing relevance/initiative policy and can
therefore be initiated, deferred or discarded without creating a curiosity
authority or a parallel relevance policy.

## Contract

The caller supplies:

- a Curiosity v1 report with `QUESTION_CANDIDATE`;
- an explicit existing `RelevanceCandidate`;
- the existing `RelevanceEvaluator`;
- the existing `PersonalInitiativeEngine`;
- optional existing `InitiativeContext`.

The relevance candidate must preserve the exact curiosity question as its
title. Topic assignment remains explicit and outside this foundation; v1 does
not infer interests from question text.

`should_ask` is true only for the existing initiative dispositions `INITIATE`
or `INTERRUPT`. `DISCARD` and `DEFER` remain non-speaking outcomes.

## Boundaries

No Gateway wiring, governed proposal creation, inbox mutation, persistence,
memory write, learning candidate, knowledge mutation, LLM, network, background
process or action execution is introduced.

`GovernedInitiativeEngine` is deliberately not consumed in this v1 because it
creates/enqueues governed proposals. Productive conversational delivery remains
a later gate.

M410, networking and Residential remain out of scope.
