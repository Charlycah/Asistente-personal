> **Current baseline pointer:** consult `ROBY_XI_2_CURRENT_TRUTH.md` first. This guide remains the deep reconciliation/decision-control reference and does not supersede the compact current-state baseline.

# ROBY XI.2 — Cognitive Inventory Reconciliation — Master Surgical Guide

**Historical guide reconciliation baseline:** 12,471 PASS · 0 FAIL · Ruff clean  
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
**Existing evidence:** explicit hypothesis source, scenario simulation, causal prediction, hypothesis deepening, multi-hypothesis discrimination, epistemic delta, hypothesis update semantics and productive consumption. Governed Hypothesis Formation is owner-certified at 12,406 PASS · 0 FAIL · Ruff clean and projects already-governed tentative/contextual claims and exact rule-result claims into alternative candidates under the same owner.  
**Current candidate boundary:** explicit structured Scenario/Causal semantics may be admitted for one exact formed candidate only with exact candidate/goal lineage plus complete provenance. The seam constructs the existing `GovernedExplicitHypothesisSource`; it performs no natural-language semantic inference and adds no LLM/retrieval authority, truth promotion, persistence, Memory/Learning/action authority or world mutation. Owner certification pending.  
**Residual after certification:** source of explicit structured semantics remains governed and explicit; later work may connect already-authorized human/evidence semantics, then reuse existing Scenario/Causal → Deepening → Discrimination.  
**Do not create:** a generic TheoryEngine, HypothesisManager or parallel research brain; reuse the existing hypothesis lifecycle and `governed_reasoning` ownership.

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

**Status:** SUBSTANTIAL / PRODUCTIVE; explicit gap + governed-topic-evidence reachability CLOSED / CERTIFIED — 12,399 PASS.  
**Owners:** Reasoning owns the epistemic gap; governed information sources own explicit topic evidence; the existing Relevance authority decides household relevance; Curiosity owns question creation; Initiative owns whether/when to ask; Conversation owns realization.  
**Existing implementation:** `core/cognitive_maturity/governed_epistemic_curiosity.py`, `hypothesis_gap_curiosity_evidence.py`, `curiosity_human_answer_evidence.py`, `curiosity_knowledge_admission_classification.py`, living-conversation curiosity, Post-M409 productive wiring, plus candidate `app/epistemic_gap_governed_topic_curiosity_runtime.py`.  
**What already exists:** gap-driven question candidate, hypothesis-gap adapter, governed source topics, Relevance/Initiative consumption, conversational realization, exact human-answer evidence, knowledge candidate, admission classification, learning evaluation. The candidate seam requires exact item identity plus exact gap lineage and never infers `InterestTopic` from text/tags/source kind.  
**Residual after certification:** richer concept/theory gaps, prioritization among competing questions, redundancy suppression, continuity across long investigations.  
**Do not reimplement Curiosity, PersonalInterestCenter, RelevanceEvaluator, or add a generic topic classifier.**

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

**Status:** SUBSTANTIAL / PRODUCTIVE; cross-domain synthesis and bounded semantic-domain evidence admission into the existing binding are CLOSED / CERTIFIED — owner gate 12,440 PASS · 0 FAIL · Ruff clean.  
**Existing components:** `knowledge_gateway.py`, `personal_knowledge_base.py`, `project_knowledge_model.py`, knowledge source policy, retrieval orchestrator/execution, governed external intelligence, object/place knowledge, adaptive knowledge evolution.  
**Residual:** no CAP-19 semantic-domain admission reachability residual remains. Ordinary autonomous semantic-domain attribution is a separate future policy problem, not part of CAP-19 synthesis authority.  
**Architecture rule:** domains are content/source vocabularies, not separate brains.

### 6.2 Local documents / Biblioteca

**Status:** PRODUCTIVE / GOVERNED READ-ONLY EVIDENCE SOURCE; CAP-17/CAP-11 continuation certified.  
**Existing components:** `core/governed_local_library/`, DocumentReading, Knowledge runtime, Unified Retrieval, local evidence Reasoning re-entry, CAP-11 Episode recording, canonical hypothesis reassessment and existing requirement admission/continuation.  
**Existing value:** an explicitly authorized local book/document root can be catalogued, selected, read and transformed into governed evidence that re-enters the existing Reasoning authority and the same bounded CAP-11 Episode. The exact prior hypothesis product is preserved through `source_report_id`, and zero/one R(N+1) is handled by existing CAP-11 authorities.  
**Certified boundary:** STOP before Planning N+1. No direct Memory/Learning integration, no background scanning, no second Reasoning/Planning/Episode authority.  
**Architecture rule:** catalogue is an instrumental source; DocumentReading owns content reading; Knowledge owns sourcing/retrieval; `governed_reasoning` owns epistemic reassessment; CAP-11 owns investigation continuation.  
**Separate future problem:** durable learning/consolidation requires its own governed admission policy and must not be inferred from CAP-17 completion.

Current certified flow:

**authorized library root → catalogue/selection → DocumentReading → Unified Retrieval/Knowledge artifact → governed Reasoning re-entry → CAP-11 Episode recording → same-hypothesis reassessment → existing requirement admission/continuation → STOP before Planning.**

### 6.2A Personal Documents as governed private source

**Status:** PRODUCTIVE SOURCE FOUNDATION / DURABLE SHARED RUNTIME — CERTIFIED.  
**Canonical authority:** `core.document_inbox.DocumentInboxManager`; `DocumentRepository` remains its persistence port and `SQLiteDocumentRepository` is the durable adapter.  
**Official provisioning:** `build_runtime_root()` creates one `document_inbox` and injects that exact instance into Personal Knowledge and Task Intelligence. `DocumentReadingService` remains a reader, not a second catalogue/source authority.  
**Provenance boundary:** `document_id` is canonical source identity; content hash proves content/version; source metadata remains distinct from general Knowledge and Biblioteca identity.  
**Certified boundary:** no automatic ingest/background scanner and no automatic transition to Reasoning, Planning, Memory or Learning. Biblioteca and Personal Documents remain distinct source domains.  
**GATE 3 document-source residual:** **ZERO** at this boundary.

### 6.3 Personal visual collection / "Pinacoteca" (provisional roadmap name)

**Status:** PRODUCTIVE FOUNDATION / EXPLICIT USER-INITIATED STORED-IMAGE ACCESS WIRED TO OFFICIAL RUNTIME.  
**Canonical authorities:** `ImageRepository` + `FileImageRepository` own private stored-media persistence; `GovernedVisionGateway` is the application boundary; `OfficialVisionCore` + `IntelligentVisionService` own governed visual analysis/policy; existing visual cognitive context remains downstream and subordinate.  
**Existing value:** explicit consent-gated JPEG/PNG/WebP storage, owner-scoped metadata listing, deletion, SHA-256 provenance, governed camera vision, scene/object/person/non-identity-face/OCR/code/document analysis and transient visual-to-cognitive projection already exist.  
**Certified closure:** GATE 3.B.1 and GATE 3.B.2 close the previously identified stored-image seam. `ImageRepository.read_asset(...)` provides owner-scoped transient asset access with SHA-256 integrity verification; `GovernedVisionGateway.analyze_stored_image(...)` delegates selected stored media to the existing `OfficialVisionCore` without camera-capture semantics; and the official runtime registers exactly one `vision.stored_images.read_analyze` capability after the historical registry order.  
**Nomenclature decision:** "Pinacoteca" remains provisional for photographs/images/art; historical music/audio usage is superseded.  
**Architecture rule:** no new visual manager/repository/core/gateway, no gallery scanning, no biometrics and no automatic Memory/Learning/Reasoning. GATE 3 visual-source residual: **ZERO** at the certified boundary; later cross-source cognition remains a separate gate.

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
- `docs/history/ESTADO_MAESTRO_INTEGRAL.md` (historical master-state trace; present-state authority is `ROBY_XI_2_CURRENT_TRUTH.md`);
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

## 12.1 CURRENT CERTIFIED-STATE RECONCILIATION

This layer interprets the historical matrices below against the latest certified
repository state. It does not erase or rewrite their historical record.

**CURRENT EXECUTABLE TRUTH + LATEST OWNER GATE > STALE HISTORICAL STATUS LABEL**

- **H3:** self-capability explanation is closed at the proven bounded residual.
- **H4-MMC:** no current generalized composition residual is proven; additional
  evidence admission remains a separate partial/future horizon.
- **H4-VOICE:** S1 and S2 are owner-certified; no current productive residual is
  proven after canonical adaptive delivery tone reaches spoken expression.
- **Voice-Situational S1:** OWNER-CERTIFIED at 13,152 PASS / 0 FAIL. Canonical
  `response_detail` and `response_structure` reach the existing vocal projection seam.
  `rate / pitch / volume` are technically available TTS controls, not a proven
  canonical acoustic decision: NO CURRENT PRODUCTIVE RESIDUAL PROVEN; STOP BEFORE S2.
- Persistent Cognitive Companion is REALIZED / BOUNDED through existing authorities;
  cross-session continuity reuses governed memory/retrieval, Cognitive Agenda lifecycle,
  bounded initiative and integrated cognition. Persistence/retrieval does not authorize
  execution or bypass Relevance, Planning or Authorization.
- S5 remains closed at C3 and STOP before Relevance unless new explicit governed
  topic evidence with exact lineage is introduced.
- ROBY Voice Identity remains FUTURE; richer embodiment is not implementation
  authorization.

**NO NEXT PRODUCTIVE HORIZON CURRENTLY PROVEN**

Historical priority/status sections below remain provenance, not automatic
implementation authorization. New work still requires inventory, reuse proof, a
minimal residual, contract, RED, GREEN, and owner certification.

---

## POST-NORTH-STAR — current interpretation of historical priorities

The P1-P10 priority/status material below is **HISTORICAL** planning provenance.
It is **NOT** the current productive BACKLOG and does not authorize new work.
Current executable truth and the latest OWNER-certified state take precedence.

**NO NEXT PRODUCTIVE RESIDUAL IS CURRENTLY DEMONSTRATED.**

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
| Biblioteca | Governed read-only source is productive through Reasoning reassessment and CAP-11 requirement continuation | DEEPEN only via separately governed learning/consolidation or justified retrieval improvements. |
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


## APP BRAIN → infrastructure repository seam reconciliation

The governed layering rule for diagnostic BRAIN composition is now explicit: application
composition receives repository contracts; concrete infrastructure repositories are built
at a higher entry-point boundary. This is dependency inversion only, not authority
succession. Identity stores remain outside this seam and require a separate audit before
any future surgery.

Status: **CLOSED / CERTIFIED — owner baseline 12,355 PASS · 0 FAIL · Ruff clean**.

### P4.A — Governed Local Music Read-Only Catalogue Foundation

The first P4 gate is implemented as a separate, explicitly provisioned read-only
catalogue. `ROBY_LOCAL_MUSIC_ROOT` defines the only authorized source root. Catalogue
metadata/provenance is productively reachable through `music.local_catalogue.read`.
Selection and playback remain intentionally outside this gate.

### P4.B — Governed Local Music Selection Foundation

P4.B adds deterministic, non-executing selection over the P4.A read-only catalogue.
Unique catalogue evidence may be selected; ambiguity requires human disambiguation.
Playback remains a separate future gate and receives no authority from selection.

### P4.C — Governed Local Music Playback Authorization / Execution Foundation

P4.C adds a separate human-authorized device execution gate after P4.A catalogue and
P4.B selection. Playback is provisioned only by an explicit local player command and
cannot be inferred from selection alone. Ambiguous or absent selections fail closed.
Transport controls and autonomous initiative remain future gates.


## Intellectual Evolution — Productive Investigation Reentry Routing reconciliation

The owner gate rejected the first routing candidate because it changed the byte-protected
governed reasoning runtime. The reconciled design therefore treats that runtime as an
immutable authority and composes only through its existing public structured-hypothesis
evaluation API.

The authorized intellectual-goal path is now separate from the ordinary automatic
explanatory-model reentry. It accepts exactly two already-structured hypotheses with
exact goal lineage, reuses existing Scenario/Causal evaluation, Hypothesis Deepening and
multi-hypothesis discrimination, and reaches CAP-11 only through the existing G4
authorized-goal requirement admission. Anything other than exactly one discriminating
requirement stops before CAP-11.

This is a composition/routing seam, not a new brain, investigation manager, hypothesis
authority, planner, executor or persistence owner. Owner certification: **12,420 PASS · 0 FAIL · Ruff clean**.
Status: **CLOSED / CERTIFIED**.


## Intellectual Evolution — CAP-11 terminal closure → M369 candidate reachability

The end-to-end reconciliation separated capability existence from productive
reachability. The G5 admission contract already existed and already enforced the correct
terminal CAP-11 lineage and M369 stop boundary; the missing piece was official runtime
exposure.

The candidate therefore adds no cognitive authority. It only exposes the existing G5
admission from `OfficialRuntimeComposition` / `OfficialROBYRuntime`. The surgery stops at
the existing review-required M369 `LearningCandidate`. Later M369 evaluation, explicit
human approval, materialization and durable writes remain separate governed boundaries.

This closes only the proven reachability residual and must not be interpreted as
autonomous knowledge admission. Owner certification: **12,425 PASS · 0 FAIL · Ruff clean**.
Status: **CLOSED / CERTIFIED**.


## Intellectual Evolution — M369 candidate → M369 evaluation reachability

The investigation path now reaches the existing M369 `LearningCandidate`. The next
verified residual was not missing evaluation semantics but official runtime reachability
to the already-existing source-neutral `GovernedLearningCandidateM369EvaluationV1`.

The candidate exposes that existing evaluator without adding a new policy, learning,
knowledge, approval, persistence or memory authority. Evaluation remains read-only and
the surgery stops before G6 explicit human approval. Owner certification: **12,430 PASS · 0 FAIL · Ruff clean**.
Status: **CLOSED / CERTIFIED**.


## Intellectual Evolution — M369 evaluation → G6 human approval reachability

The existing source-neutral G6 seam already owns explicit human approval semantics.
The verified residual was official runtime reachability only. The owner-certified surgery
exposes G6 without auto-calling it or manufacturing human approval evidence. Human
authorization therefore remains an intentional hard boundary. The certified surgery stops
before G7. Owner gate: **12,435 PASS · 0 FAIL · Ruff clean**.


## Intellectual Evolution — G6 approved learning → G7 materialization reachability

The existing source-neutral G7 seam already owns governed transformation of exact
G6-approved M369 learning into an `ApprovedLearningMemoryMaterializationReport` and,
when the existing contract permits it, a `GovernedMemoryMaterializationProposal`. The
verified residual is official runtime reachability only. This candidate exposes that
existing G7 authority without auto-calling structural eligibility or proposal methods and
without creating any persistence authority. The surgery stops before the existing memory
write adapter, `OfficialMemoryGateway` and every durable write. Owner certification: **12,440 PASS · 0 FAIL · Ruff clean**.
Status: **CLOSED / CERTIFIED**.

## R-CI-SI-S5 — Self-Epistemic Relevance Horizon Closure

**Status:** CLOSED / CERTIFIED — documentary; **13,110 PASS · 0 FAIL · Ruff clean**.

**Certified chain:** C1 `NEED_TO_ASK` → C2 existing Curiosity gap evidence with
`relevance=UNKNOWN` → C3 `NO_COMPATIBLE_GOVERNED_TOPIC_EVIDENCE_ROUTE` → STOP
before Relevance.

**Owner reconciliation:** governed information sources still own explicit topic
evidence; the existing Relevance authority decides relevance; Curiosity owns
question creation; Initiative owns whether/when to ask; Conversation owns
realization. S5 adds none of those authorities.

**Future reopening rule:** only explicit source-declared governed topic evidence
with exact self-epistemic gap lineage may reopen productive reachability through
the existing CAP-10 seam. Do not infer topics, translate UNKNOWN relevance or
create C4 from numbering alone.


## CAP-17 / R-CAP17-O3-S16 — No-new-capability reuse reconciliation

The O3 bounded residual was direct access to an explicitly supplied nested relative path excluded by the catalogue entry limit. The canonical CAP-17 catalogue implements direct path lookup (S11), and the existing Knowledge-admitted conversational selection, handoff and Unified Retrieval implement reachability (S14). No duplicate catalogue, background scanner, planner, retrieval owner, persistent index or learning write was added. S15 real-library diagnostic PASS with zero catalogue scans. The residual of general title discovery outside the catalogue limit remains **OPEN / NOT AUTHORIZED**. O3/S16 controlled baseline promotion is OWNER-CERTIFIED with an explicit M377 exception: integral Windows 13,724 PASS / 47 M377 intentional RED / 0 unexpected failures; G2 focal 16 PASS, Ruff PASS. This is not a global zero-failure GREEN. M377 HOLD and the title-discovery residual remain unchanged; see S16-CLOSE quality gate record.
