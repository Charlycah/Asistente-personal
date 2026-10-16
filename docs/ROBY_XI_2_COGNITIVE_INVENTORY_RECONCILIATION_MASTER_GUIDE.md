# ROBY XI.2 — Cognitive Inventory Reconciliation — Master Surgical Guide

**Official baseline:** 12,534 PASS · 0 FAIL · Ruff clean  
**Higher Cognitive Evolution:** CLOSED / ZERO-RESIDUAL CERTIFIED  
**Purpose:** authoritative pre-change inventory and surgical modification guide for ROBY XI.2.  
**Direction:** laptop-only; cognitive/intellectual depth before lateral expansion.  

---

## 1. Executive decision

ROBY XI.2 has reached a size where roadmap memory, filenames, milestone numbers, or isolated tests are no longer sufficient evidence that a capability is absent, partial, productive, duplicated, or historical.

From this baseline onward, **no cognitive or architectural implementation should begin from a feature name alone**. Every proposed change must first be resolved against this guide using the chain:

**capability → canonical authority → existing foundations → productive reachability → persistence owner → tests → documentation → residual → permitted surgical change.**

The default engineering decision is now:

> **integrate or extend the existing owner before creating anything new.**

A new module is justified only when the audit proves that no existing authority/foundation can own the required behavior without violating responsibility boundaries.

---

## 2. Snapshot of current repository complexity

Counts from the certified ZIP, using reproducible filesystem scopes:

- 1,256 Python files across `core/`, `app/`, `application/`, `domain/`, `infrastructure/`, `engines/`, `handlers/`, `interfaces/`, and historical `m3..m7` layers.
- 1,143 `test_*.py` files under `tests/`.
- 1,156 files under `docs/`.
- 134 direct functional subdirectories under `core/` after excluding `__pycache__` and `core/tests`.
- 362 test files whose names contain `409`, showing that the Post-M409 architecture is substantial rather than incidental.
- 29 curiosity-related tests, 18 investigation-related tests, 10 self-diagnostics/self-improvement-related tests, plus the 11 focused HCE test files.

These numbers explain the current risk profile: the main danger is no longer lack of code, but **duplicate semantics, parallel routes, stale documentation, compatibility layers mistaken for authorities, and tests that preserve historical contracts**.

---

## 3. Canonical cognitive authority map

The Cognitive Inventory declares eleven primary responsibilities. This remains the first authority map for every new change.

| Responsibility | Canonical primary | Current declared posture | Modification rule |
|---|---|---|---|
| Entry | `conversation_entry` | USER_VISIBLE | Do not add another conversational entry authority. |
| Context | `context_continuity` | OPERATIONAL_LIMITED | Extend continuity contracts, not a parallel context brain. |
| Memory | `memory_gateway` | OPERATIONAL_LIMITED | All durable cognitive memory writes ultimately pass through the official memory boundary. |
| Knowledge | `knowledge_runtime` | CONSULTATIVE | Knowledge supplies/organizes evidence; it must not silently become reasoning or memory authority. |
| Reasoning | `governed_reasoning` | OPERATIONAL_LIMITED | New inferential primitives belong here unless a proven existing authority contract says otherwise. |
| Planning | `executive_planning` | CONSULTATIVE | `cognitive_planner_shadow` remains shadow; do not promote it as a second planner. |
| Decision | `unified_cognitive_coordination` | OPERATIONAL_LIMITED | Decision/recommendation remains advisory and human-owned where contracted. |
| Execution | `capability_orchestrator` | USER_VISIBLE | Recommendation/reasoning never grants execution authority by itself. |
| Reflection | `cognitive_core_resident` | OPERATIONAL_LIMITED | Functional reflection is not a second reasoning authority. |
| Governance | `governed_capability_routing` | OPERATIONAL_LIMITED | New routes must preserve governed routing. |
| Observability | `runtime_observability` | OPERATIONAL_LIMITED | Observation/evidence must not mutate production merely because it sees it. |

**Hard rule:** no proposal may introduce a second primary authority for one of these responsibilities without an explicit architectural migration that retires the old owner. Additive parallel authorities are not allowed.

---

## 4. Master status vocabulary

Every capability must be labelled with exactly one primary maturity state plus optional qualifiers.

| State | Meaning |
|---|---|
| CLOSED | Contracted scope is complete and certified. |
| SUBSTANTIAL | Productive capability exists but deeper/general scope remains. |
| FOUNDATION | Useful primitive exists; higher-level closed loop is missing. |
| SELECTIVE | Productive only for explicitly admitted evidence/scope. |
| CONSULTATIVE | May advise but not execute or own final action. |
| TRANSIENT | No durable persistence. |
| PERSISTENT | Uses a legitimate persistence authority. |
| SHADOW | Evaluation/observation only; never production authority. |
| PARTIAL | Useful path exists but continuity/closure is incomplete. |
| LEGACY | Present for compatibility/history; not future direction. |
| OUT OF SCOPE | Not part of current laptop-only direction. |
| MISSING | No sufficiently equivalent productive capability found. |

No roadmap item may use “not implemented” merely because its preferred class/name does not exist. It must first show that the behavior is MISSING rather than FOUNDATION/SUBSTANTIAL under another name.

---

## 5. Cognitive capability reconciliation

### 5.1 Conversation and contextual continuity

**Status:** CLOSED / SUBSTANTIAL within current scope.  
**Owners:** Entry + Context authorities.  
**Existing evidence:** official conversation entry, contextual continuity, living-conversation families, conversation readiness/eligibility/timing/opportunity selection, long-term conversational continuity foundations.  
**Residual worth deepening:** richer intellectual topic continuity and shared long-lived inquiry state.  
**Do not create:** another conversation manager, dialogue brain, or private context store.

### 5.2 Memory and autobiographical continuity

**Status:** CLOSED / PERSISTENT / GOVERNED for admitted memory types.  
**Owner:** `memory_gateway`.  
**Existing evidence:** cognitive, contextual, episodic, semantic/procedural foundations, autobiographical continuity, recall, consolidation, replacement/conflict lifecycle, post-M409 governed memory-write adapter.  
**Residual:** durable personal commitments remain partial; memory admission remains intentionally governed.  
**Do not create:** ConceptMemory, BookMemory, MusicMemory, CuriosityMemory, or a new learning store.

### 5.3 User/world/relationship model

**Status:** SUBSTANTIAL / GOVERNED.  
**Owners:** existing world/model authorities; persistence remains under legitimate owners.  
**Existing evidence:** user profile, relationship memory/evidence/consolidation/evolution/traceability, world stabilization/integration, places/object knowledge, personal identity/session profiles.  
**Residual:** avoid broad inference from ambiguous observations; improve only when explicit source contracts justify it.

### 5.4 Personal organization and decision support

**Status:** CLOSED / SUBSTANTIAL / CONSULTATIVE.  
**Owners:** personal organization sources + `unified_cognitive_coordination` for decision advice.  
**Existing evidence:** goals, projects, tasks, reminders, calendar, notes, M391 organization snapshots/advisory, governed complex decision reasoning.  
**Residual:** durable open commitments remain partial; complex decisions can be deepened without changing human decision ownership.

### 5.5 Governed reasoning

**Status:** CLOSED / SUBSTANTIAL / CANONICAL.  
**Owner:** `governed_reasoning`.  
**Existing evidence:** official governed reasoning gateway, canonical episode reuse, abstention, conflict analysis, explanations, contextual rules, causal reasoning, epistemic assessment, method provenance/outcomes.  
**Residual:** deepen representational sophistication, not create another reasoning engine.

### 5.6 Scenario, hypotheses and causal reasoning

**Status:** SUBSTANTIAL / SELECTIVE.  
**Owner:** `governed_reasoning`.  
**Existing evidence:** explicit hypothesis source, scenario simulation, causal prediction, hypothesis deepening, multi-hypothesis discrimination, epistemic delta, hypothesis update semantics and productive consumption.  
**Residual:** richer explanatory model composition and multi-stage counterfactual chains.  
**Do not create:** a generic TheoryEngine until the existing hypothesis lifecycle has been reused and its exact insufficiency proven.

### 5.7 Epistemic evaluation

**Status:** CLOSED / SELECTIVE / PRODUCTIVE.  
**Owner:** `governed_reasoning` plus existing assessment projections/consumers.  
**Existing evidence:** hypothesis deepening, epistemic sufficiency, reasoning quality, method provenance, method outcome, longitudinal assessments.  
**Residual:** generalize carefully beyond currently certified sources without weakening fail-closed admission.

### 5.8 Relational abstraction and concept formation

**Status:** FOUNDATION / PRODUCTIVE-SELECTIVE.  
**Owner:** `governed_reasoning`.  
**Existing implementation:** `core/governed_reasoning/relational_abstraction.py`, bounded semantic grounding, abstraction learning bridge, structural knowledge transfer, recalled/target structural projections.  
**What already exists:** invariant relational candidates, counterexample evidence, bounded structural transfer, approved structural learning.  
**Exact residual:** no canonical higher-order representation that composes multiple governed abstractions into a hierarchical concept with constituent relations, boundaries, exceptions, parent/child structure and component-level provenance.  
**Permitted future work:** Governed Hierarchical Concept Composition.  
**Forbidden duplication:** ConceptBrain, GeneralizationEngine, parallel ontology memory.

### 5.9 Structural analogy / transfer

**Status:** SUBSTANTIAL / BOUNDED.  
**Owner:** `governed_reasoning`.  
**Existing implementation:** `structural_knowledge_transfer.py` and structural projections.  
**What already exists:** structural role correspondence across different vocabulary under certified grammar.  
**Residual:** multi-concept hierarchical mapping after hierarchical concept composition exists.  
**Rule:** do not create a standalone Analogy Engine before proving the existing transfer matcher cannot be extended under its authority.

### 5.10 Learning

**Status:** CLOSED LOOP / HUMAN-GOVERNED / SUBSTANTIAL.  
**Owners:** existing Learning authority + `memory_gateway` for durable materialization.  
**Existing evidence:** `learning_foundation.py`, `safe_learning_policies.py`, `preference_learning.py`, abstraction learning bridge, Post-M409 explicit human learning approval, learning productive end-to-end wiring, approved learning memory materialization proposal, official memory gateway write extension.  
**What already exists:** candidate evaluation → explicit approval → governed memory materialization.  
**Residual:** risk-classified autonomous admission for carefully defined low-risk knowledge.  
**Not a residual:** unrestricted autonomous learning is neither required nor authorized.

### 5.11 Epistemic curiosity

**Status:** SUBSTANTIAL / PRODUCTIVE.  
**Owners:** existing cognitive maturity/reasoning/knowledge boundaries.  
**Existing implementation:** `core/cognitive_maturity/governed_epistemic_curiosity.py`, `hypothesis_gap_curiosity_evidence.py`, `curiosity_human_answer_evidence.py`, `curiosity_knowledge_admission_classification.py`, living-conversation curiosity plus Post-M409 productive wiring.  
**What already exists:** gap-driven question candidate, hypothesis-gap adapter, conversational consumption, exact human-answer evidence, knowledge candidate, admission classification, learning evaluation.  
**Residual:** richer concept/theory gaps, prioritization among competing questions, redundancy suppression, continuity across long investigations.  
**Do not reimplement Curiosity as a new capability.**

### 5.12 Multi-step investigation

**Status:** SUBSTANTIAL / BOUNDED.  
**Owners:** existing Planning/Authorization/Execution/Reasoning boundaries.  
**Existing evidence:** multiple Post-M409 investigation waves covering continuation, evidence acquisition planning, independence authorization, Level-2 read-only execution, reasoning re-entry, stopping boundaries and mandatory closure.  
**What already exists:** a real governed multi-stage investigation loop.  
**Residual:** longer horizons, dynamic replanning, resumability, unresolved-gap ledger, broader source diversity and concept/theory integration.  
**Do not create another planner or research agent brain.**

### 5.13 Strategy and metacognition

**Status:** CLOSED / L5 TRANSIENT.  
**Owner:** `unified_cognitive_coordination` with existing governed reasoning evidence.  
**Existing evidence:** novel strategy synthesis, application evidence, exact strategy/method outcome attribution, transient future influence.  
**Residual:** durable metacognitive learning is optional future architecture, not an HCE residual.  
**Forbidden:** silent planner mutation or durable preference creation outside Learning.

### 5.14 Self-diagnostics and self-improvement assistance

**Status:** SUBSTANTIAL / GOVERNED.  
**Existing implementation:** `core/self_diagnostics/*`, Post-M409 governed self-improvement proposal generation, sandbox/proof/review/proposal contracts.  
**What already exists:** observation → hypothesis → reproducible proof → isolated proposal → sandbox/test/diff/review semantics.  
**Residual:** candidate patch generation/application can be studied later, but promotion authority must remain separate.  
**Forbidden:** autonomous code promotion, authority rewriting, governance deletion.

### 5.15 Reflection and functional inner state

**Status:** SUBSTANTIAL / OPERATIONAL_LIMITED.  
**Owner:** Reflection authority.  
**Existing evidence:** self-model, thought stream, cognitive resident/reflection, simulated functional interior.  
**Residual:** richer integration with intellectual continuity if useful.  
**Boundary:** never promote functional continuity to a technical claim of subjective consciousness.

---

## 6. Knowledge and cultural environment reconciliation

### 6.1 General knowledge intelligence

**Status:** FOUNDATION / SUBSTANTIAL infrastructure; cross-domain synthesis incomplete.  
**Existing components:** `knowledge_gateway.py`, `personal_knowledge_base.py`, `project_knowledge_model.py`, knowledge source policy, retrieval orchestrator/execution, governed external intelligence, object/place knowledge, adaptive knowledge evolution.  
**Residual:** common epistemic integration across disciplines such as biology, astronomy, psychology, zoology, botany, mathematics and programming.  
**Architecture rule:** domains are content/source vocabularies, not separate brains.

### 6.2 Local documents / Biblioteca

**Status:** FOUNDATION; collection capability MISSING.  
**Existing components:** document inbox, classification, extraction, intelligence and actions; local reading supports explicit individual documents in currently supported formats.  
**Existing value:** ROBY already has a document-processing base that should be reused.  
**Exact residual:** no governed catalogue/index over an authorized root containing thousands of books, no library-level metadata/search/retrieval lifecycle, and no evidence of a general EPUB path in the audited document-reading route.  
**Permitted new instrumental capability:** Governed Local Library Catalogue/Index, read-only by default.  
**Must not do:** copy entire books into cognitive Memory merely because they are indexed.

Recommended future flow:

**authorized library root → scanner/catalogue → metadata/content index → governed retrieval → Knowledge → Reasoning → optional governed learning.**

### 6.3 Personal visual collection / "Pinacoteca" (provisional roadmap name)

**Status:** PRODUCTIVE FOUNDATION / EXPLICIT USER-INITIATED STORED-IMAGE ACCESS WIRED TO OFFICIAL RUNTIME.  
**Canonical authorities:** `ImageRepository` + `FileImageRepository` own private stored-media persistence; `GovernedVisionGateway` is the application boundary; `OfficialVisionCore` + `IntelligentVisionService` own governed visual analysis/policy; existing visual cognitive context remains downstream and subordinate.  
**Existing value:** explicit consent-gated JPEG/PNG/WebP storage, owner-scoped metadata listing, deletion, SHA-256 provenance, governed camera vision, scene/object/person/non-identity-face/OCR/code/document analysis and transient visual-to-cognitive projection already exist.  
**Exact residual:** productive provisioning of one private repository/gateway and an explicit `image_id` selection → controlled transient asset read → existing governed vision input seam. The current repository port returns metadata only and the public vision-core analysis paths acquire from `CameraProvider`.  
**Nomenclature decision:** "Pinacoteca" remains provisional for photographs/images/art; historical music/audio usage is superseded.  
**Architecture rule:** no new visual manager/repository/core/gateway, no gallery scanning, no biometrics and no automatic Memory/Learning/Reasoning.

### 6.4 Local music/audio collection

**Status:** SEPARATE SCOPE TO RECONCILE IF RETAINED.  
**Existing related infrastructure:** intelligent audio, voice input/output, hands-free and runtime audio/session facilities.  
**Boundary:** music/audio is not CAP-18 merely because older documentation called it "Pinacoteca". Any future catalogue/playback work must be audited separately and must preserve catalogue ≠ reasoning ≠ playback execution.

---

## 7. Laptop-only legacy reconciliation

The repository still includes numerous families that conflict with the chosen future direction. Presence in code does not imply current strategic scope.

Primary legacy/out-of-scope families include:

- `android_bridge`;
- mobile companion/context/extension/presence/runtime;
- device arbitration/capabilities/continuity;
- driving companion/context/safety/transport/navigation families;
- residential node/perception/remote presence;
- distributed/presence-continuity infrastructure where it exists only for multi-device or residential ambitions.

**Status:** LEGACY / OUT OF SCOPE unless proven necessary by the current laptop runtime.

**Removal policy:** never delete by name. Before physical retirement, prove:

1. import reachability;
2. composition-root reachability;
3. runtime invocation;
4. tests depending on the contract;
5. docs/history obligations;
6. migration/compatibility consumers.

Only then classify as DEAD and remove in a dedicated retirement block.

---

## 8. Test architecture reconciliation

Tests are part of the architecture, not disposable implementation detail.

The failed HCE header promotion demonstrated this concretely: apparently cosmetic root-document changes broke 22 tests because historical document headers are protected contracts.

From now on every change must classify affected tests into:

| Test class | Purpose |
|---|---|
| Unit | Local mechanism correctness. |
| Contract | Boundary/authority/source invariants. |
| Architecture | Single authority, headers, composition, no parallel routes. |
| Reachability | Productive path reaches the capability. |
| Closed-loop | Output legitimately affects later cognition. |
| Regression | Historical behavior remains intact. |
| Fail-closed | Missing/ambiguous evidence does not fabricate success. |
| Persistence | Only legitimate authority may persist. |
| Lineage | Same canonical episode/evidence is reused rather than recomputed. |
| Documentation | Root/docs state remains synchronized without erasing historical contracts. |

### Test-change rule

A failing existing test is presumed to protect a contract until the audit proves the contract itself is intentionally being migrated.

**Never edit a test merely to make a new implementation pass.**

If a contract must change, document the architectural decision and migrate production + tests together.

---

## 9. Documentation reconciliation

Root documentation is part of the governed system.

Protected/strategic files include at minimum:

- `README.md`;
- `CHANGELOG.md`;
- `CHANGELOG_ARCHITECTURE.md`;
- `architecture_rules.md`;
- `integration_decision.md`;
- `ESTADO_MAESTRO_INTEGRAL.md`;
- `INVENTARIO_COGNITIVO_INTEGRAL_ROBY_XI_2.md`;
- HCE final certification;
- relevant per-capability docs.

### Documentation surgery rules

1. Preserve known historical header contracts.
2. Append/synchronize rather than prepend blindly.
3. Do not declare a foundation PRODUCTIVE without reachability evidence.
4. Do not declare PRODUCTIVE as CLOSED without the contracted closed-loop/gates.
5. Do not call deliberate boundedness a “bug” or “residual”.
6. Mark laptop-only legacy explicitly so historical docs are not mistaken for roadmap direction.
7. Keep the cognitive inventory current after every promoted architectural block.

---

## 10. Protected files and sensitive project state

Project credentials/configuration that are excluded from delivery packages must remain excluded. Existing root documentation explicitly protects `.roby/credentials.json` from package delivery.

Any future repository tooling, self-improvement capability, packaging script or library scanner must treat secrets/configuration as a separate protected class and must never ingest them into Knowledge/Memory merely because they are locally accessible.

---

## 11. Master anti-duplication protocol

Before writing production code, the implementer must complete the following evidence record.

### Step A — Define behavior, not class name

Write one sentence:

> “ROBY currently cannot legitimately ______ when ______ evidence is available.”

If this cannot be stated precisely, implementation is premature.

### Step B — Search semantic neighbors

Search at minimum by behavior synonyms, not only proposed names. Example for “concepts”:

`concept`, `abstraction`, `relation`, `semantic`, `schema`, `pattern`, `generalization`, `structural`, `transfer`, `category`, `ontology`, `analogy`.

### Step C — Resolve canonical owner

Identify which of the eleven authorities owns the behavior.

### Step D — Identify foundations

List existing classes/functions/contracts that already perform part of the desired operation.

### Step E — Trace productive reachability

Find who constructs and calls the foundation in the real lifecycle. A class with tests but no productive caller is not equivalent to a productive capability.

### Step F — Trace persistence

If anything becomes durable, identify the legitimate write authority before implementation.

### Step G — Trace tests

Find contract/architecture/regression tests mentioning the owner, source, output model, docs and historical invariants.

### Step H — State exact residual

The residual must be smaller than the proposed feature name.

Example:

Bad: “ROBY lacks analogy.”  
Good: “ROBY can perform bounded structural transfer but cannot map multiple hierarchical concept structures because no hierarchical concept candidate exists.”

### Step I — RED evidence

Write tests that fail because of the demonstrated residual, not because a new preferred class is absent.

### Step J — Minimal implementation

Extend the existing owner in the smallest coherent block that closes those RED tests.

### Step K — Full promotion

Required gates:

`ruff check .`  
`pytest -q`

Then update this inventory.

---

## 12. Surgical change record template

Every future implementation/modification should carry a compact record like this in its design document:

| Field | Required evidence |
|---|---|
| Change ID/title | Human-readable capability/residual, not arbitrary micro-number. |
| User-visible objective | What ROBY becomes able to do. |
| Exact current gap | Evidence that current baseline cannot do it. |
| Canonical authority | Existing owner. |
| Existing foundations reused | Exact paths/classes/functions. |
| New production code | Exact files expected to change/create. |
| Existing production code touched | Exact files and why. |
| Persistence impact | None, or exact writer/authority. |
| Execution impact | None, or exact orchestrator/consent path. |
| Productive entry | How real lifecycle reaches it. |
| Canonical output | Model/identity/fingerprint. |
| Downstream consumer | Who may consume it. |
| Fail-closed condition | What happens when evidence is insufficient. |
| Tests added | RED + architecture + reachability + regression. |
| Existing tests potentially affected | Named before modification. |
| Docs updated | Root + detailed docs. |
| Legacy interaction | Any compatibility dependency. |
| Promotion gates | Ruff + full Pytest. |
| Inventory update | Required before freeze. |

---

## 13. Current future-development decision matrix

| Candidate | Current reality | Exact action |
|---|---|---|
| Hierarchical conceptual intelligence | Relational abstraction exists; hierarchy/composition missing | NEW inside `governed_reasoning`, reusing existing abstraction. |
| Rich structural analogy | Bounded structural transfer exists | DEEPEN only after hierarchical concepts. |
| Explanatory theories | Hypothesis discrimination/update exists | COMPOSE richer explanatory model; do not create parallel hypothesis engine. |
| Advanced counterfactuals | Scenario/Causal exists | DEEPEN multi-stage chains. |
| Cross-domain knowledge | Knowledge/retrieval exists | NEW synthesis layer under existing authorities, not domain brains. |
| Curiosity | Productive Post-M409 path exists | DEEPEN; do not reimplement. |
| Long-horizon inquiry | Multi-step investigation exists | DEEPEN bounds/replanning/resumability. |
| Autonomous learning | Human-approved durable loop exists | NEW risk-governed admission policy later. |
| Durable metacognition | Transient HCE loop exists | OPTIONAL future governed learning; not residual. |
| Self-improvement | Diagnostics/proposal foundations exist | DEEPEN toward candidate patches; never self-promote. |
| Biblioteca | Individual document intelligence exists | NEW governed collection/index/retrieval. |
| Personal visual collection / Pinacoteca (provisional) | Canonical private image repository + governed vision + downstream visual cognition exist | CONTRACT productive provisioning + explicit stored-image selection/analysis seam; no new visual authority. |
| Personal intellectual continuity | Strong conversation/memory foundation | DEEPEN shared topics/inquiries/cultural continuity. |

---

## 14. Priority order after reconciliation

### P0 — Keep this master inventory synchronized

This document becomes a required pre-change control artifact.

### P1 — Governed Hierarchical Concept Composition

Highest-value demonstrated cognitive gap.

### P2 — Governed Local Library

High practical value and broad knowledge source without a new cognitive brain.

### P3 — Rich hierarchical structural mapping

Extend current transfer only after P1.

### P4 — Governed Local Music Collection / Playback

Personal cultural environment, low cognitive duplication risk.

### P5 — Explanatory model composition

Build on current hypothesis lifecycle.

### P6 — Cross-domain knowledge synthesis

Converge concepts, library knowledge, analogy and explanatory models.

### P7 — Curiosity depth + long-horizon inquiry

Deepen existing Post-M409 loops.

### P8 — Governed autonomous knowledge admission

Only after epistemic quality is sufficiently mature.

### P9 — Durable metacognitive learning

Optional, governed and reversible.

### P10 — Self-improvement candidate patches

Human/governed promotion remains mandatory.

---

## 15. Master modification rule

For every future request — whether adding, simplifying, fixing, refactoring or retiring code — start here:

> **What capability owns this behavior today, and what is the smallest proven residual?**

Then modify the owner, not the symptom.

A successful ROBY change is not the one that adds the most files or tests. It is the one that changes the fewest necessary architectural surfaces while increasing a real productive capability and preserving every unrelated contract.

---

## 16. Repository navigation appendix — current direct `core/` families

The following list is a navigation map, **not a declaration that each directory is a canonical authority**. Many are mechanisms, historical families, adapters or legacy scope. Their presence must never be interpreted as authorization to extend them.

- `core/adaptive_cognition/`
- `core/always_on_personal_runtime/`
- `core/ambient_context_foundation/`
- `core/ambient_observation_resolution/`
- `core/android_bridge/`
- `core/application_lifecycle/`
- `core/background_continuity/`
- `core/cognitive_confidence/`
- `core/cognitive_focus/`
- `core/cognitive_goals/`
- `core/cognitive_maturity/`
- `core/cognitive_model_router/`
- `core/cognitive_planning/`
- `core/cognitive_priority/`
- `core/cognitive_runtime_orchestration/`
- `core/cognitive_state_contract/`
- `core/companion_reliability_model/`
- `core/connectivity_domain/`
- `core/context_transfer/`
- `core/controlled_autonomy/`
- `core/conversation_entry_point/`
- `core/cross_context_continuity/`
- `core/current_location/`
- `core/desktop_runtime_integration/`
- `core/development_console_observability/`
- `core/device_arbitration/`
- `core/device_capabilities/`
- `core/device_continuity/`
- `core/document_actions/`
- `core/document_classification/`
- `core/document_extraction/`
- `core/document_intelligence/`
- `core/driving_companion/`
- `core/driving_context/`
- `core/driving_conversation_adaptation/`
- `core/driving_interaction_policy/`
- `core/driving_safety_coordination/`
- `core/end_to_end_local_conversation/`
- `core/executive_coordinator/`
- `core/executive_event_model/`
- `core/executive_notification_broker/`
- `core/executive_presence_attention/`
- `core/executive_recovery_health/`
- `core/executive_runtime_integration/`
- `core/external_retrieval_execution/`
- `core/face_detection/`
- `core/governed_external_intelligence/`
- `core/governed_operational_conversation_pipeline/`
- `core/governed_provider_execution_adapter/`
- `core/governed_provider_routing/`
- `core/governed_reasoning/`
- `core/governed_synchronization/`
- `core/hands_free/`
- `core/intelligent_audio/`
- `core/intelligent_vision/`
- `core/knowledge_retrieval_execution/`
- `core/knowledge_retrieval_orchestrator/`
- `core/knowledge_source_policy/`
- `core/living_conversation/`
- `core/living_conversation_conversation_candidate/`
- `core/living_conversation_conversation_eligibility_decision/`
- `core/living_conversation_conversation_readiness/`
- `core/living_conversation_conversation_timing_evaluation/`
- `core/living_conversation_opportunity_prioritization/`
- `core/living_conversation_opportunity_selection/`
- `core/living_conversation_presence_awareness/`
- `core/living_conversation_presence_consumer/`
- `core/living_conversation_presence_opportunity/`
- `core/living_conversation_presence_policy/`
- `core/local_first_provider_policy/`
- `core/local_provider_runtime_adapter/`
- `core/local_runtime_bootstrap/`
- `core/location_resolution/`
- `core/long_lived_runtime_lifecycle/`
- `core/long_term_experience_evaluation/`
- `core/map_context_integration/`
- `core/map_display/`
- `core/maps_foundation/`
- `core/memory_runtime_integration/`
- `core/mobile_companion/`
- `core/mobile_context/`
- `core/mobile_extension/`
- `core/mobile_presence/`
- `core/mobile_runtime/`
- `core/natural_greeting_response/`
- `core/navigation_coordination/`
- `core/notification_intelligence/`
- `core/object_detection/`
- `core/object_knowledge/`
- `core/operational_response_assembly/`
- `core/operational_trace_model/`
- `core/persistent_cognitive_state/`
- `core/person_detection/`
- `core/personal_identity_and_session_profiles/`
- `core/physical_transport/`
- `core/places_knowledge/`
- `core/platform_runtime_compatibility/`
- `core/presence_change_detection/`
- `core/presence_context_consumption_gateway/`
- `core/presence_context_delivery/`
- `core/presence_context_dispatch/`
- `core/presence_context_integration/`
- `core/presence_context_publication/`
- `core/presence_context_subscription/`
- `core/presence_continuity/`
- `core/presence_event_interpretation/`
- `core/presence_situation_assessment/`
- `core/presence_understanding/`
- `core/provider_health_evaluation/`
- `core/residence_domain/`
- `core/resident_runtime_service/`
- `core/residential_node/`
- `core/residential_perception/`
- `core/residential_remote_presence/`
- `core/roby_console_application/`
- `core/roby_voice_style_policy/`
- `core/route_intent_modeling/`
- `core/runtime_composition_root/`
- `core/runtime_readiness_gate/`
- `core/scene_understanding/`
- `core/self_diagnostics/`
- `core/supervised_autonomy/`
- `core/text_extraction/`
- `core/tool_runtime_integration/`
- `core/unified_companion_integration/`
- `core/unified_permission_consent/`
- `core/visual_attention/`
- `core/visual_code_detection/`
- `core/visual_context_integration/`
- `core/visual_observation_resolution/`
- `core/visual_understanding_foundation/`
- `core/web_enrichment/`


---

## 17. Post-M409 reconciliation appendix

The baseline contains a large Post-M409 body that must be considered before any future cognition work. Notable documents include:

- `docs/POST_M409_1_ADMITTED_REASONING_EVENT_HISTORY_READER_V1.md`
- `docs/POST_M409_1_ADVANCED_CAPABILITY_2B_GOVERNED_SELF_IMPROVEMENT_PROPOSAL_GENERATION.md`
- `docs/POST_M409_1_APPROVED_LEARNING_MEMORY_MATERIALIZATION_PROPOSAL_V1.md`
- `docs/POST_M409_1_CURIOSITY_EXISTING_M369_LEARNING_EVALUATION_V1.md`
- `docs/POST_M409_1_CURIOSITY_HUMAN_ANSWER_EVIDENCE_KNOWLEDGE_CANDIDATE_V1.md`
- `docs/POST_M409_1_CURIOSITY_KNOWLEDGE_ADMISSION_CLASSIFICATION_V1.md`
- `docs/POST_M409_1_CURIOSITY_RELEVANCE_INITIATIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_EXPLICIT_DELIBERATION_DECISION_OPTION_ADAPTER_V1.md`
- `docs/POST_M409_1_EXPLICIT_DELIBERATION_PRODUCTIVE_ADVISORY_WIRING_V1.md`
- `docs/POST_M409_1_EXPLICIT_HUMAN_DECISION_DELIBERATION_EVIDENCE_PRODUCER_V1.md`
- `docs/POST_M409_1_GOVERNED_COMPARATIVE_REASONING_METHOD_AWARENESS_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_COMPARATIVE_REASONING_METHOD_AWARENESS_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_EPISTEMIC_CURIOSITY_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_EPISTEMIC_SUFFICIENCY_ASSESSMENT_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_EPISTEMIC_SUFFICIENCY_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_EVIDENCE_ACQUISITION_PLANNING_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_EVIDENCE_ACQUISITION_PLANNING_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_HYPOTHESIS_EPISTEMIC_DELTA_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_HYPOTHESIS_UPDATE_SEMANTICS_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_HYPOTHESIS_UPDATE_SEMANTICS_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_INDEPENDENCE_LEVEL2_READ_ONLY_EXECUTION_GATEWAY_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_INDEPENDENCE_LEVEL_1_2_AUTHORIZATION_BOUNDARY_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_INDEPENDENCE_LEVEL_1_2_AUTHORIZATION_BOUNDARY_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_LEARNING_PRODUCTIVE_END_TO_END_WIRING_V1.md`
- `docs/POST_M409_1_GOVERNED_LEVEL_2B_PRODUCTIVE_ENTRY_REAL_WORLD_REACHABILITY_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_LEVEL_2_ACQUIRED_EVIDENCE_REASONING_REENTRY_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_LONGITUDINAL_REASONING_ASSESSMENT_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_LONGITUDINAL_REASONING_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_MEMORY_WRITE_ADAPTER_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_A2_LEVEL2_READ_ONLY_EXECUTION_E2_PRODUCTIVE_REENTRY_V1.md`
- `docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_CONTINUATION_EVIDENCE_ACQUISITION_PLANNING_PRODUCTIVE_REENTRY_V1.md`
- `docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_E2_REASONING_REENTRY_2_MANDATORY_EPISODE_CLOSURE_V1.md`
- `docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_EPISODE_STOPPING_BOUNDARY_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_P2_INDEPENDENCE_AUTHORIZATION_A2_PRODUCTIVE_REENTRY_V1.md`
- `docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_PRODUCTIVE_CONTINUATION_V1.md`
- `docs/POST_M409_1_GOVERNED_MULTI_HYPOTHESIS_COMPARISON_DISCRIMINATION_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_MULTI_HYPOTHESIS_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_ASSESSMENT_EVENT_PROJECTION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_HYPOTHESIS_DEEPENING_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_METHOD_EFFECTIVENESS_AWARENESS_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_METHOD_EFFECTIVENESS_AWARENESS_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_METHOD_OUTCOME_ASSOCIATION_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_METHOD_OUTCOME_ASSOCIATION_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_METHOD_PROVENANCE_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_METHOD_PROVENANCE_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_QUALITY_ASSESSMENT_FOUNDATION_V1.md`
- `docs/POST_M409_1_GOVERNED_REASONING_QUALITY_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_HYPOTHESIS_GAP_CURIOSITY_EVIDENCE_ADAPTER_FOUNDATION_V1.md`
- `docs/POST_M409_1_HYPOTHESIS_GAP_GOVERNED_CURIOSITY_PRODUCTIVE_CONSUMPTION_V1.md`
- `docs/POST_M409_1_LINKED_ORGANIZATION_M391_6_ADVISORY_ASSEMBLY_FOUNDATION_V1.md`
- `docs/POST_M409_1_LONGITUDINAL_REASONING_OBSERVATION_CONTRACT_GENERALIZATION_V1.md`
- `docs/POST_M409_1_M369_EXPLICIT_HUMAN_LEARNING_APPROVAL_EVIDENCE_V1.md`
- `docs/POST_M409_1_OFFICIAL_MEMORY_GATEWAY_GOVERNED_LEARNING_WRITE_CONTRACT_EXTENSION_V1.md`
- `docs/POST_M409_1_PARTIAL_ORGANIZATION_M391_5_CONSUMPTION_FOUNDATION_V1.md`
- `docs/POST_M409_1_PARTIAL_ORGANIZATION_SNAPSHOT_EXACT_LINKAGE_FOUNDATION_V1.md`
- `docs/POST_M409_1_PRODUCTIVE_CONVERSATIONAL_CURIOSITY_WIRING_V1.md`
- `docs/POST_M409_1_PRODUCTIVE_ORGANIZATION_ADVISORY_WIRING_V1.md`
- `docs/POST_M409_1_PRODUCTIVE_ORGANIZATION_EVIDENCE_PROJECTION_V1.md`
- `docs/POST_M409_1_REASONING_CONTEXT_BUNDLE_DERIVED_ASSESSMENT_CONTRACT_GENERALIZATION_V1.md`
- `docs/POST_M409_1_RF_E_3A_8_PRODUCTIVE_TEMPORARY_RULE_INTAKE_V1.md`
- `docs/POST_M409_1_RF_E_CONTEXTUAL_CASE_GROUNDING_V1.md`
- `docs/POST_M409_1_RF_E_GAP_A_BOUNDED_GRAMMAR_COMPATIBILITY_V1.md`
- `docs/POST_M409_1_RF_E_GROUNDING_BRIDGE_V1.md`
- `docs/POST_M409_1_RF_E_PRODUCTIVE_INTAKE_REACHABILITY_V1.md`
- `docs/POST_M409_1_RF_H_OBJECT_AWARE_RELATIONAL_ROLE_BINDING_V1.md`
- `docs/POST_M409_1_ROBY_CONVERSATIONAL_E2E_READ_ONLY_DESKTOP_DIAGNOSTIC_HARNESS.md`


These documents demonstrate why roadmap labels alone are insufficient: curiosity, hypothesis revision, learning materialization, investigation, decision advisory, reasoning quality/provenance, independence authorization and self-improvement proposal capabilities already have architecture beyond what a shorter cognitive inventory can convey.

---

## 18. Certification policy for this guide

This guide is a **reconciled navigation and decision-control document**, not a claim that every one of the 1,000+ files has been semantically proven dead/live in isolation.

For destructive refactors or physical legacy removal, a dedicated dependency/reachability audit is still mandatory.

For new cognitive work, however, this reconciliation is sufficient to establish the default rule:

**audit existing capability first → prove residual → extend canonical owner → run full gates → update inventory → freeze.**

---

## 19. Final decision

ROBY XI.2 should now be managed as a mature governed cognitive system, not as a feature-accumulation project.

The official development posture becomes:

**one brain → one authority per capacity → one master inventory → surgical changes → full regression gates.**

This Master Surgical Guide must be consulted before every new implementation and before every architectural modification to an existing capability.


## M367 historical inventory retirement reconciliation

M367 must no longer be treated as one removable block. M367.1 survives as an evolved current World Model façade and M367.6 remains a productive priority-reasoning capability. M367.2/.3/.4/.5/.7 were historical read-only inventory/diagnostic surfaces and are retired only after reconciling the current M368/M379/CCI-03 contracts to existing owners. The governing pattern is: **retire descriptive umbrella -> preserve specialized owners -> do not create replacement umbrella**.

Status: **CLOSED / CERTIFIED — owner gate 12,440 PASS · 0 FAIL · Ruff clean**.
