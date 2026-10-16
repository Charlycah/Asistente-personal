# ROBY XI.2 — FUTURE CAPABILITIES AND EVOLUTION GUIDE

**Status:** Future-governance documentation only  
**Purpose:** Preserve agreed future directions without changing the current certified architecture or authorizing implementation.  
**Current reference baseline at creation:** CIH-2DI.17 — LONGITUDINAL IDENTITY V1 POSITIVE-SAME MINIMAL SEMANTIC GREEN — **12,571 PASS · 0 FAIL · Ruff clean**.

---

## 1. Governing purpose

This document records future capabilities that may be evaluated for ROBY XI.2 after the currently authorized work. It is not an implementation plan, does not create new authorities, and does not change any existing capability boundary.

Every future capability described here remains subordinate to the permanent ROBY XI.2 rules:

- **ONE BRAIN — ONE AUTHORITY PER CAPABILITY**
- **INVENTORY BEFORE SURGERY**
- **REUSE BEFORE NEW AUTHORITY**
- **EVIDENCE BEFORE SURGERY**
- Documentation and code must remain synchronized when implementation eventually occurs.
- No future feature may silently create a second cognitive authority.
- Existing governed authorities must be reused whenever they already own the required decision.
- New code is justified only by a demonstrated residual.
- Future implementation must proceed in small, verifiable increments and preserve the project's validation requirements.

---

## 2. Future capability A — Self-Capability Explanation / Guided Use

### 2.1 Intent

ROBY should eventually be able to explain, conversationally, how to use ROBY and what ROBY can currently offer.

Representative questions include:

- “ROBY, ¿qué puedes hacer?”
- “¿Cómo puedo trabajar contigo?”
- “¿Qué capacidades tienes activas?”
- “¿Puedes ayudarme con esto?”
- “No sé por dónde empezar; ¿qué puedes ofrecerme?”

### 2.2 Governing principle

ROBY should not depend on a manually maintained promotional list that can drift away from reality. Its self-description should be grounded in the **real, currently authorized capability inventory** and in the actual availability of those capabilities.

The eventual design should distinguish, where applicable:

- capabilities ROBY currently possesses;
- capabilities currently available in the active environment;
- capabilities that are read-only;
- capabilities that require explicit user authorization or confirmation;
- capabilities that are unavailable or outside ROBY's authority;
- future capabilities that are documented but not implemented.

### 2.3 Non-authority rule

Self-capability explanation is descriptive. It must not become an authority for executing, learning, planning, persisting, revising, investigating, or otherwise activating a capability.

**EXPLANATION OF A CAPABILITY ≠ AUTHORIZATION TO USE THAT CAPABILITY**

### 2.4 Desired experience

A future guided introduction may allow ROBY to introduce useful capabilities progressively rather than overwhelming the user with a static manual. ROBY should be able to explain a capability when relevant, show how to invoke it, state its boundaries, and identify when confirmation is required.

The long-term objective is that ROBY itself can serve as a reliable guide to ROBY, while remaining grounded in the governed system truth.

---

## 3. Future capability B — Governed Expressive Voice

### 3.1 Intent

ROBY's future voice should go beyond plain text-to-speech. It may support controlled expressive delivery including:

- emphasis;
- pacing;
- pauses;
- calmness;
- urgency;
- surprise/asombro;
- warmth;
- restrained humor;
- explanatory cadence;
- contrast and salience.

These are properties of **expression**, not independent cognition.

### 3.2 Permanent architectural boundary

The governing separation should be:

**BRAIN → COMMUNICATIVE INTENT → VOCAL EXPRESSION → SPEECH SYNTHESIZER**

and the permanent rule:

**THOUGHT ≠ EXPRESSION**

The cognitive system decides what is justified to communicate through its existing authorities. A future governed expression capability may determine how authorized content should be rendered vocally. The speech synthesizer materializes that expression.

A TTS engine, voice provider, acoustic model, or external speech service must never become a second cognitive brain or acquire authority over ROBY's beliefs, reasoning, memory, learning, planning, initiative, or execution.

### 3.3 Expressiveness without false internal-state claims

ROBY may eventually express surprise, caution, importance, warmth, or humor prosodically without claiming an internal emotional state that has not been established by the governed architecture.

For example, a vocal rendering may make an unexpected finding sound noticeably different from a routine status report. That expressive consequence does not itself prove or create an emotion.

**EXPRESSIVE PROSODY ≠ CLAIM OF SUBJECTIVE EMOTION**

---

## 4. Future capability C — ROBY Voice Identity

### 4.1 Desired direction

ROBY should ultimately have a recognizable voice identity of its own.

Creative references such as **Samantha** or **TARS** may be used only as inspiration for qualities, not as identities to reproduce or imitate literally.

Potential qualities worth exploring include:

- Samantha-inspired qualities: conversational naturalness, warmth, fluid prosody, spontaneity and nuanced intonation;
- TARS-inspired qualities: presence, precision, controlled pauses, concise timing and restrained dry humor;
- ROBY-specific synthesis: an adult, calm, clear, warm but not artificially sentimental voice, with strong intelligibility and enough expressive range to communicate salience naturally.

The final objective is **ROBY's own voice**, not a copy of an existing fictional character or performer.

### 4.2 Timbre as replaceable presentation

The selected timbre should be replaceable without cognitive surgery.

A future implementation should allow alternative approved voices or providers to be evaluated while preserving the same governed cognitive content and personality boundaries.

**VOICE TIMBRE ≠ COGNITIVE IDENTITY**

Changing the voice should be analogous to changing the instrument through which ROBY speaks, not changing ROBY's brain.

---

## 5. Future capability D — Voice Provider Independence

ROBY should avoid architectural dependence on a single TTS provider when practical.

Before implementation, inventory must determine whether an existing provider abstraction, capability registry, external-capability authority, or speech boundary already exists and can be reused.

A provider-specific integration should remain below the governed expression boundary. Provider replacement must not require changes to unrelated cognitive authorities.

Candidate future concerns include:

- local versus external synthesis;
- latency;
- privacy;
- offline availability;
- multilingual pronunciation;
- controllable prosody;
- timbre selection;
- provider failure/fallback;
- deterministic preservation of authorized text/content;
- explicit separation between synthesis metadata and cognitive state.

These concerns do not authorize implementation by themselves.

---

## 6. Future inventory-before-surgery procedure

When this future work is eventually opened, the procedure should begin with documentation and inventory, not implementation.

### Phase 1 — INVENTORY

Locate all existing ROBY surfaces related to speech, audio, conversational presentation, personality, capability registries, external providers, self-description, help, and runtime exposure. Identify the existing owner of every relevant decision.

### Phase 2 — REUSE PROOF

Prove whether existing authorities can already support the desired capability. Prefer composition and reuse over introducing new owners.

### Phase 3 — RESIDUAL

State the smallest productive behavior that is genuinely missing. No implementation is authorized if no concrete residual can be demonstrated.

### Phase 4 — CONTRACT

Define inputs, outputs, provenance, authority boundaries, fail-closed behavior, forbidden side effects, and interaction with existing owners.

### Phase 5 — RED

Write evidence demonstrating the missing behavior and the required governance boundaries before implementation.

### Phase 6 — GREEN

Implement only the minimum semantics required to satisfy the certified contract. Validate with the full ROBY XI.2 quality gates and confirm no regressions.

The governing sequence remains:

**INVENTORY → REUSE PROOF → RESIDUAL → CONTRACT → RED → GREEN**

---

## 7. Explicit non-goals of this document

This guide does **not**:

- create a voice authority;
- create a self-description authority;
- select a TTS provider;
- select or clone a specific person's voice;
- authorize changes to the current runtime;
- authorize autonomous speech;
- authorize new Initiative, Planning, Execution, Learning, Memory, Investigation or persistence behavior;
- alter any current certified CIH boundary;
- alter CIH-2DI.18;
- justify surgery merely because a future capability is desirable.

---

## 8. Relationship to current CIH-2DI work

This document is intentionally orthogonal to the current CIH-2DI.18 investigation.

CIH-2DI.18 remains governed by its own certified scope and sequence. In particular, this future guide must not be used as momentum to broaden `SAME`, open `DISTINCT`, expand `AMBIGUOUS`, introduce candidate discovery/search, or modify protected runtime surfaces.

The current DI principle remains:

**SAME = ASSESSMENT, NOT REVISION AUTHORIZATION**

No future voice or guided-use work changes that rule.

---

## 9. Future target experience

The long-term target is a ROBY that can naturally explain what it can do, teach its users how to work with it, communicate important distinctions through controlled vocal expression, and retain a recognizable voice identity — while all substantive decisions continue to come from the same governed brain and the correct existing authority for each capability.

The desired experience is therefore not merely “ROBY has a voice.”

It is:

**ROBY understands through governed cognition, explains through governed communication, and speaks through a replaceable expressive instrument.**

---

## 10. Preservation note

Keep this document in the repository root as a future-evolution reference. Before any implementation derived from it, reconcile it against the then-current `ROBY_XI_2_CURRENT_TRUTH.md`, cognitive inventory/master guide, external-capability documentation, current code, and tests.

If future project truth conflicts with an assumption in this document, the current governed architecture takes precedence and this guide must be reconciled before surgery.
