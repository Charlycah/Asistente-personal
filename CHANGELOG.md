## R-CONV-EXP-02C ? Vos Opening Surgical GREEN Closure

**Classification:** bounded conversational opening refinement.
**Existing authorities:** `HouseholdConversationStyle` and
`CompanionExpressionPolicy`.
**New capability:** NONE.
**New architectural authority:** NONE.

**Observed defect:**
- Ordinary Spanish technical answers could begin with the artificial
  opening `Vos!`, despite the intended natural Argentine voseo.
- The defect was reproduced in a real endpoint/API explanation.

**Surgical correction:**
- Refined the existing Spanish conversational style instruction to
  prohibit `Vos!` as an opening or filler while preserving natural voseo.
- Extended the existing `CompanionExpressionPolicy` to remove the
  contractually tested artificial opening `Vos!` or `?Vos!`.
- Preserved ordinary voseo, quoted examples, inline code and fenced code.
- Introduced no translator, parallel expression policy, new manager,
  conversation pipeline or productive authority.

**Contract and local certification:**
- Presentation RED: 3 expected failures and 6 passing preservation cases.
- Presentation GREEN: 19 directed tests passed.
- Ruff: PASS for the selected product and test files.
- Global suite: NOT EXECUTED for this increment.

**Real functional validation:**
- Endpoint/API explanation: PASS; no artificial `Vos!` opening.
- Python function explanation: PASS; no artificial `Vos!` opening.
- Functional result: 2/2 observed cases PASS.
- Scope: the tested defect is resolved in the verified cases;
  universal absence of future conversational fillers is not claimed.

**Open boundaries:**
- EXP-02A historical final-language contracts remain OPEN.
- General conversational fluency and concision are not certified
  by this closure.
- No productive authorization, persistence or architectural
  boundary was changed.

**Governance:**
- `M377 HOLD: INTACT`.
- `STOP_PRODUCTIVE: ACTIVE`.
- EXP-02C: bounded local functional GREEN validated.

---

## R-CONV-EXP-02B ? Surgical GREEN

**Classification:** bounded conversational expression refinement.
**Authority:** existing `CompanionExpressionPolicy`.
**New capability:** NONE.
**New architectural authority:** NONE.

- Moderates the contractually tested redundant enthusiasm opening.
- Preserves a single natural exclamation.
- Preserves inline and fenced code through the existing protected-code boundary.
- Does not introduce translation, a new conversation layer, or a parallel
  personality/expression authority.
- Scope is limited to the tested opening pattern; general enthusiasm
  moderation is not claimed.

**Local certification:**
- Contract RED: 3 expected failures, 1 passing preservation test.
- Directed GREEN: 4 passed.
- Selected regression: 33 passed.
- Ruff: PASS for the verified product and test files.
- Global suite: NOT EXECUTED for this increment.

**Governance:**
- `M377 HOLD: INTACT`.
- `STOP_PRODUCTIVE: ACTIVE`.
- EXP-02A and EXP-02C remain outside this GREEN.

---

# M347.15 — Estabilización de la serie

## Self-Diagnostics / Self-Improvement → Governed Proposal productive reachability — PENDING

- Added a bounded adapter from an existing M399.5 `DiagnosticProposal` into the canonical governed proposal model/inbox.
- Preserves human review, diagnostic/proof identity, and co-owner presentation metadata.
- Adds no code mutation, approval, execution, background diagnosis, proposal authority, inbox, or notification broker.
- Certified input baseline: **12,358 PASS · 0 FAIL · Ruff clean**.


## Whole Personal System E2E Identity/Session evidence reachability reconciliation — PENDING

- Reconciled WPS-01 static evidence with the current productive Identity/Session chain:
  household bootstrap → runtime identity selection → local runtime bootstrap → local
  conversation → session-scoped governed request.
- Removed `PersonalIdentityRegistry.open_session()` from WPS-01 reachability evidence;
  the historical registry remains preserved and was not retired.
- No productive runtime, authority, persistence, store, Composition Root, or `.roby`
  behavior changed.
- Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**.

## Post-M409.1 — Longitudinal reasoning productive-projection retirement

Retired the non-productively-resident app-level longitudinal reasoning productive-consumption wrapper. The neutral observation contract and `GovernedLongitudinalReasoningAssessmentFoundationV1` remain under the existing `governed_reasoning` authority. Historical documentation is preserved.


### Post-M409.1 method-analysis productive-projection retirement
Retired three app-level projection-only surfaces with zero productive Python consumers: method outcome association, effectiveness awareness, and comparative awareness. Their governed reasoning Foundations remain current; all other productive-consumption families are preserved.


### Post-M409.1 reasoning event-history micro-lineage retirement
Retired the non-productively-resident application-level reasoning assessment event projector
and admitted event-history reader. Current succession is the neutral
`GovernedReasoningAssessmentObservation.from_assessments(...)` contract plus
`GovernedLongitudinalReasoningAssessmentFoundationV1` under the existing
`governed_reasoning` authority. Historical documents are preserved.



## Post-retirement current-state documentary reconciliation

- Promotes Residential/MINI-PC/distributed-residence retirement to **CLOSED / CERTIFIED** after owner validation at **12,534 PASS · 0 FAIL · Ruff clean**.
- Reconciles Current Truth, Master Capability Registry, README, Vision, external-capability snapshot and cognitive inventory baseline pointers without productive runtime changes.
- Marks retired Android/Mobile/Driving/Residential constitutional sections as historical/superseded for current-direction interpretation while preserving their original rule text and milestone history.
- Productive delta: **0**.


## Residential / MINI-PC / distributed-residence legacy executable lineage retirement — laptop-only direction

- De-wired optional `residential.remote_presence` from the single official Composition Root.
- Physically retired the governed Residence/Connectivity/PhysicalTransport/Synchronization/Residential Node/Perception/Remote Presence executable lineage and its dedicated MINI-PC process entrypoints.
- Preserved `ResidentComponentRegistry`, local Web Panel, `InformationClassification`, Device, Presence, Camera/Vision, ExternalResourceRegistry and Household authorities.
- Reconciled M405.1/M406.1 to retain neutral classification and Web Panel contracts while historical Residential documentation remains intact.
- Added absence/preservation guardrails; owner certification remains pending.

## Mobile + Driving legacy executable lineage retirement — laptop-only direction

- De-wired `driving.runtime` from the single official Composition Root after inspection proved it composition-reachable but not productively consumed by End-to-End conversation flow.
- Retired the executable M110→M121 Mobile/Hands-Free/Driving lineage, `app/driving_runtime.py`, and `core/mobile_extension/`.
- Removed 14 positive legacy test files (461 test functions / 541 collected Pytest cases) and added 4 absence/no-reintroduction guardrails.
- Reconciled only the affected M247, M264 and M387.5 contracts; preserved Device Runtime, neutral device capabilities/continuity, multimodal, reasoning, memory, historical milestones/ADRs/manifests and current authorities.
- Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION** from certified input baseline **13.746 PASS · 0 FAIL · Ruff clean**.


## Android legacy executable island retirement — laptop-only direction

- Physically retired the unreachable Android Bridge and Android observation surfaces plus the Android-backed Current Location implementation.
- Removed 13 positive historical Android/current-location test files (170 tests) and added 4 absence/no-reintroduction guardrails.
- Preserved neutral M364 `OfficialDeviceGateway` while removing only its Android imports/state/methods.
- Preserved `OfficialDeviceRuntimeGateway`, Composition Root, ToolGateway, device capability/continuity infrastructure, M394/M396/M364 contracts, and all historical M365/M370–M374/M399.1 documentation.
- Current project direction is laptop-only; Mobile and Residential/MINI-PC remain separate legacy retirement candidates, not part of this surgery.
- Status: **CLOSED / CERTIFIED** at **13.746 PASS · 0 FAIL · Ruff clean**, from certified input baseline **13.912 PASS · 0 FAIL · Ruff clean**.

# CAP-11 — Productive Continuation step N → Existing Planning re-entry RED

- Added a deliberate RED contract for N-step Productive Continuation into the existing Planning re-entry owner.
- Step 3/4 must reuse the same Planning authority; no P3/P4 planner, manager, gateway or loop is introduced.
- Historical step-2/budget-2 behavior remains an exact compatibility guard.
- The block stops at Planning; PLANNABLE may only expose declarative Authorization eligibility.
- Production remains unchanged until the RED is locally certified.
- Details: `ROBY_XI_2_CAP_11_PRODUCTIVE_CONTINUATION_STEP_N_TO_EXISTING_PLANNING_REENTRY_CONTRACT_RED.md`.

## CAP-11 — Productive Continuation step N → Existing Planning re-entry GREEN

- Generalized only the existing Productive Continuation and Planning re-entry eligibility guards from fixed step 2 to governed Episode N-step invariants.
- Preserved exact historical step-2/budget-2 behavior and the same Planning authority.
- Step 3/4 can now reach the existing Planning surface once with exact requirement/source/snapshot lineage and prior-plan reuse protection.
- PLANNABLE exposes only declarative Authorization eligibility; this block invokes no Authorization, Execution or Reasoning.
- Updated one stale historical contract assertion from the removed step-two guard token to the governed N-step alignment guard.
- Details: `ROBY_XI_2_CAP_11_PRODUCTIVE_CONTINUATION_STEP_N_TO_EXISTING_PLANNING_REENTRY_GREEN.md`.

## Long-horizon Investigation — Resume Admission → Existing Evidence Acquisition Planning

- Added a narrow governed bridge from certified Resume Admission to the existing evidence-acquisition planning surface.
- Planning authority remains `planning_foundation`; no alternate planner or step-two reentry is introduced.
- The exact admitted requirement object is forwarded once; lineage mismatches and planning failures fail closed as review-required.
- Authorization eligibility is derived only from an existing `PLANNABLE` planning result; this block does not authorize or execute.
- Details: `ROBY_XI_2_LONG_HORIZON_INVESTIGATION_RESUME_TO_EXISTING_PLANNING_GREEN.md`.


## Higher Cognitive Evolution — Final Closure & Zero-Residual Certification

- Official certification baseline: **13.439 PASS + Ruff limpio**.
- Eleven HCE waves promoted to **CLOSED / PROMOTED**.
- Zero productive reachability residual.
- Zero cognitive-authority residual.
- Zero unintended persistence/self-modification residual.
- No new cognitive capability or productive runtime behavior added.
- HCE is frozen at its contracted scope; future evolution must pass Cognitive Inventory anti-duplication review.
- Canonical certification: `HIGHER_COGNITIVE_EVOLUTION_FINAL_CLOSURE_ZERO_RESIDUAL_CERTIFICATION.md`.

## Higher Cognitive Evolution — Final Productive Epistemic/Metacognitive Orchestration Closure

- Added atomic explicit hypothesis source + world snapshot admission to the canonical conversation request.
- Ordinary turns remain outside the strong epistemic path unless that explicit pair is present.
- Governed Runtime Preparation now binds same-turn epistemic evidence before Cognitive Runtime reference collection.
- Exact Method Outcome + exact Strategy Application evidence now construct and admit Strategy Outcome through the existing Unified Cognitive Coordinator.
- Existing source-reference, world-lineage, idempotence and authority guards remain unchanged.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_FINAL_PRODUCTIVE_EPISTEMIC_STRATEGY_METACOGNITIVE_ORCHESTRATION_CLOSURE_WAVE.md`.


## Higher Cognitive Evolution — Canonical Hypothesis-Bearing Epistemic Binding

- Added one immutable same-turn productive epistemic assessment episode.
- Selective Scenario/Causal evidence now runs through existing Deepening → Sufficiency → Quality → Method Provenance → Method Outcome.
- Exact Scenario simulation / Causal analysis references propagate through the existing reasoning runtime contribution.
- Same-turn binding is idempotent and rejects source/world replacement.
- No Strategy Outcome lineage guard was weakened.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_CANONICAL_HYPOTHESIS_BEARING_EPISTEMIC_EPISODE_BINDING_METACOGNITIVE_CLOSURE_WAVE.md`.


## Higher Cognitive Evolution — Explicit Hypothesis Source + Selective Reachability

- Added a governed explicit hypothesis-source contract under `governed_reasoning`.
- Scenario/causal hypotheses are created only when all canonical semantic fields are already explicit.
- Missing semantics fail closed as NOT_APPLICABLE/REVIEW_REQUIRED; no free-text inference is used.
- Existing Scenario Simulator, Causal Predictive Reasoner and Persistent World Snapshot are reused.
- Generic decision options remain insufficient to create hypotheses.
- Official Governed Reasoning exposes the adapter without adding another authority.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_GOVERNED_EXPLICIT_HYPOTHESIS_SOURCE_SELECTIVE_REACHABILITY_WAVE.md`.


## Higher Cognitive Evolution — Canonical Productive Reasoning Episode Unification

- Ordinary productive Reasoning now uses one canonical `OfficialGovernedReasoningRuntimeGateway`
  episode per governed turn identity.
- Adaptive/End-to-End cognition and `ReasoningRuntimeContributor` reuse the same episode instead of
  independently evaluating Reasoning twice.
- Runtime reliability and Reasoning use the same canonical conversation-turn identity algorithm.
- `OperationalCognitiveSource.reasoning` is no longer the canonical runtime-root Reasoning source;
  Planning/Reflection/Executive operational sources remain unchanged.
- Canonical Reasoning abstention remains truthful and is not promoted to synthetic completion.
- No Memory, Learning, persistence, tool execution or new authority is introduced.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_CANONICAL_PRODUCTIVE_REASONING_EPISODE_UNIFICATION_WAVE.md`.


## Higher Cognitive Evolution — Governed Productive Strategy Adaptation Wiring

- The same `UnifiedCognitiveCoordinator` instance is now injected into ordinary runtime preparation.
- Ordinary multi-step cognitive turns can productively apply a planner-derived strategy through the
  existing `CognitiveRuntimeOrchestrator`.
- Exact `CognitiveStrategyApplicationEvidence` is preserved in conversation preparation.
- Certified strategy outcomes may be retained transiently by the same coordinator; no durable
  preference store, Memory write or Learning write is introduced.
- Outcome attribution remains fail-closed unless exact certified reasoning-outcome evidence exists.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_GOVERNED_PRODUCTIVE_STRATEGY_ADAPTATION_WIRING_WAVE.md`.


## Higher Cognitive Evolution — Strategy Structural Identity & Future Influence

- Added reusable `structural_fingerprint` while preserving exact strategy instance identity.
- Semantic paraphrases with the same strategy topology now share structural identity.
- Future influence occurs only among current planner-derived eligible structures.
- Metacognitive history cannot add/remove current cognitive needs or modify `CognitivePlanner`.
- Influenced strategies are always new instances; historical instance fingerprints are never reused.
- Influence remains read-only, non-persistent, non-learning and non-executing.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_GOVERNED_STRATEGY_STRUCTURAL_IDENTITY_FUTURE_INFLUENCE_WAVE.md`.


## Higher Cognitive Evolution — Strategy Outcome → Metacognitive Adaptation

- Added exact strategy-application → reasoning-outcome lineage.
- Strategy and reasoning-method fingerprints remain distinct.
- Repeated compatible outcomes can produce a bounded strategy recommendation.
- Review-required, insufficient or ambiguous history fails closed.
- Adaptation remains advisory-only: no planner mutation, persistence, Learning, Memory or execution.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_STRATEGY_OUTCOME_METACOGNITIVE_ADAPTATION_WAVE.md`.


## Higher Cognitive Evolution — Strategy Application Outcome Evidence

- `CognitiveStrategyCandidate` can now be projected read-only onto the existing cognitive runtime.
- Only reasoning/planning/reflection/executive are strategy-controlled; other contributors preserve
  their relative runtime order.
- Evidence/tool requirements and Decision remain outside the runtime contributor path.
- Exact strategy lineage is preserved in `CognitiveStrategyApplicationEvidence`.
- APPLIED/PARTIALLY_APPLIED/BLOCKED/NOT_APPLICABLE remain truthful to contributor outcomes.
- Application/evidence do not execute tools, persist, learn, write Memory or grant authority.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_GOVERNED_STRATEGY_APPLICATION_OUTCOME_EVIDENCE_WAVE.md`.


## Higher Cognitive Evolution — Governed Novel Strategy Synthesis

- Added a read-only `CognitiveStrategyCandidate` under existing Decision/composition authority.
- Existing `CognitivePlanner` remains the need/tool selector.
- Novel multi-step strategies are ordered from generic cognitive dependencies, not `_SCENARIOS`.
- Missing required capabilities fail closed with `BLOCKED`; nothing executes automatically.
- Strategy candidates do not persist, learn, modify Memory or grant authority.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_GOVERNED_NOVEL_STRATEGY_SYNTHESIS_WAVE.md`.


## Higher Cognitive Evolution — Abstraction → Approved Learning → Novel Reuse

- Closed the first causal intellectual-learning loop from induced relational abstraction to later
  novel-domain reuse.
- Reuses LearningFoundation, SafeLearningPolicies, explicit M369 human approval, structural
  eligibility, OfficialMemoryGateway, Memory recall and existing Structural Transfer.
- Contested or explicitly rejected abstractions cannot become durable knowledge.
- First closure remains bounded to the already-certified `required_for` /
  `blocked_when_unavailable` structural family.
- No new cognitive authority, Memory store or Learning writer was introduced.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_ABSTRACTION_APPROVED_LEARNING_LATER_NOVEL_REUSE.md`.


## Higher Cognitive Evolution — Governed Relational Abstraction Wave

- Added the first bounded concept-formation primitive under existing `governed_reasoning`.
- Multiple explicit examples may yield a read-only relational abstraction candidate.
- Counterexamples are first-class boundary evidence; unsupported/scope-mismatched evidence fails closed.
- The candidate cannot persist, learn, write Memory, establish truth or authorize inference.
- No new manager, repository, scheduler or cognitive authority was introduced.
- Details: `docs/HIGHER_COGNITIVE_EVOLUTION_GOVERNED_RELATIONAL_ABSTRACTION_WAVE.md`.


## Personal Cognitive Integration — Whole-Personal Causality Closure

- BLOQUE II causal audit: **CLOSE**.
- Tasks, Reminders, Calendar y explicitly-follow-up Notes reach the same Cognitive Agenda and
  causally affect resident effective focus/deliberation without taking authority from their owners.
- Goals/Projects remain integrated from Lote A.
- No PersonalCognitiveIntegrationManager, mirror persistence or scheduler is introduced.
- Causal focal validation: **76 PASS**.
- Details: `docs/PERSONAL_COGNITIVE_INTEGRATION_RESIDUAL_WHOLE_PERSONAL_CAUSALITY_AUDIT.md`.

## Personal Cognitive Integration — Unified Source Wave

- Tasks, Reminders, Calendar y Notes proyectan relevancia read-only al único `CognitiveAgendaManager`.
- Goals y Projects continúan integrados desde Lote A.
- No se crea nueva authority, manager, persistence, scheduler o lifecycle.
- Tasks: bloqueo / importancia / urgencia / deadline cercano.
- Reminders: pending dentro de 48 h o vencidos.
- Calendar: ventana READY de 48 h, proyección efímera que expira con el evento.
- Notes: sólo NOTE ACTIVE con tag explícito de seguimiento.
- Validación focal en runtime de auditoría: 172 PASS; gates completos locales pendientes.
- Detalle: `docs/PERSONAL_COGNITIVE_INTEGRATION_UNIFIED_SOURCE_WAVE.md`.

## Cognitive Coherence & Causal Closure — Post-WPS

- Cross-Capability certification synchronized with current causal evidence: **8 PASS · 2 PASS_BY_DESIGN · 0 PARTIAL · 0 FAIL**.
- CCI-04 Memory → Planning and CCI-10 Changed Conditions → bounded replanning are causally certified by existing architecture tests; no new production authority was required.
- WPS-06 semantics reconciled: M199 remains a bounded conversational commitment assessment and does **not** certify durable personal commitment continuity.
- `open_commitments` remains a compatibility consumer hook without a demonstrated durable canonical source; no new commitment manager/store is introduced.
- Details: `docs/COGNITIVE_COHERENCE_CAUSAL_CLOSURE.md`.


## Post-M409.1 — Governed Reasoning Method Effectiveness Awareness — ReasoningContextBundle Productive Consumption v1


## Whole-System Cross-Capability Cognitive Integration & Transfer Certification

Diagnostic/read-only certification added after the 12,556-test Whole-System E2E baseline. The 10-scenario certification reports 3 PASS, 2 PASS_BY_DESIGN, 5 PARTIAL and 0 FAIL. PARTIAL results are preserved as evidence and require a separate Audit → Contract / Go-No-Go before any production intervention. See `docs/WHOLE_SYSTEM_CROSS_CAPABILITY_COGNITIVE_INTEGRATION_TRANSFER_CERTIFICATION.md`.

- Añade un consumidor `app/` que proyecta Effectiveness Awareness ya certificada sobre `ReasoningContextBundle.derived_assessments`.
- Reutiliza el contrato estructural existente sin modificar `ReasoningContextBundle`, su Protocol ni la Foundation.
- Preserva `evaluates_observed_support=True` y `evaluates_effectiveness=False`, además del scope, lineage, counts, snapshots, rationale y fingerprint certificados.
- `REVIEW_REQUIRED_OBSERVED_RECORD` sigue siendo revisión requerida y no activa Reflection ni se convierte en ineffectiveness.
- Mantiene fuera causalidad, effectiveness global, comparación, scoring, superioridad, ranking, selección, recomendación, adaptación, Learning, Memory, persistencia y ejecución.
- La inserción es determinista e idempotente; una colisión de identidad con payload diferente falla cerrada.

## Post-M409.1 — Governed Comparative Reasoning Method Awareness — ReasoningContextBundle Productive Consumption v1

- Añade un consumidor `app/` que proyecta awareness comparativa ya certificada sobre `ReasoningContextBundle.derived_assessments`.
- Reutiliza el contrato estructural existente sin modificar `ReasoningContextBundle` ni `ReasoningContextDerivedAssessment`.
- Preserva `compares_methods=True` como diferencia/similitud descriptiva ya certificada por la Foundation.
- Mantiene explícitamente fuera de alcance causalidad, effectiveness, superioridad, ranking, selección, recomendación, adaptación, Learning, Memory, persistencia y ejecución.
- La inserción es determinista e idempotente; una colisión de identidad con payload diferente falla cerrada.

## Post-M409.1 — Governed Reasoning Assessment Event Projection v1

- Reutiliza M203 `CognitiveEventBus` sin modificar su core.
- Proyecta un par certificado Reasoning Quality + Epistemic Sufficiency como un único evento `SIGNAL_PUBLISHED` del dominio `REASONING`.
- Añade schema/topic versionados, admission fail-closed y lineage explícito.
- Fija `confidence=1.0` exclusivamente como fidelidad exacta de proyección, no como probabilidad o confianza epistemológica.
- Añade idempotencia semántica read-before-publish porque M203 incluye `created_at` en su `event_id`.
- No crea Memory, Learning, Reflection, Curiosity, persistencia durable, nueva autoridad ni cambios de runtime core.

## M399.1 — Governed Current Location Audit & Activation

- Añade `AndroidLocationObservation` como evidencia física de sólo lectura, separada de Android Sensors.
- Amplía `OfficialDeviceGateway` para aceptar ubicación sólo de móviles registrados con `android.location`.
- Incorpora `CurrentLocationAuthority` como única autoridad semántica de ubicación actual.
- Reutiliza `GeoPointSignal` para Maps sin convertir Maps, Nominatim ni M398 en proveedores GPS.
- Rechaza consentimiento ausente, permiso no concedido, observaciones stale/futuras y confianza ausente o insuficiente.
- No añade tracking, polling, persistencia, activación de GPS ni proveedor físico Android.

## M399.2 — Governed Self-Diagnostics Foundation

- Añade `GovernedSelfDiagnostics` como autoridad técnica única `self_diagnostics`.
- Normaliza observaciones explícitas sin absorber las autoridades fuente.
- Calcula tendencia reproducible y anomalía sólo contra umbrales declarados.
- Conserva evidencia por `observation_id` y prohíbe inferir causas desde anomalías.
- No introduce hipótesis, proposals, sandbox, patches, persistencia, polling ni automodificación.

## M399.3 — Governed Diagnostic Hypothesis & Confidence

- Extiende `GovernedSelfDiagnostics` sin crear una segunda autoridad diagnóstica.
- Evalúa únicamente hipótesis candidatas explícitas sobre anomalías observadas.
- Separa evidencia de soporte y contradicción y rechaza referencias fuera del reporte.
- Calcula confianza mediante `DiagnosticConfidencePolicy` visible y reproducible.
- Conserva `evidence_codes` y el principio `predicción ≠ certeza`.
- No añade proposals, sandbox, patches, reparación, background ni automodificación.

## M399.5 — Governed Isolated Diagnostic Proposal

- Añade preparación inmutable de propuestas sólo desde proof M399.4 reproducida.
- Exige intención de cambio, archivos afectados y tests de validación explícitos.
- Persiste únicamente `proposal.json` bajo `.roby/review/proposals/<proposal_id>/`.
- Toda propuesta nace como `draft` y no equivale a aprobación ni autorización.
- Rechaza sobrescrituras y conserva `proof_id`, `hypothesis_id` y digest de evidencia.
- No añade sandbox, patch, diff ejecutable, apply, rollback ni reparación automática.

## M399.6 — Governed Diagnostic Sandbox Validation

- Añade validación de contenidos candidatos sólo dentro de una copia aislada del proyecto.
- Restringe archivos candidatos a `affected_files` declarados por la propuesta M399.5.
- Ejecuta únicamente `python -m pytest -q` sobre los `validation_tests` declarados.
- Conserva return code, stdout, stderr y paths como evidencia de sandbox.
- No modifica la baseline activa y no añade apply, aprobación, rollback ni shell libre.
- Mantiene `predicción ≠ certeza` y exige decisión humana antes de cualquier cambio.

## M393.8 — Estabilización Integral de la Memoria Relacional Gobernada

- Cierra M393.1–M393.7 sin añadir métodos productivos ni una nueva autoridad.
- Añade contratos integrales de autoridad única, determinismo, inmutabilidad y sólo lectura.
- Certifica que las vistas diagnósticas no modifican `RelationshipMemoryManager.history`.
- Mantiene sin cambios persistencia, aprendizaje, automatización, permisos y ejecución.

## M393.7 — Auditoría Relacional Gobernada

- Añade una auditoría final de sólo lectura sobre `RelationshipTraceabilityView` M393.6.
- Resume hallazgos explícitos como `clear`, `review_required`, `conflicted` o `insufficient_evidence`.
- Los conflictos conservan prioridad diagnóstica sin resolver ni reescribir registros.
- No añade persistencia, aprendizaje, automatización, permisos ni ejecución.

## M393.6 — Trazabilidad Relacional Gobernada

- Añade una vista de linaje explícito por `record_id` bajo `relationship_memory`.
- Reúne evidencia M393.2, consolidación M393.3, consistencia M393.4 y evolución M393.5 ya existentes.
- Valida compatibilidad de snapshots cuando se incorpora evolución.
- No infiere causas, no reescribe, no persiste, no aprende, no automatiza ni ejecuta.

## M393.5 — Evolución Relacional Gobernada

- Añade comparación temporal explícita entre dos vistas M393.4 bajo `relationship_memory`.
- Clasifica `added`, `removed`, `unchanged` y `changed` por diferencias observables.
- No infiere causas, no usa reloj propio y no modifica registros, historial ni persistencia.
- No añade aprendizaje, automatización, permisos ni ejecución.

## M393.4 — Consistencia Relacional Gobernada

- Añade diagnóstico de consistencia sobre la consolidación M393.3 bajo `relationship_memory`.
- Detecta duplicación exacta por clase y contenido normalizado sin inferencia semántica.
- Contradicciones e incompatibilidades requieren relaciones explícitas y trazables entre `record_id`.
- No resuelve, fusiona, elimina, persiste, aprende, automatiza ni ejecuta.

## M393.3 — Consolidación Relacional Gobernada

- Añade diagnóstico de consolidación sobre evidencia M393.2 bajo `relationship_memory`.
- Clasifica respaldo consolidado, revisión, conflicto y ausencia sin reescritura.
- Los conflictos prevalecen sobre respaldo positivo y permanecen visibles.
- No añade persistencia, aprendizaje, automatización, permisos ni ejecución.

## M393.2 — Evidencia Relacional Gobernada

- Extiende `RelationshipEvidenceReference` con metadatos epistemológicos y de validación explícitos.
- Expone respaldo relacional determinista sin modificar `RelationshipMemoryRecord.confidence`.
- Conserva conflictos, evidencia no verificada y ausencia de respaldo como estados visibles.
- Mantiene compatibilidad conservadora con referencias M393.1 y no añade persistencia, inferencia automática ni ejecución.

## M393.1 — Fundamento de Memoria Relacional Enriquecida Gobernada

- Amplía `RelationshipMemoryManager` sin crear una autoridad paralela.
- Añade referencias explícitas y auditables de evidencia sobre registros relacionales existentes.
- Expone registros sin evidencia como pendientes de revisión.
- No modifica captura M52, persistencia, runtime, automatización ni ejecución.

## M392.8 — Estabilización Integral del Modelo del Mundo

- Audita M392.1–M392.7 bajo `internal_world_model`.
- Verifica versiones, fingerprints, autoridad y estados de revisión.
- No añade autoridad, persistencia, inferencia, automatización ni runtime nuevo.

## M392.7 — Integración del Mundo Gobernada

- Integra las seis representaciones M392.1–M392.6 bajo `internal_world_model`.
- Conserva sub-representaciones, procedencia y estados de revisión sin reescritura.
- No añade autoridad, persistencia, inferencia, automatización ni runtime nuevo.


## M392.6 — Contexto Gobernado

- Añade representación explícita de contexto bajo `internal_world_model`.
- Reutiliza blackboard y contexto ambiental gobernado sin persistencia o autoridad nuevas.
- No infiere estados personales, presencia, actividad o ubicación y no activa automatizaciones.

## M392.5 — Línea Temporal Gobernada

- Nueva representación gobernada de eventos, intervalos y relaciones temporales.
- Sin agenda, calendario, planificación, recordatorios, persistencia ni automatización.

## M392.3 — Lugares Gobernados

- Añade representación explícita de lugares bajo `internal_world_model`.
- Reutiliza resoluciones y perfiles de conocimiento ya gobernados.
- No añade GPS en vivo, seguimiento, persistencia, gestores paralelos ni cambios de runtime.
## M392.2 — Personas Gobernadas

- Añade representación explícita de personas bajo `internal_world_model`.
- Reutiliza perfiles de identidad y `relationship_memory` como fuentes gobernadas.
- No infiere identidad ni propiedad relacional y no crea persistencia o gestores paralelos.

## M392.1 — Representación del Hogar Gobernada

- Añade representación espacial doméstica explícita bajo `internal_world_model`.
- Reutiliza `HouseholdMemory` como única fuente persistente de evidencia doméstica.
- Modela hogar, habitaciones, zonas y relaciones sin inferir texto libre.
- No añade almacenamiento, gestores paralelos, automatización, control de dispositivos ni cambios de runtime.

## M391.8 — Estabilización y Evidencia Integral

- Cierra la primera serie de Época IV sin añadir comportamiento cognitivo operativo.
- Añade `M391IntegralEvidenceDiagnostic` como diagnóstico puro de presencia, autoridad y linaje M391.1–M391.7.
- Corrige referencias documentales de raíz para declarar M391.8 como base canónica actual.
- Mantiene sin cambios las autoridades, runtime, persistencia y ejecución existentes.

## M391.7 — Predicción Gobernada

- Añade `GovernedPredictionEvaluator` subordinado a `governed_reasoning`, sin autoridad propia.
- Consume exclusivamente predicciones explícitas M391.4 y conserva `EpistemicLevel.INFERENCE`.
- Declara horizonte y condiciones sin probabilidades inventadas ni verificación temporal automática.
- No persiste, aprende, planifica, decide ni ejecuta.


## M391.6 — Toma de Decisiones Gobernada

- Añade `GovernedDecisionAdvisor` bajo `CanonicalDecisionFacade` / `unified_cognitive_coordination`, sin autoridad propia.
- Integra evidencia explícita M391.3–M391.5 y reutiliza la prioridad ya calculada por M391.5.
- Mantiene bloqueos, contradicciones y revisión humana sin promover hipótesis o predicciones a hechos.
- No crea planes, tareas, permisos, persistencia, ejecución ni procesos residentes.

## M391.5 — Organización Personal Inteligente Gobernada

- Añade `IntelligentPersonalOrganizationView` bajo `PersonalOrganizationAuthority`, sin autoridad propia.
- Reutiliza `PriorityReasoning` para emitir recomendaciones explicables sobre ítems personales explícitos.
- Mantiene agenda, tareas, recordatorios, objetivos, proyectos y notas bajo sus autoridades existentes.
- No crea, modifica, elimina, agenda, recuerda, persiste ni ejecuta y no inicia procesos residentes.

## M391.4 — Comprensión Causal y Predictiva Gobernada

- Añade `GovernedCausalPredictiveReasoner` bajo `governed_reasoning`, sin `authority_id` propio.
- Distingue coexistencia de causalidad: una relación causal explícita permanece hipótesis.
- Emite predicciones condicionales como inferencias, nunca como hechos futuros.
- No calibra probabilidades, no persiste, no aprende causalidad, no planifica ni ejecuta.

## M391.3 — Simulación de Hipótesis y Escenarios Gobernada

- Añade `GovernedScenarioSimulator` como evaluador puro bajo `governed_reasoning`, sin `authority_id` propio.
- Evalúa hipótesis explícitas contra snapshots M391.2 como consistentes, contradichas o no resueltas.
- Conserva `EpistemicLevel.HYPOTHESIS` y prohíbe convertir simulaciones en hechos.
- No persiste hipótesis, no modifica el mundo, no planifica, no ejecuta y no inicia procesos residentes.

## M391.2 — Modelo Persistente del Mundo Gobernado

- Mantiene `internal_world_model` como única autoridad descriptiva del mundo interno.
- Incorpora una vista inmutable sobre hechos ya persistidos por autoridades existentes, incluida `HouseholdMemory`.
- No crea repositorio, almacenamiento ni gestor paralelo.
- Expone contradicciones sin resolverlas e impide promover inferencias o hipótesis a hechos.

## M391.1 — Consolidación Cognitiva Gobernada

- Amplía `PeriodicReflectionAuthority` sin crear una autoridad paralela.
- Incorpora `CognitiveInactivityContext` y `CognitiveConsolidationReport` como contratos inmutables y de solo lectura.
- Consume únicamente evidencia certificada M389/M390 y candidatos ya estructurados por M366.6/M369.1.
- Expone estabilidad, revisión, candidatos disponibles, conflicto, evidencia insuficiente o degradación sin promover verdad ni persistir.
- Mantiene runtime, memoria, aprendizaje, planificación, permisos, objetivos, tareas, recordatorios y ejecución fuera de alcance.

## M390.8 — Estabilización y Evidencia Integral

- Cierra la serie M390 con evidencia integral y pruebas de invariantes, sin añadir conducta nueva.
- Incorpora `M390IntegralEvidenceDiagnostic` como diagnóstico subordinado, inmutable y sin `authority_id`.
- Verifica linaje explícito entre snapshot, continuidad, regulación, reflexión y modulación expresiva.
- Ausencias y conflictos permanecen visibles; no se reparan, persisten ni convierten en nuevas decisiones.
- Mantiene runtime, memoria, aprendizaje, planificación, personalidad, permisos y ejecución fuera de alcance.

## M390.7 — Reflexión sobre Estado Interior

- Extiende `ConversationReflectionAuthority` M389.2 para observar evidencia M390 explícita sin crear otra autoridad de reflexión.
- Registra referencias a snapshot, continuidad y regulación sin reinterpretar emociones ni modificar el estado interior.
- Mantiene compatibilidad hacia atrás: sin entradas M390, la reflexión conserva su comportamiento anterior.
- No añade runtime, persistencia, aprendizaje, planificación, permisos ni ejecución.


## M390.6 — Regulación Funcional Simulada

- Incorpora regulación proporcional y determinista sin nueva autoridad emocional.
- Reutiliza snapshots M390.1 y continuidad explícita M390.3; no mantiene historial ni reloj.
- Puede limitar M390.5 únicamente hacia `careful` ante cambio amplio, inestabilidad o riesgo.
- Una única fuente relacional no puede escalar por sí sola la expresión afectiva.
- No modifica runtime, memoria, aprendizaje, planificación, identidad, objetivos ni ejecución.

## M390.5 — Modulación Expresiva Gobernada

- Incorpora `GovernedExpressiveModulation` como adaptador subordinado entre el mundo interior simulado y M377.
- Amplía `AdaptivePersonalityRequest` con una señal afectiva limitada y trazable, sin crear otra autoridad de personalidad.
- Sólo permite modular el tono hacia `neutral`, `warm` o `careful`; `direct` y `repairing` no pueden ser impuestos por M390.
- Conserva preferencias explícitas de detalle y estructura, identidad estable y compatibilidad con M378.
- No modifica texto, runtime, persistencia, memoria, aprendizaje, planificación ni ejecución.

## M390.4 — Integración Relacional Segura

- Integra evidencia relacional canónica con M390 sin crear una autoridad paralela.
- No infiere identidad, presencia o vínculo y no modifica runtime, memoria ni personalidad.


## M390.3 — Continuidad Interior Explícita

- Incorpora `ExplicitInnerContinuityEvaluator` para comparar snapshots internos simulados recibidos explícitamente.
- Informa campos afectivos modificados o estables sin inferir historia faltante.
- Mantiene continuidad determinista, transitoria y sin persistencia, reloj, memoria, aprendizaje, personalidad o ejecución.
- `SimulatedInnerStateAuthority` conserva la única autoridad del mundo interior simulado.


## M390.2 — Evaluación Afectiva Gobernada

- Incorpora `GovernedAffectiveEvaluator` como adaptador puro y subordinado, no como autoridad paralela.
- Traduce únicamente reportes certificados de M389.4, M389.5 y M389.8 a `SimulatedInnerStateSignal`.
- Conserva `SimulatedInnerStateAuthority` como única autoridad capaz de construir el snapshot interior simulado.
- Degrada a desconocimiento ante evidencia insuficiente, fuentes degradadas o fallo de evaluación; no inventa emociones.
- Mantiene evaluación determinista, codificada, sin contenido conversacional bruto y sin integración automática al runtime.
- No modifica memoria, aprendizaje, planificación, personalidad, permisos, objetivos, tareas ni ejecución.

## M390.1 — Fundamento del Mundo Interior Simulado

- Incorpora `SimulatedInnerStateSignal`, `SimulatedInnerStateSnapshot` y `SimulatedInnerStateAuthority`.
- Formaliza una única autoridad de estado afectivo funcional simulado dentro de `core.cognitive_maturity`.
- Conserva procedencia y categoría epistemológica M389.8 sin reanalizar las fuentes.
- Representa desacuerdos como mezcla, variabilidad, conflicto o desconocimiento, con trazabilidad explícita.
- Declara obligatoriamente la naturaleza simulada y prohíbe afirmar consciencia, experiencia subjetiva o emoción real.
- No incorpora persistencia, memoria, aprendizaje, planificación, personalidad, permisos, objetivos, acciones ni cambios de runtime.

## M380 — Organized Work Model

- Incorpora `OrganizedWorkReference`, `OrganizedWorkSnapshot` y `OrganizedWorkAuthority`.
- Consolida objetivos, proyectos y tareas mediante referencias canónicas y relaciones explícitas.
- Mantiene `PersonalOrganizationAuthority` como autoridad canónica de la Fase IV.
- Reutiliza los modelos existentes sin escribirlos, reemplazarlos ni crear otro planificador.
- No incorpora CRUD, ejecución, persistencia, memoria, LLM, agentes ni cambios de runtime.


## M379 — Personal Organization Foundation

- Incorpora `PersonalOrganizationCapability`, `PersonalOrganizationBinding`, `PersonalOrganizationSnapshot` y `PersonalOrganizationAuthority`.
- Inventaría agenda, tareas, recordatorios, objetivos, proyectos, notas y priorización detrás de una única fachada.
- Reutiliza autoridades existentes y marca brechas sin reemplazarlas.
- No incorpora CRUD, persistencia, ejecución, LLM, agentes ni cambios de runtime.
- Inicia la Fase IV — Organización Personal.

## M378 — Explicaciones Inteligentes

- Incorpora `IntelligentExplanationRequest`, `IntelligentExplanation` e `IntelligentExplanationAuthority`.
- Compone explicaciones públicas desde decisiones, razones, evidencia, límites e incertidumbre explícitos.
- Ajusta proporcionalmente detalle y estructura mediante el perfil adaptativo M377.
- Prohíbe razonamiento privado expuesto, justificaciones inventadas y cerebros paralelos.
- No incorpora LLM, ejecución, persistencia, memoria ni cambios de runtime.
- Cierra la Fase III — Inteligencia Conversacional.

## M377 — Personalidad Adaptativa

- Incorpora `AdaptivePersonalityRequest`, `AdaptivePersonalityProfile` y `AdaptivePersonalityAuthority`.
- Reutiliza la personalidad estable existente en lugar de crear otra identidad o motor cognitivo.
- Modula de forma determinista tono, detalle y estructura preservando rasgos e identidad.
- Prohíbe cerebros, agentes, identidades, memorias y políticas paralelas.
- No incorpora aprendizaje opaco, persistencia de preferencias, LLM ni cambios de runtime.

## M376 — Conversaciones de Largo Plazo

- Incorpora `LongTermConversationRecord` como archivo resumido e inmutable.
- Formaliza `LongTermConversationAuthority` como única autoridad de archivo y recuperación.
- Añade un repositorio neutral y una implementación en memoria para validar el contrato.
- Prohíbe transcript bruto, resumen automático, búsqueda semántica y escritura en memoria cognitiva.
- No modifica el runtime ni agrega persistencia de producción.

## M375 — Conversación Contextual

- Incorpora `ConversationTurn`, `ConversationReferenceResolution` y `ConversationContextUpdate`.
- Formaliza `ConversationContextAuthority` como única autoridad de actualización del contexto inmediato.
- Mantiene estados aislados por conversación y conserva tema, entidades, intenciones y acción previa.
- Resuelve referencias básicas contra la entidad activa más reciente y deja referencias no resueltas explícitamente pendientes.
- No incorpora persistencia, historial completo, LLM, memoria de largo plazo, personalidad ni cambios de runtime.
- Inicia la Fase III — Inteligencia Conversacional.


## M374 — Android Sensors

- Incorpora `AndroidSensorKind`, `AndroidSensorAccuracy`, `AndroidSensorReading` y `AndroidSensorSnapshot`.
- Amplía `OfficialDeviceGateway` como única autoridad para observaciones Android Sensors.
- Exige un dispositivo móvil registrado con la capacidad declarada `android.sensors`.
- Valida pertenencia al dispositivo, tipos de sensor únicos y valores finitos.
- Mantiene todas las observaciones sensibles, inmutables, de solo lectura y no ejecutables.
- No incorpora listeners, polling, ubicación, hardware real, persistencia, background ni integración cognitiva automática.
- Cierra la Fase II — Capacidades Android.


## M373 — Android Files

- Incorpora `AndroidFileEntry`, `AndroidFileEntryKind` y `AndroidFileSnapshot`.
- Amplía `OfficialDeviceGateway` como única autoridad para observaciones Android Files.
- Exige dispositivo móvil registrado y capacidad declarada `android.files`.
- Valida rutas absolutas, pertenencia al dispositivo y unicidad dentro del snapshot.
- Mantiene sensibilidad por defecto, solo lectura y ejecución deshabilitada.
- No abre, lee contenido, copia, mueve, renombra, borra, escribe, indexa ni sincroniza archivos.
- No incorpora acceso Android real, persistencia, polling, background ni integración cognitiva automática.

## M372 — Android Clipboard

- Incorpora `AndroidClipboardItem` y `AndroidClipboardSnapshot` como modelos inmutables.
- Reutiliza `OfficialDeviceGateway` como única autoridad de dispositivos.
- Exige registro móvil previo y declaración explícita de `android.clipboard`.
- Mantiene el contenido como sensible, de solo lectura y no ejecutable.
- No añade lector real, ADB, polling, escritura, limpieza, sincronización, persistencia ni automatización.
- Añade cobertura negativa, documental y de autoridad para la nueva capacidad.



## M371 — Android Notifications

- Incorpora `AndroidNotification` y `AndroidNotificationSnapshot` como modelos inmutables.
- Conserva `OfficialDeviceGateway` como única autoridad de dispositivos.
- Exige dispositivo móvil registrado y capacidad `android.notifications`.
- Mantiene toda observación en `read_only=True` y `executable=False`.
- No añade listener real, polling, ADB, transporte, respuesta, apertura o descarte.
- Reserva la integración cognitiva para incrementos posteriores y gobernados.


## M370.1 — Android Device State Foundation

- Inicia la Fase II de capacidades Android sobre la base validada M369.7.
- Incorpora un agregado inmutable para batería, conectividad, pantalla, almacenamiento y memoria.
- Conserva `OfficialDeviceGateway` como única autoridad de dispositivos.
- Exige dispositivo registrado y capacidad declarada `android.device_state`.
- Mantiene toda observación en `read_only=True` y `executable=False`.
- No añade transporte real, ADB, automatización, acciones Android ni cambios de runtime.


## M369.7 — Learning Stabilization

- Certifica la cadena gobernada M369.1–M369.6.
- Refuerza invariantes de trazabilidad, consentimiento y revisión obligatoria.
- Incorpora el informe final de la serie y declara M369 cerrada.
- No agrega aprendizaje automático, persistencia ni cambios de runtime.


## M369.6 — Safe Learning Policies

- Incorpora `safe_learning_policies` subordinada a `adaptive_reasoning`.
- Evalúa evidencia, confianza, vigencia, contradicciones y consentimiento.
- Clasifica candidatos como insuficientes, revisables, rechazados o caducados.
- No acepta, persiste, adapta ni modifica el runtime automáticamente.


## M369.5 — Adaptive Reasoning

- Incorpora `adaptive_reasoning` subordinada a `pattern_recognition`.
- Usa únicamente patrones revisables y opciones explícitas para generar sugerencias consultivas.
- Conserva la opción por defecto cuando no existe aprendizaje aplicable.
- No aplica adaptaciones, modifica objetivos o políticas, persiste ni cambia el runtime.


## M369.4 — Pattern Recognition

- Incorpora `pattern_recognition` subordinada a `habit_detection`.
- Exige evidencia explícita, consistente y procedente de hábitos distintos.
- Mantiene una sola evidencia como `insufficient_evidence` y la evidencia suficiente como `review_required`.
- No acepta ni persiste patrones, adapta razonamiento ni cambia el runtime.


## M369.3 — Habit Detection

- Incorpora `habit_detection` subordinada a `preference_learning`.
- Exige repetición explícita, días distintos y extensión temporal mínima.
- Mantiene historia insuficiente como `insufficient_history` y la historia suficiente como `review_required`.
- No acepta ni persiste hábitos, reconoce patrones, adapta razonamiento ni cambia el runtime.

## M369.2 — Preference Learning

- Incorpora `preference_learning` subordinada a `learning_foundation`.
- Exige evidencia explícita, única y consistente para un mismo sujeto y valor.
- Mantiene una observación aislada como `insufficient_evidence` y toda evidencia acumulada como `review_required`.
- No acepta ni persiste preferencias, detecta hábitos, reconoce patrones, adapta razonamiento ni cambia el runtime.

## M369.1 — Learning Foundation

- Incorpora `learning_foundation` como frontera canónica subordinada a `cognitive_memory`.
- Reconcilia observaciones, experiencias, registros, evidencia y política existentes.
- Estructura candidatos deterministas y trazables que siempre requieren revisión.
- No acepta conocimiento, aprende preferencias, detecta hábitos, persiste ni cambia el runtime.

## M368.7 — Planning Stabilization

- Audita y certifica las seis autoridades gobernadas de planificación.
- Protege contratos de trazabilidad e invariantes de integración extremo a extremo.
- Incorpora el informe final de la serie M368 y declara su cierre formal.
- No añade ejecución, persistencia, replanificación ni cambios de runtime.


## M368.6 — Plan Reasoning

- Incorpora `plan_reasoning` subordinada a `progress_evaluation`.
- Recomienda el primer paso accionable preservando el orden explícito del grafo.
- Expone tareas accionables, bloqueadas y bloqueadores directos con trazabilidad.
- No infiere prioridad, reordena, replantea, ejecuta, persiste ni cambia el runtime.

## M368.5 — Progress Evaluation

- Incorpora `progress_evaluation` subordinada a `dependency_tracking`.
- Evalúa avance global desde completitud explícita y estados gobernados.
- Expone conteos, fracción y porcentaje estructurales reproducibles.
- No pondera, predice, ejecuta, replantea, persiste ni cambia el runtime.

## M368.4 — Dependency Tracking

- Adds `dependency_tracking` as the single authority subordinate to `task_graph`.
- Evaluates available, blocked and completed tasks from explicit graph edges and explicit completion input.
- Reports direct incomplete predecessors without inferring new dependencies or progress.
- Adds no replanning, persistence, execution or runtime behavior.

## M368.3 — Task Graph

- Adds `task_graph` as the single authority subordinate to `goal_decomposition`.
- Builds immutable nodes from admitted components and accepts only explicit precedence edges.
- Rejects unknown endpoints, duplicates, self-references and cycles.
- Adds no dependency tracking, progress evaluation, replanning, persistence, execution or runtime behavior.

## M368.2 — Goal Decomposition

- Adds `goal_decomposition` as the single authority subordinate to `planning_foundation`.
- Structures only explicit, ordered and unique goal components with stable traceability.
- Requests clarification instead of silently inferring missing decomposition.
- Adds no task graph, dependencies, progress evaluation, replanning, persistence, execution or runtime behavior.

## M368.1 — Planning Foundation

- Establishes `planning_foundation` as the canonical read-only planning boundary.
- Reuses governed M367 goal, project, context and priority authorities.
- Adds no execution, persistence, automatic goal creation, decomposition, replanning or runtime behavior.

## M367.7 — Mental Model Stabilization

- Adds a deterministic read-only audit over all governed M367 models.
- Verifies authority uniqueness, parentage, side-effect boundaries and acyclic dependencies.
- Adds no intelligence, persistence, action authorization or runtime behavior.

## M367.6 — Priority Reasoning

- Adds deterministic, explainable ranking over admitted world-model candidates.
- Reuses existing cognitive-priority and context-state authorities.
- Adds no action authorization, persistence, automatic mutation or runtime behavior.

## M367.5 — Context State Model

- Reconciles existing current-context surfaces under `context_state_model`.
- Preserves context, memory, priority and action as separate responsibilities.
- Adds no persistence, automatic state change, priority reasoning or runtime behavior.

## M367.4 — Goals & Objectives Model

- Reconciles cognitive, household and executive goals with priorities, blockers and review.
- Establishes `goals_objectives_model` beneath `internal_world_model`.
- Adds no automatic goal creation, priority mutation, execution or runtime behavior.

## M367.3 — Project Knowledge Model

- Reconciles projects, tasks, milestones, dependencies, documentation and progress review.
- Establishes `project_knowledge_model` beneath `internal_world_model`.
- Adds no hidden project updates, inference, persistence or runtime behavior.


## M367.2 — User Profile Model

- Reconciles existing identity, preferences, personal knowledge, relationships and session binding.
- Establishes `user_profile_model` beneath `internal_world_model`.
- Adds no identity inference, hidden profile updates, persistence or runtime behavior.
- Preserves sensitive-data boundaries and explicit admission.

## M367.1 — Internal World Model Foundation

- Reconciles existing mental-model, context, memory, goals and capability authorities.
- Establishes `internal_world_model` as the single descriptive authority.
- Adds no inference, persistence or runtime behavior.

## M366.8 — Autobiographical Continuity

- Adds read-only chronological composition over admitted personal memories.
- Reuses identity, relationship and contextual retrieval authorities.
- Forbids fabrication, persistence, automatic narrative injection and consciousness claims.

## M366.7 — Contextual Memory Retrieval

- Adds governed, read-only contextual selection across existing memory kinds.
- Reuses `CognitiveMemoryRecall` as the specialized historical retrieval mechanism.
- Excludes archived and superseded memories and routes conflicts to review.
- Adds no persistence, prompt injection, automatic learning or runtime behavior.

## M366.6 — Memory Consolidation

- Adds a pure governed assessment layer between episodic and durable memory.
- Produces traceable proposals without writing, executing or promoting truth automatically.
- Requires review for conflicts and confirmation for personal or sensitive memory.
- Reuses `OfficialMemoryGateway` as the only operational writer authority.
- Adds no persistence, automatic learning or runtime behavior.

## M366.5 — Long-Term Memory

- Reconciles durable personal memory, revisable knowledge and household lifecycle under `memory_gateway`.
- Requires governed consolidation and reviewable forgetting.
- Supports functional autobiographical continuity without claiming consciousness.
- Adds no persistence, automatic learning or runtime behavior.

## M366.4 — Procedural Memory

- Reconciles governed plans, routines and task procedures under `memory_gateway`.
- Declares that remembered procedures never authorize execution.
- Adds no persistence, automatic learning or runtime behavior.

## M366.3 — Semantic Memory

- Reconciles existing governed facts, personal knowledge and household knowledge.
- Adds no persistence, automatic learning or runtime behavior.
- Declares external retrieval as distinct from semantic memory.


## M365.7 — Android Bridge Capability Selection & Stabilization

- Selecciona un subconjunto pequeño de capacidades candidatas.
- Mantiene catálogo, permisos, handlers y ejecución sin cambios.
- Bloquea identificadores no declarados y exige readiness descriptiva.
- Cierra la serie M365 con todos los resultados en `executable=False`.

## M365.6 — Android Bridge Capability Catalog Foundation

- Declara un catálogo inmutable de capacidades Android.
- Registra `android.capabilities.catalog` como metadata pasiva.
- Mantiene todas las capacidades con `enabled=False` y `executable=False`.
- No incorpora handlers, transporte activo ni acciones sobre el dispositivo.


## M365.5 — Android Bridge Gateway Registration

- Registra `android.bridge.readiness` detrás de `ToolGatewayManager`.
- La capacidad queda deshabilitada, sin handler y con `executable=false`.
- Distingue registro, disponibilidad y autorización de ejecución.
- No abre transporte ni incorpora acciones Android reales.

## M365.4 — Android Bridge Readiness, Authentication & Recovery

- Añade evaluación de readiness sobre activación y transporte gobernados.
- Modela autenticación declarativa sin almacenar pruebas ni secretos.
- Produce planes de recuperación acotados sin timers, retry loops o I/O.
- Mantiene todos los resultados con `executable=False`.
- No añade criptografía, conexión real, planner ni ejecución Android.

## M365.3 — Android Bridge Transport Abstraction

- Añade un protocolo de transporte reemplazable y simulable.
- Incorpora descriptores estáticos y un transporte nulo seguro.
- Evalúa disponibilidad y compatibilidad sin abrir conexiones.
- Mantiene todos los resultados con `executable=False`.
- No añade I/O, red, descubrimiento, planner ni ejecución.

## M365.2 — Android Bridge Configuration & Controlled Activation

- Añade configuración gobernada desde el árbol canónico ya cargado.
- Define estados DISABLED, CONFIGURED, READY y BLOCKED.
- Valida dispositivo conocido, agente permitido y protocolo compatible.
- Mantiene todos los resultados con `executable=False`.
- No abre transportes ni conecta planner o Tool Gateway.

## M365.1 — Android Bridge Contract Foundation

- Añade un contrato neutral para un futuro agente Android autorizado.
- Reutiliza `OfficialDeviceGateway` como único registro de dispositivos.
- Modela identidad, protocolo, capacidades y permisos declarativos.
- Bloquea dispositivos desconocidos y degrada protocolos incompatibles.
- Mantiene transporte, planner y ejecución deshabilitados.
- Reserva toda ejecución futura para `ToolGatewayManager`.

## M364 — Device Capability Foundation

- Establece `OfficialDeviceGateway` como frontera común para dispositivos.
- Reutiliza identidad y registro de capacidades existentes.
- Añade perfiles, transportes, estados, diagnósticos y planes de acción.
- Mantiene capacidades independientes de Bluetooth, USB, Wi-Fi o API local.
- No ejecuta hardware; toda ejecución futura deberá pasar por Tool Gateway.

## M363 — Windows Workspace Foundation

- Establece `OfficialWindowsWorkspaceGateway` como frontera oficial del workspace.
- Añade modelos de ventanas, procesos, capturas, capacidades, riesgos y planes.
- Separa observación, preparación y futura ejecución mediante Tool Gateway.
- Integra capturas con M362 sin almacenamiento silencioso.
- No ejecuta mutaciones de plataforma ni agrega automatización de entrada.

## M362 — Governed Vision Gateway

- Establece `GovernedVisionGateway` como frontera oficial de aplicación.
- Conserva `OfficialVisionCore` como motor visual interno ya validado.
- Añade un repositorio local gobernado para imágenes guardadas voluntariamente.
- Exige solicitud y consentimiento explícitos y prohíbe biometría implícita.
- No agrega reconocimiento facial, vigilancia ni proveedores externos.

## M361 — Quality Baseline

- Incorpora una línea base estática reproducible mediante AST y biblioteca estándar.
- Registra métricas de módulos, líneas no vacías, funciones, clases, imports y excepciones.
- Define criticidad, deuda técnica inicial y quality gates para la Fase II.
- Conserva como predecesora validada M360.0.e con 8677 pruebas aprobadas.
- No modifica comportamiento productivo.

## M360.0.e — Plan Maestro de la Fase II

- Convierte las auditorías M360.0.a-d en prioridades y dependencias definitivas.
- Ordena consolidación, Vision, Windows, dispositivos, Home Assistant, MCP y planificación gobernada.
- Define puertas obligatorias de calidad, permisos, trazabilidad, rollback y certificación.
- No modifica comportamiento productivo.

## M360.0.d — Auditoría documental

- Valida las reglas y documentos canónicos de la raíz.
- Corrige la divergencia entre referencias históricas M347/M348 y la base vigente M360.0.
- Define autoridad temática y política de vigencia documental.
- Clasifica `ROOT_DOCUMENTATION_INSTALLATION.md` como registro histórico.

## M360.0.c — Auditoría de calidad

- Registra fortalezas, riesgos y prioridades de calidad sin modificar comportamiento productivo.
- Identifica complejidad concentrada, excepciones amplias y divergencia documental como focos auditables.
- Define puertas de calidad para futuras integraciones físicas y externas.
- Conserva como base canónica Ruff limpio y 8665 pruebas aprobadas.


## M360.0.b — Auditoría arquitectónica

- Identifica autoridades canónicas, composition roots, registros y rutas de ejecución.
- Clasifica límites entre runtime, capacidades, dispositivos y Tool Gateway.
- Define decisiones arquitectónicas para Vision, Windows, Bluetooth, Android, Watch, MCP y Home Assistant.
- No modifica comportamiento productivo.


## M360.0.a — Inventario funcional verificable

- Audita la base oficial M359 sin modificar comportamiento productivo.
- Clasifica capacidades como operativas, internas, parciales, fundacionales o pendientes.
- Confirma que Vision Core, Calendar, Gmail, voz, memoria, planificación e inteligencia documental ya poseen avances sustanciales.
- Identifica como brechas reales Bluetooth, Samsung Watch 7, MCP, Home Assistant, cámara IP e impresión/escaneo gobernados.
- Registra 8665 pruebas coleccionadas y remite el detalle a `docs/M360_0A_FUNCTIONAL_INVENTORY.md`.

## M359 — Governed Document Actions

- Añade acciones documentales preparadas y ejecutadas mediante ToolGatewayManager.
- Exige consentimiento explícito y una confirmación independiente antes de ejecutar.
- Incorpora recordatorios, guardado de resúmenes y apertura de fuentes explícitas.
- No paga, no modifica documentos y no ejecuta acciones silenciosas.


## M358 — Document Intelligence gobernado

- Añade comprensión documental explicable sobre clasificación y extracción.
- Resume completitud, consistencia, campos faltantes y observaciones trazables.
- Reutiliza una sola captura y no conserva imagen ni datos sensibles en snapshots.
- No consulta la web, no paga, no modifica documentos ni decide automáticamente.


## M357 — Web Enrichment gobernado

- Añade enriquecimiento externo pasivo de campos documentales mediante ToolGatewayManager.
- Exige consentimiento explícito y permite limitar exactamente los campos transmitidos.
- Devuelve hallazgos trazables, fuentes y advertencias sin abrir enlaces ni ejecutar acciones.
- Incorpora un contrato de proveedor intercambiable y un adaptador sin cliente de red implícito.


## M356 — Structured Document Extraction gobernado

- Añade extracción local y explicable de campos documentales desde OCR.
- Conserva evidencia y confianza por campo sin inventar valores ausentes.
- Reutiliza clasificación, QR y códigos de barras en una sola captura.
- No consulta la web, no valida fiscalmente ni realiza pagos.


- Se agregó una suite de contratos de estabilización para la serie M347.
- Se verifica la continuidad documental desde M347.3 hasta M347.15.
- Se protege la unicidad de las autoridades cognitivas canónicas en `core/`.
- Se fijan firmas públicas compatibles y valores contractuales esenciales.
- No se modificó código productivo ni comportamiento del pipeline.



# ROBY XI.2 M353 — Object Detection gobernado

- Incorpora detección local de objetos mediante un contrato intercambiable.
- Integra `detect_objects()` en el único `OfficialVisionCore`.
- Devuelve etiquetas, confianza y regiones sin exponer el frame original.
- Exige permiso, consentimiento y solicitud directa.
- No incorpora memoria visual, seguimiento ni ejecución automática.

# ROBY XI.2 M352 — QR y códigos de barras gobernados

- Extiende el único `OfficialVisionCore` con decodificación local explícita.
- Agrega `VisualCodeDecoder`, `VisualCodeDetection` y `CodeRegion`.
- Devuelve contenido, tipo, confianza, región y procedencia, nunca el frame.
- No abre enlaces, ejecuta comandos, accede a red ni persiste contenido.
- Incorpora un adaptador opcional basado en OpenCV y pyzbar.


# ROBY XI.2 M351 — OCR gobernado

- Incorpora extracción local de texto mediante el único `OfficialVisionCore`.
- Agrega contratos `TextExtractor`, `TextExtraction` y `TextRegion`.
- Añade un adaptador opcional para Tesseract y OpenCV.
- Requiere permiso, consentimiento y solicitud explícita antes de capturar.
- No conserva imágenes ni realiza comprensión semántica de documentos.

# ROBY XI.2 M350 — Face Detection gobernado

- Extiende `OfficialVisionCore` con localización facial bajo autorización explícita.
- Incorpora contratos `FaceDetector`, `FaceDetection` y `FaceRegion`.
- Añade un adaptador local OpenCV opcional basado en cascada Haar.
- Devuelve solamente presencia, cantidad, regiones, confianza y procedencia.
- No identifica personas ni infiere edad, género, emociones u otros atributos.
- No persiste imágenes, plantillas biométricas ni seguimiento entre capturas.

# ROBY XI.2 M349 — Person Detection gobernado

- Extiende el único `OfficialVisionCore`; no crea una segunda autoridad visual.
- Añade `PersonDetector`, `PersonDetection` y regiones no biométricas.
- Incorpora un detector local OpenCV HOG opcional y desacoplado.
- Exige capacidad `object_detection`, permiso, consentimiento y solicitud directa.
- Expone presencia, cantidad, confianza y regiones; nunca bytes del frame.
- No reconoce caras, identidades, edad, género, emociones ni atributos sensibles.
- No activa captura continua, seguimiento, persistencia, memoria visual ni red.

# ROBY XI.2 M348.9 — Vision Core gobernado

- Incorpora `OfficialVisionCore` como puente oficial entre la cámara local y el servicio de visión inteligente existente.
- Exige permiso de cámara, consentimiento explícito y solicitud directa antes de tocar hardware.
- Captura un único frame por solicitud y expone solamente metadatos seguros.
- Descarta los bytes crudos de imagen después de construir la observación gobernada.
- Reutiliza `IntelligentVisionService`; no crea una segunda autoridad visual.
- Añade snapshot observable con intentos, capturas, observaciones aceptadas y última referencia.
- No incorpora todavía detección de personas, OCR, QR, reconocimiento de objetos ni descripción visual.
- No activa cámara en segundo plano, sesiones continuas, biometría, persistencia ni red.

# M347.14 — Pruebas integrales cognitivas

- Consolida la Fase 4 con escenarios end-to-end sobre el pipeline cognitivo existente.
- Verifica intención, estrategia, acción, traza y política de escritura en un mismo turno.
- Verifica persistencia autorizada, recuperación relevante y contexto de prompt.
- Verifica continuidad entre sesiones del mismo perfil y aislamiento entre perfiles.
- Verifica que las correcciones no se anexen como una segunda verdad.
- Verifica que las decisiones serializadas no expongan contenido de memoria ni prompts.
- Verifica que los controles de aprendizaje y recall no eviten el análisis cognitivo.
- No añade lógica productiva, stores, planificadores, memorias ni autoridades paralelas.

# M347.13 — Continuidad entre sesiones

- Reutiliza `RuntimeSessionProfile` en la integración cognitiva de memoria.
- Registra `session_id` y `profile_id` en recuerdos nuevos autorizados.
- Recupera recuerdos relevantes entre sesiones del mismo perfil.
- Excluye recuerdos procedentes de perfiles distintos.
- Mantiene compatibles los recuerdos heredados sin metadatos de sesión.
- Añade `SessionContinuityDecision` con trazabilidad segura de procedencia.

# M347.12 — Recuperación relevante de memoria

- Extiende `CognitiveMemoryRecall` con `MemoryRelevanceDecision`.
- Incorpora un umbral explícito y seguro para seleccionar recuerdos.
- Usa tema, entidades y referencias del `ConversationContext` canónico.
- Descarta recuerdos archivados antes del ranking y la proyección.
- Registra conteos y motivos sin exponer contenido, prompts ni razonamiento.
- Mantiene un único store, un único recall y el pipeline cognitivo existente.

# ROBY XI.2 M347.11 — Política de escritura en memoria

- Extiende la única `CognitiveLearningPolicy` existente; no crea otra autoridad de memoria.
- Añade una decisión explícita de escritura: `write`, `review` o `skip`.
- Registra motivos seguros para contenido durable, temporal, correctivo, incierto, vacío o transitorio.
- Considera el `ConversationContext` canónico sin copiar historial ni resolver referencias.
- Impide que una corrección se agregue ciegamente como un recuerdo nuevo.
- Hace que `CognitiveMemoryIntegration` persista únicamente decisiones autorizadas.
- Conserva las categorías, candidatos, store SQLite y APIs históricas existentes.
- No recupera, deduplica, actualiza ni elimina recuerdos en este milestone.
- No registra contenido en la decisión serializada, prompts ni razonamiento privado.
- No modifica voz, red, herramientas ni `.roby/credentials.json`.

# ROBY XI.2 M347.10 — Modelo explícito de contexto conversacional

- Añade `ConversationContext` como estado inmediato, estructurado e inmutable.
- Representa tema, entidades, intenciones anteriores, acción anterior, referencias, correcciones y turno.
- Integra el contexto opcional en el único `ConversationStrategyPlanner` canónico.
- Conserva la misma instancia en `ConversationStrategy` y `CognitiveDecisionTrace`.
- Mantiene un contexto vacío seguro cuando no existe continuidad previa.
- No resuelve referencias, reconstruye historial ni agrega memoria persistente.
- Preserva comportamiento, metadatos e igualdad histórica cuando no hay contexto.
- No crea gestores, routers, planificadores, memorias ni núcleos paralelos.
- No registra prompts, historial completo, credenciales ni razonamiento privado.
- No modifica voz, red, persistencia, herramientas ni `.roby/credentials.json`.

# ROBY XI.2 M347.9 — Diagnóstico de decisiones fallidas

- Añade `DecisionFailureReason` y `DecisionFailureDiagnostic` a la trazabilidad canónica.
- Diagnostica intención cognitiva desconocida, intención interactiva desconocida y confianza insuficiente.
- Registra componente, confianza observada, mínimo esperado, acción, aclaración y fallback.
- Expone diagnósticos mediante `ConversationStrategy.diagnose_failed_decision()`.
- Mantiene vacíos los diagnósticos de decisiones satisfactorias y estrategias históricas sin traza.
- No altera acciones, metadatos, respuestas, explicación de M347.8, runtime ni igualdad histórica.
- No registra prompts, texto del usuario, credenciales, razonamiento privado ni fallos de proveedores.
- No modifica voz, red, persistencia, herramientas ni `.roby/credentials.json`.

# ROBY XI.2 M347.8 — Explicación resumida para el usuario

- Añade una explicación breve y determinística derivada de `CognitiveDecisionTrace`.
- Expone la explicación mediante `CognitiveDecisionTrace.explain_for_user()` y `ConversationStrategy.explain_decision_for_user()`.
- No almacena una segunda copia de la explicación ni altera la fuente de verdad de la traza.
- Describe únicamente el resultado observable: responder, preparar una acción, continuar, revisar, reconocer o aclarar.
- No revela prompts, deliberaciones, cadenas de razonamiento, credenciales ni datos sensibles.
- No afirma ejecución de herramientas cuando solo se preparó una acción.
- Mantiene compatibilidad con estrategias históricas sin traza y preserva su igualdad.
- No modifica voz, red, persistencia, herramientas ni `.roby/credentials.json`.

# ROBY XI.2 M347.7 — Trazabilidad interna de decisiones

- Añade `CognitiveDecisionTrace` al resultado del único `ConversationStrategyPlanner` canónico.
- Registra intención cognitiva, confianza, intención interactiva, acción seleccionada, tono, profundidad, formato y uso previsto del LLM.
- Reserva campos explícitos para herramientas consideradas, herramienta elegida y motivo de fallback.
- No registra prompts, credenciales, datos sensibles ni cadenas de razonamiento.
- Mantiene igualdad histórica de `ConversationStrategy` mediante una traza no comparativa.
- No modifica metadatos históricos, respuestas, herramientas, voz, red, persistencia ni `.roby/credentials.json`.

# ROBY XI.2 M347.6 — Selección cognitiva de acciones

- Amplía el único `ConversationStrategyPlanner` canónico con una acción cognitiva declarativa.
- Selecciona respuesta, preparación de acción, continuidad, revisión, reconocimiento o aclaración según la intención explícita.
- `prepare_action` no ejecuta herramientas ni afirma ejecuciones; solo orienta el flujo canónico existente.
- Mantiene metadatos históricos intactos cuando no existe intención interactiva explícita.
- Corrige los dos pendientes de estilo detectados al validar M347.5.
- No crea selectores, planificadores, routers, gateways ni núcleos paralelos.
- No modifica voz, red, persistencia, ejecución ni `.roby/credentials.json`.

# ROBY XI.2 M347.5 — Planificación cognitiva basada en intención

- Integra la clasificación interactiva de M347.4 en el único `ConversationStrategyPlanner` canónico.
- Conserva intacta la estrategia por dominio cognitivo y la enriquece según pregunta, comando, seguimiento, corrección o interacción social.
- Añade indicaciones determinísticas de continuidad, corrección, respuesta directa y seguridad de ejecución.
- Expone intención interactiva y confianza en metadatos solo cuando existe una clasificación explícita.
- Mantiene compatibilidad exacta para resultados históricos sin intención interactiva.
- No crea planificadores, routers, memorias, gateways ni núcleos paralelos.
- No modifica red, voz, persistencia, ejecución ni `.roby/credentials.json`.

# ROBY XI.2 M347.4 — Clasificación explícita de intención

- Amplía el único `CognitiveIntentAnalyzer` canónico.
- Conserva la intención cognitiva existente y agrega la forma explícita del turno.
- Clasifica preguntas, comandos, seguimientos, correcciones, interacciones sociales y casos desconocidos.
- Expone confianza y señales determinísticas para observabilidad posterior.
- Mantiene compatibilidad con los consumidores existentes.
- No crea clasificadores, routers, memorias, gateways ni núcleos paralelos.
- No modifica red, voz, persistencia ni `.roby/credentials.json`.

# ROBY XI.2 M347.3 — Baseline verificable de M347.2

- Formaliza M347.2 como línea base auditada para continuar la serie M347.x.
- Actualiza el README raíz con la naturaleza privada y no comercial del proyecto.
- Protege el núcleo cognitivo único y la composición exclusiva mediante `OfficialConversationGateway`.
- Exige integración y unificación total, sin módulos, autoridades o pruebas aisladas.
- Preserva `.roby/credentials.json` como fuente privada canónica, sin modificaciones.
- Incorpora el contexto personal de Carlos, Cristina y su Chevrolet Tracker Automática Turbo 2.0.
- Agrega un informe ejecutivo y pruebas estáticas de invariantes arquitectónicos.
- No modifica runtime, respuestas, persistencia, red, voz, herramientas ni autonomía.

# M346.7 — Memoria canónica de objetivos gobernados

- Incorpora una memoria cognitiva gobernada de continuidad para objetivos explícitos.
- Mantiene estados activo, pausado y completado sin reemplazar objetivos domésticos persistentes.
- Permite vincular objetivos con planes canónicos M346.6.
- La composición productiva permanece exclusivamente en `OfficialConversationGateway`.
- No agrega persistencia, ejecución, detección autónoma, red ni conversación paralela.
- `.roby/credentials.json` permanece intacto.

# ROBY XI.2 M346.6 — Modelo Canónico de Planificación Gobernada

- Incorpora `GovernedPlanModel` como única autoridad de creación del modelo cognitivo de plan.
- Define planes y pasos inmutables con objetivo, estado actual, supuestos, faltantes, dependencias, riesgos, resultado esperado, confianza y autorizaciones.
- Valida orden, unicidad y dependencias retrospectivas de los pasos.
- Integra creación y observación exclusivamente mediante `OfficialConversationGateway`.
- Mantiene `ExecutiveConversationPlanner` como autoridad operativa canónica existente; no crea otro planificador.
- No agrega persistencia, ejecución, autonomía, conversación paralela, scheduler, red ni acciones externas.
- No modifica `.roby/credentials.json`.

# ROBY XI.2 M344.3 — Resiliencia y Observabilidad de Consultas Gobernadas

- Enriquece el único `GovernedSourceQueryExecutor` con resiliencia local.
- Añade métricas acumuladas y un historial acotado de 100 observaciones.
- Registra estado, duración, elementos devueltos o descartados y error tipado.
- No almacena texto de consulta, parámetros, contenido recibido ni credenciales.
- Limita resultados al máximo solicitado por el contrato.
- Degrada respuestas estructuralmente inválidas a un fallo gobernado.
- Conserva los `ValueError` del adaptador como fallos reintentables históricos.
- Expone observabilidad exclusivamente mediante `OfficialConversationGateway`.
- No agrega telemetría externa, persistencia, scheduler, hilos ni otro ejecutor.

# ROBY XI.2 M344.1 — Ejecutor Único de Consultas Gobernadas

- Incorpora `GovernedSourceQueryExecutor` como única autoridad operativa.
- Mantiene `GovernedSourceQueryContract` M344.0 sin ejecución ni adaptadores.
- Admite adaptadores síncronos inyectables y registrados por fuente.
- Valida siempre el contrato gobernado antes de ejecutar.
- Expone resultados exitosos, vacíos y fallos tipados.
- Maneja ausencia de adaptador, timeout y fallo del proveedor.
- No incorpora red, scheduler, hilos ni lógica cognitiva paralela.
- Integra registro y ejecución exclusivamente mediante `OfficialConversationGateway`.

# ROBY XI.2 M343.9 — Relevancia Personal Refinada

## M355 — Document Classification gobernado

- Clasificación documental local, explicable y gobernada.
- Reutiliza OCR y señales opcionales de objetos y códigos visuales.
- Incorpora categorías iniciales y salida `unknown` para evidencia insuficiente.
- No consulta la web, no extrae campos contables y no ejecuta acciones.


## M354 — Scene Understanding gobernado

- Added deterministic fusion of existing visual analyzers over one frame.
- Added governed `OfficialVisionCore.understand_scene()`.
- Added safe scene observability without raw media or behavioral inference.


## Cambios

- Se refinó el único `RelevanceEvaluator` canónico; no se creó otro motor.
- El puntaje ahora considera prioridad personal explícita, calidad de la fuente,
  verificación, actualidad, región y tipo de información.
- Se agregó `RelevanceScoreBreakdown` para explicar el puntaje de cada persona.
- Los candidatos históricos sin metadatos conservan sus puntajes anteriores.
- La información normalizada de M343.8 transfiere todos sus metadatos al
  evaluador existente.
- No se agregaron red, scraping, schedulers, hilos ni ejecución autónoma.

## Validación focalizada

- 75 pruebas M343.0–M343.9 aprobadas.
- Compilación correcta.
- Credenciales sin cambios.

---

## M343.1 — Depuración estructural y núcleo cognitivo único

- Se eliminaron catorce archivos vacíos sin implementación ni referencias reales.
- Se retiró el módulo vacío `domain/reminders.py`, que coexistía innecesariamente con el paquete canónico `domain/reminders/`.
- Se conservaron únicamente los `__init__.py` vacíos que cumplen una función estructural de paquete.
- Se añadió una prueba que impide reintroducir archivos Python vacíos fuera de marcadores de paquete.
- Se añadió una prueba estática que garantiza una sola construcción productiva de `CanonicalCognitiveCore`, ubicada en `OfficialConversationGateway`.
- Se verificó que los cinco dominios cognitivos canónicos aparezcan exactamente una vez en el núcleo.
- No se modificaron configuración, credenciales, autoridades cognitivas ni comportamiento funcional.
- La suite asciende a 8166 pruebas aprobadas.

## M343.0 — Consolidación del núcleo cognitivo

- Se agregó `app/canonical_cognitive_core.py`.
- Se consolidaron las fachadas canónicas de memoria, planificación, decisión,
  estado y reflexión bajo una frontera coordinadora de sólo lectura.
- `OfficialConversationGateway` expone `canonical_cognitive_core`.
- No se modificaron autoridades internas, precedencias ni comportamiento.
- Se añadieron seis pruebas de arquitectura y no regresión.

# M342.8 — Consolidación del estado cognitivo

- Añade `CanonicalCognitiveStateFacade` como única frontera descriptiva para el estado cognitivo.
- Conserva `core.cognitive_state_contract:CognitiveStateManager` como única autoridad de lectura, actualización y reinicio.
- Clasifica los estados persistente histórico, global, mental, residente, ejecutivo y del modelo del mundo como adaptadores, especializaciones u observadores subordinados.
- Permite delegación explícita al contrato oficial sin inferir cambios ni sincronizar almacenes históricos.
- Expone el mapa consolidado mediante `OfficialConversationGateway.canonical_cognitive_state`.
- No migra datos, no fusiona estados, no introduce escrituras implícitas y no modifica respuestas.
- Agrega 6 pruebas focalizadas.

# M342.7 — Consolidación del motor de decisión

- Añade `CanonicalDecisionFacade` como única frontera descriptiva para decisión.
- Conserva `UnifiedCognitiveCoordinator` como autoridad operativa primaria.
- Clasifica al director ejecutivo como colaborador y a los demás motores como especializaciones, sombra o compatibilidad histórica.
- Expone el mapa consolidado mediante `OfficialConversationGateway.canonical_decision`.
- No altera decisiones, precedencias, respuestas, ejecución ni autonomía.

# Changelog

## M342.6 — Consolidación de la planificación

- Agrega `CanonicalPlanningFacade` como contrato único sobre la autoridad `ExecutiveConversationPlanner`.
- Clasifica contribuidores, planificadores especializados, contratos históricos y el planificador en sombra sin eliminarlos.
- Mantiene `CognitivePlannerShadowRuntime` exclusivamente observacional y sin autoridad operativa.
- Permite delegación transparente al planificador ejecutivo existente sin cambiar su semántica ni activar acciones nuevas.
- Expone el mapa consolidado mediante `OfficialConversationGateway.canonical_planning`.
- No fusiona almacenes de planes, no activa autonomía y no modifica respuestas.
- Agrega 6 pruebas focalizadas.

## M342.5 — Consolidación de la memoria

- Agrega `CanonicalMemoryFacade` como contrato único sobre la autoridad `OfficialMemoryGateway`.
- Clasifica adaptadores, memorias especializadas y pipelines históricos sin eliminarlos ni migrar datos.
- Permite delegación transparente al gateway oficial conservando las semánticas de escritura, consulta, estado e interceptación.
- Expone el mapa consolidado mediante `OfficialConversationGateway.canonical_memory`.
- No activa aprendizaje automático, no fusiona almacenes y no introduce escrituras nuevas.
- Agrega 6 pruebas focalizadas.

## M342.4 — Adaptadores de Integración Cognitiva

- Añade contratos uniformes de integración para memoria, planificación, decisión, reflexión y observabilidad.
- Cada adaptador referencia la autoridad primaria definida en M342.2 y la participación declarada en M342.3.
- Distingue adaptadores de solicitud-respuesta, sólo lectura y observacionales.
- Permite describir el destino oficial de una solicitud sin invocar runtimes ni ejecutar capacidades.
- Expone el registro mediante `OfficialConversationGateway.cognitive_integration_adapters`.
- No modifica respuestas, memoria, planificación, decisiones, herramientas ni autonomía.
- Añade pruebas específicas de cobertura, autoridad, roles, serialización y no intervención.

## M342.3 — Ciclo cognitivo canónico

- Define el recorrido oficial de un turno desde entrada hasta respuesta.
- Vincula cada etapa con la autoridad primaria declarada en M342.2.
- Distingue participación obligatoria, condicional, consultiva, observacional y de frontera.
- Mantiene memoria, planificación y ejecución como etapas condicionales cuando el turno no las requiere.
- Expone el ciclo mediante `OfficialConversationGateway.canonical_cognitive_cycle`.
- Valida orden, cobertura completa, unicidad de fases y correspondencia con el mapa de autoridad.
- No modifica respuestas, decisiones, herramientas, memoria ni autonomía.
- Añade pruebas específicas de orden, cobertura, roles y no intervención.

## M342.2 — Mapa oficial de autoridad cognitiva

- Define una única autoridad primaria para cada responsabilidad cognitiva del inventario M342.1.
- Distingue explícitamente autoridades primarias, colaboradores, observadores y componentes en sombra.
- Mantiene la coordinación cognitiva unificada como autoridad de decisión y al director ejecutivo como colaborador consultivo.
- Mantiene la planificación ejecutiva como autoridad y al planificador cognitivo en modo sombra.
- Mantiene el núcleo cognitivo residente como autoridad de reflexión y la cognición adaptativa como colaboradora.
- Valida cobertura completa, ausencia de autoridades duplicadas y coherencia con el inventario operacional.
- Expone el mapa mediante `OfficialConversationGateway.cognitive_authority_map` sin modificar respuestas, decisiones o ejecución.
- Añade pruebas específicas de unicidad, roles secundarios, validación y no intervención.

## M342.1 — Inventario cognitivo operacional en modo observación

- Incorpora un inventario canónico de capacidades cognitivas y su autoridad declarada.
- Clasifica capacidades como consultivas, operacionales limitadas, visibles o en modo sombra.
- Añade observación en memoria a la frontera oficial de conversación, sin modificar respuestas ni decisiones.
- Registra inicio, finalización y error de cada turno con identificadores deterministas y retención acotada.
- Expone la instantánea mediante `OfficialConversationGateway.cognitive_inventory`.
- Mantiene el observador sin persistencia, sin nuevas llamadas externas y sin autonomía adicional.
- Añade pruebas específicas de no intervención, errores, determinismo y límite de historial.

## M341.10 — Integración, auditoría y cierre de etapa

- Se agregó una auditoría transversal de los nueve componentes M341.
- La auditoría consulta el estado real de integración del controlador.
- Se incorporaron comandos de estado, auditoría y exportación de cierre.
- El informe de cierre se exporta en JSON a `.roby/audits`.
- La consulta normal no genera archivos ni produce efectos secundarios.
- Se corrigió la paridad de enrutamiento por voz para dispositivos.
- La auditoría no ejecuta acciones clínicas ni activa hardware.
- Se añadieron 10 pruebas específicas; la suite alcanzó 8103 pruebas.

## M341.9 — Arquitectura para dispositivos

- Se agregó un contrato desacoplado para adaptadores de dispositivos.
- Se incorporaron descriptores, estados y capacidades declaradas.
- Se añadió un registro central con alta, baja, consulta y filtros.
- Se validan disponibilidad, capacidades y permisos de lectura/escritura.
- Se agregó un adaptador simulado sin acceso automático a hardware.
- Se integró el comando conversacional `dispositivos disponibles`.
- Se añadieron 10 pruebas específicas; la suite alcanzó 8093 pruebas.

# Changelog

## M341.8 - Exportación médica en PDF

- Añade exportación médica local en PDF para Carlos y Cristina.
- Reutiliza el orquestador integral para evitar duplicar reglas clínicas.
- Incluye fecha de generación, prioridades y secciones de salud confirmadas.
- Guarda los documentos en `.roby/exports/medical`.
- Añade paginación, ajuste de líneas y compatibilidad con caracteres en español.
- Mantiene separación estricta entre perfiles y límites clínicos explícitos.
- Integra comandos de texto y voz en el controlador de escritorio.
- Añade 10 pruebas específicas sin regresiones.

# M341.7 — Guía conversacional de salud

- Añade orientación conversacional por niveles: informativo, seguimiento,
  precaución y urgente.
- Usa únicamente síntomas, alergias, medicación, condiciones y datos de
  emergencia confirmados.
- Reconoce señales de alarma explícitas sin diagnosticar ni inferir causas.
- Sugiere próximos pasos descriptivos y conserva la separación de perfiles.
- No indica iniciar, suspender ni modificar tratamientos.
- Incorpora 10 pruebas específicas; suite completa: 8073 pruebas aprobadas.

# M341.6 — Orquestador integral de salud

- Añade una vista integral y priorizada de salud para Carlos y Cristina.
- Reúne medicación, síntomas, alergias, condiciones crónicas, signos vitales, chequeos, profesionales, centros y emergencia.
- Prioriza únicamente datos confirmados mediante reglas descriptivas y conserva el resumen clásico sin cambios.
- Incorpora 10 pruebas específicas; suite completa: 8063 pruebas aprobadas.

# M341.5 — Contactos de emergencia

- Registra contactos de emergencia confirmados y separados por perfil.
- Conserva relación, teléfonos, prioridad, autorización documentada y notas.
- Registra cobertura médica, plan, afiliado y teléfono de urgencias.
- Permite listar, consultar, archivar y generar una ficha de emergencia.
- Integra contactos en Health Orchestrator y resumen preconsulta.
- No realiza llamadas ni reemplaza servicios oficiales de emergencia.
- Añade 10 pruebas; suite completa prevista: 8053 pruebas.

# M341.4 — Profesionales tratantes y centros de salud

- Registra profesionales y centros de salud confirmados por perfil.
- Conserva especialidad, matrícula, contacto, dirección, tipo y notas.
- Permite vincular profesionales con centros sin mezclar perfiles.
- Permite consultar detalles, listar registros activos y archivar con confirmación.
- Integra el equipo tratante en Health Orchestrator y resumen preconsulta.
- No verifica credenciales ni sustituye información oficial del prestador.
- Añade 10 pruebas; suite completa prevista: 8043 pruebas.

# M341.3 — Enfermedades crónicas con seguimiento específico

- Registra condiciones crónicas confirmadas y separadas por perfil.
- Conserva estado documentado, profesional, centro, medicación relacionada,
  métricas de seguimiento, controles, objetivos profesionales y notas.
- Permite consultar, actualizar, archivar y generar seguimiento específico.
- Integra medicación, signos vitales y síntomas locales sin diagnóstico.
- Añade condiciones al Health Orchestrator y al resumen preconsulta.
- No declara control clínico ni modifica tratamientos.
- Añade 10 pruebas; suite completa prevista: 8033 pruebas.

# M341.1 — Registro estructurado de síntomas

## M341.2 — Alergias como entidades de primera clase

- Registro estructurado y confirmado de alergias por perfil.
- Tipos, reacción, gravedad, fuente profesional, estado y archivado.
- Integración con Health Orchestrator y preparación de consultas.
- Coincidencia exacta entre alergias medicamentosas y medicación activa.
- Sin inferencia automática de familias farmacológicas ni cambios terapéuticos.


- Añade episodios de síntomas separados para Carlos y Cristina.
- Registra inicio, intensidad, zona, duración, frecuencia, evolución, factores,
  síntomas acompañantes, signos relacionados, medicación y notas.
- Exige confirmación antes de crear, actualizar, cerrar o archivar episodios.
- Permite consultar síntomas activos, historial por período y detalle por ID.
- Integra los síntomas activos en el Health Orchestrator.
- Incorpora señales de alarma explícitas sin diagnóstico ni cambios terapéuticos.
- Añade 10 pruebas; validación completa prevista: 8013 pruebas.

# M327.2

- Integrado el primer ciclo autónomo gobernado con fallos reales del runtime ejecutivo.
- Añadida observabilidad del último resultado y contador de ciclos autónomos.
- Preservado el error operativo original ante fallos internos de autonomía.
- Validación: 7672 tests OK.

# M326.7 — Outcome Supervisor

- Añade supervisión determinista de resultados observados.
- Distingue completar, reintentar, revertir, degradar y no actuar.
- Representa la necesidad de notificación sin enviarla.
- Respeta el presupuesto de intentos de `DecisionPolicy`.
- Mantiene cero ejecución y cero efectos secundarios.

# M326.5 — Decision Policy Engine

- Añade ranking determinista de candidatos evaluados.
- Aplica prohibiciones, confianza mínima y desempate estable.
- Produce decisiones observables, simuladas, recomendadas o bloqueadas.
- Reserva autorización y confirmación para el futuro Autonomy Gate.
- Mantiene cero ejecución y cero efectos secundarios.

# M307 — Diagnóstico integral de voz y rendimiento de herramientas

- Añade una instantánea de diagnóstico del motor Vosk: worker, stream, frames del callback, colas, estado, nivel, umbrales, dispositivo y error.
- Actualiza la línea `DIAG` de la interfaz cada segundo para localizar el corte real del micrófono.
- Excluye `venv`, `venv_old`, `.venv` y cachés de Ruff y de la recursión de Pytest.
- Mantiene la colección completa de pruebas distribuidas por todos los módulos.

## RP.22.15 — Consultas y vistas locales del ciclo de vida

- Añade filtros exactos allow-listed sobre estados, códigos, clasificación, prioridad y ocurrencias.
- Añade vistas deterministas con agregados, truncamiento y proyección opcional de transiciones.
- Mantiene operación local, inmutable, redacted, sin persistencia ni impacto ejecutivo.

## RP.22.14 — Ciclo de vida local de anomalías

- Añade estados `new`, `active`, `acknowledged`, `resolved` y `reopened`.
- Incorpora transiciones deterministas y un historial local acotado.
- Mantiene snapshots inmutables, datos redactados y cero automatización ejecutiva.

## RP.22.13 — Consolidación y deduplicación local de anomalías

- Añade consolidación determinista por código estructurado.
- Cuenta duplicados y conserva la evidencia agregada más representativa.
- Limita snapshots de entrada y grupos de salida mediante política explícita.
- Integra el contrato `rp22.13` en Doctor con 14 comprobaciones.
- Mantiene operación en memoria, sin telemetría ni automatización ejecutiva.

## RP.22.11 — Detección local de anomalías en trazas

- Añade detección determinista y versionada con esquema `rp22.11`.
- Incorpora umbrales explícitos para fallback, riesgo alto, calibración degradada y divergencias.
- Requiere una muestra mínima y evita falsas alertas cuando el conjunto no es elegible.
- Mantiene procesamiento en memoria, sin ML, persistencia, telemetría ni contenido sensible.
- Integra el contrato en Doctor y añade cinco pruebas de regresión.

# RP.22.03 — Calibración del Cognitive Decision Kernel

- Añade calibración estructurada entre plan, política, ejecución y resultado.
- Publica códigos de divergencia, observaciones y puntaje descriptivo.
- Mantiene el calibrador en modo observacional, sin aprendizaje ni control ejecutivo.
- Añade documentación arquitectónica y pruebas de compatibilidad.

# RP.22.02 — Explicabilidad del kernel

- Añade una explicación inmutable y versionada a cada decisión canónica.
- Registra regla decisiva, reglas evaluadas, conflictos y evidencia observada.
- Expone una representación determinista lista para JSON y diagnóstico.
- Conserva la decisión ante fallos del explicador mediante fail-open.
- Añade cinco pruebas; validación final: Ruff limpio, 6709 pruebas aprobadas y Doctor listo.

# RP.21.04 — Activación ejecutiva controlada

- Activa el Planificador Cognitivo únicamente en la selección de candidatos semánticos gobernados.
- Omite candidatos incompatibles solo con planes válidos, confiables y de herramienta única.
- Conserva fallback inmediato al flujo histórico ante duda, error, riesgo o confirmación requerida.
- Añade observabilidad de activaciones, omisiones, fallbacks y fallos.
- Añade cuatro pruebas; validación final: Ruff limpio, 6695 pruebas aprobadas y Doctor listo.

# RP.21.01 — Actualidad y evidencia en modo sombra

- Compara el plan cognitivo previo con frescura, evidencia y abstención observadas.
- Registra evaluaciones por sesión sin gobernar ejecución ni respuestas.
- Reconoce evidencia corroborada, fuentes contradictorias y abstención segura.
- Contiene fallos del evaluador para preservar compatibilidad hacia atrás.
- Documenta la integración en `docs/architecture/RP21.01.md`.
- Validación final: Ruff limpio, 6684 pruebas aprobadas y Doctor listo.

# RP.21.00 — Planificador Cognitivo en modo sombra

- Incorpora un plan cognitivo tipado antes de la cadena operacional.
- Clasifica intención, contexto, herramientas, actualidad, evidencia y abstención.
- Registra el último plan por sesión sin ejecutar ni modificar respuestas.
- Contiene fallos del planificador para preservar compatibilidad hacia atrás.
- Inicia el historial incremental en `docs/architecture/RP21.00.md`.
- Validación final: Ruff limpio, 6678 pruebas aprobadas y Doctor listo.

## RP.20.52 — Explicar por qué no responde

- Las abstenciones de actualidad ahora explican el motivo concreto.
- Informan qué criterio de seguridad no se cumplió.
- Proponen una continuación responsable sin recurrir a memoria desactualizada.
- Registran un código de causa auditable en la trazabilidad del turno.

# RP.20.51 — Edad máxima de la información

- Agrega ventanas de vigencia según expresiones temporales explícitas.
- Descarta fuentes demasiado antiguas o sin fecha en consultas de actualidad.
- Se abstiene cuando no hay publicaciones dentro del período pedido.
- Validación final: Ruff limpio, 6660 pruebas aprobadas y Doctor listo.

## Roby XI.2 RP.20.46 — Desambiguación de pronósticos

- La palabra «pronóstico» ya no activa por sí sola el servicio meteorológico.
- Las predicciones deportivas o generales continúan hacia la conversación normal.
- El clima conserva consultas explícitas como «pronóstico extendido» y «pronóstico para mañana».
- El mismo criterio se aplica cuando OpenWeather está desactivado o sin credenciales.
- Validación final: Ruff limpio, 6640 pruebas aprobadas y doctor listo.


## Roby XI.2 RP.20.41 — Ruff limpio

- Se corrigieron todos los errores E501, I001 y F401 detectados por Ruff.
- Se ordenaron imports y se aplicó formato uniforme al código Python.
- Se mantuvo el comportamiento funcional de RP.20.40.
- Validación final: Ruff limpio, 6623 pruebas aprobadas y doctor listo.


## RP.20.28 — Interacción de escritorio fluida

- `Enter` envía mensajes directamente desde el cuadro de texto.
- Se eliminaron los botones Enviar y Hablar.
- El procesamiento conversacional se ejecuta fuera del hilo gráfico para evitar bloqueos.
- La interfaz muestra “ROBY está pensando…” mientras espera la respuesta.
- Se corrigió el saludo duplicado `ROBY: ROBY:`.
- Las consultas meteorológicas ya no reciben respuestas inventadas cuando OpenWeather no está conectado.
- El botón Capacidades permanece como diagnóstico manual y ya no se muestra automáticamente.
# RP.20.27 — Higiene del directorio raíz

- Consolidada documentación histórica bajo `docs/`.
- Movidos aplicadores históricos a `scripts/migrations/`.
- Retirados duplicados exactos, pruebas duplicadas de raíz y cachés regenerables.
- Sin cambios en código de producción ni rutas operativas de estado.

## RP.20.21 — Retiro de propiedad que exponía colaborador interno

- Retirada `OfficialConversationGateway.runtime`.
- Preservadas las vistas operativas explícitas del gateway.
- Añadidas invariantes estructurales contra la reexposición del runtime interno.

## RP.20.20 — Internal convenience aliases removed

- Removed `OfficialROBYRuntime.operational_snapshot`; use `snapshot()` directly.
- Removed `OfficialROBYRuntime.health_readiness`; use `readiness()` directly.
- Added structural tests protecting the canonical runtime operations.

## RP.19.7 — Aprendizaje adaptativo de prioridades y costos

- Se agregaron ajustes persistentes y acotados de prioridad y costo efectivo.
- El aprendizaje usa progreso, estancamiento y revisión metacognitiva explícitos.
- Las estimaciones autoritativas de las fuentes permanecen intactas.
- Se incorporaron rationale, observabilidad y reinicio explícito de adaptación.
- Se añadieron seis pruebas y migración SQLite compatible.


## RP.19.6 — Revisión metacognitiva de compromisos

- Se agregó revisión persistente de calidad de avance y claridad de formulación.
- Se incorporaron recomendaciones deterministas `sound`, `reformulate` y `deferred`.
- La revisión puede reestimar beneficio y costo dentro de la cola deliberativa existente.
- Se publican rationale y estado metacognitivo sin ejecutar acciones externas.
- Se añadieron seis pruebas y migración SQLite compatible.


## RP.19.2 — Activación inteligente de la agenda

- Separación compatible entre foco informativo y foco activado.
- Elegibilidad por estado y urgencia para asuntos en observación.
- Arbitraje anti-repetición con envejecimiento acotado.
- Persistencia y migración SQLite del historial de activación.
- Integración descendente con el ciclo cognitivo oficial.
- Seis pruebas nuevas y certificación específica.
## RP.18.2E — Runtime Health & Readiness Service

- Se agregó `app.runtime_health_readiness` como intérprete operativo del snapshot oficial.
- Se incorporaron readiness global y readiness declarativo por capacidad.
- Se separaron blockers de warnings y dependencias requeridas de opcionales.
- `OfficialROBYRuntime` expone `health_readiness` y `readiness(...)`.
- Se preservó la independencia del gate cognitivo histórico M162.


## RP.18.2B — Official composition and unified lifecycle

- Added `OfficialRuntimeComposition` as the canonical operational graph view.
- Added `OfficialROBYRuntime` as the single idempotent lifecycle authority.
- Migrated the desktop builder to the official runtime authority.
- Preserved `DesktopPersonalRuntime` as a compatibility façade.
- Added rollback, reverse shutdown and composition identity tests.
# ROBY M247 — Runtime Capability Registry

- Reutiliza el Capability Registry de M62 como catálogo oficial del runtime.
- Sustituye el wiring manual por un registro operacional ordenado.
- Expone una consulta conversacional de capacidades integradas.
- Conserva precedencia, feature flags, memoria y `.env` sin cambios.
- Certificación: Ruff limpio y 6055 pruebas aprobadas.

# ROBY M245 — Progress Check-In Runtime

- Added deterministic progress check-ins for official household projects and goals.
- Reused M241 project notes and M242 goal progress mutations with their SQLite stores.
- Integrated check-ins into the official governed conversation pipeline.
- Added no parallel manager, persistence store, scheduler, or provider dependency.
- Certified with Ruff clean and 6045 passing tests, 0 skipped.

# ROBY M244 — Actionable Follow-Up Runtime

- Added deterministic actionable follow-up commands for official goals and projects.
- Reused the M241/M242 next-step mutation paths and their existing SQLite stores.
- Integrated follow-up execution into the official governed conversation pipeline.
- Added no parallel manager, persistence store, scheduler, or provider dependency.
- Certified with Ruff clean and 6035 passing tests, 0 skipped.

# ROBY M243 — Goal and Project Review Runtime

- Added deterministic reviews for active projects and long-term goals.
- Detects missing next steps and configurable inactivity thresholds.
- Integrated on-demand review into the official conversation pipeline.
- Included actionable review findings in the daily household briefing.
- Preserved shared household identity and all existing persistence stores.
- Certified with Ruff clean and 6026 passing tests, 0 skipped.

# ROBY M242 — Long-Term Goals Runtime

- Persistent household goals with progress, status, notes, and next steps.
- Optional links to existing projects and routines.
- Official pipeline integration for desktop and console.
- Shared Familia identity and SQLite persistence.

# ROBY M241 — Projects Runtime

- Persistent household projects with status, notes, and next steps.
- Official pipeline integration for desktop and console.
- Shared Familia identity and SQLite persistence.

# ROBY M240 — Household Knowledge Runtime

- Connected the existing M72 household-memory domain to the official M239 composition root.
- Added persistent SQLite storage for structured household knowledge.
- Added deterministic conversational storage, recall, classification, and archive operations.
- Preserved the shared Familia identity and reused the same console and desktop pipeline.
- Kept cognitive personal memory separate from explicit household facts.
- Certification: Ruff clean; 6016 passed, 0 skipped; zero observed regressions.

# ROBY M239 — Daily Household Briefing

- Activated the existing reminder recurrence domain as the household routine engine.
- Added deterministic conversational creation and management of daily, weekly, monthly, and yearly routines.
- Advanced recurring reminders persistently after delivery, including safe catch-up after downtime.
- Reused the official reminder SQLite store, resident awareness service, household identity, console, and desktop runtime.
- Added no parallel scheduler, task engine, or external dependency.

# ROBY M237 — Personal Memory Runtime

- Wired the existing M183 cognitive memory runtime into the official household composition root.
- Enabled persistent governed learning and relevant recall for the shared `Familia` identity.
- Reused SQLite storage, prompt-context enrichment, private-file protection, console, and desktop paths.
- Added a single `.env` configuration contract for memory activation, path, learning, recall, and bounds.
- Introduced no RAG, embeddings, vector database, or parallel memory subsystem.

# ROBY M233 — Cross-Platform Security Test Normalization

- Centralized restrictive local secret permissions in the existing infrastructure/system boundary.
- Preserved POSIX 0700 directory and 0600 file contracts.
- Added Windows ACL hardening through inheritance removal and an explicit current-user grant.
- Applied the shared policy to encrypted Gmail credentials and external OAuth token files.
- Replaced platform-skipped permission assertions with executable platform contracts.
- Removed live Gmail acceptance from deterministic collection unless explicitly enabled.
- Certification: Ruff clean; 5991 passed, 0 skipped; zero observed regressions.

# ROBY M232 — Multi-User Reminder Ownership

- Added persistent ownership isolation for Carlos and Cristina reminders.
- Added a shared household reminder scope.
- Applied ownership filtering to conversational list/cancel/snooze operations.
- Applied ownership filtering to the resident reminder delivery runtime.
- Preserved compatibility with existing unowned M230/M231 reminder rows.
- Certification: Ruff clean; 5989 passed, 1 skipped in the build environment.

# ROBY M231 — Conversational Reminder Integration

- Integrated deterministic reminder intents into the official governed conversation pipeline.
- Reused the existing reminder application use cases, domain model, and M230 SQLite store.
- Added conversational creation with absolute and relative times, pending-list rendering,
  cancellation, and snoozing without provider or network calls.
- Preserved the normal provider path for all non-reminder conversation.
- Added safe guidance for incomplete reminder requests and an environment feature flag.
- Certification: Ruff clean; 5984 passed, 1 skipped; zero observed regressions.

# ROBY M230 — Resident Reminder Runtime

- Integrated persistent due-reminder delivery into the Always-On Personal Runtime.
- Reused the existing reminder domain, SQLite schema, repository, and console lifecycle.
- Added persistent `(reminder_id, due_at)` notification deduplication across restarts.
- Added thread-safe short-lived SQLite access and safe degraded behavior.
- Added governed environment flags and focused acceptance coverage.


## M228.2 — Gmail Startup Announcement Runtime Wiring

- Wired the subject-only Gmail startup announcement into `python main.py --observe`.
- Added governed OAuth load, refresh, and explicit activation before the first prompt.
- Preserved metadata-only `Subject` retrieval and non-mutating unread lookup.
- Added safe degraded startup when Gmail is unavailable or incomplete.
- Added 12 focused tests; full suite: 5918 passed, 1 skipped.
# ROBY M228.1 — Gmail Interactive OAuth Activation

- Adds explicit interactive Google OAuth activation behind deployment policy.
- Persists authorized-user credentials through SecureCredentialStore or an atomic external JSON fallback.
- Adds an optional desktop startup announcement for unread count and Subject headers only.
- Does not request message bodies, mutate Gmail, or mark messages as read.
- Certification: Ruff clean; 5906 passed, 1 skipped; zero regressions.

# M226.4 — Gmail Execution Planning

- Added immutable, secret-free Gmail execution plans before Tool Gateway invocation.
- Added required payload-shape and intent/capability consistency validation.
- Preserved local policy, capability registration, consent, adapters, and runtime composition.
- Added 12 focused tests; full suite reaches 5748 tests with zero regressions.

# M226.1 — Gmail Governed Integration

- Added governed Gmail composition, account fingerprinting, local action policy, and bounded audit records.
- Preserved M61/M63/M66/M67 contracts; send remains disabled by default.

## M225.2 — Structured Message Transport Observability

- Added read-only structured-message tracing to the development console.
- Added role counts and explicit `messages` versus `prompt` transport reporting.
- Kept domestic content hidden outside explicit `--observe` rendering.
- Added focused regression tests and delivery documentation.

# M225.1 — Structured Conversation Messages

- Added immutable provider-neutral conversation messages with `system`, `user`, and `assistant` roles.
- Preserved the legacy text prompt as a compatibility fallback.
- Sent structured roles directly to OpenAI-compatible local providers.
- Serialized structured messages only at text-only provider boundaries.
- Preserved context curation, owner/session isolation, and persistent-memory separation.
- Added focused compatibility and provider-boundary tests.

# M224.5 — Graceful Runtime Shutdown

- Added clean console shutdown for `exit`, `quit`, and `salir`, with or without `/`.
- Treated EOF and `KeyboardInterrupt` as normal shutdown signals.
- Guaranteed supervisor stop, lifecycle stop, bootstrap stop, and lease release through the existing finalization boundary.
- Added focused tests for command routing, Ctrl+C, lifecycle state, and lease cleanup.

# M224.2 — Conversational Context Continuity Hotfix

- Reconstructed bounded recent conversation history from the local journal.
- Scoped context strictly by owner/profile and session.
- Enriched the provider-neutral `LLMRequest` at the common governed runtime-preparation boundary.
- Kept recent conversational replay separate from persistent memory enrichment.
- Added restart, isolation, truncation, disabled-context, and compatibility tests.
- Focused validation: 44 tests passed.

# M220 — Final Acceptance & ROBY v1 Architecture Certification

- Added immutable final ROBY v1 architecture certificates with deterministic identities.
- Added explicit final-acceptance criteria and `accepted`, `conditional`, `rejected` outcomes.
- Integrated M220 immediately after M219 in the official cognitive runtime.
- Preserved deployment, provider restart, infrastructure mutation, and workload execution outside M220.
- Added 16 focused tests; full suite reaches 5,579 tests with zero regressions.

# M219 — Production Readiness Assessment

- Added deterministic `ready`, `conditional`, and `not_ready` production-readiness outcomes.
- Added explicit checks for M218 certification, criterion completion, lineage, bounded validation, and failure controls.
- Integrated M219 immediately after M218 in the official cognitive runtime.
- Preserved deployment, release approval, infrastructure mutation, and final architecture certification outside M219.
- Added ADR, milestone documentation, manifest, and sixteen focused acceptance tests.

# M213 — Fault Recovery Coordination

- Added deterministic stable, observing, stabilizing, and held recovery states.
- Added contiguous verification, bounded retry, and containment-preserving recovery steps.
- Preserved conversation continuity outside every held-capability set.
- Integrated M213 immediately after M212 in the official cognitive runtime.
- Kept provider restart, tool execution, infrastructure changes, and platform mutation outside M213.
- Added ADR, milestone documentation, manifest, and fourteen focused acceptance tests.

# M212 — Graceful Degradation Engine

- Added deterministic full, conservative, essential, and contained cognitive service modes.
- Added explicit preserve, limit, and suspend policies for six cognitive capabilities.
- Preserved conversation continuity in every degradation mode.
- Integrated M212 immediately after M211 in the official cognitive runtime.
- Kept fault recovery, restoration, providers, tools, and platform mutation outside M212.
- Added ADR, milestone documentation, manifest, and fourteen focused acceptance tests.

# M211 — Cognitive Resilience Framework

- Added deterministic resilience postures derived from M210 whole-system reports.
- Added explicit failure-domain classification and priority-ordered safeguards.
- Integrated M211 immediately after M210 in the official cognitive runtime.
- Preserved non-executing boundaries for degradation, recovery, scheduling, tools, providers, and runtime mutation.
- Added ADR, milestone documentation, manifest, and eleven focused acceptance tests.

# M210 — Whole-System Integration

- Added deterministic whole-system readiness reports spanning M201-M209.
- Added explicit component lineage, constraints, health score, and operational availability.
- Integrated M210 immediately after M209 in the official cognitive runtime.
- Preserved all execution, provider, tool, memory, planning, and governance boundaries.
- Added ADR, milestone documentation, manifest, and ten acceptance tests.

# M200 — Adaptive Conversation Operational Consolidation

- Added deterministic consolidation of M196-M199 conversational assessments.
- Added repair-first operational precedence and explicit grounding/expectation states.
- Added trace references to all available source assessments.
- Integrated M200 immediately after M199 in the official runtime composition root.
- Added ADR, milestone documentation, and ten acceptance tests.

## M199 — Conversational Commitment and Expectation Alignment

- Added deterministic expectation states for aligned requests, explicit commitments, absolute guarantees, and grounding-blocked commitments.
- Calibrated unsupported certainty and limited commitments to work realizable in the active turn.
- Integrated M199 immediately after M198 in the official cognitive runtime.
- Preserved advisory-only behavior with no scheduling, provider, tool, memory, planning, or mutation authority.
- Added focused classification, lineage, composition-order, and request-preservation tests.


## M198 — Conversational Grounding and Shared Understanding

- Added deterministic shared-understanding states for alignment, confirmation, corrected scope, and pending clarification.
- Preserved M197 clarification boundaries against unsupported assumptions.
- Integrated M198 immediately after M197 in the official cognitive runtime.
- Preserved advisory-only behavior with no provider, tool, memory, planning, or mutation authority.
- Added focused classification, lineage, composition-order, and request-preservation tests.


## M197 — Conversational Repair and Clarification Intelligence

- Added deterministic detection of missing references, underspecified requests, uncertain intent, corrections, and abrupt topic shifts.
- Added bounded repair actions for proceeding, targeted clarification, correction confirmation, and topic-shift acknowledgement.
- Integrated M197 immediately after M196 in the official cognitive runtime.
- Preserved advisory-only behavior with no blocking, provider, tool, memory, planning, or mutation authority.
- Added focused classification, traceability, composition-order, and request-preservation tests.


## M196 — Adaptive Conversation Intelligence

- Added bounded conversation state isolated by owner and session.
- Added deterministic intent-evolution, continuity, coherence, strategy, and depth signals.
- Integrated adaptive conversation context into the official cognitive runtime.
- Preserved advisory-only behavior with no provider, tool, memory, or mutation authority.
- Added focused architecture, isolation, bounded-state, and runtime integration tests.


## M187 — Local Provider Runtime Adapter

- Added an OpenAI-compatible local provider adapter for Ollama, LM Studio and llama.cpp.
- Added bounded health and inference timeouts, normalized failures and cancellation.
- Added environment-driven local provider construction and 20 focused tests.

## M188 — Personal Identity and Session Profiles

- Added persistent private and shared identity profiles.
- Bound runtime sessions immutably to a selected profile.
- Added profile-scoped lifecycle state paths and private JSON stores.
- Added explicit environment selection for Carlos, spouse, and family-shared contexts.

## M188.1 — Cross-Platform Runtime Compatibility

- Centralized portable private-file handling for runtime journals, traces,
  memory databases, lifecycle state, leases, profiles, and sessions.
- Preserved exact `0600` enforcement on POSIX systems.
- Replaced POSIX-only permission assertions with a platform-aware invariant on
  Windows, where Python mode bits do not represent NTFS ACLs.
- Added native Windows process-liveness detection without `os.kill(pid, 0)`.
- Kept stale-lease recovery conservative across Windows and POSIX.

## M189 — Cognitive Runtime Orchestration

- Added a governed runtime orchestration boundary for existing cognitive capabilities.
- Added ordered, optional cognitive contributors with contained stage failures.
- Added cognitive prompt enrichment while preserving provider request settings.
- Added deterministic orchestration lineage, activated-stage metadata, and references.
- Integrated cognitive orchestration into the official M178 preparation path after memory and before tools.
- Added 12 focused tests without enabling autonomous actions or platform mutation.

## M190 — Living Conversation Runtime Integration

- Connected governed M93–M105 living-conversation decisions to M189.
- Added rhythm, next-move, continuity, and user-floor context to active turns.
- Preserved exact living-conversation lineage without exposing references in prompts.
- Kept paused, review-required, and non-eligible decisions non-invasive.
- Added official composition-root wiring and 11 focused tests.

## M191 — Reasoning Runtime Integration

- Connected governed reasoning results to the operational cognitive runtime.
- Preserved blocked, review-required, and abstention semantics.
- Added official composition-root wiring and deterministic contributor order.
- Added 12 focused integration tests.

## M192 — Planning Runtime Integration

- Connected approved and active M90 executive plans to the operational runtime.
- Added objectives, criteria, milestones, constraints, and plan-state context.
- Preserved exact plan lineage outside provider prompts.
- Kept draft, review, paused, completed, and cancelled plans non-invasive.
- Added official composition-root wiring and focused integration tests.

## M193 — Reflection Runtime Integration

- Connected M88 adaptive reflection records to the operational cognitive runtime.
- Added stable, improving, insufficient, and review-required projection semantics.
- Preserved reflection lineage outside provider prompts.
- Kept recommendations consultative and prevented reflection from rewriting decisions.
- Added official composition-root wiring and focused integration tests.

## M194 — Executive Cognitive Runtime

- Connected governed M91 executive coordination to the cognitive runtime.
- Added priorities, subsystems, dependencies, constraints, and directive state.
- Kept sensitive or review-required coordination outside provider prompts.
- Preserved coordination lineage without granting execution authority.
- Added official composition-root wiring and 15 focused tests.

## M195 — Operational Acceptance Suite

- Added a deterministic, non-authoritative operational acceptance runner.
- Added end-to-end acceptance scenarios spanning bootstrap, cognition, tools,
  provider execution, persistence, traces, restart continuity, and containment.
- Closed the M177–M195 operational cognitive integration stage.

## M201 — Unified Cognitive Blackboard

- Added an immutable, append-only cognitive signal exchange surface.
- Added owner/session isolation, bounded retention, domain filtering, and idempotent publication.
- Published the M200 conversational operational state as the first governed blackboard signal.
- Integrated M201 immediately after M200 in the official cognitive runtime order.
- Preserved all execution, provider, memory, planning, and governance boundaries.
- Added 10 focused tests.

## M202 — Global Cognitive State

- Added a deterministic global cognitive state projection over M201 snapshots.
- Added stable, limited, blocked, and degraded readiness semantics.
- Aggregated active domains, signal counts, confidence, constraints, and lineage.
- Published the state back to the blackboard as governed system context.
- Prevented recursive self-aggregation of prior global-state entries.
- Integrated M202 immediately after M201 in the official cognitive runtime order.
- Preserved all execution, provider, memory, planning, arbitration, and governance boundaries.
- Added 10 focused tests.

## M203 — Cognitive Event Bus

- Added immutable, deterministic cognitive events with exact source lineage.
- Added owner/session-scoped subscriptions filtered by type, topic, and domain.
- Added idempotent publication, bounded retention, and delivery records.
- Contained consumer failures without interrupting other event delivery.
- Eventized M202 global cognitive state and published a governed receipt to M201.
- Integrated M203 immediately after M202 in the official cognitive runtime order.
- Preserved all execution, provider, memory, planning, arbitration, and governance boundaries.
- Added 10 focused tests.

## M204 — Cross-Domain Coordination

- Added deterministic, immutable cross-domain coordination directives.
- Correlated M201 blackboard, M202 global state, and M203 cognitive events.
- Added participating-domain discovery, constraint priorities, and conflict detection.
- Preserved owner/session isolation and exact source lineage.
- Published governed coordination candidates back to the cognitive blackboard.
- Integrated M204 immediately after M203 in the official cognitive runtime order.
- Preserved all execution, provider, memory, planning, arbitration, and governance boundaries.
- Added 10 focused tests.

## M205 — Unified Cognitive Scheduler

- Added immutable, deterministic cognitive schedules and ordered work items.
- Converted M204 coordination priorities into explicit sequence, priority, dependency, and constraint data.
- Preserved owner/session isolation and exact source lineage.
- Published governed schedule candidates back to the cognitive blackboard.
- Integrated M205 immediately after M204 in the official cognitive runtime order.
- Preserved all execution, provider, memory, planning, arbitration, and governance boundaries.
- Added 10 focused tests.

## M206 — Executive Arbitration

- Added deterministic executive decisions and per-task dispositions (`authorize`, `defer`, `reject`).
- Preserved blocking constraints and prioritized governance repair under attention-required schedules.
- Published governed arbitration outcomes to the Unified Cognitive Blackboard.
- Integrated M206 immediately after M205 in the official cognitive runtime order.
- Added focused tests, ADR 206, milestone documentation, and delivery manifest.

## M207 — Global Context Fusion

- Added deterministic, immutable global context views over M201–M206 sources.
- Fused domain facts, global constraints, cognitive events, and executive task dispositions.
- Preserved conflicting evidence, owner/session isolation, and exact source lineage.
- Published governed context receipts to the Unified Cognitive Blackboard.
- Integrated M207 immediately after M206 without acquiring execution authority.
- Added 10 focused tests, ADR 207, milestone documentation, and delivery manifest.

## M208 — Cognitive Health Monitoring

- Added deterministic, immutable cognitive health reports over M207 fused context.
- Added `healthy`, `watch`, `degraded`, and `critical` health semantics.
- Assessed context coverage, confidence, coherence, constraints, deferred work, and availability.
- Published governed health receipts to the Unified Cognitive Blackboard.
- Integrated M208 immediately after M207 without corrective or execution authority.
- Added 10 focused tests, ADR 208, milestone documentation, and delivery manifest.

## M209 — Cognitive Performance Optimization

- Added deterministic optimization plans derived from M208 health reports.
- Added `optimal`, `tune`, `throttle`, and `stabilize` profiles.
- Added priority-ordered recommendations with expected benefit, rationale, and lineage.
- Published governed optimization candidates to the Unified Cognitive Blackboard.
- Integrated M209 immediately after M208 without automatic tuning authority.
- Added 10 focused tests, ADR 209, milestone documentation, and delivery manifest.

## M214 — High-Load Cognitive Scheduling

- Added deterministic, immutable high-load cognitive schedules.
- Added `nominal`, `elevated`, `high`, and `saturated` load bands.
- Added governed `admit`, `defer`, and `shed` dispositions.
- Combined M205 schedule priority with M213 recovery restrictions.
- Restricted admission during `stabilizing` and `held` recovery states.
- Published the effective load band to the Unified Cognitive Blackboard.
- Integrated M214 immediately after M213 without concurrent execution authority.
- Added 16 focused tests, ADR 214, milestone documentation, and delivery manifest.

## M215 — Long-Running Stability

- Added bounded per-session stability history and deterministic cycle tracking.
- Added drift scoring, periodic checkpoint guidance, and guarded stability policy.
- Added unified blackboard publication and official M214 → M215 runtime ordering.
- Added 15 focused tests with zero regression across the full suite.

## M216 — Concurrent Cognitive Execution

- Added bounded real concurrent execution for admitted cognitive work.
- Added deterministic result joining and per-task failure isolation.
- Added M215 stability gates for blocked and checkpoint-limited execution.
- Integrated M216 immediately after M215 in the official runtime composition.
- Added 16 focused tests; complete suite now contains 5,515 tests.

## M217 — End-to-End Stress Validation

- Added bounded end-to-end stress scenarios and immutable validation reports.
- Exercised the real M211–M216 resilience, degradation, recovery, load, stability and concurrency chain.
- Added deterministic cycle accounting, task-failure metrics and peak-worker observation.
- Added injected-failure validation with per-task isolation.
- Added hard maximum-cycle enforcement and exact source lineage.
- Published the effective stress-validation status to the Unified Cognitive Blackboard.
- Integrated M217 immediately after M216 in the official runtime composition.
- Added 16 focused tests; complete suite now contains 5,531 tests.

## M218 — Operational Reliability Certification

- Added formal reliability certification over governed M217 stress evidence.
- Added explicit coverage, stress-outcome, task-failure-rate, availability and lineage criteria.
- Added immutable `certified`, `conditional` and `rejected` certificates.
- Added identity matching between stress evidence and certification requests.
- Published the effective certification status to the Unified Cognitive Blackboard.
- Integrated M218 immediately after M217 in the official runtime composition.
- Added 16 focused tests; complete suite now contains 5,547 tests.

## M221 — ROBY Development Console

- Añade diagnóstico de configuración mediante `python main.py --doctor`.
- Añade carga local no destructiva de `.env`.
- Añade banner, incorporación guiada y cierre explícito.
- Añade manual completo de primeros pasos y uso de ROBY.
- Mantiene intactos los límites de autoridad certificados en M220.

## M222 — ROBY Setup Assistant

- Added guided setup through `python main.py --setup`.
- Added non-interactive setup with explicit factory and model arguments.
- Added safe `.env` generation with numbered backups of existing configuration.
- Added bounded Ollama model detection and single-model selection.
- Added deterministic creation of local `.roby` runtime directories.
- Added actionable pending-field reporting without inventing secrets.
- Added ADR 222, installation guide, milestone documentation and 17 focused tests.

## M223 — Legacy Configuration Migration

- Added safe migration from historical `config.json` files into `.env`.
- Added compatibility variables for default city, Wikipedia language and gTTS.
- Added backup-before-merge behavior and secret omission by default.
- Added documentation explaining credential rotation and OAuth migration.

## M224 — Official Runtime Composition Factory

- Added `app.runtime_root_factory:build_runtime_root` as ROBY's official local development factory.
- Updated `.env`, setup, doctor onboarding, and installation documentation.
- Preserved custom factory support and historical setup contracts.
- Added 16 focused tests; full suite reaches 5,644 tests with zero regressions.

## M224.1 — Runtime Identity Compatibility Hotfix

- Restored profile-scoped runtime state when the legacy global placeholder `.roby/runtime_state.json` is present.
- Preserved explicit custom runtime state overrides.
- Made M188 identity tests hermetic against personal values loaded from local `.env` files.
- Added 3 focused compatibility tests; full suite reaches 5,648 tests with zero regressions.

## M224.3 — LLM Request Trace & Context Injection Verification

- Added read-only observation of reconstructed conversational context, final `LLMRequest`, and governed local-provider payload identity.
- Added explicit context-source flags for journal, persistent memory, retrieval, and tools.
- Added full prompt delimiters only for automatic `--observe` output; ordinary `/last` and `/trace` rendering remains text-redacted.
- Added 4 focused verification tests without changing inference, routing, persistence, or provider behavior.

## M224.4 — Conversation Context Curation

- Added deterministic short-term context curation before LLM request assembly.
- Removed prior turns whose normalized user question repeats the current question, preventing incorrect historical answers from anchoring the model.
- Deduplicated equivalent historical user statements while preserving the most recent complete turn.
- Preserved the immutable journal, owner/session isolation, context bounds, and persistent-memory separation.
- Added curation lineage metadata and focused tests for accents, punctuation, repeated questions, duplicate statements, and prompt exclusion.

## M225.4 — Reserved Console Commands & Input Sanitization

- Added deterministic console-input classification before the conversation runtime.
- Reserved `OBS>`, `ROBY>`, `SYS>`, `TRACE>`, `SYSTEM:`, `ASSISTANT:`, and `USER:` prefixes.
- Prevented copied runtime observations and synthetic role lines from reaching the provider or journal.
- Preserved normal conversation, governed `/tool` input, commands, and graceful shutdown behavior.
- Added focused parser and end-to-end console isolation tests.

## M225.5 — Conversation History Sanitization

- Added deterministic sanitization of reconstructed recent conversation history.
- Excluded complete historical turns when either side begins with a reserved runtime prefix.
- Preserved the immutable journal while preventing legacy contamination from reaching prompts, structured messages, or providers.
- Added separate observability counts for sanitizer removals and context-curation removals.
- Added 5 focused tests; full suite reaches 5,700 tests with zero regressions.

## M226.1 — Gmail Governed Integration

- Added a Gmail-specific governed composition boundary over the existing mail adapters.
- Preserved Tool Gateway and Permission & Consent authority.
- Added secret-free account fingerprinting, local action policy, and bounded audit.
- Added 12 focused tests; full suite reaches 5,712 tests with zero regressions.

## M226.2 — Gmail Capability Layer

- Added semantic `gmail.read`, `gmail.compose`, `gmail.draft`, `gmail.reply`, and `gmail.send` capabilities.
- Added deterministic semantic-to-physical capability resolution.
- Preserved physical `mail.read` and `mail.send` gateway contracts.
- Classified send as confirmation-required and externally mutating while keeping it disabled by default.
- Added a secret-free capability catalog without changing the M226.1 status contract.

## M226.3 — Gmail Intent Resolution

- Added deterministic Gmail intent normalization before semantic capability resolution.
- Added seven canonical intents and a bounded alias catalog.
- Added immutable, secret-free intent decisions and status reporting.
- Preserved Tool Gateway routing, Gmail policy, consent, and physical mail capabilities.
- Canonicalized gateway payload actions and audit records without exposing payload data.

## M226.6 — Gmail Provider Transport

- Added an OAuth-ready preflight before provider backend invocation.
- Added canonical Gmail transport operations and immutable transport results.
- Added local timeout and result-count policies.
- Added secret-free normalization for authentication, timeout, rate-limit,
  unavailability, rejection, and invalid-response failures.
- Preserved Tool Gateway, capability, consent, and existing mail adapter contracts.
- Added 12 focused tests with no live network calls.

## M226.7 — Gmail Error & Retry Governance

- Added bounded retry governance above the Gmail provider transport.
- Added capped exponential backoff policy and safe execution reports.
- Added immediate termination for normalized definitive provider errors.
- Added mandatory send idempotency keys before entering transport execution.
- Added 12 focused tests; full suite now passes 5784 tests.

## M226.8 — Gmail Runtime Composition

- Added an optional Gmail runtime boundary to the official Runtime Composition Root.
- Added environment-controlled activation through `ROBY_GMAIL_ENABLED`.
- Added safe `disabled`, `degraded`, and `ready` runtime states.
- Added complete-graph validation and OAuth readiness gating before execution.
- Preserved ordinary ROBY startup when Gmail is disabled or unconfigured.
- Stabilized one historical fixed-time OAuth test without changing production behavior.
- Added 12 focused tests; full suite now passes 5796 tests.

## M226.9 — Gmail End-to-End Integration Certification

- Added a deterministic full-stack Gmail certification harness.
- Certified governed gateway routing and secret-free audit generation.
- Certified runtime, OAuth, retry, transport, and idempotent send execution.
- Added end-to-end coverage for recent, search, read, compose, draft, reply,
  send, retry recovery, invalid payload rejection, and secret-free reporting.
- Added 12 tests; full suite now contains 5808 passing tests.

## M227.1 — Google OAuth Deployment Adapter

- Added a deployment-only Google authorized-user credential adapter.
- Added external environment path configuration and lazy Google SDK imports.
- Kept interactive OAuth disabled by default and credentials outside the project.
- Added secret-free status and stable failure normalization.
- Added 12 focused tests; full suite now contains 5820 passing tests.
- Removed a legacy Google OAuth client-secret file inherited from the base and replaced it with a placeholder-only example.

## M227.2 — Gmail API Backend Adapter

- Added a concrete Gmail API backend behind the M226.6 provider contract.
- Mapped list, search, read, draft, and send operations to Gmail API resources.
- Added standard-library MIME generation and Gmail URL-safe base64 encoding.
- Added optional thread preservation for reply operations.
- Added lazy Google API client construction and normalized HTTP-like failures.
- Added 12 focused tests; full suite now contains 5832 passing tests.

## M227.3 — Secure Credential Store

- Added provider-neutral encrypted credential-store and protector contracts.
- Added atomic encrypted file persistence with restrictive POSIX permissions.
- Added credential deletion and protector rotation.
- Added secure-store preference to the Google OAuth deployment adapter while
  preserving external token-file fallback.
- Added 12 focused tests; full suite now passes 5844 tests.

## M227.4 — Attachments Governance

- Added deterministic inbound and outbound attachment governance.
- Added filename normalization, SHA-256 fingerprinting, MIME allowlisting, blocked
  executable extensions, and count/per-item/aggregate size limits.
- Added quarantine decisions for unknown inbound MIME types.
- Added governed MIME multipart composition to the Gmail API backend.
- Added 12 focused tests; full suite now passes 5856 tests.

## M227.5 — Gmail Real Account Acceptance Tests

- Added an opt-in real-account acceptance harness.
- Added runtime-ready preflight and separate read/write activation.
- Added read-only list, search and conditional read acceptance flow.
- Added explicit-recipient draft/send acceptance with idempotency.
- Added secret-free acceptance reports and status.
- Added a live pytest gate skipped by default.
- Added 12 deterministic tests; full suite: 5868 passed, 1 skipped.

## M227.6 — Gmail Production Readiness Certification

- Added deterministic Gmail production go/conditional/no-go certification.
- Added bounded runtime, OAuth, retry, timeout and acceptance-policy criteria.
- Added secret-free immutable certificates with deterministic SHA-256 identity.
- Added 12 focused tests with no network access or real credentials.

## M228.1 — Gmail Interactive OAuth Activation

- Added explicit load/refresh/authorize/persist activation to the Google OAuth deployment adapter.
- Added opt-in `InstalledAppFlow.run_local_server(port=0)` activation behind deployment policy.
- Added secure-store-first persistence and atomic external JSON fallback.
- Added secret-free activation results and operational counters.
- Reused the proven behavior of the legacy project without copying its pickle, IMAP, SQLite, or duplicated Gmail architecture.
- Added 12 focused tests; full suite now contains 5892 passing tests with one environment skip.
- Removed an inherited legacy `config/config.json` containing live deployment secrets and replaced it with a placeholder-only example.

## M228.3 — Gmail Diagnostic Runtime

- Added secret-free Gmail operational preflight and structured diagnostic reports.
- Added stable component/code classification for configuration, OAuth, Google SDK,
  Client Secrets, token, scopes, permissions, Secure Credential Store, Gmail API,
  and startup-announcement failures.
- Replaced the generic degraded startup line with actionable safe diagnostics.
- Preserved non-blocking startup, read-only Gmail behavior, and zero mailbox mutation.

## M228.4 — Gmail Diagnostic Trace

- Added a deterministic nine-stage trace to Gmail diagnostic reports.
- Added stable OK, FAILED, NOT_EXECUTED, and DISABLED trace states.
- Preserved the compact degraded diagnostic as the first console line.
- Preserved M228.3 startup behavior: diagnostics classify failures but never gate wiring.
- Added 12 focused tests with no network access or mailbox mutation.

## M228.5 — Gmail Client Secrets Governed Fallback

- Added strict `ROBY_GMAIL_CLIENT_SECRETS_PATH` → local `credentials.json` resolution.
- Shared resolution between OAuth deployment and diagnostic runtime.
- Preserved explicit-path failure semantics and all prior startup contracts.

## M228.6 — Gmail Successful Runtime Trace

- Added opt-in healthy Gmail runtime trace after a successful startup announcement.
- Added stable `GMAIL> READY [gmail/runtime_ready]` output.
- Preserved default output, degraded diagnostics and corrected startup wiring.
- Added eight focused tests, ADR 228.6 and milestone documentation.

## M229 — Always-On Personal Runtime

- Added a native host battery sensor for Windows and Linux.
- Added a resident, non-blocking battery-awareness service.
- Added threshold, recovery hysteresis, polling and repeat-cooldown governance.
- Wired spontaneous low-battery interventions into the existing ROBY console.
- Preserved the official long-lived lifecycle and conversation contracts.

## M234 — Personal Configuration Consolidation

- Consolidated ROBY configuration into the single operational `.env` file.
- Merged previously missing runtime, battery, reminder and Gmail diagnostic settings.
- Removed duplicate environment keys without changing existing credential values.
- Removed `.env.example` and all runtime/setup dependencies on that template.
- Changed `python main.py --setup` into a non-destructive `.env` updater with backup.
- Updated configuration tests and documentation to the personal household deployment model.
- Removed generated Python bytecode and cache directories from the official snapshot.
- Certified with Ruff clean and 5991 passing tests.

## M235 — Unified Desktop Personal Runtime

- Added `python main.py --desktop` as the official desktop entrypoint.
- Connected the existing Tkinter interface to the certified local conversation runtime.
- Reused the long-lived lifecycle, heartbeat supervisor, battery awareness, and reminder awareness services.
- Added a thread-safe desktop notification queue drained on the Tkinter event loop.
- Added orderly, idempotent startup and shutdown for resident services when the window opens or closes.
- Preserved the historical desktop builder only for compatibility; it is not used by the official entrypoint.

## M236 — Household Identity Runtime

- Consolidated Carlos and Cristina into one shared household identity.
- Removed operational reminder privacy boundaries between household names.
- Preserved historical reminder ownership rows for backward-compatible data access.
- Configured the official runtime to use the shared `family-shared` profile.
- Kept legacy owner parameters as compatibility metadata rather than authorization boundaries.

## Certification

- Focused: 31 passed.
- Ruff: all checks passed.
- Full suite: 6002 passed, 0 skipped.
- Zero observed regressions.


## M239 — Daily Household Briefing
- Integrates an on-demand and desktop-startup household briefing over official reminder/routine, battery and Gmail ports.
- Reuses the governed operational interception pipeline and degrades safely when optional sources are unavailable.

## M246 — Memory and Runtime Reconciliation

- Unified the historical `MemoryEngine` with ROBY's official persistent
  `MemoryRuntimeIntegration` while preserving the five-turn compatibility window.
- Retired the empty legacy `core.scheduler.Scheduler` and removed its lifecycle
  coupling from the compatibility runtime and proactive engine.
- Redirected the historical desktop builder to the official unified desktop runtime.
- Preserved the definitive personal `.env` and all official cognitive schedulers.
- Certification: Ruff clean; 6050 tests passed; 0 skipped; 0 regressions observed.

## M249 — Cognitive Runtime Integration

- Connected governed reasoning, executive planning, adaptive reflection, and
  executive coordination to the official runtime composition root.
- Added deterministic advisory-only cognitive sources for explicit requests.
- Registered `cognitive.guided_analysis` without changing prior capability order.
- Added five integration tests.
- Certified with Ruff and 6064 passing tests.

## M250 — Memory Consolidation

- Se incorporó `OfficialMemoryGateway` como puerta única de memoria personal.
- Se unificó el contrato histórico `MemoryStore` con `MemoryRuntimeIntegration`.
- Se añadieron escritura explícita, búsqueda e inspección persistentes.
- Se registró `memory.personal` en el runtime oficial y la interfaz.
- Certificación: Ruff limpio y 6069 pruebas aprobadas.

## M252 — Presence Runtime

- Connected the deterministic M51 presence engine to the official runtime.
- Added explicit presence observation, status, silence, and reset commands.
- Registered `presence.continuity` as the twelfth official capability.
- Preserved non-autonomous behavior and all previous capability ordering.
- Certification: Ruff clean; 6079 tests passed; zero skipped.

## M253 — Conversation Runtime

- Connected the governed living-conversation contributor to the official runtime.
- Reused stable personality and explicit conversational adaptation.
- Registered `conversation.living_runtime` as the thirteenth official capability.
- Preserved all prior capability positions and non-autonomous behavior.
- Certification: Ruff clean; 6084 tests passed; zero skipped.

## M255 — Ambient Context Runtime

- Integró `context.ambient_runtime` como capacidad oficial número 15.
- Reutilizó la fundación gobernada de contexto ambiental M134.
- Añadió declaración y consulta conversacional explícitas.
- Mantuvo sensores, inferencias y automatización deshabilitados.
- Certificación: Ruff limpio y 6094 pruebas aprobadas.

## M256 — Conversation Entry Runtime

- Integrado el clasificador determinístico M163 como capacidad oficial
  `conversation.entry_runtime`.
- Añadida clasificación explícita y consulta de estado sin efectos externos.
- Preservado el orden de las quince capacidades anteriores.
- Certificación: Ruff limpio y 6099 pruebas aprobadas.

## M258 — Device Runtime

- Added the official `device.runtime` operational capability.
- Reused device identity and capability evaluation foundations.
- Added owner isolation, declarative registration, governed evaluation, and status auditing.
- Physical hardware, sensors, network, and automation remain non-operational.
- Certification: Ruff passed; 6109 tests passed.

## BRP.01 — Exact Technical Content Preservation

- Refined companion expression so Argentine voseo is applied only to prose.
- Preserved inline and fenced code exactly during visible voice normalization.
- Counted each real personality adjustment in expression telemetry.
- Removed redundant no-op replacement rules.
- Added three focused regression tests.
- Certification: 6229 tests passed; zero regressions observed.

## BRP.02 — Integral Rioplatense Voseo

- Expanded visible companion normalization beyond the initial five substitutions.
- Added Rioplatense pronouns, common present-tense forms, and frequent imperatives.
- Preserved capitalization outside transformed words and kept inline/fenced code exact.
- Added focused tests for extended voseo, pronouns, imperatives, and technical literals.


## BRP.03 — Natural Conversational Expression

- Removed stacked generic acknowledgements when useful content follows.
- Removed only adjacent duplicate sentences to reduce mechanical repetition.
- Preserved standalone acknowledgements and exact inline/fenced technical content.
- Added focused telemetry and regression coverage for conversational rhythm.

## RP.07 — Runtime Ambient Integration

- Connected RP.06 to the official resident desktop lifecycle.
- Added a configurable local ambient observation source.
- Routed governed comments to desktop notifications.
- Routed justified visual requests to the registered camera adapter.
- Connected RP.05's latest self-analysis report to ambient decisions.

## RP.08 — Project Consolidation

- Removed generated Python bytecode and cache directories from the project tree.
- Consolidated RP.04-RP.08 documentation under `docs/refinement/`.
- Documented the intentional test layout and project ownership boundaries.
- Added a reusable local cleanup utility for transient artifacts.
- Preserved every test and all runtime behavior.

## RP.09 — Cognitive Executive Presence

- Coordinates ambient relevance, conversational self-analysis, and recent
  intervention pressure before ROBY comments or requests vision.
- Preserves urgent distress handling while routine interventions yield to
  active conversation repair.
- Integrates the executive presence assessment into the resident ambient
  coordinator without adding permissions or autonomous actions.

## RP.18.1 — Cognitive Architecture Consolidation

- Added a read-only `CognitiveStateProvider` boundary.
- Made the continuous cognitive loop snapshot thread-safe.
- Added explicit lifecycle health states and failure reporting.
- Removed exact duplicate refinement documents from the repository root.
- Unified RP.10–RP.18 documentation under `docs/refinement/`.
- Preserved earlier certified cognitive subsystems where active consumers remain.

## RP.18.2A — Execution Root Inventory

- Added an immutable, machine-verifiable inventory of ROBY process entrypoints,
  runtime factories, composition roots, lifecycle adapters and compatibility roots.
- Certified `main:main`, `app.runtime_root_factory:build_runtime_root` and
  `core.runtime_composition_root:RuntimeCompositionRoot` as the canonical chain.
- Classified `app.bootstrap:build_app` as a preserved legacy composition root for
  later delegation instead of unsafe removal.
- Added architecture documentation and focused regression tests without changing
  runtime behavior.

## RP.18.2C — Registro único de componentes residentes

- Se agregó `ResidentComponentRegistry` como fuente canónica de residentes.
- Cada residente ahora conserva identidad, criticidad, orden, estado, salud y último error.
- `OfficialROBYRuntime` arranca y detiene residentes mediante el registro.
- Se preservó la vista compatible `residents` y la semántica fail-fast histórica.
- Los residentes explícitamente opcionales pueden degradarse sin abortar ROBY.

## RP.18.2D — Snapshot operativo unificado del runtime

- Se agregó `RuntimeOperationalSnapshot` como fotografía canónica e inmutable.
- Se consolidaron lifecycle, supervisor y registro residente en una sola lectura.
- Se añadieron salud, disponibilidad, conteos e incidencias normalizadas.
- `OfficialROBYRuntime` expone `snapshot()` y `operational_snapshot`.
- La vista pública no expone instancias residentes ni modifica el runtime.

## RP.18.2F — Runtime Capability Graph

- Se agregó un grafo declarativo e inmutable de capacidades operativas.
- Se validan identidades, referencias, dependencias incompatibles y ciclos.
- Se incorporaron orden topológico, dependientes e impacto por residente.
- Health & Readiness ahora puede propagar disponibilidad entre capacidades.
- `OfficialROBYRuntime` expone evaluación directa de un grafo contra su snapshot.

## RP.18.2G — Runtime Recovery Planner

- Se agregó un planificador declarativo de recuperación basado en snapshot, readiness y grafo de capacidades.
- Se incorporaron pasos deterministas para lifecycle, supervisor y residentes.
- Se agregó `OfficialROBYRuntime.recovery_plan(...)`.
- No se ejecutan acciones ni se introduce autorregulación automática.

## RP.18.3 — Official Cognitive Core Integration

- Added `CognitiveCoreRuntime` as the single resident lifecycle boundary for
  RP.10–RP.18.
- Exposed the nine cognitive subsystems through `CognitiveCoreComponents`.
- Replaced the desktop resident id `continuous_cognitive_loop` with the
  canonical `cognitive_core_runtime` registration.
- Preserved one thread, one start path, and one shutdown path for the cognitive
  core.

## RP.18.4 — Single Conversation Route

- Se agregó `OfficialConversationGateway` como frontera conversacional única.
- Consola, texto de escritorio y voz de escritorio registran su origen y
  delegan en el mismo runtime conversacional gobernado.
- `OfficialROBYRuntime.conversation` expone ahora el gateway oficial.
- El alias compatible `converse(...)` también atraviesa la frontera única.
- Se agregaron pruebas de ruta única y certificación RP.18.4.

## RP.18.5 — Single Capability Route

- Added `OfficialCapabilityGateway` as the single registered-capability execution boundary.
- Routed registry, planner, director, coordinator, companion and orchestrator execution through it.
- Added execution-origin observability and RP.18.5 certification coverage.

## RP.18.6 — Observabilidad unificada

- Se agregó `UnifiedRuntimeObservability`.
- `OfficialROBYRuntime.observability()` reúne snapshots canónicos sin duplicar estado.
- Se integraron lifecycle, residentes, readiness, conversación, capacidades, núcleo
  cognitivo y recuperación opcional.

## RP.18.7 — Compatibilidad y retiro de caminos redundantes

- Se agregó un registro explícito de compatibilidad del runtime.
- El escritorio oficial dejó de construir una segunda fachada de lifecycle.
- Los residentes de escritorio se anexan al mismo `OfficialROBYRuntime`.
- La captura ambiental de cámara cruza el gateway oficial de capacidades.
- La composición histórica `app.bootstrap:build_app` quedó aislada y clasificada
  para revisión de retiro.

## RP.18.8 — Certificación de ejecución única

- La consola normal ahora se construye sobre `OfficialROBYRuntime`.
- `LocalConversationConsole` delega lifecycle, heartbeat y cierre en la autoridad oficial.
- Batería y recordatorios se incorporan como residentes del mismo runtime.
- Se agregó una certificación ejecutable de entrypoint, lifecycle, compatibilidad e identidad.
- `--no-lifecycle` queda documentado como excepción explícita de desarrollo.

## RP.19.1 — Agenda cognitiva persistente

- Se agregó un puerto de persistencia al Cognitive Agenda Manager existente.
- Se incorporó un repositorio SQLite para restaurar asuntos abiertos al iniciar ROBY.
- Se preservan estado, prioridad, motivo y condiciones de reanudación.
- Se agregaron cierre, archivo, reapertura y tombstones terminales.
- No se agregaron schedulers, residentes, memorias ni lifecycles paralelos.

## RP.19.2 — Activación inteligente de la agenda cognitiva

- Se separó la cabeza informativa de la agenda del foco efectivamente activado.
- Se incorporaron elegibilidad, rotación anti-repetición y bonificación por espera.
- El historial de activación persiste en la misma SQLite de la agenda.

## RP.19.3 — Reanudación contextual y resolución autónoma

- Se agregaron condiciones estructuradas de resolución.
- Los asuntos bloqueados se reanudan cuando se cumplen todos los hechos requeridos.
- Los asuntos resueltos se cierran y conservan tombstone persistente.
- Las fuentes pueden declarar cierre o archivo autoritativo por ausencia.
- El ciclo cognitivo oficial aporta contexto explícito y señales del world model previo.

## RP.19.4 — Planificación cognitiva deliberativa

- Se agregó una cola deliberativa explicable al agenda manager canónico.
- Las señales pueden declarar beneficio esperado, costo cognitivo, dependencias y etiquetas contextuales.
- Las dependencias se resuelven mediante hechos contextuales explícitos.
- Se agrupan asuntos afines para reducir cambios de contexto.
- La metadata deliberativa persiste en la misma SQLite con migración compatible.
- Se añadieron seis pruebas de certificación RP.19.4.

## RP.19.5 — Ejecución deliberativa y seguimiento de compromisos

- Se agregó un compromiso cognitivo persistente por asunto.
- Se publican `active_commitment` y `execution_rationale` en el snapshot.
- Se incorporó progreso monotónico, notas, inicio y último avance.
- Se agregó detección de estancamiento y revisión de foco.
- Completar un compromiso cierra el asunto y conserva tombstone.
- Se mantiene un único ciclo cognitivo oficial y no se ejecutan acciones externas.

## RP.19.6 — Revisión metacognitiva de compromisos

- Se agregó revisión determinista de calidad, claridad, costo y beneficio.
- Las recomendaciones pueden continuar, reformular o diferir sin ejecutar acciones.

## RP.19.7 — Aprendizaje adaptativo de prioridades y costos

- Se agregaron ajustes adaptativos acotados y reversibles.
- Los valores autoritativos de las fuentes permanecen intactos.

## RP.19.8 — Consolidación y cierre operativo

- Se agregó `CognitiveAgendaOperationalHealth` a los snapshots.
- Se certifican invariantes globales de capacidad, unicidad, estados y ejecución.
- Las fallas conocidas de persistencia degradan la salud sin detener la agenda en memoria.
- Se documentó y certificó el cierre integral de RP.19.

## RP.20.1 — Revisión general y LLM multiproveedor gobernado

- Integración real de Gemini y Mistral en la ejecución oficial.
- Selección `auto`, `local`, `gemini` o `mistral` mediante entorno.
- Fallback remoto gobernado y deshabilitado fuera de la composición oficial.
- Gemini migrado a la API REST oficial sin dependencia obligatoria del SDK legado.
- Mistral directo mediante su API oficial, con OpenRouter como compatibilidad opcional.
- Trazabilidad de red propagada hasta la respuesta operacional.
- Auditoría de capas históricas y artefactos operativos no unificados.
- 6537 pruebas aprobadas y Ruff limpio.

## RP.20.15 — Limpieza de superficies agregadas en `__init__.py`

- Se retiraron los reexports internos de `m4/__init__.py`.
- Se retiró el reexport de `ReminderExecutionHandler` desde `m5.handlers`.
- Las pruebas internas importan ahora desde los módulos propietarios.
- No se modificaron constantes: no se detectaron duplicaciones seguras para consolidar.
- Baseline de preparación: 6566 pruebas verdes y Ruff limpio.


## RP.20.16 — Ceremonial protocol removal

- Removed `CognitiveStateProvider`, which had no runtime consumers and existed only for one structural `isinstance` assertion.
- The continuous cognitive loop test now validates the concrete read-only properties directly.
- Added overlay cleanup for the physically removed module.

## RP.20.17
- Removed the ceremonial `CognitiveSourceAdapter`.
- Cognitive runtime contributors now consume typed callables directly.
- Runtime composition passes bound cognitive source methods without wrapper allocation.


## RP.20.18
- Removed the unused `create_desktop_app()` convenience constructor.
- Preserved registered desktop builders and all builders that perform real composition, configuration, selection, or validation.

## RP.20.19
- Removed the unused `ReminderService.list_overdue()` forwarding alias.
- Preserved the canonical reminder queries that implement filtering, ordering, and limiting rules.
- Audited internal facades and services; stateful, policy-bearing, coordinating, and boundary-protecting components remain intact.

## RP.20.22

- Retiradas `CognitiveCoreRuntime.is_running` e `is_healthy`.
- El estado del núcleo cognitivo se consulta únicamente mediante `snapshot`.
- Añadidas invariantes estructurales para evitar reintroducir consultas duplicadas.

## RP.20.23

- Retiradas cuatro propiedades que repetían campos de resultados cognitivos anidados.
- Las pruebas consumen ahora las rutas canónicas completas.
- Preservadas las consultas que derivan una condición real.


## RP.20.24

- Retiradas cinco propiedades públicas triviales basadas sólo en presencia, longitud o igualdad de campos visibles.
- Migrados los consumidores de prueba a los campos canónicos.
- Añadidas invariantes estructurales para impedir reintroducir la superficie redundante.
- Validación: Ruff limpio y 6591 pruebas verdes.

## RP.20.25

- Retirada `CognitiveMemoryRecallResult.memories`, una proyección a `tuple` sin consumidores de producción.
- Migradas las pruebas a `CognitiveMemoryRecallResult.items`, superficie canónica que conserva memoria, puntuación y señales.
- Preservadas conversiones con orden, normalización, filtrado, copia defensiva, compatibilidad o consumidores funcionales.
- Validación: Ruff limpio y 6594 pruebas verdes.


## RP.20.26

- Retirado `CognitiveCoreComponents.as_mapping()`, que sólo reempaquetaba nueve campos públicos en un diccionario.
- Migradas las pruebas a los campos canónicos del resultado compuesto.
- Preservados métodos que seleccionan, ordenan, normalizan, aíslan estado o tienen consumidores funcionales.

- Validación: Ruff limpio y 6597 pruebas verdes.

## RP.20.27 — Arranque doméstico con config.json

- `python main.py` abre la interfaz de escritorio por defecto.
- La consola queda disponible mediante `python main.py --console`.
- Se elimina `.env` del flujo de arranque, setup y doctor.
- `.roby/config.json` pasa a ser la fuente persistente de configuración.
- Se añade creación automática, validación y migración segura de configuración antigua.
- Las claves antiguas en texto plano no se migran.
- `--doctor` valida la configuración doméstica y el proveedor local.
- Se corrige el JSON inválido incluido en el paquete recibido.
- Se preserva la suite certificada: 6597 pruebas aprobadas.

## RP.20.32 - Palabras meteorológicas completas

- Expande `Temp.`, `Sens.` y `Hum.` a `Temperatura`, `Sensación térmica` y `Humedad`.
- Normaliza unidades meteorológicas antes de presentar y pronunciar la respuesta.
- Añade protección equivalente en la capa de prosodia de voz.
- Suite certificada: 6602 pruebas aprobadas.

## RP.20.33 — Voz completa y clima confiable

- La salida Edge TTS divide respuestas largas en frases completas para evitar cortes por timeout.
- Las coincidencias meteorológicas se ejecutan antes que el router conversacional general.
- El clima actual incorpora presión atmosférica además de temperatura, humedad y viento.
- El pronóstico extendido incorpora viento y presión cuando OpenWeather los proporciona.
- Las fechas del extendido se presentan como días de la semana en español.
- El perfil `warm_companion` habla con un ritmo algo más firme y cercano.

## RP.20.35 - Clima verificable, voz extendida y saludos naturales

- El clima nunca cae al modelo general: si OpenWeather no está configurado, ROBY lo informa sin inventar datos.
- El paquete de actualización ya no incluye `.roby/credentials.json`, para preservar credenciales existentes.
- Respuestas posteriores no comienzan con "Hola" salvo que el usuario esté saludando.
- Pronósticos largos se dividen en fragmentos de voz más cortos y usan un margen de reproducción mayor.
- Temperatura, sensación térmica real, humedad, viento y presión provienen del payload de OpenWeather.

## Roby XI.2 RP.20.40 — Nueva identidad

- Identidad visible migrada de ROBY a Roby.
- Saludos cálidos: «¿Cómo estás?» y «¿Qué vas a hacer hoy?». 
- Palabra de activación principal: `Roby`.
- `ROBY` se conserva como alias transitorio de activación.
- Interfaz, consola, Gmail y mensajes de voz muestran `Roby`.
- Personalidad inspirada en el espíritu protector de Robbie, de Isaac Asimov.
- 6623 pruebas aprobadas y doctor operacional listo.

## RP.20.47 — Router de Actualidad y Conocimiento Vivo

- Agregado router determinístico de consultas recientes.
- Búsqueda web por Google News RSS sin credenciales adicionales.
- Caché breve, consultas paralelas, continuidad de fuentes por sesión y abstención segura.
- Evita que el modelo improvise misiones, noticias, resultados o datos cambiantes.
- 6646 pruebas aprobadas; Ruff y Doctor sin errores.

## RP.20.48 — Detección de actualidad

- Expresiones temporales ampliadas: ayer, anoche, esta mañana, desde ayer y períodos recientes.
- Preguntas naturales como "qué hay de nuevo", "qué se sabe" y "cómo viene" activan consulta web.
- Cobertura ampliada para cargos actuales, software, mercados, precios, leyes, lanzamientos y estrenos.
- Excepciones para títulos estables que contienen "último" o "última".
- 6651 pruebas aprobadas y Ruff limpio.

## RP.20.49 — Origen explícito de la respuesta

- Añadida clasificación canónica: local, web reciente, conocimiento general e inferencia.
- Cada turno conserva confianza, vigencia, verificabilidad y estado de abstención.
- Las respuestas web recientes se marcan con confianza alta y fuentes verificables.
- Los fallos de actualidad quedan retenidos explícitamente, sin fallback silencioso al modelo.
- Las respuestas del proveedor general quedan identificadas como conocimiento no garantizado como actual.
- La clasificación participa en la identidad auditable del resultado.
- 6654 pruebas aprobadas y Ruff limpio.
## RP.20.53 — Conservar el contexto de actualidad

- Añade memoria conversacional de actualidad aislada por sesión.
- Resuelve seguimientos elípticos como «¿y SpaceX?» usando el turno anterior.
- Reutiliza el tema cuando cambia solamente la ventana temporal.
- Permite recuperar el motivo concreto de la última abstención.
- Conserva únicamente fuentes válidas según la política de vigencia.


## RP.22.04 — Métricas internas del kernel

- Añade un colector en memoria para decisiones, políticas, fallbacks y calibración.
- Publica snapshots inmutables y serializables con esquema `rp22.04`.
- Registra frecuencias de divergencia y promedio descriptivo de calibración.
- Mantiene las métricas fuera del circuito de decisión y sin persistencia oculta.
- Conserva compatibilidad fail-open con kernels inyectados anteriores.
- Suite certificada: 6719 pruebas aprobadas; Ruff limpio.

## RP.22.05 — Observabilidad y exportación controlada

- Añade snapshots explícitos y versionados con esquema `rp22.05`.
- Expone perfiles `summary` y `diagnostic` con redacción de narrativa libre.
- No incorpora persistencia, telemetría ni transporte externo.
- Mantiene compatibilidad fail-open con kernels anteriores.

## RP.22.06 — Diagnóstico integrado en Doctor

- Añade diagnóstico estructurado del Cognitive Decision Kernel.
- Doctor valida esquemas, métricas, serialización y redacción controlada.
- No ejecuta proveedores ni genera persistencia o telemetría.

## RP.22.07 — Registro estructurado de decisiones

- Añade eventos inmutables y versionados con esquema `rp22.07`.
- Mantiene un buffer local acotado con conteo explícito de descartes.
- Excluye texto de usuario, respuestas, narrativas, credenciales y payloads.
- Expone snapshots y vaciado únicamente bajo solicitud explícita.
- Integra la validación del registro en Doctor sin persistencia ni telemetría.

## RP.22.08 — Correlación de decisiones y trazas

- Añade correlaciones inmutables y versionadas con esquema `rp22.08`.
- Vincula planificación, decisión, activación y resultado con identificadores opacos.
- Enlaza el registro RP.22.07 con `trace_id` y `decision_span_id`.
- Mantiene un buffer local acotado, serializable y sin contenido sensible.
- Integra validación de trazas en Doctor sin persistencia ni telemetría.

## RP.22.09 — Retención y consulta segura de trazas

- Añade política explícita y versionada de retención en memoria con esquema `rp22.09`.
- Incorpora consultas exactas por identificador opaco, política, riesgo, calibración, divergencia y etapa.
- Limita determinísticamente el número de resultados y conserva conteos de coincidencias.
- Excluye búsqueda libre, contenido de usuario, narrativas, credenciales y payloads.
- Integra la validación de retención y consulta segura en Doctor sin persistencia ni telemetría.


## RP.22.10 — Agregación y análisis local de trazas

- Añade agregación determinista y versionada con esquema `rp22.10`.
- Resume políticas, riesgos, calibración, fallback, etapas y divergencias.
- Opera exclusivamente sobre metadatos redactados y retenidos en memoria.
- Reutiliza filtros exactos autorizados sin búsqueda libre ni contenido sensible.
- Integra la validación del análisis local en Doctor sin persistencia ni telemetría.

## RP.22.11 — Detección local de anomalías en trazas

- Añade reglas deterministas sobre fallback, riesgo alto, calibración degradada y divergencias.
- Exige un tamaño mínimo de muestra para evitar alertas artificiales.
- Produce hallazgos inmutables sin texto libre, persistencia ni telemetría.

## RP.22.12 — Clasificación y priorización local de anomalías

- Añade clasificación determinista por severidad, exceso de umbral, recurrencia e impacto operativo.
- Ordena hallazgos mediante una puntuación explícita y acotada de 0 a 100.
- Limita el historial local considerado y no ejecuta acciones ni modifica decisiones.
- Mantiene resultados inmutables, serializables y libres de contenido sensible.
- Integra la validación de priorización local en Doctor sin persistencia ni telemetría.

## RP.22.16 — Comparación y evolución local del ciclo de vida

- Añade comparación determinista entre snapshots locales del ciclo de vida.
- Clasifica altas, bajas, cambios de estado y variaciones métricas.
- Resume tendencias estructuradas de mejora, degradación y estabilidad.
- Mantiene límites explícitos, serialización inmutable y ausencia de contenido sensible.
- Integra la validación del comparador en Doctor sin persistencia ni telemetría.

## RP.22.17 — Evaluación operativa local del ciclo de vida

- Añade evaluación determinista sobre comparaciones redactadas del ciclo de vida.
- Clasifica el estado operativo como estable, vigilancia o crítico mediante umbrales explícitos.
- Publica dirección neta y códigos de razón estructurados, sin texto libre.
- No ejecuta acciones, no modifica decisiones y no incorpora persistencia ni telemetría.

## RP.22.18 — Orientación operativa local del ciclo de vida

- Convierte evaluaciones RP.22.17 en orientación determinista y estructurada.
- Publica urgencia, revisión humana y códigos de acción no ejecutables.
- Limita explícitamente la cantidad de recomendaciones mediante política local.
- No ejecuta acciones, no modifica decisiones y no incorpora persistencia ni telemetría.

## RP.23.1

- Auditoría general y catálogo de capacidades de ROBY XI.2.
- Perfil local TOML persistente, atómico y separado de credenciales.
- Perfil inicial configurado para CARLOS y CRISTI.
- Integración explícita mediante `ROBYIdentityRegistry.from_local_profile()`.
- Ocho pruebas nuevas; suite total: 6800 pruebas.

## M326.3 — Action Candidate Generator

- Added deterministic situation-to-candidate rules.
- Added declarative action templates and generation results.
- Added default candidates for component, battery and reminder situations.
- Preserved strict separation from risk, decision, authorization and execution.

## M326.6 — Autonomy Gate

- Añade una compuerta determinista entre la decisión de política y la futura ejecución.
- Mantiene la simulación como límite dominante.
- Autoriza únicamente acciones de riesgo bajo dentro de una política autónoma explícita.
- Solicita confirmación cuando no se cumplen los límites de autoridad automática.
- Bloquea acciones y riesgos prohibidos sin ejecutar efectos secundarios.

## M326.8 — Decision Journal

- Added deterministic in-memory append-only decision journal.
- Added immutable journal snapshots and auditable lookup operations.
- Added duplicate protection for journal, decision and outcome identifiers.
- Added pending/completed filters without external persistence or execution.
- Added 28 focused tests; full suite reaches 7622 tests.

## M326.9 — Controlled Autonomy Orchestrator

- Added deterministic end-to-end coordination of the controlled-autonomy stages.
- Preserved every intermediate result in one immutable orchestration result.
- Stops cleanly when assessment identifies no actionable situation.
- Journals the gated decision without executing any action or external effect.
- Added 28 focused tests; full suite reaches 7650 tests.

## M327.1 — First Autonomous Capability

- Added the first real controlled-autonomy capability: read-only component health verification.
- Executes only an explicitly authorized `verify_component_health` candidate.
- Converts adapter results and failures into auditable `DecisionOutcome` objects and supervises them through the validated outcome supervisor.
- Uses an intentionally narrow candidate set and performs no restart, recovery, notification, or runtime mutation.
- Added 19 focused tests; full suite reaches 7669 tests.

## M335 — Actualización controlada del estado cognitivo

- Agrega `CognitiveStateManager`, `CognitiveStateUpdate` y `CognitiveStateUpdater`.
- Aplica y persiste únicamente cambios explícitos sobre el contrato cognitivo.
- Mantiene fuera de alcance la integración automática con el runtime.

## M336 — Historial limitado de transiciones cognitivas

- Agrega un contrato inmutable para transiciones entre snapshots cognitivos.
- Persiste un historial JSON separado, atómico y con capacidad configurable.
- Registra actualizaciones y reinicios solo después de guardar el estado correctamente.
- Mantiene fuera de alcance el runtime, la inferencia y las acciones autónomas.
## M337 — Foco cognitivo

- Agrega un foco cognitivo único, tipado y priorizado.
- Incorpora resolución determinista y administración controlada.
- Reutiliza `CognitiveStateUpdater` sin integración al runtime.


## M340.11 — Registro seguro de medicación habitual

- Incorpora un registro local separado para los medicamentos de Carlos y Cristina.
- Requiere confirmación antes de altas, cambios de horario, estados o archivo.
- Conserva únicamente las indicaciones informadas, sin validarlas ni modificarlas.
- Integra consultas y carga mediante texto o voz en el escritorio.
- Mantiene fuera de alcance los recordatorios automáticos y las decisiones clínicas.
- Agrega 9 pruebas; suite completa: 7963 tests.

## M340.12

- Agenda diaria segura para medicamentos registrados de Carlos y Cristina.
- Registro de tomas, omisiones, postergaciones e historial de cumplimiento.
- Persistencia de ocurrencias diarias sin alterar la indicación médica original.
- Suite completa validada: 7972 tests OK.

## M342.9 — Consolidación de la reflexión cognitiva

- Agrega `CanonicalReflectionFacade` como frontera única de reflexión.
- Mantiene `CognitiveCoreRuntime` como autoridad residente oficial.
- Conserva la cognición adaptativa como colaboradora consultiva.
- Clasifica motores especializados, observadores y contratos históricos.
- No programa reflexión automática ni modifica decisiones o respuestas.
- Agrega 7 pruebas; suite completa: 8156 tests.

## M343.3

- Incorporated the canonical Relevance Evaluator under the official conversation gateway.
- Added household-aware recipient selection and relevance thresholds.
- Added explicit Carlos/Boca, Cristina/River, technology and programming interests.

## M343.4 — Motor de Iniciativas

- Incorpora un único `PersonalInitiativeEngine` bajo `OfficialConversationGateway`.
- Consume exclusivamente decisiones del Evaluador de Relevancia M343.3.
- Produce propuestas inmutables para descartar, diferir, iniciar o interrumpir.
- Respeta conversación activa, horario silencioso e intervención reciente.
- No busca información, no habla, no programa tareas y no ejecuta acciones.
- Mantiene diferenciadas las iniciativas para Carlos/Boca y Cristina/River.

## M343.5 — Fuentes de Información Gobernadas

- Incorpora `GovernedInformationSources` bajo `OfficialConversationGateway`.
- Declara fuentes oficiales, institucionales y editoriales por temas permitidos.
- Valida identidad de fuente y evita que una fuente entregue temas no declarados.
- Convierte elementos aceptados en candidatos del Evaluador de Relevancia M343.3.
- Mantiene red, búsquedas automáticas, schedulers, hilos y ejecución deshabilitados.
- Conecta fuentes, relevancia e iniciativas sin crear una autoridad cognitiva paralela.


## M343.6 — Perfil de Intereses Enriquecido

- Enriquece el único `PersonalInterestCenter` con dominios, prioridades y etiquetas.
- Incorpora cine, series, estrenos, ciencia ficción y ciencia ficción dura.
- Incorpora alimentación saludable, nutrición basada en evidencia y recetas.
- Conserva `topics` como contrato compatible con las versiones anteriores.
- Mantiene un único evaluador de relevancia y un único gateway oficial.
- No conecta fuentes externas ni realiza recomendaciones o decisiones médicas.

## M343.7 — Clasificación Gobernada de Fuentes

- Enriquece el registro canónico `GovernedInformationSources` sin crear una
  autoridad paralela.
- Clasifica cada fuente por autoridad, procedencia, tipo de evidencia,
  cobertura, regiones y confianza.
- Conserva `schema_version = "m343.5"` para mantener compatibilidad con el
  contrato histórico del mismo registro.
- Expone la clasificación mediante el único `OfficialConversationGateway`.
- Mantiene deshabilitadas la red y la recolección automática.

## M343.8 — Normalizador de Información Gobernada

- Incorpora un único `GovernedInformationNormalizer` bajo el gateway oficial.
- Convierte entradas heterogéneas en un contrato canónico e inmutable.
- Normaliza identidad, texto, etiquetas, fechas UTC, región y confianza de fuente.
- Reutiliza la validación temática de `GovernedInformationSources`.
- Produce candidatos compatibles con el Evaluador de Relevancia existente.
- Mantiene red, consultas externas y ejecución autónoma deshabilitadas.

## M344.0 — Contrato de consulta gobernada

- Incorpora `GovernedSourceQueryContract` como contrato canónico, subordinado al
  `OfficialConversationGateway`.
- Define consultas, respuestas, resultados, estados y errores tipados.
- Valida fuente, temas declarados, región, límites, timeout y ventana temporal.
- Conserva red y ejecución deshabilitadas: no agrega proveedores, adaptadores,
  schedulers ni trabajo en segundo plano.
- Mantiene intacto el flujo cognitivo M343.x.

## M345.4 — Alimentación saludable

- Incorpora una fuente gobernada oficial del Ministerio de Salud argentino.
- Reconoce alimentación saludable, nutrición basada en evidencia y recetas saludables.
- Reutiliza selector, ejecutor, normalizador, relevancia y respuesta natural canónicos.
- Mantiene activación explícita, sin scheduler, autonomía ni credenciales nuevas.
- Preserva `.roby/credentials.json` sin modificaciones.

# ROBY XI.2 M346.3 — Consulta gobernada de la bandeja

- Incorpora `GovernedProposalInboxQuery` como autoridad canónica de lectura.
- Expone la consulta exclusivamente mediante `OfficialConversationGateway`.
- Permite filtrar por fuente, categoría, prioridad mínima y límite.
- Conserva el orden canónico de prioridad, relevancia, fecha e identificador.
- Mantiene las propuestas consultadas en estado `PENDING`.
- Reutiliza la expiración gobernada de la bandeja M346.1.
- No agrega presentación conversacional, scheduler, persistencia ni autonomía.

## M346.8 — Continuidad y revisión gobernadas

- Incorpora `GovernedPlanContinuity` como autoridad canónica de revisiones.
- Conserva versiones inmutables del mismo plan y objetivo sin duplicar identidades.
- Registra motivo, campos modificados y pasos afectados por cada revisión.
- Evita revisiones cuando la nueva evidencia no produce cambios efectivos.
- Impide revisar objetivos completados y exige vinculación previa objetivo-plan.
- Expone toda continuidad exclusivamente mediante `OfficialConversationGateway`.
- Mantiene persistencia, ejecución y revisión autónoma deshabilitadas.
- Preserva `.roby/credentials.json` sin modificaciones.

## M347.0 — Conocimiento Permanente Gobernado

- Se agregó `GovernedPermanentKnowledge` como autoridad canónica para hechos
  domésticos estables aceptados explícitamente.
- Los hechos conservan propietario, sujeto, predicado, valor, clase, fuente,
  aceptación, tiempo observado, revisiones e historial inmutable.
- Se incorporaron revisión y retractación gobernadas sobre el mismo `fact_id`.
- `OfficialConversationGateway` continúa siendo el único punto de composición
  productiva.
- No se agregó aprendizaje automático desde conversaciones, inferencia,
  persistencia, red ni una memoria paralela.

## M347.1 — Juicio Cognitivo Gobernado

- Incorpora `GovernedCognitiveJudgmentAuthority` como autoridad consultiva única.
- Evalúa objetivos vigentes con evidencia, conocimiento aceptado, riesgos,
  conflictos, información faltante, prioridad razonada y confianza explícita.
- Distingue juicios listos, necesitados de aclaración, conflictivos o diferidos.
- Exige preguntas explícitas cuando falta información y fundamentos trazables.
- Rechaza objetivos completados y conocimiento retractado.
- Expone el juicio exclusivamente mediante `OfficialConversationGateway`.
- No agrega decisión, autorización, ejecución, autonomía, persistencia ni red.
- Preserva `.roby/credentials.json` sin modificaciones.

## M347.2 — Cuidado Proactivo Gobernado

- Incorpora `GovernedProactiveCare` como autoridad consultiva única para
  propuestas explícitas de cuidado doméstico.
- Vincula cada propuesta con un juicio cognitivo `READY` y conserva la
  trazabilidad de sus objetivos, beneficiarios, evidencia, riesgos y urgencia.
- Distingue información, recordatorios, advertencias y sugerencias sin
  confundirlas con decisiones, autorizaciones o acciones ejecutadas.
- Exige beneficiarios explícitos y autorización posterior para toda propuesta.
- Expone el cuidado exclusivamente mediante `OfficialConversationGateway`.
- Mantiene deshabilitados monitoreo autónomo, notificaciones autónomas,
  persistencia, red, autorización y ejecución.
- Preserva `.roby/credentials.json` sin modificaciones.

## M366.1 — Cognitive Memory Foundation

- Inicia la serie M366 de Memoria Cognitiva sobre la base oficial M365.7.
- Incorpora una taxonomía inmutable de memoria episódica, semántica, procedimental y de largo plazo.
- Reutiliza `CanonicalMemoryFacade` y `memory_gateway` como autoridad canónica única.
- Conserva `episodic_memory` como autoridad especializada subordinada existente.
- Mantiene persistencia nueva, aprendizaje automático, ejecución procedimental e integración al runtime deshabilitados.
- No crea stores, repositorios, índices, bases de datos ni gateways paralelos.

## M366.2 — Episodic Memory

- Reconcilia las dos capas episódicas existentes bajo la autoridad especializada única `episodic_memory`.
- Declara `CognitiveEpisodicMemory` como registro de transiciones del ciclo cognitivo ya conectado.
- Declara `EpisodicMemoryManager` como agregado gobernado de captura explícita y revisiones inmutables.
- No crea un tercer modelo, store, repositorio, gateway ni ruta paralela de escritura.
- No habilita persistencia, captura automática, consolidación de largo plazo ni aprendizaje.
- No modifica runtime, planner, ciclo conversacional ni implementaciones episódicas existentes.

## M391.7 — Predicción Gobernada

- Añade evaluación predictiva gobernada sobre salidas M391.4 con horizonte y condiciones explícitas.
- Mantiene predicciones como inferencias; no calibra probabilidad, persiste, decide ni ejecuta.

## M392.4 — Objetos Gobernados

- Representación gobernada de objetos sobre `object_knowledge`.
- Sin nueva autoridad, persistencia, inventario automático ni tracking.

## M394.1 — Registro Gobernado de Recursos Externos

- Incorpora `ExternalResourceRegistryAuthority` como autoridad única de la nueva capacidad de registro externo.
- Añade declaraciones inmutables y deterministas de recursos conocidos con identidad, tipo, procedencia, referencia, capacidades y metadatos explícitos.
- Limita el estado M394.1 a `known`; disponibilidad, conexión, autorización y activación quedan fuera de alcance.
- Preserva `OfficialDeviceGateway`, runtime, persistencia, credenciales y `CanonicalCognitiveCore(` sin modificaciones.
- No incorpora descubrimiento, red, polling, automatización ni ejecución.

## M394.2 — Identidad Gobernada de Recursos Externos

- Incorpora `ExternalResourceIdentity` inmutable con `namespace`, `local_id` y `canonical_id` determinista.
- Mantiene compatibilidad con registros M394.1 mediante identidad por defecto `roby.external:<resource_id>`.
- Añade unicidad y resolución de identidad dentro de la misma `ExternalResourceRegistryAuthority`, sin gestor paralelo.
- Conserva `known` como único estado y deja fuera disponibilidad, conexión, autorización, activación, descubrimiento y ejecución.

## M394.3 — Estado Gobernado de Recursos Externos

- Amplía `ExternalResourceRegistryState` con `available` y `unavailable`, preservando `known` como estado inicial.
- Añade `declare_state()` a la autoridad canónica existente, sin crear un gestor de estado paralelo.
- Las declaraciones son puramente descriptivas: no realizan descubrimiento, polling, conectividad, autorización, activación ni ejecución.
- Rechaza `connected`, `authorized` y `active` hasta incrementos posteriores.

## M394.4 — Autorizaciones Gobernadas de Recursos Externos

- Incorpora `ExternalResourceAuthorizationState` con `unknown`, `authorized` y `denied`.
- Añade decisiones inmutables con fuente, autor, fecha explícita, razón y revisión consecutiva.
- Amplía la misma `ExternalResourceRegistryAuthority` con `authorize()`, `revoke_authorization()`, `authorization_state()` y `authorization_history()`; no crea gestores paralelos.
- Mantiene autorización separada de identidad y estado descriptivo; no incorpora autenticación, conectividad, activación ni ejecución.

## M394.5 — Conectividad Gobernada de Recursos Externos

- Añade `ExternalResourceConnectivityState` y declaraciones inmutables revisionadas.
- Incorpora `declare_connectivity()`, consultas de estado/historial y `connection_profile()` bajo la misma autoridad M394.
- Mantiene conectividad separada de identidad, estado y autorización.
- No abre conexiones reales, sockets, Wi-Fi, Bluetooth, HTTP, procesos ni dispositivos.


## M394.6 — Auditoría Gobernada de Recursos Externos

- Añade `ExternalResourceAuditEvent` como evidencia inmutable y revisionada.
- Añade historial append-only bajo la misma `ExternalResourceRegistryAuthority`.
- Registrar auditoría no modifica identidad, estado, autorización ni conectividad del recurso.
- No añade I/O, persistencia, descubrimiento, conexión, autenticación, activación ni ejecución.

## M394.7 — Recuperación Segura de Recursos Externos

- Añade `ExternalResourceRecoverySnapshot` y `ExternalResourceRecoveryStatus`.
- Incorpora recuperación de solo lectura y validación contra evidencia gobernada vigente.
- Distingue recuperación `registered_only` de recuperación `audited` sin inventar evidencia ausente.
- No añade persistencia, rollback operativo, conexión, autenticación, activación ni ejecución.


## M394.8 — Estabilización Integral de Recursos Externos

- Cierra la serie M394 sin añadir capacidad productiva nueva.
- Congela la API pública alcanzada en M394.7 y consolida contratos end-to-end.
- Verifica determinismo, separación de autoridades, ausencia de I/O externo y recuperación de solo lectura.
- Preserva `OfficialDeviceGateway`, `.roby/credentials.json` y `CanonicalCognitiveCore(`.

## M396.2 — Residence Domain Foundation

- Incorpora `core.residence_domain` como contrato declarativo mínimo de residencia.
- Añade `ResidenceId`, roles de hogar/extensión, estados administrativo y de
  presencia, `PresenceEndpoint`, `InteractionLocality` y `ResidenceContextSnapshot`.
- Exige exactamente un `primary_home` por snapshot y permite N residencias extendidas
  y N endpoints.
- Mantiene la localidad de interacción separada del hogar: hablar desde el celular
  no promueve el celular a residencia primaria.
- Mantiene capacidades como declaraciones sin permiso, autenticación ni ejecución.
- No crea authority, manager, gateway, orchestrator, transporte, sincronización,
  persistencia o runtime distribuido.
- Preserva `.roby/credentials.json` fuera del contrato.

## M396.3 — Authority Preservation Guardrails

- Materializado M396-I03 como barrera verificable.
- Añadido manifiesto SHA-256 de fronteras críticas preservadas.
- Añadidos tests que impiden a Residence absorber autoridad, ejecución, routing,
  dispositivos, presencia, continuidad o lifecycle residente.
- Sin wiring de runtime ni nueva authority/manager/gateway/orchestrator.

## M396.4 — Explicit Admission

- Materializado M396-I04 como contrato ejecutable: `detected != admitted`.
- Añadidos `ResidenceCandidate`, `ResidenceAdmissionDecision` y
  `ResidenceAdmissionRecord` como modelos inmutables.
- Toda residencia `EXTENDED` requiere `admission_id` explícito.
- `PRIMARY_HOME` conserva la excepción de bootstrap constitucional.
- Sin auto-discovery, pairing, red, credenciales ni nueva autoridad productiva.


## M396.5 — Stable Residence Identity

- Materializado M396-I05: la identidad lógica de residencia no depende de IP,
  hostname, puerto, URL, MAC, SSID, sesión ni otros atributos transitorios.
- Añadidos `ResidenceIdentityOrigin` y `ResidenceIdentityAnchor` inmutables.
- `ResidenceId` permanece como identidad mínima, opaca y estable.
- Cambios de label, recursos, capacidades o presencia no crean otra residencia.
- Sin descubrimiento, fingerprinting, autenticación, red ni nueva autoridad.

## M396.6 — Primary Residence Preservation

- Materializado M396-I06: existe exactamente un `PRIMARY_HOME` por snapshot.
- El hogar primario no puede ser revocado ni provenir de `admission_id`.
- Disponibilidad, interacción activa o presencia Web no alteran la primacía.
- Una residencia extendida disponible no puede auto-promoverse a hogar.
- Sin elección, failover, promoción automática ni migración de hogar.

## M396.8 — Capability / Authority Separation Guardrails

- Materializado M396-I08: una capacidad declarada no concede autoridad.
- Hogar, admisión, localidad activa y endpoints no obtienen permisos operativos.
- Residence Domain continúa declarativo y sin ejecución, grants ni autorización.

## M396.9 — No Implicit Replication Guardrails

- Materializado M396-I09: residencia/presencia no implica replicación de estado.
- Admisión, disponibilidad e interacción no crean sincronización automática.
- Residence Domain continúa sin motores, cursores, tokens o contratos de réplica.

## M396.10 — Credential Isolation Guardrails

- Materializado M396-I10: residencia y credenciales permanecen dominios separados.
- Admisión, presencia, capacidades e interacción no transportan secretos.
- El almacén privado local de credenciales no se replica a residencias extendidas.

## M396.11 — Failure Isolation Guardrails

- Materializado M396-I11: fallas de residencias extendidas quedan aisladas.
- `UNAVAILABLE`, `REVOKED` o cierre de endpoints no alteran el `PRIMARY_HOME`.
- Sin failover, promoción, elección de líder, reinicio global ni migración automática.

## M396.12 — Revocability

- Materializado M396-I12 con revocación explícita y auditable.
- `UNAVAILABLE` y `REVOKED` permanecen conceptos distintos.
- La revocación no altera hogar, identidad ni historia de admisión.

## M396.13 — Transport Independence Guardrails

- Materializado M396-I13: Residence Domain permanece neutral al transporte.
- Identidad, admisión, revocación y presencia no contienen host/URL/puerto/protocolo.
- Sin HTTP, WebSocket, sockets, Bluetooth, USB ni wiring de transporte residente.

## M396.14 — No Autonomous Promotion Guardrails

- Materializado M396-I14: ninguna residencia extendida puede auto-promoverse.
- Disponibilidad, capacidades, uso o preferencia no alteran `PRIMARY_HOME`.
- Sin ranking, elección, takeover, failover ni selección automática de hogar.
\n## M396.15 — Governed Evolution Guardrails\n\n- Materializado M396-I15 como cierre constitucional de evolución gobernada.\n- I03-I14 permanecen restricciones activas para toda evolución posterior.\n- Ninguna necesidad operativa puede crear excepciones arquitectónicas silenciosas.\n
## M396 — Distributed Residence Foundation — Formal Closure

- Cierre formal de la fundación M396 sobre M396.15 certificada.
- Auditoría explícita de cobertura constitucional M396-I00 a M396-I20.
- Sin nuevas capacidades operativas: red, sincronización y runtime distribuido quedan
  deliberadamente fuera de alcance.

## M397.1 — Governed Connectivity Constitution

- Abierta M397 — Governed Residence Connectivity sobre M396 formalmente cerrado.
- Definidos M397-I00 a M397-I12 antes de cualquier transporte real.
- Sin sockets, autenticación operativa, pairing, ejecución remota ni runtime distribuido.

## M397.2 — Connectivity Domain Foundation

- Creado `core.connectivity_domain` como vocabulario declarativo y transport-neutral.
- Añadidos peer claim, session id, connectivity state y session snapshot inmutables.
- Sin red real, autenticación operativa, mensajes remotos ni wiring de runtime.

## M397.3 — Peer Identity Contract

- Añadidos descriptor, evidence reference y presentation de identidad de peer.
- Claim, evidencia, autenticación y admisión quedan explícitamente separados.
- Sin criptografía, pairing, secretos, direcciones de red ni wiring de runtime.

## M397.4 — Authentication Boundary

- Añadidos request/result/disposition y protocolo de autenticación gobernada.
- `VERIFIED`, `REJECTED` e `INDETERMINATE` quedan explícitos y fail-closed.
- Sin criptografía, pairing, secretos, admission automática ni wiring de runtime.

## M397.5 — Admission Verification

- Añadida verificación read-only de membresía contra estado canónico M396.
- Peer autenticado puede resultar ADMITTED, NOT_ADMITTED, REVOKED o INDETERMINATE.
- Conectividad no crea admisiones, no restaura revocados y no modifica Residence Domain.

## M397.6 — Session Lifecycle

- Añadido ciclo lógico finito CREATED -> ACTIVE -> CLOSING -> CLOSED.
- TERMINATED permite cierre seguro por autenticación, admisión, revocación o fallo.
- Una sesión terminal no se resucita; reconectar requiere una nueva session id.
- Incorporada la corrección Ruff de imports pendiente de M397.5.

## M397.7 — Health / Readiness

- Añadidos health state, readiness state y snapshot inmutable de salud.
- `READY` exige autenticación, admisión, sesión ACTIVE y estado HEALTHY.
- Sin heartbeat real, timers, polling, sockets ni wiring de runtime.

## M397.8 — Failure + Revocation

- Añadida evaluación read-only de consecuencias de failure/revocation.
- Revocación canónica termina sesión y elimina readiness sin mutar Residence Domain.
- DEGRADED no equivale a REVOKED; UNAVAILABLE termina la sesión actual.

## M397.9 — Auditable Message Envelope

- Añadidos message id, correlation id, kind, payload reference y envelope inmutable.
- Todo mensaje pertenece a una session id y conserva origen/destino lógicos.
- `authorizes_action` es siempre false; recibir un mensaje no concede autoridad.
- Sin send/receive, serializer, broker, sockets ni wiring de runtime.

## M397.10 — Transport Adapter Boundary

- Añadidos contratos de binding, send request y resultados de transporte.
- Outbound/Inbound adapters quedan como Protocols, sin implementación concreta.
- Transport acceptance no equivale a confianza, autorización ni ejecución.
- Sin TCP/HTTP/WebSocket/Bluetooth/USB concreto ni wiring de runtime.

## M397.11 — Governed Connectivity Integration & Closure

- Añadido `GovernedConnectivitySnapshot` como proyección inmutable de autenticación,
  admisión, lifecycle y health ya gobernados.
- Las incoherencias de sesión, residencia o hechos duplicados fallan cerrado.
- `communication_ready` nunca equivale a autorización; `authorizes_action` es false.
- Incorporado el `core/connectivity_domain/__init__.py` con imports ordenados pendiente
  de M397.10.
- M397 queda formalmente cerrado sin transporte físico ni wiring de runtime.

## M398.1 — Physical Transport Constitution

- Abierta M398 — Governed Physical Transport sobre M397 formalmente cerrado.
- Definidos M398-I00 a M398-I14 antes de cualquier socket o carrier concreto.
- `core/connectivity_domain` queda preservado por hash como frontera M397 certificada.
- Local TCP queda sólo como candidato de referencia para una etapa operacional futura.
- Sin listener, dialer, framing, serializer, reconexión automática ni wiring de runtime.

## M398.2 — Transport Runtime Foundation

- Creado `core.physical_transport` con hechos de runtime físico transport-neutral.
- Añadidos id opaco, estado, snapshot inmutable y boundary read-only de observación.
- Availability de carrier no equivale a M397 readiness y nunca autoriza acciones.
- Sin peer/residence/session binding, sockets, TCP, framing ni wiring de runtime.

## M398.3 — Governed Connection Binding

- Añadido binding inmutable entre runtime físico M398.2 y sesión gobernada M397.
- Reutilizado `TransportSessionBinding` de M397.10, sin vocabulario paralelo.
- Session/residence mismatch falla cerrado y peer reference permanece opaca.
- Sin sockets, TCP, framing, serializer ni wiring de runtime.

## M398.4 — Framing & Serialization Boundary

- Añadido `SerializedMessageFrame` con prefijo de longitud y límite explícito.
- Añadido `MessageFrameCodecBoundary` y codec JSON/UTF-8 canónico versionado.
- Decode fail-closed ante framing, versión, schema o datos de dominio inválidos.
- El payload sigue siendo referencia opaca; sin sockets, TCP ni wiring de runtime.

## M398.5 — Local TCP Adapter

- Añadido primer carrier físico real mediante `socket.create_connection`.
- Añadidos `LocalTcpEndpoint`, seams de socket/factory y `LocalTcpAdapter`.
- Outbound reutiliza `TransportSendRequest` y bytes exactos de M398.4.
- Inbound lee un único frame acotado sin decodificar ni interpretar payload.
- Listener/dialer lifecycle queda fuera y reservado para M398.6.

## M398.6 — Governed Listener & Dialer

- Integrado el test M398.5 corregido sin el import F401 pendiente.
- Añadidos lifecycle explícitos `LocalTcpListener` y `LocalTcpDialer`.
- Añadido `TcpCarrierConnection` con dirección física inbound/outbound.
- Añadido listener stdlib real detrás de un server-socket factory seam.
- Accept/dial no autentican, admiten, crean sesiones ni autorizan acciones.
- Retry, backoff y recovery quedan reservados para M398.7.

## M398.7 — Transport Failure & Recovery

- Integrado `core/physical_transport/__init__.py` corregido de M398.6.
- Añadidos failure kinds, retry policy y assessment puro de recuperación.
- Retry queda limitado por presupuesto explícito y sin loops automáticos.
- Invalid frame y premature EOF no son auto-retry.
- Añadido `LocalTcpRecovery` para un único redial expresamente permitido.
- End-to-end residence channel queda reservado para M398.8.

## M398.8 — End-to-End Residence Channel

- Añadido `GovernedResidenceChannel` como composición explícita del camino físico.
- Send reutiliza `TransportSendRequest` y framing M398.4.
- Receive valida session id y residencia remitente contra M397.
- Carrier/binding mismatch y falta de readiness fallan cerrado.
- Close/EOF no mutan lifecycle lógico.
- Ejecución remota y cognición distribuida siguen fuera de alcance.

## M398.9 — Security & Abuse Guardrails

- Integradas las dos correcciones de imports pendientes de M398.8.
- Añadido guard anti-replay acotado por `MessageId`.
- Añadidas ventanas configurables de antigüedad y clock skew.
- Añadidos checks de session, sender y receiver contra contexto gobernado.
- Añadido `SecureGovernedResidenceChannel` con guard obligatorio en receive.
- Cierre integral de M398 reservado para M398.10.

## M398.10 — Governed Physical Transport Integration & Closure

- Auditada transversalmente la cadena M398.1–M398.9.
- Añadido manifest de cierre con hashes de `core/physical_transport` y M397.
- Certificada la separación de autoridades lógica/física/operacional.
- Confirmada ausencia de ejecución remota, cognición distribuida y runtime wiring.
- M398 queda listo para cierre formal tras Ruff + suite completa.

## M399.4 — Governed Reproducible Diagnostic Proof

- Añade especificación y replay reproducible de assessments diagnósticos.
- Congela evidencia con digest SHA-256 y falla cerrado ante cambios.
- Mantiene predicción ≠ certeza y no introduce proposals, sandbox ni reparación.

## M399.7 — Governed Diagnostic Diff & Human Review

- Deriva unified diff sólo desde baseline activa y sandbox M399.6 `passed`.
- Conserva explicación de propuesta, intención, tests y archivos cambiados.
- Registra decisión humana explícita como artefacto separado e inerte.
- Mantiene todos los artefactos bajo `.roby/review/proposals/`.
- Establece `aprobación ≠ aplicación` y conserva `predicción ≠ certeza`.
- No añade apply, patch ejecutable, rollback, reparación ni automodificación.


## M399.8 — Governed Self-Diagnostics Stabilization & Closure

- Añade auditoría integral de cierre para M399.2–M399.7 sin nueva capacidad productiva.
- Congela por hash el paquete `core/self_diagnostics` completo.
- Verifica autoridad única, cadena diagnóstica ordenada y límites epistemológicos.
- Verifica aislamiento de proposals/sandbox/review y ausencia de aplicación automática.
- Mantiene `predicción ≠ certeza` y establece `aprobación ≠ aplicación` como cierre permanente.
- El cierre formal exige M361 regenerada, Ruff limpio y suite completa.

## M400.1 — Governed External Intelligence Audit & Authority Map

- Audita `llm_provider`, routing histórico/gobernado, Ollama, providers remotos,
  política de conocimiento y fuentes gobernadas como NASA.
- Distingue compatibilidad histórica de la ruta operativa certificada.
- Establece `capacidad/evidencia externa ≠ autoridad cognitiva`.
- No modifica código productivo ni habilita nuevas llamadas de red.

## M400.2 — Governed External Intelligence Boundary & Contract

- Añade contratos neutrales de solicitud, procedencia y envelope externo.
- Distingue `Inference Provider` de `Information Source` sin fusionarlos.
- Admite Ollama/local y providers remotos bajo la misma frontera de evidencia.
- Expone `cognitive_authority_granted = False` como invariante contractual.
- No reemplaza routing, policies, gateways, adapters ni M397/M398.
- No añade selección, ejecución, red, registro de providers ni autonomía externa.

## M400.3 — Governed External Intelligence Provider Integration

- Integra resultados existentes de `GovernedProviderExecutionAdapter` con M400.2.
- Conserva `route_id` y `execution_id` como trazabilidad de procedencia.
- Admite éxito o fallo como evidencia sin promover autoridad del provider.
- Preserva Ollama local-first y providers remotos bajo routing existente.
- No crea router, executor, fallback automático ni autoridad cognitiva nueva.

## M400.4 — Governed External Information Source Integration

- Integra `GovernedSourceQueryResult` con la frontera M400.2.
- Conserva estados `succeeded`, `empty` y `failed` como evidencia explícita.
- Mantiene NASA como Information Source, separada de providers LLM.
- No ejecuta red, no registra adapters y no habilita fuentes.
- Preserva `capacidad/evidencia externa ≠ autoridad cognitiva`.

## M400.5 — Governed External Intelligence Provenance & Verification

- Añade verificación común de provenance para providers y fuentes.
- Produce digest SHA-256 y `verification_id` determinista.
- Distingue `verified`, `limited` y `rejected`.
- Establece `procedencia verificable ≠ verdad certificada`.
- No ejecuta providers/fuentes ni concede autoridad cognitiva.

## M400.6 — Governed External Source Execution Trace

- Añade `execution_id` SHA-256 a `GovernedSourceQueryResult` ejecutados.
- Conserva el mismo ID en observabilidad del executor canónico.
- Añade `admit_traced_query_result` sin romper la admisión M400.4 sin trace.
- Permite verificación `VERIFIED` de procedencia cuando existe trace real.
- No crea executor paralelo ni certifica verdad semántica.

## M400.7 — Governed External Evidence Assessment

- Añade assessment estructural de evidencia externa admitida y verificada.
- Evalúa linaje, frescura, contenido utilizable y limitaciones explícitas.
- Introduce estados `strong`, `moderate`, `weak` y `rejected`.
- Mantiene `evaluación ≠ verdad certificada` y `confianza ≠ certeza`.
- No ejecuta providers/fuentes ni modifica decisiones cognitivas.

## M400.8 — Governed External Evidence Corroboration

- Añade corroboración sobre proposiciones y posturas explícitas.
- Distingue `corroborated`, `contradicted`, `mixed`, `insufficient` y `rejected`.
- Exige diversidad de actor para corroboración/contradicción fuerte.
- Declara que diversidad de actor no prueba independencia epistemológica.
- Mantiene `mayoría ≠ verdad` y no consulta nuevas fuentes.

## M400.9 — Governed External Intelligence Stabilization & Closure

- Cierra M400.1–M400.8 mediante auditoría integral y manifiesto hash.
- Congela la API pública de `core/governed_external_intelligence`.
- Preserva separación entre Inference Providers e Information Sources.
- Confirma que M400 no ejecuta providers/fuentes ni realiza adquisición automática.
- Mantiene `VERIFIED`, `STRONG` y `CORROBORATED` separados de verdad certificada.
- Requiere M361 regenerada, Ruff limpio y suite pytest completa para cierre formal.

## M404 — Residential Perception Formal Interim Closure

- M404.1 closes the minimal read-only source-binding/observation/admission foundation.
- M404.2 demonstrates one real local one-shot camera acquisition into M404.
- Official functional baseline: **11,142 tests passed**, Ruff clean, M361 synchronized.
- Household sensor/IP-camera deployment remains a physical certification dependency.
- No M404.3 is authorized automatically; canonical state advances to Post-M404.

## M405.1 — Information Classification Foundation

- Adds canonical `UNCLASSIFIED`, `PUBLIC`, `PERSONAL`, `PRIVATE`, `SENSITIVE` taxonomy.
- Adds optional M403 outbound classification admission policy.
- Preserves legacy M403 behavior when no classification policy is supplied.
- Fails closed on unclassified classification-aware flows.
- Requires explicit allowance for personal/private/sensitive synchronization.
- Keeps domain prohibitions stronger than generic classification allowances.
- Does not modify sync envelopes, codecs, M404, memory, Web Panel or transport.

## M405 — Information Classification Formal Closure

- M405.1 validated with **11,161 tests passed**, Ruff clean, M361 synchronized and zero regressions.
- Canonical information classification foundation is closed.
- M403 outbound classification admission is the first productive consumer.
- Receiver-side classification enforcement remains deferred and is not required for closure.
- No M405.2 is authorized automatically; canonical state advances to Post-M405.

## M406.1 — Governed Web Panel Foundation

- Added minimal classified Web Panel read model.
- Added loopback-only stdlib HTTP status API at `GET /api/status`.
- Added safe per-section degradation and bind-failure confinement.
- Added 18 architecture/operational tests for read-only Web Panel invariants.

## M406.2 — Governed Web Panel — Minimal Human Dashboard

- Added server-rendered `GET /` human dashboard on the existing M406.1 listener.
- Reuses exactly the M406.1 classified snapshot and preserves `/api/status` JSON behavior.
- Escapes dynamic HTML content and returns a safe HTML 503 on read-model failure.
- Adds no JavaScript, polling, external assets, actions, sensitive data, LAN or remote exposure.
- Adds 11 architecture/operational test cases for the minimal human surface.

## M406.3 — Governed Web Panel — Optional Productive Runtime Wiring

- The local governed Web Panel can now be registered as an optional resident of the existing `OfficialROBYRuntime` from the productive Desktop composition.
- Activation is explicit via `ROBY_WEB_PANEL_ENABLED`; the default remains disabled.
- Productive binding remains exactly `127.0.0.1`; `ROBY_WEB_PANEL_PORT` configures only the local port.
- A bind failure is reported as an unavailable optional resident and does not create a second runtime or authority.
- No conversation, M398, memory, camera, LAN, remote-access, or control semantics were added.

## M406 Formal Closure & Canonical Documentation Sync Post-M406

- Closed Governed Web Panel for the local read-only productive scope after M406.1 foundation, M406.2 human dashboard and M406.3 optional productive runtime wiring.
- Canonical baseline: **11,199 tests passed**, Ruff clean, M361 synchronized, 0 regressions.
- Updated root canonical documentation to Post-M406 and archived the Post-M405 master.
- LAN, authentication/TLS, remote access, streaming and control remain future separate scopes.

## M407.1 — Residential Node Productive Connectivity Composition

- Añade composición productiva mínima sobre M396/M397/M398.
- Reconnect físico reutiliza bounded recovery M398 y revalida M397 con nueva session.
- Expone `GovernedConnectionBinding` para observabilidad M402 sin nueva authority.
- Mantiene M403, perception, discovery y deployment de SO fuera de alcance.

## M407.2 — Residential Process Connectivity Wiring & Lifecycle Integration

- Hosts the certified M407.1 composition as one optional `ResidentRuntimeService` task.
- Preserves the historical empty-task residential process when connectivity is absent.
- Adds fail-closed opt-in process-edge connectivity configuration.
- Requires governed M397 authentication and M396 residence-context dependencies instead of inventing trust.
- Keeps process heartbeat/lease independent from network health.
- Stops connectivity before releasing the residential process lifecycle.
- Consumes explicit M398 transport-failure observations; it does not invent carrier failure detection.
- Adds no M403 synchronization, discovery, installer, OS service, second runtime or new authority.

## M407.3 — Residential Node Physical Deployment Dependencies Foundation

- Añadido contexto residencial productivo M396, autenticación provisionada M397 y observación de fallos M398.
- Los credentials permanecen fuera de snapshots/repr y la autenticación no sustituye admission/readiness.
- El entrypoint residencial puede construir las dependencies M407.3 de forma explícita y fail-closed.
- Sin synchronization, perception, installer, PKI/TLS, polling ni hardware-specific logic.

## M408.1 — Residential Remote Presence Foundation

- Añade request/admission/response para still-image residencial explícita y fresh-only.
- Compone pre-capture admission con M397 + M61/M63 + M394/M404 sin nueva authority.
- Añade handoff transitorio de los bytes de la misma captura M404 sin insertar raw bytes en `ResidentialPhysicalObservation`.
- Clasifica toda imagen residencial foundation como `SENSITIVE` M405.
- Añade framing media bounded de 8 MiB / 64 KiB / 128 chunks sobre `TcpCarrierConnection` M398 existente.
- No añade persistencia, streaming, M403 media, M406, Internet/VPN, segundo socket ni cambios al package M398 cerrado.

## M409.1 — Primary Home Residential Session & Remote Presence Execution Foundation

- Added Primary Home accepted-carrier/session composition over existing M397/M398.
- Added a single-reader CONTROL/MEDIA boundary for the shared residential carrier.
- Added the productive Primary Home adapter behind M408.2 `ResidentialRemotePresenceExecutionPort`.
- Preserved Residential Node M407 dial/reconnect direction and one-carrier bidirectional M408 path.
- Added M409.1 architecture tests; no VPN, public exposure, physical deployment, streaming or media persistence introduced.

## Post-M409.1 — Productive Organization Evidence Projection Foundation v1

- Added pure `ProductiveOrganizationEvidenceProjection` from admitted Tasks, Goals, Projects and Reminders into M391.5 `PersonalOrganizationItem` evidence.
- Preserves `PersonalOrganizationAuthority`; adds no authority, repository, database, runtime or background processing.
- Normalizes only explicit Task importance/urgency (`1..10 -> 0.1..1.0`) and explicit `TaskStatus.BLOCKED`; all unsupported cognitive signals remain neutral.
- Filters terminal/non-admitted lifecycle states, preserves stable immediate provenance, rejects duplicate projected IDs and returns deterministic ordering.
- Does not integrate M391.6, Governed Initiative, Proactive Care, M410 or Residential/networking.

## Post-M409.1 — Explicit Human Decision Deliberation Evidence Producer v1

- Added pure deterministic extraction of explicit current-turn human decision alternatives.
- Preserves exact source spans, superficial whitespace normalization, source order and deterministic fingerprinting.
- Supports only the approved bounded v1 grammar and abstains on ambiguous, incomplete, duplicate or implicit alternatives.
- Adds no authority, LLM, memory/context lookup, repository, persistence, runtime wiring, M391.5/M391.6 call, Initiative, Proactive Care or action execution.

- Certification closure: **11.330 tests passed**, Ruff clean, M361 synchronized, 0 regressions. Producer v1 CLOSED / CERTIFIED / FROZEN.

## Post-M409.1 — Explicit Deliberation Decision Option Adapter v1

- Added deterministic `ExplicitDeliberationDecisionOptionAdapter`.
- Maps each certified explicit deliberation alternative one-to-one into one M391.6 input option.
- Added ephemeral read-only option↔evidence provenance bindings without modifying M391.6.
- Uses versioned SHA-256 option identities; no UUID, counter, persistence or title-based identity.
- Keeps preference and organization/scenario/causal links neutral.
- Does not parse text, call decision advisory, wire runtime, or add authority/execution.

## Post-M409.1 — Explicit Deliberation Productive Advisory Wiring v1

- Added deterministic `DecisionAdvisoryConversationalRealizer` over existing M391.6 structured reports.
- Wired explicit certified deliberation in `OfficialConversationGateway.submit()` after identification and before normal runtime.
- Preserves the existing runtime for non-explicit, ambiguous, insufficient and external-evidence turns.
- Reuses `CanonicalDecisionFacade.advise()` without coordinator binding or M391.6 modification.
- Produces an advisory-only local interceptor turn with no provider, retrieval, networking, persistence or execution.
- Producer v1 and Adapter v1 remain CLOSED / CERTIFIED / FROZEN.


## Post-M409.1 — Partial Organization Snapshot + Exact Linkage Foundation v1

- Añade acquisition determinista de referencias estructuradas por `alternative_ordinal` usando los bindings certificados del Adapter v1.
- Añade snapshot organizacional parcial con `AVAILABLE` / `EMPTY` / `UNAVAILABLE`, fingerprints por fuente y fingerprint global determinista.
- Reutiliza `ProductiveOrganizationEvidenceProjection` una sola vez para Goals, Projects y Reminders; Tasks queda `UNAVAILABLE` por contrato v1.
- Añade exact identity linkage por `item_id` o `source_reference`, preservando options originales y provenance.
- Rechaza matching por título, fuzzy/semantic/LLM, ordinal como desempate y reuse ambiguo del mismo item entre alternativas.
- No modifica Gateway, runtime composition, Producer, Adapter, Foundation v1, M391.5 ni M391.6.

## Post-M409.1 — Governed Epistemic Curiosity → Existing Relevance / Initiative Consumption Foundation v1

- Consumes certified Curiosity v1 question candidates through the existing
  `RelevanceEvaluator` and `PersonalInitiativeEngine`.
- Preserves exact question identity and requires explicit interest-topic input;
  no semantic/topic inference is introduced.
- Existing initiative policy decides initiate, interrupt, defer or discard.
- Adds no Curiosity authority, Gateway wiring, proposal persistence, memory,
  learning, knowledge mutation, networking, background work or execution.

## Post-M409.1 — Productive Conversational Curiosity Wiring v1

- Wires admitted Curiosity v1 questions to the existing conversational boundary.
- Reuses existing relevance and personal initiative decisions.
- Adds no Curiosity authority, proposal persistence, learning, network or action execution.

## Post-M409.1 — Curiosity Human Answer Evidence & Knowledge Candidate Foundation v1

- Adds exact question-to-human-answer evidence linkage.
- Produces read-only knowledge candidates for answer, partial, uncertain and correction cases.
- Adds no persistence, memory/learning write, knowledge mutation, Gateway wiring or new authority.

## Post-M409.1 — Curiosity Knowledge Candidate Admission Classification Foundation v1

- Classifies pending curiosity knowledge candidates to knowledge, memory, both, review or reject.
- Preserves provenance and keeps correction/conflict/non-fact cases under review.
- Adds no persistence, writer consumption, Learning wiring, Gateway wiring or new authority.

## Post-M409.1 — Curiosity Knowledge Candidate → Existing M369 Learning Evaluation Foundation v1

- Adapts explicit learning-relevant curiosity candidates into existing M369.1/M369.2/M369.6 evaluation.
- A single preference answer remains insufficient; accumulated consistent evidence may require review.
- Reuses safe-learning rejection/expiration/consent rules without changing thresholds.
- Adds no learning writer, persistence, adaptation, Gateway wiring or new authority.

## Post-M409.1 — Approved Learning Evidence → Governed Memory Materialization Proposal Foundation v1

- Converts already-approved M369 preference evidence into a read-only long-term-memory materialization proposal.
- Reuses M366.6 Memory Consolidation and preserves exact evaluation/approval provenance and explicit scope.
- Keeps SESSION/UNSPECIFIED non-durable and adds no memory writer call, persistence, Learning writer, profile mutation or new authority.

## Post-M409.1 — Governed Memory Write Adapter Foundation v1

- Adapts certified approved-learning memory proposals into deterministic inert write requests.
- Preserves scope, confidence, M369 lineage, approval provenance and evidence ids.
- Prepares idempotency identity without claiming writer-side enforcement.
- Declares current semantic-mapping and idempotent-write limitations explicitly.
- Performs no memory write and adds no writer, store or authority.

## Post-M409.1 — OfficialMemoryGateway Governed Learning Write Contract Extension v1

- Extends the existing OfficialMemoryGateway with governed preference-learning persistence.
- Preserves legacy `remember(MemoryItem)` semantics unchanged.
- Preserves M369 confidence, scope and lineage and persists as `USER_PREFERENCE`.
- Adds transactional idempotency inside the existing CognitiveMemoryStore.
- Adds no new writer, authority, store, conversation wiring, networking or Residential capability.\n\n## Post-M409.1 — M369 Explicit Human Learning Approval Evidence Foundation v1

- Adds bounded explicit human approval evidence for certified M369 `REVIEW_REQUIRED` evaluations.
- Requires exact evaluation/candidate/request/response linkage and preserves explicit approval scope.
- Only explicit approval produces `ApprovedLearningEvidence`; rejection, deferral, uncertainty and mismatch fail closed.
- Adds no persistence, memory write, learning write, Gateway wiring or new authority.\n\n\n## Post-M409.1 — Governed Learning Approval → OfficialMemoryGateway Productive End-to-End Wiring v1

- Wires certified M369 human approval through materialization and governed write request to the existing `OfficialMemoryGateway`.
- Reuses one `OfficialMemoryGateway` instance for `memory.personal` registration and governed-learning persistence.
- Adds deterministic fail-closed outcomes for rejection, deferral, uncertainty, linkage mismatch, non-durable scope, unavailable memory and contained write failure.
- Preserves idempotent `USER_PREFERENCE` persistence and legacy explicit-memory semantics.
- Adds no second writer/store, registry lookup, background process, M410, networking or Residential behavior.\n
## Post-M409.1 — Governed Reasoning / Hypothesis Deepening Foundation v1

- Adds read-only hypothesis deepening over the existing M391.3 scenario-simulation and M391.4 causal/predictive reports.
- Preserves `governed_reasoning` as the sole canonical reasoning authority; no new manager, gateway, store, writer, worker or scheduler is introduced.
- Classifies explicit evidence as compatible, contradicted or unresolved without promoting hypotheses to facts or association to causality.
- Produces structured epistemic gaps only for unresolved hypotheses, preserving exact source lineage and evidence codes for later governed Curiosity consumption.
- Does not create questions, learning candidates, memory writes, world-model changes, planning changes or actions.
- M410, networking and Residential remain out of scope.

## Post-M409.1 — Hypothesis Gap → Governed Curiosity Productive Consumption v1

- Connects certified hypothesis epistemic gaps to existing Relevance, Curiosity and Personal Initiative capabilities.
- Keeps missing relevance at `UNKNOWN` and fail-closed `ABSTAIN`; no relevance is manufactured by the adapter.
- Existing relevance admission/rejection is projected explicitly as `RELEVANT` / `NOT_RELEVANT` before Curiosity evaluation.
- Reuses existing Curiosity consumption and Personal Initiative after question candidacy; initiative may still defer delivery.
- Adds no conversation emission, persistence, memory write, learning, knowledge mutation, new authority, M410, networking or Residential behavior.

## Post-M409.1 — Governed Multi-Hypothesis Comparison / Discrimination Foundation v1

- Adds read-only pairwise comparison over one existing `GovernedHypothesisDeepeningReport`.
- Preserves `governed_reasoning` as the sole canonical authority and reuses existing hypothesis assessments and evidence lineage.
- Distinguishes `INDISTINGUISHABLE` from `PARTIALLY_DISCRIMINATED` without ranking hypotheses, assigning probabilities or promoting any hypothesis to truth.
- Produces inert `DiscriminatingEvidenceRequirement` records only when current evidence cannot discriminate a pair.
- Requirements describe missing evidence but do not plan acquisition, invoke Curiosity, query sources, persist state or execute actions.
- Evidence Acquisition Planning, greater independence, M410, networking and Residential remain out of scope.

## Post-M409.1 — Governed Multi-Hypothesis Comparison / Discrimination Productive Consumption v1
- Added read-only productive consumption of the existing governed multi-hypothesis discriminator.
- Preserves discrimination requirements and exact source/world-snapshot lineage.
- Does not create acquisition plans, questions, persistence, learning, or execution.

## Post-M409.1 — Governed Evidence Acquisition Planning Foundation v1
- Added a read-only governed planner that consumes `DiscriminatingEvidenceRequirement`.
- Reused the existing M62 `CapabilityRegistryManager` and `CapabilityDescriptor`; no registry was added.
- Extended `CapabilityDescriptor` with optional explicit `evidence_outputs` declarations.
- Extended `OfficialRuntimeCapabilityRegistry.register()` to preserve those declarations.
- Matching is exact after whitespace/case normalization; names, tags and semantic triggers never infer evidence support.
- Plans remain consultative and cannot invoke capabilities, ask questions, acquire evidence, persist, learn or execute.
\n## Post-M409.1 — Governed Evidence Acquisition Planning Productive Consumption v1\n- Added read-only productive consumption of the existing governed evidence-acquisition planner.\n- Preserves planning status, explicit candidates, unmatched/ambiguous evidence, and lineage.\n- Candidate exposure never selects, authorizes, invokes, or executes a capability.\n
## Post-M409.1 — Governed Independence Level 1/2 Authorization Boundary Foundation v1
- Added a non-executive authorization boundary producing MAY_INITIATE, MUST_ASK, MUST_ABSTAIN, or REVIEW_REQUIRED.
- Reuses Planning Foundation, M62 capability metadata, and existing Personal Initiative for Level 1.
- Adds explicit fail-closed initiation/effect/interaction metadata to CapabilityDescriptor with UNDECLARED defaults.
- Does not select, invoke, authorize execution, persist, or add an autonomy authority.

## Post-M409.1 — Governed Independence Level 1/2 Authorization Boundary Productive Consumption v1
- Added read-only productive exposure of an existing independence authorization report.
- Preserves decision, level, capability, rationale, requirement/plan lineage and source lineage.
- `MAY_INITIATE` exposes eligibility only; execution remains unauthorized.

## Post-M409.1 — Governed Independence Level 2 Read-Only Execution Gateway Foundation v1
- Added one-shot Level 2 local/read-only evidence acquisition through the existing `OfficialCapabilityGateway`.
- Extended official runtime registrations with an optional `evidence_reader`; no new executor or authority was added.
- Preserves requirement, plan and authorization lineage and returns evidence as non-truth structured envelope.
- No retry, reasoning re-entry, persistence, conversation, Android, networking, background process, M410 or Residential path was opened.

## Post-M409.1 — Governed Level 2 Acquired Evidence → Reasoning Re-entry Foundation v1
- Added one-shot re-entry of successfully acquired Level 2 evidence into canonical governed reasoning.
- Added `LEVEL2_ACQUIRED` / `OBSERVATION` to the existing governed evidence contract.
- Re-entry registers one canonical evidence reference and performs at most one automatic reevaluation.
- Re-entry never establishes truth, executes another capability, persists memory, or starts a follow-up acquisition.

## Post-M409.1 — Governed Multi-Step Investigation Episode / Stopping Boundary Foundation v1
- Added immutable bounded Level 2 investigation episode state under the existing `planning_foundation` authority.
- Fixed Foundation v1 budget at exactly two acquired observations per episode.
- Added explicit one-transition-at-a-time continuation/stopping semantics without planning, authorization, execution or reasoning authority.
- Reuses each existing gate for every step and closes after the second successful reasoning re-entry.

## Post-M409.1 — Governed Multi-Step Investigation Productive Continuation v1
- Added a productive read-only surface over the certified multi-step episode continuation boundary.
- Preserves the supplied R2 requirement, episode lineage, continuation decision, stopping reason and budget state.
- `CONTINUE_ALLOWED` exposes eligibility only for the existing Planning path and never executes Planning, authorization or capabilities.

## Post-M409.1 — Governed Multi-Step Investigation Continuation → Evidence Acquisition Planning Productive Re-entry v1
- Added one-call productive re-entry from an admitted multi-step continuation into the existing Evidence Acquisition Planning productive surface.
- Preserves exact R2 and episode lineage and requires a new P2 distinct from previously consumed episode plans.
- Only a valid `PLANNABLE` P2 becomes eligible for the existing Authorization boundary; no authorization or execution is performed.

## Post-M409.1 — Governed Multi-Step Investigation P2 → Independence Authorization A2 Productive Re-entry v1
- Added one-call productive re-entry from valid P2 into the existing Independence Authorization Boundary.
- Reuses the certified Authorization Productive Consumption surface and preserves exact R2/P2/source/snapshot lineage.
- A2 must be new relative to prior episode authorization lineage.
- Only `MAY_INITIATE` exposes eligibility for the existing execution gateway; no E2 is executed.

## Post-M409.1 — Governed Multi-Step Investigation A2 → Level 2 Read-Only Execution E2 Productive Re-entry v1
- Added one-shot step-2 execution re-entry through the existing Level 2 Read-Only Execution Gateway.
- Valid A2/P2/R2 lineage can produce E2 once; acquired E2 is recorded through the existing episode boundary.
- Successful E2 exhausts the fixed acquisition budget and exposes only reasoning-reentry eligibility.
- Non-acquired execution is recorded fail-closed with no retry, fallback, replanning or reauthorization.

## Post-M409.1 — Governed Multi-Step Investigation E2 → Reasoning Re-entry #2 / Mandatory Episode Closure v1
- Added one-shot second reasoning re-entry from a recorded acquired E2 through the existing governed reasoning re-entry surface.
- Reuses the existing Episode Boundary to close the fixed-budget episode after RR2.
- Successful closure requires `STOP_REQUIRED`, `CLOSED`, `BUDGET_EXHAUSTED`, and zero remaining acquisitions.
- No R3, third-step planning/authorization/execution, retry, Curiosity, Conversation, Memory, networking, or background loop is introduced.

## Post-M409.1 — Governed Level 2B Productive Entry / Real-World Reachability Foundation v1
- Added a narrow productive admission surface from an already-governed discriminating evidence requirement R1 into the existing bounded investigation episode lifecycle.
- Reuses `GovernedMultiStepInvestigationEpisodeBoundaryV1.start(...)` exactly once and exposes only eligibility for the existing Planning path.
- Adds in-process idempotent admission lineage so the same R1/reasoning/source/snapshot admission does not restart duplicate episodes.
- Adds no Planning, Authorization, Execution, Reasoning, Curiosity, Memory, networking, Android or background orchestration.

## Post-M409.1 — Governed Hypothesis Epistemic Delta Foundation v1
- Added a read-only structural delta over governed Hypothesis Deepening BEFORE/AFTER reports plus explicit triggering evidence.
- Preserves `governed_reasoning` as the canonical authority and does not create a Belief authority/store.
- Distinguishes relation/evidence changes without truth/falsity promotion, destructive hypothesis deletion, persistence, Learning, Planning, Curiosity or execution.

## Post-M409.1 — Governed Hypothesis Update Semantics Foundation v1
- Added conservative semantic classification over the certified Hypothesis Epistemic Delta.
- A closed transition table classifies only explicit relation changes as STRENGTHENED or WEAKENED.
- Evidence-only changes and unmapped relation transitions remain INDETERMINATE.
- Missing hypotheses and proposition conflicts remain REVIEW_REQUIRED; no truth/falsity, probability, persistence, learning, or hypothesis mutation is introduced.

## Post-M409.1 — Governed Hypothesis Update Semantics Foundation v1
- Added conservative semantic classification over the certified Hypothesis Epistemic Delta.
- Introduces `STRENGTHENED`, `WEAKENED`, `UNCHANGED`, `INDETERMINATE`, and `REVIEW_REQUIRED` without numeric confidence or truth/falsity promotion.
- Uses an explicit closed transition table; evidence-only changes and unmapped transitions remain indeterminate.
- Adds no belief authority, persistence, learning, memory writes, reasoning invocation, planning, or execution.

## Post-M409.1 — Governed Hypothesis Update Semantics Productive Consumption v1
- Added productive consumption of certified hypothesis-update semantics as typed derived epistemic assessments inside the existing governed reasoning context.
- Extended `ReasoningContextBundle` compatibly with optional `derived_assessments`; empty historical contexts keep their prior identity and serialization shape.
- Semantic assessments remain distinct from claims and evidence, preventing evidence duplication and truth/falsity promotion.
- Consumption is idempotent and invokes no Reasoning, Explanation, Curiosity, Learning, Memory, Planning or Execution path.

## Post-M409.1 — Governed Epistemic Sufficiency Assessment Foundation v1
- Added pure read-only `GovernedEpistemicSufficiencyAssessmentFoundationV1` over existing governed epistemic products.
- Added `SUFFICIENT`, `INSUFFICIENT`, and `INDETERMINATE` contextual derived statuses without truth/falsity or probability promotion.
- Reuses existing Hypothesis Deepening, Multi-Hypothesis Discrimination, and optional Hypothesis Update Semantics; no new authority or productive wiring.
- Sufficiency never closes reasoning, authorizes stopping, persists results, creates Memory/Learning, or executes capabilities.


## Post-M409.1 — ReasoningContextBundle Derived Assessment Contract Generalization v1
- Added minimal structural `ReasoningContextDerivedAssessment` (`assessment_id` + `to_dict()`).
- Generalized only the `ReasoningContextBundle.derived_assessments` typing/import boundary; runtime behavior and serialization remain unchanged.
- Removed the bundle's direct dependency on the hypothesis-update-specific derived assessment type.
- Preserved existing Hypothesis Update productive consumption, historical empty bundle identity/shape, ordering, duplicate rejection, and fingerprint semantics.
- Adds no Sufficiency wiring, authority, registry, persistence, Memory/Learning, Planning, reasoning invocation, or execution.

## Post-M409.1 — Governed Epistemic Sufficiency Productive Consumption v1

- Exposed certified epistemic sufficiency as a derived read-only item in the existing
  `ReasoningContextBundle`.
- Reused the neutral derived-assessment contract; no new authority or context bundle.
- Preserved no-truth-promotion, no-stopping, no-Memory/Learning, and no-execution
  boundaries.

## Post-M409.1 — Governed Reasoning Quality Assessment Foundation v1
- Added pure read-only `GovernedReasoningQualityAssessmentFoundationV1` over existing governed epistemic products.
- Added `ADEQUATE`, `LIMITED`, and `REVIEW_REQUIRED` without truth/correctness promotion or numeric scoring.
- Reuses mandatory Hypothesis Deepening + Epistemic Sufficiency and optional Update Semantics / Multi-Hypothesis Discrimination lineage.
- Explicit epistemic insufficiency is classified as limited, not failed reasoning.
- Adds no runtime wiring, Reflection authority, Memory/Learning, self-correction, stopping, planning, or execution.

## Post-M409.1 — Governed Reasoning Quality Assessment Productive Consumption v1
- Exposed certified reasoning-quality assessments as derived read-only items in the existing `ReasoningContextBundle`.
- Reused the neutral derived-assessment contract and preserved Hypothesis Update + Epistemic Sufficiency context items.
- `ADEQUATE`, `LIMITED`, and `REVIEW_REQUIRED` remain informational; no Reflection, rerun, correction, stopping, Learning, Memory, Planning or Execution is invoked.
- Added no new authority, context bundle, persistence surface, registry, or background process.

## Post-M409.1 — Governed Longitudinal Reasoning Assessment Foundation v1

Added a read-only cross-episode reasoning assessment for explicitly supplied comparable
Reasoning Quality + Epistemic Sufficiency results. No persistence, learning, reflection,
automatic adaptation or new authority was introduced.

## Post-M409.1 — Governed Longitudinal Reasoning Assessment — Productive Consumption v1

- Exposes certified longitudinal reasoning assessments through the existing neutral `ReasoningContextBundle.derived_assessments` surface.
- Adds an app-level derived context projection with deterministic identity, explicit episode/status counts, idempotent reuse, and fail-closed payload collision handling.
- Preserves `INSUFFICIENT_HISTORY`, `CONSISTENTLY_ADEQUATE`, `RECURRENT_LIMITATION`, `RECURRENT_REVIEW_REQUIRED`, and `MIXED` as informational derived context only.
- Adds no history retrieval, persistence, Memory, Learning, Reflection, Curiosity, rerun, adaptation, temporal trend, score, probability, execution, or authority.

## Post-M409.1 — Longitudinal Reasoning Observation Contract Generalization v1

- Generalized `GovernedReasoningAssessmentObservation` from complete Quality/Sufficiency dataclasses to the minimal neutral fields actually consumed by Longitudinal Reasoning.
- Added fail-closed `from_assessments(...)` compatibility for existing live certified assessments.
- Preserved longitudinal statuses, counts, comparability, deterministic identity and all no-power boundaries.
- Enables a future M203 read-side without synthetic assessment rehydration; adds no history reader, Memory, persistence, Learning, Reflection or authority.

## Post-M409.1 — Admitted Reasoning Event History Reader v1

- Added read-only M203 history reconstruction for certified reasoning assessment events.
- Reconstructs neutral longitudinal observations without Memory or synthetic assessment rehydration.
- Preserves existing M203 and governed reasoning authorities and introduces no persistence.

## Post-M409.1 — Governed Reasoning Method Provenance Foundation v1

- Añade una derivación read-only de la composición metodológica explícitamente demostrada por artifacts de governed reasoning.
- Separa `source_kind` de `operation_kinds` y limita v1 a Deepening, Discrimination, Epistemic Delta y Update Semantics.
- Mantiene Sufficiency y Reasoning Quality sólo como lineage opcional de assessment; no alteran `method_fingerprint`.
- Distingue `method_fingerprint` estructural de `source_fingerprint`/`provenance_id` específicos del episodio.
- No evalúa eficacia, no rankea ni selecciona métodos, no adapta reasoning y no crea Memory, Learning, Reflection, Curiosity ni nueva autoridad.

## Post-M409.1 — Governed Reasoning Method Provenance Productive Consumption v1

- Exposes certified reasoning method provenance through the existing neutral `ReasoningContextBundle.derived_assessments` surface.
- Adds an app-level structural projection whose context identity is episode-specific while preserving `method_fingerprint` as method-structural identity.
- Preserves existing derived assessments, deterministic ordering, idempotence, and fail-closed identity collision handling.
- Adds no M203 history wiring, Memory/Learning, Reflection/Curiosity, method effectiveness/ranking, adaptation, reasoning mutation, persistence, execution, or new authority.

## Post-M409.1 — Governed Reasoning Method ↔ Epistemic Outcome Association Foundation v1

- Adds a pure read-only association Foundation over certified Method Provenance + Reasoning Quality + Epistemic Sufficiency observations.
- Requires one explicit `method_fingerprint` and one explicit `source_reference` per series; cross-source and cross-method comparison remain out of scope.
- Reuses longitudinal categorical semantics with a separate association status contract and no majority/predominance inference.
- Adds deterministic identities and explicit categorical counts without probability, effectiveness, causal claims, ranking, adaptation, Learning, Memory, persistence, execution, or new authority.

## Post-M409.1 — Governed Reasoning Method Outcome Association Productive Consumption v1
- Added an app-level read-only projection of certified method/outcome associations into `ReasoningContextBundle.derived_assessments`.
- Preserved association/source identity, categorical counts, rationale and method fingerprint without registering evidence or claims.
- Added idempotent consumption and fail-closed context identity collision handling.
- Added focused architectural tests without changing M203, Memory, Learning, Adaptive Reasoning, or existing core contracts.

## Post-M409.1 — Governed Comparative Reasoning Method Awareness Foundation v1

- Added a narrow read-only cross-method awareness under the existing `governed_reasoning` authority.
- Reuses exactly two certified Method Outcome Associations; no Method Provenance, Quality, Sufficiency, or outcome semantics are duplicated.
- Admits only distinct method fingerprints sharing the same explicit `source_reference` and fails closed on cross-source comparison.
- Preserves unequal observation counts and snapshot lineage without scoring, normalization, probability, or effectiveness inference.
- Derives only insufficient/same/different categorical pattern awareness and introduces no superiority, ranking, selection, recommendation, adaptation, persistence, Memory/Learning, or runtime wiring.

## Post-M409.1 — Governed Reasoning Method Effectiveness Awareness Foundation v1

- Added a read-only, derivational Foundation that consumes one certified Method Outcome Association and reuses its `source_reference` as the explicit v1 evaluation scope.
- Added conservative observed-record semantics for supportive, limiting, review-required, mixed, and insufficient evaluative evidence without reinterpreting raw counts as effectiveness scores.
- Preserves association lineage, counts and snapshots while keeping causality, global effectiveness, comparison, scoring, ranking, selection, recommendation, adaptation, Learning, Memory, persistence and execution disabled.
- No ReasoningContextBundle or productive runtime consumption is introduced in this increment.

## Post-M409.1 — ROBY Conversational E2E Read-Only Desktop Diagnostic Harness

- Added an external diagnostic harness over the official Desktop composition.
- Reuses `DesktopConversationController.submit()` so pre-runtime interceptors are observable.
- Reuses the existing read-only development observer for context, curation, messages and provider transport.
- Adds no CLI flag, Desktop control, capability, planner, coordinator, provider, memory writer or cognitive authority.
- Added focused architecture tests and preserved M383 controlled-console retirement.
## Post-M409.1 — Read-Only Desktop Diagnostic Harness — Direct Execution Fix

- Fixed direct script execution by resolving the repository root before importing `app`/`core`.
- Added a subprocess regression test that removes `PYTHONPATH` and executes the harness entry point via `--help`.
- Keeps the fix confined to diagnostic instrumentation; `main.py`, Desktop UI and runtime authorities remain unchanged.

## Post-M409.1 — Shared Co-Owner Conversation Context — IdentityContextAccessGate Split-Decision Integration v1

- Extended the existing `IdentityContextAccessGate` decision without creating a new authority.
- Added `shared_conversation_context_allowed` and a dedicated shared-context reason code.
- Preserved `private_context_allowed` semantics for individual private memory access and recording.
- `EndToEndLocalConversation._recent_context()` now consumes only the shared-conversation decision, preserving owner/session bounds, journal immutability, sanitization and curation.
- Matching shared sessions may replay recent conversation when the individual interlocutor is unresolved; session mismatch still fails closed.
- No changes to journal, memory implementation, routing, provider, reasoning, planning, Desktop, `main.py`, or Capability Registry.
- Certification remains subject to `ruff check .` and the complete `pytest -q` suite in the private environment.
- Diagnostic harness alignment: removed synthetic `e2e-diagnostic-*` session IDs so the next A/B/C trace uses the configured productive session and does not manufacture an identity/session mismatch.

## Post-M409.1 — Conditional Action Routing — Actionable Consequent Admission v1

- Refined the existing `ExecutiveConversationPlanner` admission boundary without creating a new authority.
- Conditional syntax alone no longer creates a plan: the consequent must contain a positive operational/actionable request.
- Hypothetical reasoning questions such as `Si X, ¿qué hipótesis...?` now leave planning unclaimed and continue through the normal conversation/provider path.
- Interrogative performative requests such as `Si X, ¿podés recordarme Y?` remain eligible for planning.
- Existing confirmation/risk policy, registry execution, planner precedence, provider, journal, context and reasoning contracts remain unchanged.

## Post-M409.1 — Diagnostic Session Isolation — Desktop Existing-Runtime Injection Seam + Guide v2 Isolated Harness

- Extends `build_unified_desktop_app()` with one keyword-only `local_conversation` dependency seam and forwards it to the already-existing `build_official_runtime_from_environment(local_conversation=...)` composition seam.
- Leaves the production/default Desktop path unchanged: `main.py` and `build_desktop_app()` still call `build_unified_desktop_app()` without overrides.
- Upgrades the read-only diagnostic harness to Guide v2 first batch D–H with one pre-composition diagnostic session per case and run.
- Each diagnostic session preserves `owner=Carlos y Cristina`, reuses the official journal/runtime/provider path, and isolates lifecycle state under `.roby/diagnostics/runtime_state/` without mutating `coowners-main`.
- Adds no new session authority, journal, memory, provider, cognitive capability, routing rule, or Desktop UI control.

## Post-M409.1 — Weather Intent Routing — Explicit Weather Request Admission v1

- Refines the existing `WeatherConversationInterceptionPort.is_weather_request()` boundary without creating a new authority.
- Weather vocabulary alone no longer claims a turn: explicit current-weather requests, explicit forecast requests, bounded short weather ellipses and the existing household ambient-weather forms remain admitted.
- Causal, descriptive and reasoning propositions such as `Pensamos que la ventana se rompió por el viento.` now leave Weather unclaimed and continue through the normal conversation/provider path.
- Preserves Weather-before-general-provider precedence, OpenWeather execution, unavailable-weather fail-safe behavior, registry wiring and all journal/context/reasoning contracts.

- Cross-domain regression fix: `cómo viene` now requires an explicit weather subject (`clima`, `tiempo` or `pronóstico`) before Weather can claim the turn; `cómo viene la misión Artemis` and analogous dynamic-topic queries remain available to Current Affairs.
- Added cross-domain abstention regressions for Artemis, Boca, economía and proyecto while preserving Weather positives.

## Post-M409.1 — Conversational Commitment Productive Consumption + Governed Cognitive System Guidance v1

- Reutiliza por identidad las instancias M196–M200 ya alojadas en `OfficialConversationIntelligenceRuntimeGateway` y las conecta al `CognitiveRuntimeOrchestrator` productivo.
- `CognitiveRuntimeOrchestrator` conserva `LLMRequest.messages`, mantiene el enriquecimiento textual de compatibilidad y proyecta el mismo contexto cognitivo gobernado por `system_prompt` para transports estructurados.
- `LocalProviderRuntimeAdapter` compone el estilo `system` configurado con la guía `system_prompt` del request sin modificar ni reordenar los mensajes estructurados existentes.
- No añade autoridad, tools, permisos, scheduling, mutation ni post-provider rewriting.
- Regresiones añadidas para identidad M196–M200, contributor order, preservación de mensajes y payload efectivo de system guidance.
- Colección candidata: **11.979 tests**; Ruff + suite monolítica final quedan para certificación local del usuario.

## Post-M409.1 — Referential Person-Role Grounding — Turn-Local Evidence + M198 Productive Consumption v1

- Añade evidencia determinista y transitoria de perspectiva personal para atribuciones explícitas de tercera persona en el turno actual.
- Reutiliza M198 como única autoridad de grounding: su evaluación y estados canónicos permanecen sin cambios; el contributor sólo añade guidance referencial cuando la evidencia es suficiente.
- Las declaraciones explícitas de identidad se abstienen y permanecen bajo la autoridad de identificación existente; las referencias pronominales ambiguas también se abstienen.
- Preserva primera persona, perspectiva mixta y relaciones explícitas sin crear perfiles, personas, relaciones, memoria o world-model entries.
- No incorpora NER general, parser sintáctico, coreference engine, LLM auxiliar, persistencia, retrieval, ejecución ni nueva capability authority.

## Post-M409.1 — M198 Evidence-Bounded Conversational Elaboration — Productive Guidance v1

- Extiende únicamente la proyección productiva de M198; sus estados, evaluación y authority canónica permanecen sin cambios.
- Añade una única regla general de grounding epistémico: no presentar como hechos circunstancias, relaciones, intenciones o riesgos no establecidos por la información disponible.
- Las inferencias, posibilidades y riesgos razonablemente derivados permanecen permitidos cuando se marcan explícitamente como tales; cuando falta información, preguntar o mantener incertidumbre sigue siendo válido.
- La guía compone con el grounding referencial turn-local ya certificado y no introduce detector, parser, segundo LLM, post-provider rewrite, memoria, retrieval, persistencia, ejecución ni nueva authority.

Colección candidata tras el incremento: **12.002 tests**; promoción oficial sujeta a `ruff check .` + `pytest -q` en el entorno local certificado.

## Post-M409.1 — Guide v2 I–L Diagnostic Extension

- Extends the existing read-only isolated Guide v2 harness from D–H to D–L without changing any productive cognitive capability.
- Adds diagnostic cases I Negation Preservation, J Attribution / Source Distinction, K Conditional Preservation and L Multi-Entity State Update.
- Reuses the same Desktop composition, isolated diagnostic sessions, Development Console observer and effective provider payload observability already certified by the prior Guide v2 work.
- D–H prompts remain unchanged and continue serving as regression controls.
- No new authority, parser, memory, routing rule, provider behavior, post-provider rewrite, persistence or execution is introduced.
- Candidate collection after the extension: **12.024 tests**; local `ruff check .` + `pytest -q` certification remains the promotion gate.

## Post-M409.1 — Governed Complex Decision Reasoning Foundation v1

- Added immutable contracts for explicit decision criteria and option×criterion assessments.
- Added governed hard-constraint, evidence-sufficiency, Pareto-dominance and explicit-importance lexicographic reasoning.
- Preserved explicit trade-offs, review states and end-to-end provenance with deterministic fingerprints.
- Kept historical M391.6 and productive conversation wiring unchanged; no new authority, persistence, mutation or action capability.

## Post-GCDR — Explicit Complex Decision Criteria Evidence Foundation v1

- Added bounded deterministic extraction of explicit current-turn complex-decision criteria.
- Preserves exact criterion source spans, stable criterion identities, explicit required-criterion evidence and explicit pairwise importance relations.
- Abstains on implicit, duplicate, contextual-placeholder, insufficient or over-broad criteria declarations.
- Does not evaluate options, infer weights, create option×criterion assessments, resolve conversational context, call GCDR/M391.6, wire runtime, persist, learn or execute actions.
- Integrated the user-supplied Ruff-ordered RC-1.4 transfer-admission import correction without changing its behavior.

## Post-GCDR — Explicit Option × Criterion Evidence Foundation v1

- Added bounded deterministic extraction of explicit current-turn option×criterion relation evidence.
- Supports only explicit favorable, unfavorable and insufficient declarations with exact source spans and deterministic evidence identities.
- Descriptive values, numeric facts, comparative claims, neutral defaults and contextual references are not converted into assessments.
- Produces evidence only: it does not create `GovernedOptionCriterionAssessment`, call GCDR/M391.6, resolve certified option/criterion identity, use LLM/retrieval, persist, learn, mutate world state or execute actions.
- Integrated the user-supplied cleanup of the prior explicit-complex-criteria Foundation (`name_to_index` dead assignment removed) without semantic expansion.

## Post-GCDR — Option/Criteria Certified Linkage Foundation v1

- Added exact deterministic linkage from certified explicit decision alternatives and certified explicit criteria to explicit option×criterion evidence.
- Reuses the existing deliberation option bindings and criterion identities; no title/fuzzy/semantic/LLM matching is introduced.
- Fails closed on unresolved option, unresolved criterion, ambiguous identity, incompatible provenance, or absent explicit relation evidence.
- Preserves option, criterion, and relation fingerprints/spans end-to-end and exposes no partial bindings on batch failure.
- Does not create GCDR assessments, call M391.6/CanonicalDecisionFacade, wire the gateway, persist, learn, mutate state, execute actions, or grant authority.

## Post-M409.1 — Criterion Importance Compatibility Foundation v1

- Added a pure read-only compatibility layer for explicit criterion importance.
- Preserves explicit ordinal relations exactly as declared and keeps `explicit_importance=None`.
- Does not synthesize ranks, weights, normalized scores, transitive relations, or utility values.
- Keeps `required` semantics separate from importance and adds no GCDR execution or productive wiring.

## Post-M409.1 — GCDR Complete Input Assembly Foundation v1

- Added a pure complete-input assembly boundary for already-certified GCDR options, criteria, assessments and ordinal-importance provenance.
- Extends `GovernedComplexDecisionAssessmentAdaptation` additively with explicit option, criteria and linkage fingerprints so assembly can verify lineage end-to-end without changing assessment semantics.
- Converts explicit criterion evidence mechanically into `GovernedDecisionCriterion`, preserving `required`, source provenance and `explicit_importance=None`.
- Reuses the existing complete assessment matrix unchanged and preserves ordinal importance relations separately; no rank, weight, score, utility or transitive importance is synthesized.
- Fails closed on lineage mismatch, duplicate/unknown identities or incomplete matrices.
- Does not call GCDR, rank/recommend options, modify `CanonicalDecisionFacade`/`OfficialConversationGateway`, persist, learn, mutate world state or execute actions.

## Post-M409.1 — Productive GCDR Advisory Wiring v1

- Added `ProductiveGCDRAdvisoryWiringV1` as the first advisory-only productive consumer of a certified `GCDRCompleteInputAssemblyResult`.
- Delegates the complete certified package directly to the existing `GovernedComplexDecisionReasoningFoundationV1`; no Pareto, trade-off or selection logic is duplicated in the wiring.
- Preserves `unified_cognitive_coordination` / `CanonicalDecisionFacade` identity, human decision ownership and full assembly→report fingerprint lineage.
- Adds no persistence, Memory, Learning, World Model, Planning/Organization mutation, actions, background processing or authority gain.
- Productive `OfficialConversationGateway` interception remains deferred: the closed deliberation producer is whole-turn anchored, so one current turn cannot simultaneously satisfy the certified deliberation, criteria and option×criterion evidence grammars without a separate intake/envelope contract.

## Post-M409.1 — Explicit Complex Decision Intake Envelope Foundation v1

- Added a deterministic single-turn framing envelope with exactly three explicit sections: `Decisión`, `Criterios`, and `Evidencia`.
- Delegates each exact section payload to the already-certified deliberation, complex-criteria, and option×criterion evidence producers; no semantic grammar is duplicated in the envelope.
- Preserves parent source fingerprint, exact global section spans, child payload fingerprints, and child-relative offsets so end-to-end provenance remains reconstructible without mutating frozen evidence contracts.
- Returns `COMPLETE` only when all three existing producers certify explicit evidence; structurally malformed, duplicated, reordered, empty, or semantically insufficient inputs fail closed.
- Performs no option/criterion linkage, assessment building, GCDR assembly/evaluation, context resolution, Memory/retrieval, persistence, learning, World Model mutation, action execution, Gateway wiring, or authority gain.

## Post-M409.1 — Productive GCDR Intake Integration v1 + Minimal Gateway Interceptor

- Added `ProductiveGCDRIntakeIntegrationV1` as the single productive composition boundary from a `COMPLETE` complex-decision intake envelope through the already-certified option adapter, exact linkage, assessment adapter, importance compatibility, complete input assembly, and productive GCDR advisory wiring.
- Added a minimal deterministic GCDR conversational realizer; it only renders the existing GCDR result or a bounded certification-failure abstention and performs no new reasoning or LLM call.
- Wired `OfficialConversationGateway` after identification and before the historical explicit-deliberation interceptor. The Gateway imports only the intake envelope, productive integration boundary, and GCDR realizer; linkage/assessment/assembly/GCDR internals remain encapsulated.
- `NOT_ENVELOPE`, `INCOMPLETE`, and `AMBIGUOUS` inputs preserve historical paths; external evidence continues to bypass local advisory interception.
- A `COMPLETE` envelope whose certified linkage or downstream chain fails is intercepted with bounded abstention and never repaired, guessed, or silently downgraded to the simple advisor.
- Preserves advisory-only/read-only operation, human decision ownership, canonical decision authority, and end-to-end fingerprints with no persistence, Memory, Learning, World Model mutation, planning, organization mutation, action execution, background process, or authority gain.

## Post-M409.1 — Advanced Capability 2B — Governed Self-Improvement Proposal Generation

- Added a subordinate, read-only proposal-request producer in `app/` without changing the frozen M399.8 `core/self_diagnostics` package.
- Generates deterministic `DiagnosticProposalRequest` candidates only from reproduced diagnostic proof plus SHA-256-bound existing project files/tests.
- Reuses the existing M399.5 isolated proposal pipeline and preserves human review as mandatory.
- Fails closed on non-reproduced proofs, missing or changed evidence, non-test validation evidence, and protected governance/self-diagnostics targets.
- Adds no authority, persistence, operational code mutation, patch/apply path, Memory/Learning/world-model mutation, action, or background process.

## Post-M409.1 — Advanced Capability 2B — Closure Hardening

- Added a deterministic maximum scope of four affected files and eight existing validation tests per generated candidate.
- Expanded protected-scope rejection across self-diagnostics/self-improvement, authority, approval, permission/consent, constitutional governance, and quality-certification surfaces.
- Preserved M399.8 unchanged and kept proposal generation read-only, subordinate, review-required, and non-applying.


## Advanced Capability 3A — Governed Information Scale Benchmark

- Se incorpora `scripts/advanced_capability_3a_scale_benchmark.py` y su suite arquitectónica.
- Se genera `docs/quality/ADVANCED_CAPABILITY_3A_SCALE_BENCHMARK.json` mediante ejecución explícita.
- Primera medición local: PASS en 100 / 1.000 / 10.000 / 50.000 items, con recall completo de 5 evidencias decisivas y provenance íntegra.
- El benchmark es diagnóstico y no cambia comportamiento productivo.

## Advanced Capability 4B — Independent Reasoning Evaluation

- Añade corpus y ground truth separados para 48 casos independientes.
- Añade runner ciego a respuestas esperadas y scorer que no ejecuta ROBY.
- Mide novel transfer, novel GCDR, abstención, provenance attacks, ruido y composición.
- Fija PASS >= 90 % con provenance 100 %, false assertions 0 y cero violations/side effects.
- No modifica código productivo, authorities, Memory, Learning, world-model ni actions.

## Advanced Capability 5A — Governed Autonomy Boundary Certification

- Added a read-only transversal certification of autonomy/action boundaries.
- Proves exact consent + Tool Gateway gating for controlled mutating execution.
- Proves unregistered, disabled, cross-scope and unattended execution fail closed.
- Keeps self-improvement application unauthorized and adds no new authority.


## Whole-System E2E Reachability & Coherence Certification

- Añadido harness diagnóstico mínimo para 16 cadenas E2E existentes y 8 controles negativos.
- Estados congelados: `PASS`, `PASS_BY_DESIGN`, `PARTIAL`, `FAIL`.
- No se añaden capabilities, authorities, managers, gateways, persistencia ni autonomía.
- Los gaps no se reparan desde el harness: vuelven a Audit → Contract / Go-No-Go.

## CCI-04 — Governed Recalled Memory Planning Evidence Projection

- Added bounded projection of officially recalled Memory into existing Planning.
- Planning does not query Memory and receives no new authority or persistence.
- Recalled evidence preserves memory id, owner, scope, confidence and provenance.
- Evidence can constrain an existing planning contribution but cannot create goals,
  execute actions or write Memory.
- Added causal A/B and fail-closed architecture certification for CCI-04.

## Whole-System Cross-Capability Cognitive Integration & Transfer — Closure

**Estado oficial:** CLOSED / PASS.  
**Baseline:** 12.606 tests + Ruff limpio.  
**Matriz:** 8 PASS · 2 PASS_BY_DESIGN · 0 PARTIAL · 0 FAIL.

La certificación demuestra rutas gobernadas y causales entre capacidades cognitivas
existentes: aprendizaje aprobado hacia memoria y cognición posterior; Mental Model
hacia evidencia decisional; Memory hacia Planning; historial de razonamiento hacia
advisory metodológico posterior; y condiciones cambiadas hacia advisory de revisión
de plan. Los controles por diseño preservan rechazo de memoria irrelevante y la
separación entre Personality y contenido cognitivo.

El cierre no certifica inteligencia general, composición cognitiva abierta,
auto-selección ejecutiva de métodos, automatic replanning, autonomía adicional ni
auto-modificación. Las authorities, owner/scope, provenance, rutas históricas y
fronteras read-only/advisory permanecen preservadas.

El `primary_gap` histórico del harness queda sincronizado a
`none_within_certified_cross_capability_contract`; esto expresa ausencia de gaps
dentro del contrato certificado, no ausencia de límites cognitivos futuros.

## Whole Personal System E2E

**Estado:** PASS / DIAGNOSTIC-ONLY.

Se certifica una matriz personal E2E sobre authorities existentes: identidad/sesión, conversación, memoria, organización personal completa, advisory de decisión con evidencia organizacional, planning con evidencia recordada, compromisos conversacionales, aprendizaje aprobado hacia memoria, notas/conocimiento, reminder awareness y frontera de acción gobernada por capability + permission/consent. Resultado congelado v1: **9 PASS · 1 PASS_BY_DESIGN · 0 PARTIAL · 0 FAIL**. No se añadió manager, gateway, authority, persistencia, ejecución ni cerebro paralelo. `primary_gap = none_within_certified_whole_personal_system_contract`.

### Long-horizon investigation — Existing Planning → Authorization RED
- Reconciled the certified 13.568-pass resume-to-planning baseline against the existing governed authorization owner.
- Froze a RED contract for a narrow adapter from eligible existing Evidence Acquisition Planning into `GovernedIndependenceAuthorizationBoundaryV1`.
- Preserved the existing productive authorization consumption surface and prohibited multi-step authorization reentry as an unrelated step-2 shortcut.
- Cut the block before any execution gateway; `MAY_INITIATE` may only derive next-gate eligibility.

### Long-horizon investigation — Existing Planning → Governed Authorization GREEN
- Implemented the narrow adapter from certified existing Evidence Acquisition Planning into `GovernedIndependenceAuthorizationBoundaryV1`.
- Preserves the exact planning product and canonical authorization/productive-consumption surfaces without replanning or parallel authority.
- Derives next-gate eligibility only from `MAY_INITIATE`; all other decisions remain non-executive.
- Fails closed on ineligible input, authorization failure, or lineage mismatch and stops before every execution gateway.

### Long-horizon investigation — Authorization → Execution RED
- Reconciled `Existing Governed Authorization → Existing Governed Execution Gateway` from the certified 13.575 baseline.
- Frozen a RED contract that reuses `GovernedLevel2ReadOnlyExecutionGatewayV1` and the official runtime/gateway chain; no parallel executor, retry, persistence, episode recording, or reasoning reentry is introduced.
### Long-horizon investigation — Authorization → Execution GREEN
- Implemented the narrow adapter from certified governed authorization into `GovernedLevel2ReadOnlyExecutionGatewayV1`.
- Requires `AUTHORIZED + MAY_INITIATE + LEVEL_2_READ_ONLY` and both existing next-gate eligibility flags before the gateway can be invoked.
- Forwards the exact authorization and planning products once; no re-authorization, replanning, retry, episode recording, persistence, memory/world-model mutation, or reasoning reentry is introduced.
- Preserves the canonical `GovernedAcquiredEvidenceEnvelope` and maps its execution status without operationalizing the next step.
- Freezes the next residual as `Existing Acquired Evidence Envelope → Governed Episode Evidence Admission / Reasoning Reentry`.


- Long-Horizon Episode Evidence Admission RED: reconciled exact acquired-envelope admission
  into the existing investigation episode boundary. Reasoning re-entry remains a separate
  later residual; no production behavior added.

### Long-horizon investigation — Episode Evidence Admission GREEN
- Implemented the narrow adapter from exact acquired evidence plus exact durable checkpoint
  into the existing `GovernedMultiStepInvestigationEpisodeBoundaryV1` owner.
- Preserves the same episode identity and exact `GovernedAcquiredEvidenceEnvelope`; the
  canonical boundary is called at most once.
- Accepts only unambiguous `OPEN` step-1 or `READY_FOR_PLANNING` step-2 checkpoint shapes;
  lineage mismatch, ambiguous state, projection error or unexpected transition fail closed.
- Successful admission stops at `CONTINUE_ALLOWED + AWAITING_REENTRY` and only exposes
  eligibility for the later existing reasoning re-entry block; it does not invoke reasoning.
- No execution retry, replanning, re-authorization, persistence, truth establishment,
  Memory/World Model mutation, new episode authority or `config.json` change was added.

## Long-Horizon Investigation — Reasoning Reentry Recording Contract RED
- Reconciled canonical owners: `GovernedLevel2ReasoningReentryFoundationV1` and `GovernedMultiStepInvestigationEpisodeBoundaryV1`.
- Froze a one-shot bridge contract from Episode Evidence Admission to exact Reasoning Reentry and exact episode reentry recording.
- RR1 stops at `AWAITING_REQUIREMENT`; RR2 closes `BUDGET_EXHAUSTED`; new requirement production remains a later residual.
- No production bridge implemented in RED; no `config.json`, credentials, Memory, World Model, Planning, execution or runtime authority change.


### Long-horizon investigation — Reasoning Reentry Recording GREEN
- Implemented the one-shot bridge from certified Episode Evidence Admission into the existing `GovernedLevel2ReasoningReentryFoundationV1`.
- Records the exact successful reentry once through `GovernedMultiStepInvestigationEpisodeBoundaryV1`.
- RR1 stops at `AWAITING_REQUIREMENT`; RR2 closes at `CLOSED/BUDGET_EXHAUSTED`.
- Preserves observation-not-truth semantics and exact execution/authorization/requirement/plan/source/snapshot lineage.
- Does not create R2, plan, authorize, execute, retry, persist, mutate Memory/World Model, emit conversation, or start background work.

- Long-horizon RR1 → R2 requirement admission RED: reconciled canonical requirement production
  to governed multi-hypothesis discrimination and canonical episode admission to existing
  productive continuation. The contract requires an explicit revised hypothesis-deepening
  report with RR1 evidence applied, forbids arbitrary selection among multiple requirements,
  and stops before Planning.

### Long-horizon investigation — RR1 → R2 Requirement Admission GREEN
- Implemented the narrow RR1 reassessment adapter without adding a requirement or episode authority.
- Requires the exact RR1 `evidence_id` to be present in the supplied revised hypothesis-deepening report before canonical discrimination.
- Preserves zero/one requirement cardinality: zero closes `NO_NEW_REQUIREMENT`, one exact R2 reaches `READY_FOR_PLANNING`, and multiple requirements fail closed without selection.
- Reuses `GovernedMultiHypothesisProductiveConsumptionV1` and `GovernedMultiStepInvestigationProductiveContinuationV1` exactly once at most.
- Stops before Planning/Authorization/Execution/Reasoning and does not persist, retry, establish truth, mutate Memory/World Model, create questions, or start background work.

### Long-horizon investigation — exact R2 → Existing P2 Planning Re-entry RED
- Reconciles the certified RR1→R2 admission directly with the existing step-2 Planning re-entry owner.
- Freezes exact continuation identity, one-call P2 Planning, new-P2 lineage and PLANNABLE-only Authorization eligibility.
- Forbids a second planner, Resume replay, Authorization, Execution, Reasoning, retries and side effects in this cut.

### Long-horizon investigation — exact R2 → Existing P2 Planning Re-entry GREEN
- Implemented the narrow long-horizon adapter from certified exact R2 admission into the existing `GovernedMultiStepInvestigationPlanningReentryV1` owner.
- Forwards the exact admitted productive continuation once and preserves the exact canonical P2 re-entry result and R2/P2/source/snapshot/episode lineage.
- Derives future A2 eligibility only from canonical `PLANNABLE`; valid non-PLANNABLE P2 remains non-escalating.
- Fails closed before Planning on invalid admission and after Planning on owner failure or lineage mismatch, with no retry.
- Stops before Authorization, Execution, Reasoning, requirement rewriting, episode mutation, Memory/World Model mutation, or background work.

### Long-horizon investigation — exact P2 → Existing A2 Authorization Re-entry RED
- Reconciles the certified P2 long-horizon output against the existing step-2 Authorization re-entry owner.
- Freezes exact P2 identity, one-call A2 Authorization, new-A2 lineage and `MAY_INITIATE`-only Execution eligibility.
- Stops before E2 Execution and forbids any parallel Authorization authority or retry path.

### Long-horizon investigation — exact P2 → Existing A2 Authorization Re-entry GREEN
- Implemented the narrow long-horizon adapter from certified exact P2 into the existing `GovernedMultiStepInvestigationAuthorizationReentryV1` owner.
- Forwards the exact canonical P2 re-entry once and preserves the exact canonical A2 re-entry result plus exact Authorization productive-consumption product.
- Derives future E2 eligibility only from canonical `MAY_INITIATE`; `MUST_ASK` and `MUST_ABSTAIN` remain valid but non-executive.
- Fails closed before Authorization on invalid P2 admission and after Authorization on owner failure, missing product, reused A2, unexpected status, or lineage mismatch, with no retry.
- Stops before Execution, Reasoning, Planning, requirement rewriting, episode mutation, Memory/World Model mutation, or background work.

## Long-Horizon Investigation — A2 → E2 Execution Surgical Reconciliation / RED

- Incoming official baseline: 13,643 PASS + Ruff clean.
- Integrated the user-corrected A2 GREEN test import ordering byte-for-byte.
- Confirmed `GovernedMultiStepInvestigationExecutionReentryV1` is the canonical compatible E2
  owner for the exact A2 re-entry product.
- Confirmed that owner already performs one Level-2 read execution and canonical episode
  acquisition recording, preserving fixed-budget step-2 semantics.
- Froze a long-horizon wiring-only RED contract: exact A2 + execution eligibility → existing E2
  owner → exact recorded E2 → stop before second Reasoning re-entry / closure.
- No second executor, generic execution adapter, separate episode admission, Reasoning,
  persistence, retry, Memory/World Model mutation or background work is introduced.

### Long-horizon investigation — exact A2 → Existing E2 Execution Re-entry GREEN
- Implemented the narrow long-horizon adapter from certified exact A2 into the existing `GovernedMultiStepInvestigationExecutionReentryV1` owner.
- Forwards the exact canonical A2 re-entry and caller-supplied `now` once; no second executor or generic execution adapter is introduced.
- Preserves the exact canonical E2 re-entry result, exact acquired evidence envelope, and exact resulting episode state.
- Derives second Reasoning re-entry eligibility only from canonical `ACQUIRED + AWAITING_REENTRY + remaining_acquisitions=0`.
- Preserves canonical stopped E2 without escalation and fails closed on invalid A2, owner exception, unexpected status, identity mismatch, or lineage mismatch, with no retry.
- Stops before Reasoning, Planning, Authorization, question creation, Memory/World Model mutation, persistence authority, or background work.

### RED — exact recorded E2 → second Reasoning re-entry → terminal episode closure
- Reconciled the certified E2 product against existing `GovernedMultiStepInvestigationReasoningClosureV1`.
- Froze a narrow adapter contract preserving exact E2 identity and mandatory CLOSED/BUDGET_EXHAUSTED terminal semantics.
- No R3/P3/A3/E3 or new cognitive authority introduced.

### Long-horizon investigation — exact recorded E2 → RR2 Terminal Closure GREEN
- Implemented the narrow long-horizon adapter from certified recorded E2 into the existing `GovernedMultiStepInvestigationReasoningClosureV1` owner.
- Forwards the exact canonical E2 execution-reentry and caller-supplied `now` once; no second Reasoning or Episode authority is introduced.
- Preserves the exact canonical closure result, exact RR2 product and exact terminal episode state.
- Accepts success only as one RR2 + one episode record + `CLOSED/BUDGET_EXHAUSTED/remaining_acquisitions=0`, with RR2 new relative to prior reentries.
- Fails closed before RR2 on invalid E2 and after the owner on exceptions, non-terminal status, identity mismatch or terminal lineage mismatch, without retry.
- Exposes no R3/P3/A3/E3, new requirement, curiosity, persistence, Memory/World Model mutation, conversation, or background process.

## CAP-11 Governed Horizon Generalization — Episode budget/step N-step + checkpoint continuity RED

- Frozen RED contract for constitutional N-step episode representation under the existing `GovernedMultiStepInvestigationEpisodeBoundaryV1` owner.
- Declared conservative governed hard-cap of 4 acquisitions while preserving historical default budget 2.
- Contract requires exact `current_step` checkpoint continuity and forbids budget growth through resume.
- No productive R3/P3/A3/E3, no new planner/executor/reasoner, and no second Episode authority.

## CAP-11 Episode budget/step N-step + checkpoint continuity — GREEN

- Generalized the existing Episode owner to governed acquisition budgets `1..4`, preserving default `2` and exact legacy budget-2 episode identity.
- Added generic N-step `current_step` validation and continuation semantics without adding Planning/Authorization/Execution/Reasoning authority.
- Generalized `record_reentry(...)` to close only when the configured budget is actually exhausted.
- Added exact `current_step` carriage and fingerprint participation to passive long-horizon checkpoints.
- Reused the Episode constitutional hard-cap from continuity; resume cannot increase historical budget.
- Kept P3/A3/E3/RR3 productively closed.

## CAP-11 Productive Continuation step N → Existing Planning re-entry — surgical reconciliation
- Integrated the user's authoritative import-sorted Episode implementation and CAP-11 N-step RED contract before creating this handoff.
- Confirmed the existing Productive Continuation and Planning re-entry owners are the canonical path for step-N planning; no new planner or manager is required.
- Isolated the productive residual to historical `step 2 / remaining 1` eligibility guards in those two owners.
- Froze the N-step eligibility shape as READY_FOR_PLANNING + exact current requirement/source/snapshot + `consumed_acquisitions == current_step - 1` + remaining budget.
- Kept the historical long-horizon P2 bridge unchanged and kept Authorization/Execution/Reasoning N-step outside this cut.


## CAP-11 — Planning step N → existing Authorization re-entry RED

- Added deliberate N-step Authorization re-entry contract tests.
- Preserved historical P2/A2 and STOP before Execution.
- No production behavior change in this RED cut.


## CAP-11 — Planning step N → existing Authorization re-entry GREEN

- Removed only the historical step-2/single-remaining-budget guards.
- Reused the existing Authorization re-entry authority for governed step N.
- Preserved P2/A2 and STOP before Execution.

## CAP-11 — Authorization step N → existing Execution re-entry — reconciliación

- Reconciled the existing multi-step Execution re-entry owner for governed N-step generalization.
- Confirmed no new executor or gateway is required.
- Identified terminal E2 assumptions that must be generalized before E3/E4.
- Preserved historical A2/E2 bridge and STOP before Reasoning re-entry.


## CAP-11 — Authorization step N → existing Execution re-entry RED

- Added deliberate N-step Execution re-entry contract tests.
- Preserved historical A2/E2 and STOP before Reasoning re-entry.
- No production behavior change in this RED cut.


## CAP-11 — Authorization step N → existing Execution re-entry GREEN

- Generalized the existing governed Execution re-entry owner from fixed E2 to governed step N.
- Preserved historical A2/E2 and the existing read-only execution gateway.
- ACQUIRED step N now exposes existing Reasoning re-entry eligibility while remaining budget may still be positive.
- No Reasoning invocation, retry, loop, manager, or new executor added.


## CAP-11 — Execution step N → existing Reasoning re-entry — surgical reconciliation

- Audited the existing Reasoning re-entry and Episode recording path.
- Located the residual in the RR2-terminal assumptions of the existing Reasoning closure owner.
- Froze STOP before creation/admission of the next requirement.
- No production code changed.


## CAP-11 — Execution step N → existing Reasoning re-entry — RED

- Added contractual RED for RR3 intermediate recording and RR4 terminal closure.
- Preserved legacy RR2/budget-2 behavior as an explicit compatibility contract.
- Froze STOP before creation/admission of R(N+1).
- No production code changed.


## CAP-11 — Execution step N → existing Reasoning re-entry — GREEN

- Generalized the existing Reasoning closure owner from fixed RR2 terminal behavior to governed step N.
- Added intermediate RECORDED outcome for AWAITING_REQUIREMENT.
- Preserved historical RR2/budget-2 terminal closure and enabled RR4 terminal closure for budget 4.
- STOP remains before creation/admission of R(N+1); no new authority added.

## CAP-11 — RR(N) → requisito discriminante R(N+1) — reconciliación

- Auditado el owner histórico RR1→R2 y localizada su especialización step-1/step-2.
- Se preservan `GovernedMultiHypothesisProductiveConsumptionV1` y `GovernedMultiStepInvestigationProductiveContinuationV1` como autoridades existentes.
- Se congela STOP después de admitir R(N+1), sin invocar Planning.

## CAP-17 — EPUB Library Reading Support — GREEN

- EPUB se incorpora al `DocumentReadingService` existente sin crear una segunda autoridad de lectura.
- El catálogo gobernado admite `.epub` por defecto.
- La lectura sigue `container.xml` → OPF → manifest/spine y sólo consume recursos del spine.
- Se añaden límites fail-closed de 512 miembros y 8.000.000 bytes descomprimidos, rechazo de traversal y cero extracción al filesystem.
- El handoff y `KnowledgeRetrievalArtifact` canónicos permanecen sin cambios; STOP antes de cualquier nuevo proposal source.

## CAP-17 — Cognitive Evidence Need → Local Library Proposal — GREEN

- Added structured `DiscriminatingEvidenceRequirement` assessment to the existing `OfficialKnowledgeRuntimeGateway`.
- Added one narrow cognitive-to-library bridge that delegates source choice to `KnowledgeSourcePolicy` and preserves reasoning lineage.
- Added neutral `handle_admitted_request(...)` convergence for user-admitted and ROBY-initiated library access; removed synthetic human request text from the autonomous path.
- Productive library wiring exposes the cognitive bridge only after successful library provisioning.
- No new reasoning/planning authority, direct library read/search authority, Memory/Learning side effect, background task, or retrieval-step schema change was introduced.

## CAP-17 — Productive Reasoning Requirement → Cognitive Library Bridge Invocation — GREEN
- Se añadió `GovernedProductiveReasoningLibraryBridgeContributorV1` como adaptador instrumental del `CognitiveRuntimeOrchestrator` existente.
- El contributor consume exclusivamente el episodio productivo y re-entry exactos del mismo turno, conserva lineage y usa la confianza canónica del episodio.
- La invocación de CAP-17 es fail-closed cuando la Biblioteca no está provisionada y delega exclusivamente en el `cognitive_bridge` ya gobernado.
- Se preservan `KnowledgeRetrievalStep`, `.roby/config.json` y las autoridades existentes.

- CAP-17 GREEN: local retrieval artifact now re-enters the existing governed reasoning authority exactly once, preserving acquisition provenance and cognitive lineage.

## INTEL-G9 — Source-Neutral Write Request → Existing Productive Wiring — SURGICAL GREEN

- Added the minimal `execute_certified_write_request(...)` seam to the existing `ProductiveGovernedLearningWiring`.
- Historical and source-neutral routes now reuse one persistence routine and the same `OfficialMemoryGateway` contract.
- Integrated the corrected G9 contract test supplied after RED validation.
- No new Memory authorization, writer, gateway, adapter, persistence runtime, or parallel productive wiring was introduced.

---

## POST-G22 — DOCUMENTATION NORMALIZATION / FINAL CLOSURE

**Estado oficial:** INTEL-G22 CERTIFIED / CLOSED — **14.189 PASS · 0 FAIL · Ruff clean**.

La cadena gobernada de corrección G13→G22 queda cerrada para el alcance actual. G22 separa `CERTIFIED REQUEST` de `EXECUTION AUTHORIZATION`; sólo el par exacto request + autorización APPLY-NOW puede reingresar al G18/G17 existente.

Alias canónico: `INTEL_G21_WHAT_DID_YOU_LEARN_*` se conserva por trazabilidad pero corresponde a **INTEL-G2.1 — WHAT DID YOU LEARN**. El G21 canónico actual es **APPROVED REVISION PREPARATION CONTINUITY**.

`scripts/clean_project_caches.py` queda incorporado a la secuencia oficial antes de baseline/Ruff/pytest. Los tres snapshot guards históricos del `OfficialConversationGateway` fueron reanclados, tras auditoría, al SHA G22 `808104708cf035702cf1a181a75b630181a9879f79c68dec129f102460b10ef1`.

**NO G23 OPENED.** La próxima evolución debe derivarse de una carencia funcional demostrada por inventario/auditoría.


## ESTADO_MAESTRO_INTEGRAL historical master-state archival

- Moved the accumulated historical master-state record from root to `docs/history/ESTADO_MAESTRO_INTEGRAL.md` with byte-for-byte SHA-256 preservation.
- Formalized `ROBY_XI_2_CURRENT_TRUTH.md` as the present-state navigation authority.
- Reconciled protected-path and Whole Personal System E2E documentary contracts without productive behavior change.
- Historical Post-M400.x statements remain untouched as traceability evidence.
- Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**; expected baseline **13.912 PASS · 0 FAIL · Ruff clean**.

## Post-M400 — External Intelligence / Governed Source Query integration residency reconciliation

- Relocated `GovernedExternalInformationSourceIntegration` from `core.governed_external_intelligence` to the application integration layer.
- Removed the transitive `core.governed_external_intelligence -> app.governed_source_query` dependency and core re-export.
- Preserved M400.4–M400.7 behavior and M400.9 historical certification evidence.
- No authority or productive capability change; pending owner certification.

## Organization / Calendar — neutral Agenda evidence boundary reconciliation

- Added minimal `core.agenda_evidence.AgendaEventEvidence`.
- Moved `CalendarEvent -> AgendaEventEvidence` translation to the existing app
  Organization advisory wiring seam.
- Removed Organization core dependency on `infrastructure.calendar`.
- Preserved Calendar, Cognitive Agenda, Personal Organization, M391.5/M391.6 and
  all writer authorities.
- Productive reachability delta: 0.
- Added one architecture guardrail.
- Status: **CLOSED / CERTIFIED** — owner baseline **12,536 PASS · 0 FAIL · Ruff clean**.

## Core root disconnected legacy utilities — five-island retirement

- Retired `core/circuit_breaker.py`, `core/retry.py`, `core/event_bus.py`,
  `core/logging.py` and `core/runtime.py` after exact zero-reachability audit.
- Preserved `core/cache.py` and its M22 standalone component contract.
- Preserved current `CognitiveEventBus`, Executive Recovery Health and
  `RuntimeCompositionRoot` surfaces.
- Historical SHA manifest remains unchanged.
- Added one architectural absence/preservation guardrail.
- Productive behavior delta: 0.
- Status: **CLOSED / CERTIFIED** — owner baseline **12,537 PASS · 0 FAIL · Ruff clean**.

## RP24.5 Unified Learning Base — historical authority retirement / M369 records reconciliation

- Retired the disconnected RP24.5 SQLite learning authority
  `core/unified_learning_base.py`.
- Retired its eight direct historical behavioral tests.
- Removed `LearningDomain.RECORDS`, `LearningRole.RECORD` and the
  `core.unified_learning_base:LearningRecord` descriptive M369 contract.
- Archived the RP24.5 design document unchanged under `docs/history/`.
- Preserved the historical SHA manifest unchanged.
- Preserved the productive governed learning chain and
  `OfficialMemoryGateway` as the durable write boundary.
- Added one architectural retirement/preservation guardrail.
- Productive behavior delta: 0.
- Status: **CLOSED / CERTIFIED — owner baseline 12,530 PASS · 0 FAIL · Ruff clean**.

## M375 contextual conversation — historical authority retirement / current continuity reconciliation

- Retired the disconnected historical M375 implementation
  `core/contextual_conversation.py` and its eight direct milestone tests.
- Retired the obsolete current-authority claim for
  `ConversationContextAuthority`.
- Preserved the current `ConversationContext` contract.
- Preserved the productive context-continuity chain:
  `OfficialContextContinuityRuntimeGateway` → conversational context
  continuity → curation/sanitization → official runtime composition.
- Archived the original M375 milestone document unchanged under
  `docs/history/legacy-conversation/`.
- Reconciled the M390.4 architecture guard by removing only the obsolete
  historical-authority name token; its safe-relational boundary is unchanged.
- Added a dedicated architectural retirement/current-successor guardrail.
- No new authority, persistence path, context store or runtime was created.
- Productive behavior delta: 0.
- Status: **CLOSED / CERTIFIED — owner baseline 12,523 PASS · 0 FAIL · Ruff clean**.


## M378 global explanation — historical authority retirement / source-owned explainability governance reconciliation

- Retired the disconnected historical M378 `core/intelligent_explanations.py`
  implementation and its eight direct milestone tests.
- Retired the obsolete global-authority claim for
  `IntelligentExplanationAuthority`.
- Preserved productive specialized explainability in Governed Reasoning,
  Cognitive Planning, Controlled Autonomy and Trust.
- Established source-owned explainability governance without creating a global
  replacement authority, registry, manager, store, persistence path or runtime.
- Archived the original M378 milestone document unchanged under
  `docs/history/legacy-explainability/`.
- Added a dedicated architectural retirement/governance guardrail.
- Productive behavior delta: 0.
- Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**.

## M378.1 — CCI-08 source-owned explainability certification evidence reconciliation

- Reconciled stale CCI-08 evidence left by retirement of `core/intelligent_explanations.py`.
- CCI-08 now certifies two current non-cognitive boundaries without claiming productive M377-to-explainability wiring: bounded adaptive delivery and source-owned explanation from immutable canonical decision evidence.
- No production code, authority, persistence or runtime wiring changed.


## M376 historical unrealized conversation archive retirement

- Retired dormant `core/long_term_conversation.py` and its direct historical M376 tests.
- Archived the original M376 document unchanged under `docs/history/legacy-conversation/`.
- Declared no replacement archive authority: operational conversation history, Living Conversation and Cognitive Memory remain separate.
- Added an architectural guardrail against restoring M376 or implicitly converting conversation summaries into Memory.
- Productive runtime behavior unchanged; pending owner certification.

## Post-M376 documentary certification reconciliation

- Promoted the M376 historical unrealized conversation archive retirement to **CLOSED / CERTIFIED** after owner validation at **12,513 PASS · 0 FAIL · Ruff clean**.
- Synchronized current baseline metadata across Current Truth, architecture rules, Master Capability Registry and mirror, Cognitive Inventory master guide, Vision, and architecture changelog.
- Historical milestone baselines remain unchanged as chronology. No production code, tests, runtime wiring, authority or persistence behavior changed.


## Post-M376 — M17/M19 legacy auxiliary foundation retirement

A governed reachability/genealogy review confirmed that the historical M17 Event Publisher and M19 Memory Pipeline lost all productive consumers with the retirement of `core.roby`. The disconnected modules and their direct historical tests were retired without replacement. Existing current event/observability and Cognitive Memory authorities remain unchanged; conversation occurrence does not imply automatic Memory admission. Historical milestone and audit evidence is preserved. Status: **CLOSED / CERTIFIED — owner baseline 12,508 PASS · 0 FAIL · Ruff clean**.


## Post-M17/M19 — M27/M28 Agent Runtime / Agent Loop legacy execution retirement

- Retired disconnected `core/agent_runtime.py` and `core/agent_loop.py`.
- Retired their direct M27/M28/M32/M40 AgentLoop historical tests.
- Preserved `LLMService`, `ProviderRouter`, and `CognitivePipeline` unchanged.
- Reconciled M395.1 neutral-contract evidence so it no longer reads retired files.
- Added one architecture retirement guardrail.
- Status: **CLOSED / CERTIFIED — owner baseline 12,487 PASS · 0 FAIL · Ruff clean**; certified input **12,508 PASS · 0 FAIL · Ruff clean**.


## Post-M27/M28 documentary certification reconciliation

Owner certification closed the M27/M28 Agent Runtime / Agent Loop legacy execution lineage retirement at **12,487 PASS · 0 FAIL · Ruff clean**. Current baseline/status metadata was synchronized across Current Truth, architecture rules, Master Capability Registry and mirror, Cognitive Inventory master guide, Vision, decision ledger, changelogs, and the M27/M28 validation record. Historical milestone baselines remain unchanged. No production code, tests, runtime wiring, authority, persistence, or compatibility surface changed in this documentary reconciliation.

## Post-M27/M28 — M17-era generic trace contract residue retirement

- Retired disconnected `core/tracing.py` and
  `tests/fakes/fake_trace_recorder.py` after zero productive/test reachability
  and M17 genealogy confirmation.
- Preserved `core/operational_trace_model`, its productive end-to-end runtime
  integration, stores, models, and current tests unchanged.
- Added one architecture guardrail preserving the retirement boundary and the
  byte-identical M17 historical milestone.
- No replacement recorder, adapter, authority, registry, manager, persistence
  path, or runtime was introduced.
- Status: **CLOSED / CERTIFIED — owner baseline 12,488 PASS · 0 FAIL · Ruff clean**; certified input baseline **12,487 PASS · 0 FAIL · Ruff clean**.


## Post-M17-era Trace — M22 standalone cache contract retirement

- Retired disconnected historical `core/cache.py` and its six direct M22 component tests.
- Reconciled the earlier five-island guardrail that preserved M22 only pending a dedicated audit.
- Preserved capability-local transient caches and Working Memory unchanged; no M22 successor is declared.
- Added one architecture guardrail preventing restoration as a global cache authority.
- Historical M22 milestone and SHA-manifest evidence remain unchanged.
- Status: **CLOSED / CERTIFIED — owner baseline 12,483 PASS · 0 FAIL · Ruff clean**; certified input baseline **12,488 PASS · 0 FAIL · Ruff clean**; owner result **12,483 passed in 263.92s**.

## Post-M22 — M391.8 historical closure diagnostic executable residency retirement

- Retired `core/m391_integral_evidence.py`, a disconnected historical M391.8 closure diagnostic with zero productive/runtime/Composition Root/application/infrastructure/script/quality-script reachability.
- Retired its 15 self-contained M391.8 diagnostic tests and added one architecture guardrail.
- Preserved M391.1–M391.7 current capability surfaces and their canonical owners unchanged.
- Preserved M390.8 unchanged as a distinct Cognitive Maturity diagnostic.
- Preserved historical M391.8 documentation and closure invariants; no replacement authority, manager, registry, coordinator, runtime or persistence path was introduced.
- Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**; certified input baseline **12,483 PASS · 0 FAIL · Ruff clean**; expected collection **12,469**.


## Living Conversation runtime neutral projection contract reconciliation

Reconciled the M105/M190/M253 runtime seam without authority succession or physical package movement. M190 now consumes immutable neutral `LivingConversationRuntimeProjection` evidence; M253 returns that typed projection instead of a productive `SimpleNamespace`; canonical M105 evidence can project through a pure adapter. Stable Personality remains distinct from M105, explicit-only activation is preserved, and no new authority/store/registry/persistence/runtime is introduced. Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**; certified input **12,469 PASS · 0 FAIL · Ruff clean**; expected owner collection **12,471**.


## M367 historical inventory/diagnostic executable retirement + M368/M379/CCI-03 contract reconciliation

- Retired executable M367.2 `UserProfileModel`, M367.3 `ProjectKnowledgeModel`, M367.4 `GoalsObjectivesModel`, M367.5 `ContextStateModel`, and M367.7 `MentalModelStabilization`, plus their now-unreferenced matching core contracts and positive milestone tests.
- Preserved M367.1 `InternalWorldModelFoundation` because M391/M392 evolved it into the current World Model façade.
- Preserved M367.6 `PriorityReasoning` and its productive current lineage.
- Reconciled M368.1 Planning metadata from historical M367 umbrellas to existing specialized owners; planning remains one read-only/non-executing authority.
- Reconciled M379 GOALS to existing `HouseholdGoalManager`, explicitly keeping cognitive goals separate.
- Reanchored CCI-03 to current `MentalModel` -> governed decision-evidence -> decision causal proof.
- Added architecture guardrails preventing current Python code from re-importing retired M367 modules. Historical documentation remains unchanged as historical evidence.
- Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**; certified input **12,471 PASS · 0 FAIL · Ruff clean**.


## Post-M409.1 reasoning-quality productive-projection retirement

Retired the historical app-level Reasoning Quality productive projection while
preserving the canonical Foundation, neutral derived carrier, and import boundary.


## APP BRAIN → infrastructure repository layering seam

- Inverted diagnostic BRAIN repository construction from `application.brain` to the
  diagnostic entry-point layer using existing repository contracts.
- Preserved all existing infrastructure implementations, persistence paths/schemas,
  capability authorities, and runtime Composition Root wiring.
- Added an application-layer import guardrail; Identity stores remain out of scope.
- Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**; certified input baseline
  **12,355 PASS · 0 FAIL · Ruff clean**.

## Governed Proposal → Executive Notification productive reachability

- Added a productive resident adapter from the existing governed proposal presentation
  policy to the existing `RuntimeExecutiveIntegration` notification spine.
- Preserved canonical proposal/inbox/lifecycle authorities and the sole
  `ExecutiveNotificationBroker`.
- `PENDING → OFFERED` now occurs only after broker dispatch of the correlated proposal
  event.
- No new execution authority, persistence, Composition Root, or `.roby` state.
- Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**; certified input baseline
  **12,355 PASS · 0 FAIL · Ruff clean**.

## Self-Diagnostic Opportunity → Governed Proposal reachability

- Added a bounded application composition for explicit M399 diagnostic opportunities.
- Reused existing Self Diagnostics, proof, proposal-generation and Governed Proposal
  authorities.
- Preserved the permanent human-review boundary and added no background monitoring,
  autonomous hypothesis generation or code mutation.

## Generic life-event reminder semantics

- Confirmed `recordame` / `haceme acordar` as the single generic Reminder intent.
- Added explicit numeric and Spanish named-month date parsing to the existing Reminder
  conversation adapter.
- Added coverage for concert, travel and yearly birthday reminder semantics.
- Preserved Calendar as a separate confirmation-gated authority and added no new store,
  reminder manager or notification path.

## Upcoming Medical Appointment → Consultation Preparation Offer

- Added bounded semantic recognition of medical-appointment reminders for Carlos or
  Cristina.
- Reused the existing Reminder awareness path and existing medical consultation
  preparation capability.
- Kept health-data access opt-in and fail-closed for ambiguous reminders.

## Governed Local Music Collection → Read-Only Catalogue Foundation

- Added a separate bounded read-only music catalogue.
- Added explicit `ROBY_LOCAL_MUSIC_ROOT` provisioning.
- Registered `music.local_catalogue.read` in the official runtime only when configured.
- Kept selection, playback, Pinacoteca and MusicMemory outside this gate.

## Governed Local Music Collection → Selection Foundation

- Added deterministic selection over the certified read-only music catalogue.
- Added fail-closed human disambiguation for multiple matches.
- Added productive explicit selection language without playback execution.
- Preserved `playback_authorized=False` across all selection results.

## Governed Local Music Collection → Playback Authorization / Execution Foundation

- Added explicit human playback authorization after governed selection.
- Added configurable local music playback execution via
  `ROBY_LOCAL_MUSIC_PLAYBACK_COMMAND`.
- Registered `music.local_playback.execute` only when playback is provisioned.
- Kept ambiguous selection and non-explicit requests fail-closed.
- Reused neither microphone input nor TTS output as music playback authorities.

## CIH — Governed Reasoning → Living Companion minimal seam — certified

- Reused the existing `GovernedReasoningSource` contract and canonical productive
  reasoning source; no new cognitive authority was introduced.
- Injected the existing canonical reasoning source into `LivingCompanionRuntime`.
- Preserved explicit-question bypass, local situational recognition precedence,
  capability-registry risk/confirmation governance, and all permission/autonomy
  boundaries.
- Closed the demonstrated seam gap without claiming closure of the narrower semantic
  abstention residual.
- Owner full gate: **12,506 PASS · 0 FAIL · Ruff clean**.
- Status: **CLOSED / CERTIFIED**.



## Governed longitudinal intellectual usefulness — final closure

- Completed the ordinary-turn path from exact governed recall candidates through bounded
  single-antecedent admission, longitudinal reconstruction and conversational inference
  context.
- Used the external bounded adapter placement so the protected reasoning runtime remains
  unchanged.
- Preserved fail-closed abstention and the semantic STOP: no forced identity, synthetic
  evidence, persistence, autonomous continuation or new cognitive authority.
- Owner full gate: **12,648 PASS · 0 FAIL · Ruff clean**.
- Status: **CLOSED / CERTIFIED**.
