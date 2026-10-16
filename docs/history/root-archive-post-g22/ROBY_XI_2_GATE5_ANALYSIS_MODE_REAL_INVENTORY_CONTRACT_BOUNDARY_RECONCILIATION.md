# ROBY XI.2 — GATE 5 — Analysis Mode Real Inventory / Contract Boundary Reconciliation

**Type:** SURGICAL RECONCILIATION / REAL INVENTORY / CONTRACT BOUNDARY

**Entry baseline:** GATE 4 certified and closed — 13,975 PASS + Ruff clean + 0 FAIL.

**Production changes in this gate:** NO.

## 1. Objective

Determine what the roadmap concept **“ROBY, entrá en modo análisis”** means against the real certified repository before creating any productive component.

This gate must distinguish:

- analysis of an external/user problem;
- introspection about ROBY's published internal state;
- technical/project state reporting;
- architectural diagnosis;
- presentation/session semantics called “mode”.

The governing rule is unchanged: **Analysis Mode is not a second brain and does not own Reasoning, Planning, Reflection, Self Model, Self Diagnostics, Capability Registry or runtime state.**

## 2. Roadmap intent recovered

The historical strategic roadmap defines Analysis Mode as a **conversational interface over governed introspection**, with conceptual activation `ROBY, entrá en modo análisis` and three possible views:

1. **Personal analysis** — general state, pending matters, degraded capabilities, active investigations.
2. **Technical analysis** — owners, states, episodes, budgets, registries, errors, dependencies, versions, capabilities and certifications.
3. **Architectural analysis** — evidence-backed explanation of excessive responsibility concentration, incomplete capabilities, possible duplication, degraded components, existing code without exposure, documentation/code inconsistencies, architectural debt and test/certification state.

The roadmap also requires that ROBY explain real, traceable state without pretending subjective internal states or a verbatim “secret thought”.

## 3. Existing productive authorities and seams

### 3.1 `cognitive.guided_analysis` already exists

`app/runtime_root_factory.py` registers exactly one official capability named:

`cognitive.guided_analysis`

Its description explicitly integrates governed reasoning, planning, reflection and coordination for explicit cognitive requests. Its interceptor is `CognitiveCapabilityMarker`, which is a registry marker only; it does not itself execute another cognitive authority.

**Verdict:** `EXISTING OFFICIAL COGNITIVE CAPABILITY / NOT ANALYSIS-MODE AUTHORITY`.

This capability analyzes a requested problem. It must not be renamed or reinterpreted as the introspective user interface called Analysis Mode.

### 3.2 Explicit analysis intent is already detected by the Cognitive Planner

`core.cognitive_planning.CognitivePlanner.assess_cognitive_needs(...)` already recognizes explicit verbs such as analyze/reason/evaluate/compare and maps them to existing `CognitiveNeed` values.

`app/cognitive_runtime_sources.OperationalCognitiveSource` then produces only the relevant advisory artifacts. Existing M249 tests demonstrate that an explicit request such as `Analizá cognitivamente este problema` activates Reasoning while ordinary conversation does not activate the cognitive sources.

**Verdict:** `EXISTING TURN-SCOPED COGNITIVE ANALYSIS ROUTING`.

This is not a persistent or session-scoped “mode”.

### 3.3 Existing cognitive composition is already unified

The official runtime already owns one `CognitiveRuntimeOrchestrator` with the existing governed contributors for reasoning, planning, reflection, executive coordination and other certified cognitive contributors.

The project also contains `UnifiedCognitiveCoordinator` and governed cognitive strategy projection infrastructure. Those components preserve advisory-only and no-authority-granting boundaries.

**Verdict:** `EXISTING UNIFIED COGNITIVE COMPOSITION`.

No `AnalysisModeReasoner`, `AnalysisPlanner`, `AnalysisReflectionEngine` or second orchestrator is justified.

### 3.4 Unified introspection is already closed and certified

GATE 4 established `UnifiedRuntimeObservability` as the official read-only projection seam. GATE 4.A.1 certified explicit projections for:

- Capability Registry;
- published Self Model;
- Reflection structural/published state;
- Self Diagnostics availability without fabricated report.

**Verdict:** `EXISTING OFFICIAL READ-ONLY INTROSPECTION SOURCE`.

Analysis Mode must consume this seam rather than read internal objects ad hoc or create a new introspection repository.

### 3.5 Conversational self-analysis is a different capability

`app/conversational_self_analysis.py::AutonomousConversationalSelfAnalysis` performs bounded advisory analysis of conversation quality (user correction, context reuse, repeated opening, response length). It is selected internally and explicitly states it is not a public command.

**Verdict:** `EXISTING SPECIALIZED CONVERSATION-QUALITY SELF-ANALYSIS / NOT ANALYSIS MODE`.

It must not become the owner of general introspection or architectural analysis.

## 4. What does NOT exist as a certified capability

Repository inspection found no canonical productive class or runtime state named `AnalysisModeManager`, `IntrospectionManager`, `UnifiedIntrospectionManager`, `AnalysisModeRuntime` or equivalent authority.

More importantly, there is no demonstrated certified contract for:

- entering/leaving a user-visible Analysis Mode;
- keeping such mode session-scoped;
- selecting Personal / Technical / Architectural views;
- formatting the read-only introspection projection conversationally by level;
- deciding which unavailable facts must be reported as unavailable rather than inferred;
- producing architectural findings from current code/docs/tests without an explicit evidence-acquisition contract.

This absence is a **surface/interaction seam**, not absence of a brain capability.

## 5. Real capability boundary

### 5.1 Analysis Mode must be a subordinate interaction/profile layer

The correct architecture is:

`Official Conversation / Runtime entry`
→ explicit user activation or explicit analysis-view request
→ subordinate Analysis Mode interaction/profile seam
→ `UnifiedRuntimeObservability` for ROBY-state introspection
→ existing `OfficialRuntimeCapabilityRegistry.interface_snapshot()` through observability
→ published Self Model / Reflection through observability
→ honest Self Diagnostics availability state
→ existing `cognitive.guided_analysis` / governed Reasoning only when the user asks to analyze an external problem
→ response.

The mode itself owns **no cognition and no source of truth**.

### 5.2 “Mode” is presentation/session semantics, not cognitive authority

A future Analysis Mode may remember that the user explicitly entered the mode for the current conversation/session, but that state must be treated as a bounded interaction preference/profile, not as a new cognitive state authority.

Activation must never enable additional autonomy, permissions, tools, Memory/Learning writes or execution rights.

### 5.3 Personal analysis

The existing read-only observability seam is sufficient as the primary source for a first bounded Personal view.

It may summarize only published/available state. If active investigations or pending matters are not exposed by an existing official read-only source, the answer must state that limitation rather than scan or infer hidden state.

### 5.4 Technical analysis

The repository already exposes useful pieces such as capability registration, runtime health/readiness, cognitive resident state and certified observability projections.

However, the complete roadmap list — owners, episodes, budgets, registries, errors, dependencies, versions and certifications — is **not currently proven to exist as one official read-only runtime projection**.

Therefore Technical view is `PARTIAL / COMPOSABLE`, not fully closed by merely exposing observability.

### 5.5 Architectural analysis

The roadmap requires evidence-backed findings about duplication, incompleteness, concentration of responsibility, code without exposure, documentation/code inconsistencies and test/certification state.

`GovernedSelfDiagnostics` is substantial but GATE 4 deliberately established that there is no official current diagnostic report source provisioned in runtime. Calling `diagnose()` simply to populate Analysis Mode would manufacture new diagnostic state and violate the read-only boundary.

The repository also has no certified automatic project-code/document/test evidence collector owned by Analysis Mode.

Therefore Architectural view is `FOUNDATION AVAILABLE / PRODUCTIVE EVIDENCE CONTRACT NOT YET CLOSED`.

## 6. Demonstrated residuals

### G5-R1 — No Analysis Mode interaction contract

There is no official contract for explicit `enter / leave / current-view` semantics. Existing `cognitive.guided_analysis` is turn-scoped cognitive routing and must remain separate.

### G5-R2 — No governed level projection

Personal / Technical / Architectural are roadmap concepts, but no single subordinate projection currently selects and formats existing official sources by those levels.

### G5-R3 — Technical view is only partially represented

Capabilities and runtime/introspection state are available, but the full requested technical inventory (episodes, budgets, dependencies, versions, certifications, errors) is not proven as one canonical read-only projection. Missing fields must remain explicitly unavailable until mapped to existing authorities.

### G5-R4 — Architectural analysis lacks a certified evidence-acquisition seam

Self Diagnostics exists, but no current report is provisioned. Analysis Mode must not call `diagnose()` or scan code/docs/tests implicitly. Architectural findings require a separate explicit, evidence-backed contract reusing existing diagnostics/project evidence authorities.

### G5-R5 — No user-facing conversational exposure of the certified introspection projection

`UnifiedRuntimeObservability` is available through `OfficialRuntime.observability(...)`, but there is no demonstrated user-facing conversational Analysis Mode adapter that consumes it without creating new authority.

## 7. Explicitly NOT missing

GATE 5 does **not** justify creating:

- another Reasoning authority;
- another Planner;
- another Reflection engine;
- another Self Model;
- another Self Diagnostics engine;
- another Capability Registry;
- another observability/introspection root;
- a new cognitive orchestrator;
- a background project scanner;
- a chain-of-thought viewer.

## 8. Contractual classification

**Global classification:**

`EXISTING COGNITIVE ANALYSIS + CERTIFIED READ-ONLY INTROSPECTION AUTHORITIES — MINIMAL USER-INITIATED ANALYSIS-MODE INTERACTION / LEVEL-PROJECTION SEAM REQUIRED`

## 9. Recommended next gate

### GATE 5.A — Existing Official Conversation + UnifiedRuntimeObservability → Explicit User-Initiated Analysis Mode Interaction — CONTRACT BOUNDARY RECONCILIATION

Central question:

> Can a subordinate, session-bounded interaction seam expose Personal / Technical / Architectural analysis views by reading only existing certified authorities, while keeping `cognitive.guided_analysis` as the existing cognitive-analysis capability and refusing to invent unavailable technical/architectural evidence?

Before any RED, GATE 5.A must determine exactly:

1. which existing official conversation interception/wiring surface owns activation parsing;
2. whether mode state is per-turn or explicit session-scoped state and where such interaction state canonically belongs;
3. exact activate/deactivate/status phrases without accidental activation from ordinary uses of “analysis”;
4. the safe projection schema for Personal / Technical / Architectural levels;
5. exact existing authority for every projected field;
6. unavailable-state semantics;
7. whether Architectural view remains informative-only until a later evidence-acquisition gate.

Only after that reconciliation should a CONTRACT RED be written.

## 10. STOP

GATE 5 itself is documentary/reconciliatory only.

STOP before:

- productive Analysis Mode implementation;
- `AnalysisModeManager` or any parallel authority;
- automatic or background introspection;
- automatic code/document/test scanning;
- automatic `GovernedSelfDiagnostics.diagnose()`;
- capability execution from Analysis Mode;
- Memory writes;
- Learning;
- Planning N+1;
- self-repair or code modification;
- new autonomy permissions;
- chain-of-thought/private reasoning exposure;
- invented subjective/emotional state;
- configuration mutation;
- `.roby/config.json` modification.

Preserve `credencial.json` if present.

## 11. Verdict

GATE 5 finds **no missing cognitive brain authority**.

The strategic roadmap capability called Analysis Mode is best understood as a **governed conversational/session presentation layer over existing cognitive and introspective authorities**.

There are demonstrated interaction/projection residuals, so GATE 5 is **RECONCILED, NOT ZERO-RESIDUAL CLOSED**.

Next authorized work: **GATE 5.A — contract boundary reconciliation only.**
