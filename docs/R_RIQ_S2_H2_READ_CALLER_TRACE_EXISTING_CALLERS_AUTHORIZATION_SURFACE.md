# ROBY XI.2 — R-RIQ-S2-H2-READ-CALLER-TRACE

**Subtitle:** Existing Callers & Authorization Surface  
**Class:** Scientific static/documentary investigation. **Status:** CANDIDATE — OWNER APPROVAL PENDING.  
**Baseline:** `ultima version corregida(9).zip`, ZIP root `ultima version corregida/`.  
**STOP_PRODUCTIVE:** ACTIVE.

## 1. Scope and governance

Identify actual consumers of `RuntimeComposition`, `conversation_pipeline.repository`, `last_result`, and the operational response repository; distinguish internal observation from a demonstrated authorized research read boundary. Preserve the single canonical authority and existing diagnostics. No execution, tests, code edits, instrumentation, or experiment.

Prior act `R_RIQ_S2_H2_ACCESS_BOUNDARY_RECONCILIATION_RUNTIME_WIRING_AUTHORIZED_READ.md` was locally integrity-verified; its separate formal Owner approval was not explicitly recorded when this phase was requested.

## 2. Verified static call chain

1. `core/runtime_composition_root/root.py:543,553–579`: composition constructs the assembler and pipeline and retains references in `RuntimeComposition`.
2. `core/local_runtime_bootstrap/bootstrap.py:15–37,47–79`: `LocalRuntimeBootstrap` retains the composition in `_composition`, exposes it through `composition`, and assigns it on `start()`. The presence of a state store for lifecycle state does **not** prove persisted pipeline results.
3. `core/end_to_end_local_conversation/runtime.py:127` invokes `composition.conversation_pipeline.process(...)` on the existing local conversation route.
4. `core/development_console_observability/observer.py:8–16`: `DevelopmentConsoleObserver` receives an `EndToEndLocalConversation` instance and reads its bootstrap composition. Its docstring characterizes the projection as read-only.
5. `core/development_console_observability/observer.py:34–72`: `last_turn()` and `turn_observation(sequence)` use existing turn history and traces; lines 64–72 retrieve `composition.conversation_pipeline.repository.get(turn.pipeline_result_id)` if composition is available. **This is a demonstrated read caller**, not merely a theoretical repository protocol.
6. `core/development_console_observability/observer.py:101–108`: the observation includes turn ID, trace ID, pipeline result ID, and operational response ID. Additional observed metadata derives from the matched pipeline result and inference request; no universal H2 epistemic assessment correlation is established.
7. `scripts/diagnostics/roby_conversational_e2e_harness.py:177–215`: an existing diagnostic harness constructs a desktop app with an isolated local conversation and instantiates `DevelopmentConsoleObserver(runtime)`. At lines 217–249 it starts the app, submits prompts, and consults `observer.last_turn()` after a created runtime turn. This is **not a passive read of already-existing production results**: it runs new diagnostic conversations. Its comments distinguish the read-only observer from the prompt-submitting harness.
8. `core/governed_operational_conversation_pipeline/pipeline.py:63–66` offers `last_result` over the repository. In the targeted production-source search, no separate direct consumer of this pipeline property or direct `response_assembler.repository.get/list_all` consumer was identified. This negative finding is limited to the inspected Python sources and literal call patterns, not proof of global absence.

## 3. Access and authorization distinctions

| Surface | Evidence | Assessment |
|---|---|---|
| Repository `get` | Used by `DevelopmentConsoleObserver` | `CONFIRMED_STATICALLY` |
| Existing observer | `runtime_observation`, `last_turn`, `turn_observation` | `CONFIRMED_STATICALLY` |
| Turn/result ID correlation | Turn contains `pipeline_result_id`, used for lookup | `CONFIRMED_WITHIN_OBSERVED_LOCAL_ROUTE` |
| In-process availability | Requires live populated composition and retained history | `CONDITIONAL` |
| Owner/session context | Observer reads `bootstrap.config.owner` and `session_id` for runtime observation | `CONTEXT_VISIBLE_NOT_AUTHORIZATION_PROOF` |
| Authorization gate for research reads | No dedicated access grant established by inspected call chain | `NOT_DEMONSTRATED` |
| Read-only historical production access | No authorized persistent result retrieval proven | `NOT_DEMONSTRATED` |
| H2 assessment-to-final-response link | Not proven | `NOT_DEMONSTRATED` |
| C0/C1 comparison | Not enabled | `EXPERIMENT_NOT_ENABLED` |

The observer's read-only nature does not imply the diagnostic harness is read-only in its overall effects. Neither the observer constructor nor the repository `get()` call by itself proves caller authorization. Absence of an explicit gate at that location does not prove absence of security controls elsewhere.

## 4. Research implications

**Positive:** Existing canonical observability is stronger than the earlier generic repository hypothesis. It already connects local turn identity to a pipeline result without introducing a new observer, ledger, agent, or authority. Existing tests and diagnostic harness are historical implementation evidence, not experiments executed in this phase.

**Limit:** This is an in-process observational path for a specific local conversation runtime. The diagnostic harness actively submits new prompts; it cannot be reclassified as passive observation of existing production data. We cannot assume completeness for all desktop interceptions, all ROBY responses, all sessions, or durable history.

**Measurement:** The existing H2 evidence ledger may cite these fields only when actual instance access, consent/authorization, independent reference labels, and response linkage are separately established. Missing evidence stays missing; no scores, gains, or epistemic abstention conclusions may be inferred.

## 5. Determination

`READ_CALLER_EXISTENCE: CONFIRMED_STATICALLY`  
`CANONICAL_OBSERVER: DEVELOPMENT_CONSOLE_OBSERVER`  
`TURN_TO_PIPELINE_RESULT_LOOKUP: CONFIRMED_STATICALLY`  
`OBSERVER_READ_ONLY_PROJECTION: CONFIRMED_BY_IMPLEMENTATION`  
`DIAGNOSTIC_HARNESS_PASSIVE: FALSE`  
`AUTHORIZED_RESEARCH_ACCESS: NOT_DEMONSTRATED`  
`LIVE_RESULT_ACCESS: NOT_DEMONSTRATED`  
`DURABLE_HISTORY: NOT_DEMONSTRATED`  
`EPISTEMIC_TO_RESPONSE_LINK: NOT_DEMONSTRATED`  
`H2: PARTIALLY_FEASIBLE`  
`C0_C1: EXPERIMENT_NOT_ENABLED`  
`PRODUCTIVE_CHANGES: NONE`  
`TESTS_EXECUTED: NONE`  
`STOP_PRODUCTIVE: ACTIVE`

## 6. Next governed gate

After local integrity verification and explicit Owner approval, recommend `R-RIQ-S2-H2-OBSERVER-BOUNDARY-ASSESSMENT — Existing Observer Scope & Non-Invasive Research Eligibility (Static)`: inspect the observer's data minimization, call-site scope, lifecycle, session ownership and existing governance documentation, **without running the harness**. If authorized passive access remains unproven, close the sub-question as `INSUFFICIENT_EVIDENCE` rather than producing new instrumentation or reopening certified audits.

## 7. Evidence limitations

Static source inspection only of ZIP `(9)`; no assertion about the user's current local working tree after later documentary additions, live deployment, owner authorization, actual runtime contents, experimental outcomes, or full cross-channel coverage. All line references are within ZIP files, not external citations. This candidate requires Owner review and approval.
