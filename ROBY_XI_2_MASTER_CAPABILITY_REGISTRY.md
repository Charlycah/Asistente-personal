> **Current baseline pointer:** interpret this registry together with `ROBY_XI_2_CURRENT_TRUTH.md`; the registry owns capability mapping, while Current Truth owns compact present-state navigation.

# ROBY XI.2 --- Master Capability Registry

**Historical registry reconciliation baseline:** 12,471 PASS · 0 FAIL · Ruff clean\
**Higher Cognitive Evolution:** CLOSED / ZERO-RESIDUAL CERTIFIED\
**Purpose:** canonical surgical registry to consult before any new
implementation, refactor, deletion, authority change, persistence
change, or test/documentation modification.\
**Direction:** laptop-only; cognitive/intellectual depth, integration
and simplification.

------------------------------------------------------------------------

## 1. Registry rule

No change begins from a feature name. It begins from this chain:

**requested behavior → existing capability → canonical authority → owner
files → productive callers → writers/persistence → contract tests →
documentation → exact residual → minimum permitted change.**

Default decision:

> **extend/integrate the existing owner; create a new capability only
> when equivalence and reachability audits prove the behavior is
> genuinely missing.**

This registry is a control map, not permission to delete code. `LEGACY`,
duplicate-looking names, or apparently unused modules require a separate
dependency/reachability audit before physical removal.

------------------------------------------------------------------------

## 2. Repository scale snapshot

The certified repository contains **136 direct directories under `core/`
including support/test/cache entries**; the previous reconciled count is
**134 functional direct `core/` subdirectories after exclusions**. The
Master Surgical Guide records **1,256 Python files** across principal
code layers, **1,143 `test_*.py` files**, and **1,156 documentation
files**. At this scale, filenames and milestone memory are insufficient
evidence of ownership or absence.

------------------------------------------------------------------------

## 3. Canonical authority map

  ----------------------------------------------------------------------------------
  Responsibility          Canonical primary                  Hard boundary
  ----------------------- ---------------------------------- -----------------------
  Entry                   `conversation_entry`               No second
                                                             conversational entry
                                                             authority.

  Context                 `context_continuity`               No parallel context
                                                             brain/store.

  Memory                  `memory_gateway`                   Durable cognitive
                                                             writes use the official
                                                             memory boundary.

  Knowledge               `knowledge_runtime`                Consultative
                                                             evidence/knowledge, not
                                                             silent reasoning or
                                                             memory ownership.

  Reasoning               `governed_reasoning`               Canonical inferential
                                                             owner.

  Planning                `executive_planning`               Shadows/diagnostics do
                                                             not become a second
                                                             planner.

  Decision                `unified_cognitive_coordination`   Advisory/decision
                                                             coordination under
                                                             existing contracts.

  Execution               `capability_orchestrator`          Reasoning never grants
                                                             execution by itself.

  Reflection              `cognitive_core_resident`          Reflection is not a
                                                             second reasoning
                                                             authority.

  Governance              `governed_capability_routing`      New routes preserve
                                                             governed routing.

  Observability           `runtime_observability`            Observation does not
                                                             mutate production
                                                             merely by observing.
  ----------------------------------------------------------------------------------

------------------------------------------------------------------------

## 4. Capability cards

### CAP-01 --- Conversation & contextual continuity

**Authority / owner boundary:** `Entry / Context`\
**State:** **CLOSED / SUBSTANTIAL**

**Primary implementation anchors:** - `core/conversation_entry_point/` -
`core/context_transfer/` - `core/cross_context_continuity/` -
`core/living_conversation/`

**Representative contractual evidence:** -
`tests/architecture/test_m383_9_local_conversation_factory_separation.py` -
`tests/architecture/test_m386_11_conversation_entry_evidence_adapter.py` -
`tests/architecture/test_m386_17_controlled_conversational_identification_flow.py` -
`tests/architecture/test_m389_2_conversation_reflection.py` -
`tests/architecture/test_m408_2_official_conversation_human_consumer.py` -
`tests/architecture/test_post_m409_1_decision_advisory_conversational_realization.py` -
`tests/architecture/test_post_m409_1_productive_conversational_curiosity_wiring_v1.py` -
`tests/architecture/test_post_m409_1_roby_conversational_e2e_read_only_desktop_diagnostic_harness.py`

**Representative documentation:** -
`docs/M196_ADAPTIVE_CONVERSATION_INTELLIGENCE.md` -
`docs/M197_CONVERSATIONAL_REPAIR_AND_CLARIFICATION_INTELLIGENCE.md` -
`docs/M253_CONVERSATION_RUNTIME.md` -
`docs/M264_END_TO_END_CONVERSATION_RUNTIME.md` -
`docs/M268_MULTIMODAL_CONVERSATION_INTEGRATION.md` -
`docs/M269_CONVERSATION_RELIABILITY_OBSERVABILITY.md`

**Exact residual / surgical rule:** Profundizar continuidad intelectual
de temas e investigaciones; no crear otro dialogue/context brain.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-02 --- Memory & autobiographical continuity

**Authority / owner boundary:** `memory_gateway`\
**State:** **CLOSED / PERSISTENT / GOVERNED**

**Primary implementation anchors:** - `core/cognitive_memory.py` -
`core/cognitive_memory_store.py` - `core/cognitive_memory_recall.py` -
`core/memory_runtime_integration/`

**Representative contractual evidence:** -
`tests/ROBY XI.2 #U0393#U00c7#U00f6 Whole-System Advanced Capability Consolidation Audit Agosto 22 2026.txt` -
`tests/ROBY XI.2 #U2014 Whole-System Advanced Capability Consolidation Audit Agosto 22 2026.txt` -
`tests/ROBY XI.2 ΓÇö Whole-System Advanced Capability Consolidation Audit Agosto 22 2026.txt` -
`tests/ROBY XI.2 — Whole-System Advanced Capability Consolidation Audit Agosto 22 2026.txt` -
`tests/ROBY XI.2 ╬ô├ç├╢ Whole-System Advanced Capability Consolidation Audit Agosto 22 2026.txt` -
`tests/architecture/test_cross_capability_learned_memory_later_reasoning.py` -
`tests/architecture/test_cross_capability_memory_planning.py` -
`tests/architecture/test_m385_5_canonical_memory_ownership.py`

**Representative documentation:** -
`docs/CCI_02_GOVERNED_LEARNED_MEMORY_CROSS_EPISODE_REUSE_CERTIFICATION.md` -
`docs/INTEGRATION_NOTE_RC_1_1_GOVERNED_RECALLED_KNOWLEDGE_STRUCTURAL_PROJECTION_V1.md` -
`docs/M366_1_COGNITIVE_MEMORY_FOUNDATION.md` -
`docs/M366_2_EPISODIC_MEMORY.md` - `docs/M366_3_SEMANTIC_MEMORY.md` -
`docs/M366_4_PROCEDURAL_MEMORY.md`

**Exact residual / surgical rule:** No crear
ConceptMemory/BookMemory/MusicMemory. Toda persistencia cognitiva debe
conservar el gateway oficial.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-03 --- Knowledge & retrieval

**Authority / owner boundary:** `knowledge_runtime`\
**State:** **SUBSTANTIAL / CONSULTATIVE**

**Primary implementation anchors:** -
`core/knowledge_retrieval_execution/` -
`core/knowledge_retrieval_orchestrator/` -
`core/knowledge_source_policy/` - `core/personal_knowledge_base.py`

**Representative contractual evidence:** -
`tests/test_m169_knowledge_source_policy.py` -
`tests/test_m170_knowledge_retrieval_orchestrator.py` -
`tests/test_m171_knowledge_retrieval_execution.py` -
`tests/test_m74_personal_knowledge_base.py`

**Representative documentation:** -
`docs/adr/ADR_076_personal_knowledge_base.md` -
`docs/adr/ADR_171_knowledge_source_policy.md` -
`docs/adr/ADR_172_knowledge_retrieval_orchestrator.md` -
`docs/adr/ADR_173_knowledge_retrieval_execution_gateway.md` -
`docs/milestones/M169_KNOWLEDGE_SOURCE_POLICY.md` -
`docs/milestones/M170_KNOWLEDGE_RETRIEVAL_ORCHESTRATOR.md`

**Exact residual / surgical rule:** Falta síntesis multi-dominio
profunda; Knowledge no debe transformarse en reasoning o memory
authority.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-04 --- Governed reasoning

**Authority / owner boundary:** `governed_reasoning`\
**State:** **CLOSED / SUBSTANTIAL / CANONICAL**

**Primary implementation anchors:** - `core/governed_reasoning/`

**Representative contractual evidence:** -
`tests/architecture/test_post_m409_1_longitudinal_reasoning_observation_contract_generalization_v1.py` -
`tests/architecture/test_post_m409_1_governed_comparative_reasoning_method_awareness_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_reasoning_method_effectiveness_awareness_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_reasoning_method_effectiveness_awareness_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_reasoning_method_outcome_association_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_reasoning_method_outcome_association_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_reasoning_method_provenance_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_reasoning_method_provenance_productive_consumption_v1.py` -
`tests/architecture/test_post_m409_1_governed_reasoning_quality_assessment_foundation_v1.py`

**Representative documentation:** -
`docs/POST_M409_1_LONGITUDINAL_REASONING_OBSERVATION_CONTRACT_GENERALIZATION_V1.md` -
`docs/POST_M409_1_GOVERNED_REASONING_HYPOTHESIS_DEEPENING_FOUNDATION_V1.md` -
`docs/POST_M409_1_GOVERNED_COMPARATIVE_REASONING_METHOD_AWARENESS_FOUNDATION_V1.md` -
`docs/POST_M409_1_GOVERNED_REASONING_METHOD_EFFECTIVENESS_AWARENESS_FOUNDATION_V1.md` -
`docs/POST_M409_1_GOVERNED_REASONING_METHOD_EFFECTIVENESS_AWARENESS_FOUNDATION_V1.md` -
`docs/POST_M409_1_GOVERNED_REASONING_METHOD_OUTCOME_ASSOCIATION_FOUNDATION_V1.md` -
`docs/POST_M409_1_GOVERNED_REASONING_METHOD_OUTCOME_ASSOCIATION_FOUNDATION_V1.md`

**Exact residual / surgical rule:** Toda nueva primitive inferencial
debe intentar extender esta authority antes de crear otra.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-05 --- Hypothesis discrimination & revision

**Authority / owner boundary:** `governed_reasoning`\
**State:** **SUBSTANTIAL / SELECTIVE**

**Primary implementation anchors:** -
`core/governed_reasoning/governed_hypothesis_formation.py` -
`core/governed_reasoning/hypothesis_semantic_grounding.py` -
`core/governed_reasoning/explicit_hypothesis_source.py` -
`core/governed_reasoning/hypothesis_deepening.py` -
`core/governed_reasoning/multi_hypothesis_discrimination.py` -
`core/governed_reasoning/hypothesis_update_semantics.py` -
`core/governed_reasoning/hypothesis_epistemic_delta.py`

**Representative contractual evidence:** -
`tests/architecture/test_governed_hypothesis_formation.py` -
`tests/architecture/test_hypothesis_candidate_structured_semantics.py` -
`tests/architecture/test_hce_canonical_hypothesis_bearing_epistemic_episode_binding_metacognitive_closure_wave.py` -
`tests/architecture/test_hce_governed_explicit_hypothesis_source_selective_reachability_wave.py` -
`tests/architecture/test_hcpdq_v2_h7_hypothesis_measurable_family_contract.py` -
`tests/architecture/test_m391_3_governed_hypothesis_scenario_simulation.py` -
`tests/architecture/test_post_m409_1_governed_hypothesis_deepening_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_hypothesis_epistemic_delta_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_hypothesis_update_semantics_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_hypothesis_update_semantics_import_boundary_v1.py`

**Representative documentation:** -
`docs/HIGHER_COGNITIVE_EVOLUTION_CANONICAL_HYPOTHESIS_BEARING_EPISTEMIC_EPISODE_BINDING_METACOGNITIVE_CLOSURE_WAVE.md` -
`docs/HIGHER_COGNITIVE_EVOLUTION_GOVERNED_EXPLICIT_HYPOTHESIS_SOURCE_SELECTIVE_REACHABILITY_WAVE.md` -
`docs/M391_3_GOVERNED_HYPOTHESIS_SCENARIOS.md` -
`docs/M399_3_GOVERNED_DIAGNOSTIC_HYPOTHESIS_CONFIDENCE.md` -
`docs/POST_M409_1_GOVERNED_HYPOTHESIS_EPISTEMIC_DELTA_FOUNDATION_V1.md` -
`docs/POST_M409_1_GOVERNED_HYPOTHESIS_UPDATE_SEMANTICS_FOUNDATION_V1.md`

**Governed Hypothesis Formation:** owner-certified at **12,406 PASS · 0 FAIL · Ruff
clean**. It projects already-governed tentative/contextual claims and exact rule-result
claims into read-only hypothesis candidates under `governed_reasoning`.

**Current candidate / owner gate pending:** one exact formed candidate can admit explicit
structured Scenario/Causal semantics only when complete semantics and provenance are
supplied and exact candidate/goal lineage matches. The seam constructs the existing
`GovernedExplicitHypothesisSource`; it does not infer semantic fields from text.

**Exact residual / surgical rule:** semantic admission is not autonomous semantic
generation. Future work may deepen how explicit structured semantics are obtained from
already-governed evidence or human input, but must not introduce a Theory Engine,
HypothesisManager, free-form LLM authority or parallel research brain.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-06 --- Scenario / causal / prediction

**Authority / owner boundary:** `governed_reasoning`\
**State:** **SUBSTANTIAL / SELECTIVE**

**Primary implementation anchors:** -
`core/governed_reasoning/scenario_simulation.py` -
`core/governed_reasoning/causal_prediction.py` -
`core/governed_reasoning/governed_prediction.py` -
`core/governed_reasoning/prediction_outcome_evaluation.py`

**Representative contractual evidence:** -
`tests/architecture/test_adaptive_cognitive_closed_loop_preimplementation_causal_red.py` -
`tests/architecture/test_hcpdq_v2_h2_h8_causal_lineage_gap_contract.py` -
`tests/architecture/test_hcpdq_v2_h6_isolation_adapter_causal_architectural_recertification.py` -
`tests/architecture/test_hcpdq_v2_h6_productive_gap_causal_architectural_recertification.py` -
`tests/architecture/test_hcpdq_v2_h7_minimal_isolation_adapter_causal_recertification.py` -
`tests/architecture/test_m391_3_governed_hypothesis_scenario_simulation.py` -
`tests/architecture/test_m391_4_governed_causal_predictive_reasoning.py` -
`tests/architecture/test_m391_7_governed_prediction.py`

**Representative documentation:** -
`docs/COGNITIVE_COHERENCE_CAUSAL_CLOSURE.md` -
`docs/M391_3_GOVERNED_HYPOTHESIS_SCENARIOS.md` -
`docs/M391_4_GOVERNED_CAUSAL_PREDICTION.md` -
`docs/M391_7_GOVERNED_PREDICTION.md` -
`docs/PERSONAL_COGNITIVE_INTEGRATION_RESIDUAL_WHOLE_PERSONAL_CAUSALITY_AUDIT.md`

**Exact residual / surgical rule:** Profundizar a contrafactual
multi-etapa; preservar source explícito y fail-closed.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-07 --- Relational abstraction / concept foundation

**Authority / owner boundary:** `governed_reasoning`\
**State:** **FOUNDATION / SELECTIVE / ADMISSION GREEN-1→4 ISOLATED**

**Primary implementation anchors:** -
`core/governed_reasoning/contextual_semantic_grounding.py` -
`core/governed_reasoning/relational_abstraction.py` -
`core/governed_reasoning/productive_abstraction_admission.py` -
`app/governed_relational_abstraction_learning_bridge.py`

**Representative contractual evidence:** -
`tests/architecture/test_hce_governed_relational_abstraction_wave.py` -
`tests/architecture/test_hce_abstraction_approved_learning_later_novel_reuse.py` -
`tests/architecture/test_cap_07_productive_abstraction_admission_green_1_4.py`

**Representative documentation:** -
`docs/HIGHER_COGNITIVE_EVOLUTION_GOVERNED_RELATIONAL_ABSTRACTION_WAVE.md` -
`ROBY_XI_2_CAP_07_DEEP_SURGICAL_CAPABILITY_MAP.md` -
`ROBY_XI_2_CAP_07_PRODUCTIVE_REACHABILITY_COMPOSITION_ROOT_TRACE.md` -
`ROBY_XI_2_CAP_07_GOVERNED_PRODUCTIVE_ABSTRACTION_ADMISSION_CONTRACT_RED_EVIDENCE.md` -
`ROBY_XI_2_CAP_07_PRODUCTIVE_ABSTRACTION_ADMISSION_GREEN_1_4.md`

**Exact residual / surgical rule:** GREEN-1→4 now provides certified-grounding
normalization, bounded session-local accumulation and selective reuse of the
existing inducer, but it is intentionally **not wired to the composition root**.
Next residual: GREEN-5→7 canonical read-only productive episode consumption and
gateway wiring. Hierarchical concept composition remains blocked until that
reachability closes. No Concept Brain, Concept Memory or second abstraction
engine.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------


**HCC GREEN-1→4 update:** isolated governed hierarchical concept composition is implemented under `governed_reasoning`; no gateway wiring/persistence/transfer. Remaining residual is productive concept episode + consultative consumption.


**HCC GREEN-5 update:** canonical productive concept episode binding and consultative gateway consumption are implemented read-only. Ordinary-turn multi-abstraction input diversity remains uncertified.


**CAP-07 Multi-Family GREEN-1→4 update:** Productive Abstraction Admission now preserves two bounded normalization families under the same authority, with family-isolated transient accumulation and a shared scope bound. Historical R1 remains unchanged; VELAR provides bounded R2. Learning and Structural Transfer remain unchanged. HCC can now receive genuinely distinct abstraction pairs when both families are productively observed.

### CAP-08 --- Structural transfer / bounded analogy

**Authority / owner boundary:** `governed_reasoning`\
**State:** **SUBSTANTIAL / BOUNDED**

**Primary implementation anchors:** -
`core/governed_reasoning/structural_knowledge_transfer.py` -
`core/governed_reasoning/recalled_knowledge_structural_projection.py` -
`core/governed_reasoning/target_problem_structural_projection.py` -
`core/governed_reasoning/transfer_admission_guard.py` -
`core/governed_reasoning/transfer_instantiation.py`

**Representative contractual evidence:** -
`tests/architecture/test_post_hcpdq_strong_generalization_multi_family_structural_transfer_challenge.py` -
`tests/architecture/test_post_m409_1_approved_structural_knowledge_bridge_causal_certification_v1.py` -
`tests/architecture/test_post_m409_1_approved_structural_knowledge_learning_bridge_red_v1.py` -
`tests/architecture/test_post_m409_1_rc_1_3_governed_transfer_instantiation_package_v1.py` -
`tests/architecture/test_post_m409_1_rc_1_4_governed_transfer_admission_guard_v1.py` -
`tests/architecture/test_post_m409_1_rc_1_governed_structural_knowledge_transfer_candidate_v1.py`

**Representative documentation:** -
`docs/INTEGRATION_NOTE_RC_1_3_GOVERNED_TRANSFER_INSTANTIATION_PACKAGE_V1.md` -
`docs/INTEGRATION_NOTE_RC_1_4_GOVERNED_TRANSFER_ADMISSION_GUARD_V1.md` -
`docs/INTEGRATION_NOTE_RC_1_GOVERNED_STRUCTURAL_KNOWLEDGE_TRANSFER_CANDIDATE_V1.md`

**Exact residual / surgical rule:** No crear Analogy Engine. Futuro
residual: mapping de conceptos jerárquicos ricos.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-09 --- Epistemic evaluation

**Authority / owner boundary:**
`governed_reasoning + cognitive maturity evidence`\
**State:** **CLOSED / SUBSTANTIAL**

**Primary implementation anchors:** -
`core/governed_reasoning/epistemic_sufficiency.py` -
`core/governed_reasoning/derived_epistemic_assessment.py` -
`core/cognitive_maturity/epistemic.py` -
`core/cognitive_maturity/unified_epistemic_evidence.py`

**Representative contractual evidence:** -
`tests/architecture/test_hce_canonical_hypothesis_bearing_epistemic_episode_binding_metacognitive_closure_wave.py` -
`tests/architecture/test_hce_final_productive_epistemic_strategy_metacognitive_orchestration_closure_wave.py` -
`tests/architecture/test_m386_2_epistemic_levels.py` -
`tests/architecture/test_m388_3_productive_epistemic_classification.py` -
`tests/architecture/test_m389_1_epistemic_consistency.py` -
`tests/architecture/test_m389_8_unified_epistemic_evidence.py` -
`tests/architecture/test_post_m409_1_governed_epistemic_curiosity_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_epistemic_sufficiency_assessment_foundation_v1.py`

**Representative documentation:** -
`docs/HIGHER_COGNITIVE_EVOLUTION_CANONICAL_HYPOTHESIS_BEARING_EPISTEMIC_EPISODE_BINDING_METACOGNITIVE_CLOSURE_WAVE.md` -
`docs/HIGHER_COGNITIVE_EVOLUTION_FINAL_PRODUCTIVE_EPISTEMIC_STRATEGY_METACOGNITIVE_ORCHESTRATION_CLOSURE_WAVE.md` -
`docs/M389_8_UNIFIED_EPISTEMIC_EVIDENCE.md` -
`docs/POST_M409_1_GOVERNED_EPISTEMIC_CURIOSITY_FOUNDATION_V1.md` -
`docs/POST_M409_1_GOVERNED_EPISTEMIC_SUFFICIENCY_ASSESSMENT_FOUNDATION_V1.md` -
`docs/POST_M409_1_GOVERNED_EPISTEMIC_SUFFICIENCY_PRODUCTIVE_CONSUMPTION_V1.md`

**Exact residual / surgical rule:** Reutilizar estados/contratos
existentes antes de inventar nuevas taxonomías.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-10 --- Epistemic curiosity

**Authority / owner boundary:**
`cognitive maturity under governed lifecycle`\
**State:** **SUBSTANTIAL / PRODUCTIVE; explicit gap→topic-evidence reachability CLOSED / CERTIFIED — 12,399 PASS**

**Primary implementation anchors:** -
`core/cognitive_maturity/governed_epistemic_curiosity.py` -
`core/cognitive_maturity/hypothesis_gap_curiosity_evidence.py` -
`core/cognitive_maturity/curiosity_human_answer_evidence.py` -
`core/cognitive_maturity/curiosity_knowledge_admission_classification.py`

**Representative contractual evidence:** -
`tests/architecture/test_post_m409_1_curiosity_existing_m369_learning_evaluation_v1.py` -
`tests/architecture/test_post_m409_1_curiosity_human_answer_knowledge_candidate_v1.py` -
`tests/architecture/test_post_m409_1_curiosity_knowledge_admission_classification_v1.py` -
`tests/architecture/test_post_m409_1_curiosity_relevance_initiative_consumption_v1.py` -
`tests/architecture/test_post_m409_1_governed_epistemic_curiosity_foundation_v1.py` -
`tests/architecture/test_post_m409_1_hypothesis_gap_curiosity_evidence_adapter_foundation_v1.py` -
`tests/architecture/test_post_m409_1_hypothesis_gap_curiosity_unreached_productive_composition_retirement.py` -
`tests/architecture/test_epistemic_gap_governed_topic_curiosity_runtime.py` -
`tests/architecture/test_post_m409_1_productive_conversational_curiosity_wiring_v1.py`

**Representative documentation:** -
`docs/POST_M409_1_CURIOSITY_EXISTING_M369_LEARNING_EVALUATION_V1.md` -
`docs/POST_M409_1_CURIOSITY_HUMAN_ANSWER_EVIDENCE_KNOWLEDGE_CANDIDATE_V1.md` -
`docs/POST_M409_1_CURIOSITY_KNOWLEDGE_ADMISSION_CLASSIFICATION_V1.md` -
`docs/POST_M409_1_CURIOSITY_RELEVANCE_INITIATIVE_CONSUMPTION_V1.md` -
`docs/POST_M409_1_GOVERNED_EPISTEMIC_CURIOSITY_FOUNDATION_V1.md` -
`docs/POST_M409_1_HYPOTHESIS_GAP_CURIOSITY_EVIDENCE_ADAPTER_FOUNDATION_V1.md`

**Current explicit reachability candidate:**
`app/epistemic_gap_governed_topic_curiosity_runtime.py` composes an existing governed
information item with an exact `HypothesisEpistemicGap` evidence reference, then reuses
the existing Relevance, Curiosity, Initiative and Conversation authorities. It fails
closed when topic evidence is not source-declared or cannot be proven in the gap lineage.
It performs no topic inference and does not restore the retired historical compositor.

**Exact residual / surgical rule:** After owner certification, treat the explicit
gap + governed-topic-evidence boundary as productively reachable. Future CAP-10 work is
intellectual depth (concept/theory gaps, prioritization, redundancy suppression and
long-investigation continuity), not another curiosity engine or generic topic classifier.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-11 --- Multi-step investigation

**Authority / owner boundary:**
`Planning + authorization + execution + reasoning re-entry`\
**State:** **SUBSTANTIAL / BOUNDED**

**Primary implementation anchors:** -
`app/governed_multistep_investigation_episode.py` -
`app/governed_independence_authorization_boundary.py` -
`app/governed_level2_read_only_execution_gateway.py` -
`app/governed_level2_reasoning_reentry.py` -
`app/planning_foundation.py`

**Representative contractual evidence:** -
`tests/architecture/test_post_m409_1_governed_multistep_investigation_authorization_reentry_v1.py` -
`tests/architecture/test_post_m409_1_governed_multistep_investigation_episode_foundation_v1.py` -
`tests/architecture/test_post_m409_1_governed_multistep_investigation_execution_reentry_v1.py` -
`tests/architecture/test_post_m409_1_governed_multistep_investigation_planning_reentry_v1.py` -
`tests/architecture/test_post_m409_1_governed_multistep_investigation_productive_continuation_v1.py` -
`tests/architecture/test_post_m409_1_governed_multistep_investigation_reasoning_closure_v1.py`

**Representative documentation:** -
`docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_A2_LEVEL2_READ_ONLY_EXECUTION_E2_PRODUCTIVE_REENTRY_V1.md` -
`docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_CONTINUATION_EVIDENCE_ACQUISITION_PLANNING_PRODUCTIVE_REENTRY_V1.md` -
`docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_E2_REASONING_REENTRY_2_MANDATORY_EPISODE_CLOSURE_V1.md` -
`docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_EPISODE_STOPPING_BOUNDARY_FOUNDATION_V1.md` -
`docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_P2_INDEPENDENCE_AUTHORIZATION_A2_PRODUCTIVE_REENTRY_V1.md` -
`docs/POST_M409_1_GOVERNED_MULTISTEP_INVESTIGATION_PRODUCTIVE_CONTINUATION_V1.md`

**Exact residual / surgical rule:** Profundizar horizonte, replanning,
resumability y stopping; no crear segundo planner.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-12 --- Governed learning

**Authority / owner boundary:** `Learning authority + memory_gateway`\
**State:** **SUBSTANTIAL / PERSISTENT WHEN APPROVED**

**Primary implementation anchors:** - `core/learning_foundation.py` -
`core/safe_learning_policies.py` - `core/learning_stabilization.py` -
`app/governed_relational_abstraction_learning_bridge.py`

**Representative contractual evidence:** -
`tests/test_m369_1_learning_foundation.py` -
`tests/test_m369_6_safe_learning_policies.py` -
`tests/test_m369_7_learning_stabilization.py`

**Representative documentation:** -
`docs/M369_1_LEARNING_FOUNDATION.md` -
`docs/M369_6_SAFE_LEARNING_POLICIES.md` -
`docs/M369_7_LEARNING_STABILIZATION.md`

**Exact residual / surgical rule:** Autonomía de admisión aún no
equivale a aprendizaje irrestricto; no crear otro learning store.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-13 --- Strategy & metacognition

**Authority / owner boundary:**
`unified_cognitive_coordination / existing HCE owners`\
**State:** **CLOSED / TRANSIENT**

**Primary implementation anchors:** -
`core/governed_reasoning/comparative_reasoning_method_awareness.py` -
`core/governed_reasoning/reasoning_method_effectiveness_awareness.py` -
`core/governed_reasoning/historical_method_advisory.py`

**Representative contractual evidence:** -
`tests/architecture/test_cci_05_governed_historical_reasoning_method_advisory.py` -
`tests/architecture/test_hce_abstraction_approved_learning_later_novel_reuse.py` -
`tests/architecture/test_hce_canonical_hypothesis_bearing_epistemic_episode_binding_metacognitive_closure_wave.py` -
`tests/architecture/test_hce_canonical_productive_reasoning_episode_unification_wave.py` -
`tests/architecture/test_hce_final_productive_epistemic_strategy_metacognitive_orchestration_closure_wave.py` -
`tests/architecture/test_hce_governed_explicit_hypothesis_source_selective_reachability_wave.py` -
`tests/architecture/test_hce_governed_novel_strategy_synthesis_wave.py` -
`tests/architecture/test_hce_governed_productive_strategy_adaptation_wiring_wave.py`

**Representative documentation:** -
`docs/CCI_05_GOVERNED_HISTORICAL_REASONING_METHOD_ADVISORY.md` -
`docs/HIGHER_COGNITIVE_EVOLUTION_CANONICAL_HYPOTHESIS_BEARING_EPISTEMIC_EPISODE_BINDING_METACOGNITIVE_CLOSURE_WAVE.md` -
`docs/HIGHER_COGNITIVE_EVOLUTION_FINAL_PRODUCTIVE_EPISTEMIC_STRATEGY_METACOGNITIVE_ORCHESTRATION_CLOSURE_WAVE.md` -
`docs/HIGHER_COGNITIVE_EVOLUTION_GOVERNED_STRATEGY_APPLICATION_OUTCOME_EVIDENCE_WAVE.md` -
`docs/HIGHER_COGNITIVE_EVOLUTION_STRATEGY_OUTCOME_METACOGNITIVE_ADAPTATION_WAVE.md` -
`docs/INTEGRATION_NOTE_COMPARATIVE_REASONING_METHOD_AWARENESS_FOUNDATION_V1.txt`

**Exact residual / surgical rule:** HCE congelado. Persistencia
metacognitiva durable sería una nueva decisión de Learning, no un
residual.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-14 --- Self diagnostics & improvement proposals

**Authority / owner boundary:**
`self_diagnostics + governed app proposal boundary`\
**State:** **SUBSTANTIAL / HUMAN-PROMOTED**

**Primary implementation anchors:** - `core/self_diagnostics/` -
`app/self_improvement_proposal_generation.py`

**Representative contractual evidence:** -
`tests/architecture/test_m399_8_governed_self_diagnostics_stabilization_closure.py` -
`tests/architecture/test_post_m409_1_governed_self_improvement_proposal_generation.py` -
`tests/test_m399_2_governed_self_diagnostics_foundation.py`

**Representative documentation:** -
`docs/M399_2_GOVERNED_SELF_DIAGNOSTICS_FOUNDATION.md` -
`docs/M399_8_GOVERNED_SELF_DIAGNOSTICS_STABILIZATION_CLOSURE.md` -
`docs/POST_M409_1_ADVANCED_CAPABILITY_2B_GOVERNED_SELF_IMPROVEMENT_PROPOSAL_GENERATION.md` -
`docs/quality/M399_2_SELF_DIAGNOSTICS_FOUNDATION.json` -
`docs/quality/M399_8_SELF_DIAGNOSTICS_CLOSURE.json`

**Exact residual / surgical rule:** Puede profundizar hacia patch
candidates; no autorizar autopromoción ni modificación de authorities.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-15 --- Reflection / self-model

**Authority / owner boundary:** `Reflection authority`\
**State:** **SUBSTANTIAL / FUNCTIONAL**

**Primary implementation anchors:** -
`core/cognitive_maturity/conversation_reflection.py` -
`core/cognitive_maturity/periodic_reflection.py` -
`core/cognitive_maturity/explicit_inner_continuity.py` -
`core/cognitive_maturity/functional_psychology.py`

**Representative contractual evidence:** -
`tests/architecture/test_m382_7_post_turn_reflection_observer.py` -
`tests/architecture/test_m387_8_post_turn_reflection_learning.py` -
`tests/architecture/test_m389_2_conversation_reflection.py` -
`tests/architecture/test_m389_4_functional_psychology.py` -
`tests/architecture/test_m389_6_periodic_reflection.py` -
`tests/architecture/test_m390_3_explicit_inner_continuity_architecture.py` -
`tests/architecture/test_m390_7_inner_state_reflection_architecture.py` -
`tests/test_m193_reflection_runtime_integration.py`

**Representative documentation:** -
`docs/M193_REFLECTION_RUNTIME_INTEGRATION.md` -
`docs/M389_4_FUNCTIONAL_PSYCHOLOGY.md` -
`docs/M389_6_PERIODIC_REFLECTION.md` -
`docs/M390_3_EXPLICIT_INNER_CONTINUITY.md` -
`docs/M390_7_INNER_STATE_REFLECTION.md` -
`docs/RP_13_COGNITIVE_REFLECTION_ENGINE.md`

**Exact residual / surgical rule:** Profundizar continuidad funcional
sin afirmar consciencia subjetiva.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-16 --- Local document intelligence

**Authority / owner boundary:** `existing document services`\
**State:** **FOUNDATION**

**Primary implementation anchors:** - `core/document_intelligence/` -
`core/document_extraction/` - `core/document_classification/` -
`core/document_actions/`

**Representative contractual evidence:** -
`tests/test_m340_4_document_reading.py` -
`tests/test_m355_document_classification.py` -
`tests/test_m355_document_classification_contract.py` -
`tests/test_m356_structured_document_extraction.py` -
`tests/test_m356_structured_document_extraction_contract.py` -
`tests/test_m358_document_intelligence.py` -
`tests/test_m358_document_intelligence_contract.py`

**Representative documentation:** -
`docs/M355_DOCUMENT_CLASSIFICATION.md` -
`docs/M356_STRUCTURED_DOCUMENT_EXTRACTION.md` -
`docs/M358_DOCUMENT_INTELLIGENCE.md`

**Exact residual / surgical rule:** Foundation para Biblioteca; falta
catálogo/indexación de colección completa y retrieval por colección.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-17 --- Personal Biblioteca

**Authority / owner boundary:**
`GovernedLocalLibraryCatalogueV1 + DocumentReading + Knowledge + governed_reasoning + CAP-11 Episode`\
**State:** **PRODUCTIVE / GOVERNED READ-ONLY EVIDENCE SOURCE — CERTIFIED THROUGH REQUIREMENT CONTINUATION**

**Primary implementation anchors:** - `core/governed_local_library/` -
`app/document_reading.py` - `app/knowledge_runtime.py` -
`app/unified_retrieval_execution_runtime.py` -
`app/governed_local_library_runtime_wiring.py` -
`app/governed_local_evidence_reasoning_reentry.py` -
`app/governed_multistep_investigation_episode.py` -
`app/governed_long_horizon_investigation_reassessment_requirement_admission.py` -
`core/governed_reasoning/hypothesis_deepening.py`

**Representative contractual evidence:** -
`tests/architecture/test_cap17_governed_local_library_catalogue_contract_red.py` -
`tests/architecture/test_cap17_library_selected_document_knowledge_handoff_red.py` -
`tests/architecture/test_cap17_execution_scoped_local_selection_unified_runtime_red.py` -
`tests/architecture/test_cap17_library_conversational_access_user_initiated_ambiguity_red.py` -
`tests/architecture/test_cap17_cap11_governed_local_evidence_episode_recording_red.py` -
`tests/architecture/test_cap17_cap11_governed_evidence_hypothesis_reassessment_requirement_continuation_contract_red.py`

**Current implementation boundary:** read-only metadata catalogue over one explicitly
authorized injected root; explicit-selection handoff to the existing document reader;
one-shot execution-scoped transport into Unified Retrieval; governed Knowledge and
Reasoning re-entry; recording of local evidence in the existing CAP-11 Episode under
the shared acquisition budget; same-hypothesis reassessment by the canonical
`governed_reasoning` authority; and admission of zero/one next discriminating
requirement through the existing CAP-11 continuation authority. Exact hypothesis
product provenance is preserved through `source_report_id`. STOP remains before any
new Planning step. No Memory/Learning side effects.

**Exact residual / surgical rule:** CAP-17/CAP-11 local evidence continuation is closed
through existing requirement continuation. Any later durable learning/consolidation is
a separate governed admission problem. Do not connect Biblioteca directly to
Memory/Learning and do not create another Reasoning, Planning, retrieval or Episode
authority.

**Certified baseline:** **13.928 PASS + Ruff limpio + 0 FAIL**.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-18 --- Personal visual collection / "Pinacoteca" (provisional name)

**Authority / owner boundary:** `ImageRepository + GovernedVisionGateway + OfficialVisionCore`\
**State:** **PRODUCTIVE FOUNDATION / EXPLICIT USER-INITIATED STORED-IMAGE ACCESS WIRED TO OFFICIAL RUNTIME**

**Existing canonical implementation anchors:** - `core/governed_image_repository.py` -
`infrastructure/vision/file_image_repository.py` - `core/intelligent_vision/` -
`app/vision_core.py` - `app/vision_gateway.py` -
`core/cognitive_runtime_orchestration/visual_context.py`

**Representative contractual evidence:** - `tests/test_rp248_intelligent_vision.py` -
`tests/test_m348_9_vision_core.py` - `tests/test_m362_governed_vision_gateway.py` -
`tests/architecture/test_post_hcpdq_unified_multimodal_visual_to_cognitive_bridge_challenge.py`

**Nomenclature rule:** "Pinacoteca" remains provisional for personal
photographs/images/art. Historical music/audio meaning is superseded; music/audio is a
separate capability family if retained in scope.

**Current certified boundary:** GATE 3.B.1 and GATE 3.B.2 close the stored-image
selection and official-runtime reachability seam. `ImageRepository.read_asset(...)`
performs owner-scoped transient asset access with SHA-256 integrity verification;
`GovernedVisionGateway.analyze_stored_image(...)` reuses the existing
`OfficialVisionCore` without camera-capture semantics; and the official runtime exposes
one `vision.stored_images.read_analyze` capability using exact `image_id`, explicit
request and fresh consent.

**Exact residual / surgical rule:** **ZERO inside the GATE 3 visual-source boundary.**
Do not create a Pinacoteca manager, second repository, second Vision Core/Gateway,
background scanner, biometrics, or automatic Memory/Learning/Reasoning. Any later
cross-source cognition or durable learning is a separate governed gate.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, privacy/provenance boundary, and all tests
protecting the touched contract before editing.

------------------------------------------------------------------------

### CAP-19 --- Cross-domain knowledge synthesis

**Authority / owner boundary:** `Knowledge + Reasoning`\
**State:** **SUBSTANTIAL / SEMANTIC-DOMAIN ADMISSION REACHABILITY CLOSED / CERTIFIED — 12,440 PASS**

**Primary implementation anchors:** - `core/governed_reasoning/cross_domain_concept_synthesis.py`
- `app/governed_reasoning_runtime.py`
- `app/semantic_domain_cross_domain_binding.py` (owner-certified at 12,440 PASS).

**Representative contractual evidence:** -
`tests/test_m204_cross_domain_coordination.py`

**Representative documentation:** -
`docs/M204_CROSS_DOMAIN_COORDINATION.md` -
`docs/adr/ADR_204_cross_domain_coordination.md`

**Certified closure:** The synthesis authority already exists. The certified semantic-domain admission seam admits only registered, explicit, concept-bound evidence into the existing productive cross-domain binding. Ordinary autonomous domain classification remains outside this boundary.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

### CAP-20 --- Governed autonomous knowledge admission

**Authority / owner boundary:** `Learning`\
**State:** **MISSING AS AUTONOMOUS ADMISSION**

**Primary implementation anchors:** - No single productive owner
equivalent identified in this audit; resolve against foundations before
creating one.

**Representative contractual evidence:** -
`tests/architecture/test_post_m409_1_curiosity_knowledge_admission_classification_v1.py`

**Representative documentation:** -
`docs/POST_M409_1_CURIOSITY_KNOWLEDGE_ADMISSION_CLASSIFICATION_V1.md`

**Exact residual / surgical rule:** Diseñar por clases de riesgo,
provenance y reversibilidad; prohibir authority/self-promotion changes.

**Pre-change requirement:** identify public API/import surface,
productive caller(s), mutation/writer path, and all tests protecting the
touched contract before editing.

------------------------------------------------------------------------

## 5. Legacy / out-of-direction families

**Current retirement status:** the Android executable island is **CLOSED / CERTIFIED** at **13,746 PASS · 0 FAIL · Ruff clean**. The Mobile/Hands-Free/Driving executable lineage is also **CLOSED / CERTIFIED** at **13,209 PASS · 0 FAIL · Ruff clean** after its separate reachability review proved `driving.runtime` composition-reachable but not productively consumed. The Residential/MINI-PC/distributed-residence lineage is also **CLOSED / CERTIFIED** at **12,534 PASS · 0 FAIL · Ruff clean** after governed retirement of the distributed-residence executable lineage. Neutral `OfficialDeviceGateway`, Device Runtime, Presence, ResidentComponentRegistry, local Web Panel, InformationClassification, Camera/Vision, ExternalResourceRegistry and Household surfaces remain protected.

The current laptop-only direction marks
Android/mobile/residential/distributed-device expansion as **LEGACY /
OUT OF SCOPE for future growth**. The repository still contains families
such as:

-   `core/android_bridge/`
-   historical Mobile/Hands-Free/Driving families M110→M121 and RP249 — **retired / certified**
-   Residence/Connectivity/PhysicalTransport/Synchronization/Residential Node/Residential Perception/Remote Presence — **RETIRED / HISTORICAL — CLOSED / CERTIFIED**
-   neutral current Device/Presence/Resident/Web Panel infrastructure — **protected / current**.

**Rule:** do not extend these families merely because they exist. Also
do not delete them by roadmap decision alone. Removal requires import
graph + composition-root + runtime reachability + tests +
persistence/config compatibility audit.

------------------------------------------------------------------------

## 6. Surgical Change Record --- mandatory template

Every future code change should create/fill a record like this before
implementation:

  -----------------------------------------------------------------------
  Field                               Required answer
  ----------------------------------- -----------------------------------
  Requested behavior                  What must ROBY be able to do that
                                      it cannot do now?

  Registry capability                 CAP-XX or genuinely new candidate

  Current state                       CLOSED / SUBSTANTIAL / FOUNDATION /
                                      MISSING / LEGACY

  Canonical authority                 Exact existing owner

  Existing foundations                Files/classes/contracts already
                                      performing part of behavior

  Productive entry                    Where real runtime can reach it

  Productive consumer                 Who consumes the canonical result

  Writers                             What state can be mutated

  Persistence owner                   Memory/Learning/other legitimate
                                      boundary, or NONE

  Contract tests                      Exact tests that protect current
                                      behavior

  Documentation contracts             Root/milestone docs that must
                                      remain synchronized

  Residual                            Behavioral sentence, not a desired
                                      class/module name

  RED evidence                        Test proving the residual exists

  Minimum change                      Smallest owner extension that
                                      closes the residual

  Forbidden duplication               Existing components that must not
                                      be recreated

  Promotion gate                      Focused tests → `ruff check .` →
                                      full `pytest -q`

  Rollback                            Files/behavior to revert if gate
                                      fails
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 7. Modification classes

### Class 0 --- Documentation-only

No productive code change. Still inspect contractual documentation tests
and protected headers.

### Class 1 --- Internal refactor

No behavior/authority/reachability/persistence change. Requires
equivalence tests and full gates.

### Class 2 --- Existing capability deepening

Preferred cognitive evolution path. Extend the canonical owner and prove
the residual with RED evidence.

### Class 3 --- New instrumental capability

Example: governed Biblioteca catalogue or personal visual collection selection.
It may add infrastructure but must consume existing cognitive
authorities rather than become another brain.

### Class 4 --- New cognitive primitive

Highest scrutiny. Requires proof that no current authority/foundation
can represent the behavior. Must be integrated into the existing
owner/lifecycle.

### Class 5 --- Authority/persistence migration

Exceptional. Requires explicit migration design, retirement of the
former owner, compatibility plan, tests, docs, and zero parallel
authority after promotion.

------------------------------------------------------------------------

## 8. Test governance

Tests are architectural evidence, not obstacles to make green by
weakening assertions.

When a change fails tests:

1.  classify each failure as contract violation, legitimate expected
    evolution, stale test, or unrelated regression;
2.  inspect why the test exists;
3.  preserve historical/root-document contracts unless an explicit
    migration authorizes their change;
4.  never modify tests merely to accommodate a preferred implementation;
5.  run focused affected tests;
6.  run `ruff check .`;
7.  run complete `pytest -q`.

Historical registry reconciliation baseline is **12,471 PASS · 0 FAIL · Ruff clean**.
Current operative baseline is owned by `ROBY_XI_2_CURRENT_TRUTH.md`.

------------------------------------------------------------------------

## 9. Documentation governance

Before promotion, reconcile:

-   `README.md`
-   `CHANGELOG.md`
-   `CHANGELOG_ARCHITECTURE.md`
-   `docs/history/ESTADO_MAESTRO_INTEGRAL.md` — accumulated historical master-state trace; present-state authority is `ROBY_XI_2_CURRENT_TRUTH.md`
-   `VISION.md`
-   `architecture_rules.md`
-   `integration_decision.md`
-   `INVENTARIO_COGNITIVO_INTEGRAL_ROBY_XI_2.md`
-   the Cognitive Inventory Reconciliation Master Surgical Guide
-   this Master Capability Registry
-   capability-specific closure/audit documents.

Protected historical first-line/header contracts must be preserved
unless a deliberate migration changes the tests and documentation
constitution together.

------------------------------------------------------------------------

## 10. Immediate roadmap control

Before implementing further source/collection capabilities, use this registry in this order:

1.  **CAP-07 Relational abstraction / concept foundation** --- map exact
    public classes, callers and tests.
2.  **CAP-08 Structural transfer** --- prove the new concept work does
    not recreate existing transfer/analogy behavior.
3.  **CAP-09 Epistemic evaluation** --- reuse current
    sufficiency/abstention semantics.
4.  **CAP-12 Governed learning** --- keep first concept candidate
    transient; do not add persistence accidentally.
5.  **CAP-16 Local document intelligence** --- foundation for
    Biblioteca.
6.  **CAP-17 Biblioteca** --- new collection/index capability, source
    only.
7.  **CAP-18 Personal visual collection / Pinacoteca (provisional)** ---
    existing storage/vision authorities; contract explicit selection and governed
    stored-image analysis before any productive expansion.

------------------------------------------------------------------------

## 11. Registry maintenance rule

This file becomes a living architectural index.

A promoted capability change must update its CAP card with:

-   new/retired owner files;
-   productive entry/caller;
-   persistence changes;
-   new contract tests;
-   new canonical docs;
-   maturity state;
-   residuals still intentionally open.

A capability is not considered architecturally promoted if code and
tests pass but this registry still describes the old
ownership/reachability model.

------------------------------------------------------------------------

## 12. Certification boundary

This first registry is **evidence-based but not a complete
static-call-graph certification of every file**. It records the
canonical map and representative anchors found in the certified
repository. Before deleting, merging, or moving a specific
implementation, perform a focused import/call/reachability audit for
that target.

That limitation is intentional: the registry must prevent false
certainty as well as duplication.

------------------------------------------------------------------------

## 13. Master decision

From this baseline onward:

> **No new ROBY implementation or modification should proceed without
> first locating its CAP entry and completing the Surgical Change
> Record.**

If no CAP entry exists, the first task is not coding. The first task is
to prove whether the requested behavior is truly **MISSING**, or already
**FOUNDATION / SUBSTANTIAL / LEGACY** under another name.

This is the permanent anti-redundancy control for the next cognitive and
intellectual evolution of ROBY XI.2.


### HCC Productivo Ordinario — closure update

CAP-07 ordinary productive reachability now closes the path from distinct canonical
R1/R2 abstraction episodes to the existing governed HCC composer and canonical
productive concept episode. The runtime gateway performs only bounded,
session/scope-local orchestration; it does not own concept semantics or introduce a
new cognitive authority. Same-family repetition cannot fabricate HCC diversity.
Learning, Memory and Structural Transfer remain outside this path.


### CAP-08 — Rich Hierarchical Structural Analogy update

CAP-08 now includes bounded read-only comparison of two canonical productive HCC
concept episodes through `GovernedHierarchicalStructuralAnalogyMatcher`. It matches
multi-component relation/outcome structure and HCC link topology while preserving
exact scope and provenance. This extends the existing structural-transfer owner; it
does not replace `GovernedStructuralKnowledgeTransferMatcher`, instantiate a rule,
admit transfer, persist results, create Learning/Memory, or authorize inference or
action. The existing RC-1 transfer chain remains the sole executable structural
transfer path.


### Productive Hierarchical Analogy — reasoning contribution update

CAP-08 hierarchical structural analogy is now ordinarily reachable through the
official governed reasoning runtime. The gateway compares the latest prior canonical
HCC concept with a new concept only inside exact owner/session/scope, reuses the
existing `GovernedHierarchicalStructuralAnalogyMatcher`, and exposes only valid
analogy candidates as same-turn consultative reasoning context. No new authority,
persistence, Memory, Learning, executable Structural Transfer, rule registration or
action path is introduced.

### CAP-05 — Explanatory Model Composition update

CAP-05 now includes bounded multi-hypothesis explanatory model composition under the
existing `governed_reasoning` authority. It reuses hypothesis deepening and existing
multi-hypothesis discrimination, preserves component-local evidence/gaps and pairwise
relations, and exposes only consultative productive context. No Theory Engine, second
hypothesis authority, persistence, Memory, Learning, truth/causality promotion,
Structural Transfer or action path is introduced.

### Ordinary Multi-Hypothesis Reachability update

CAP-05 explanatory composition is now ordinarily reachable from multiple distinct
explicit structured hypothesis sources accumulated only within exact
owner/session/world-snapshot scope. The official governed reasoning runtime reuses
the existing scenario/causal foundations, hypothesis deepening, discrimination and
explanatory composer. Semantic duplicates do not create diversity. No hypothesis
generator, new authority, persistence, Memory, Learning, truth establishment,
transfer execution or action path is introduced.

### Explanatory Model → Discriminating Inquiry → Investigation Re-entry update

La salida multi-hipótesis ordinaria puede ahora entregar un único
`DiscriminatingEvidenceRequirement` exacto al boundary Post-M409 de investigación
existente. La composición conserva reasoning/source/world-snapshot lineage y no crea
Curiosity, Planner, Investigation Engine ni autoridad paralela. La re-entry sólo abre
el episodio bounded y lo deja elegible para planning existente; no planifica,
autoriza, ejecuta, adquiere evidencia, aprende ni inicia procesos de fondo.


## CAP-19 — Cross-Domain Concept Synthesis — Productive Reachability

- Authority: `governed_reasoning`; knowledge sourcing remains `knowledge_runtime`.
- Status: productively reachable, bounded, consultative.
- Explicit distinct-domain provenance is preserved independently of HCC scope.
- Cross-domain correspondence does not establish truth, causality, inference, transfer, learning, memory or action.
- Certified CAP-19 semantic-domain admission seam (owner gate 12,440 PASS): registered canonical evidence must explicitly carry `semantic_domain`, exact `session_id`, and exact `concept_episode_id` before the existing binding can be invoked.
- Source kind, scope domain, cognitive domain, interest topic, free tags and unregistered strings are not semantic-domain authority.
- This seam adds no taxonomy engine, persistence, autonomous classification, learning or action authority. Documentary certification is closed on owner gate 12,440 PASS · 0 FAIL · Ruff clean.

## CAP-05 update — Evidence-driven Explanatory Model Revision

- **Authority:** `governed_reasoning` (existing owner; no new engine).
- **Productive chain:** Explanatory Model V1 → acquired discriminating evidence re-entry → same-hypothesis reassessment → revised discrimination → Explanatory Model V2 → consultative Reasoning.
- **Admission:** exact V1 requirement/source/snapshot lineage, exact hypothesis-set preservation, acquired evidence must reach reassessment, and a material model change is required.
- **Fail-closed:** no successful re-entry, lineage mismatch, evidence not applied, hypothesis replacement, non-candidate V2, or no material change.
- **Governance:** read-only/consultative; no truth, causality, Memory, World Model, Learning, Structural Transfer, rule registration, action, persistence, or new authority.


## CAP-06 update — Advanced Counterfactual / Multi-stage Causal Deliberation

- **Authority:** `governed_reasoning`; no Counterfactual Engine ni causal authority paralela.
- **Productive chain:** explicit causal stages → governed multi-stage causal path → governed counterfactual path comparison → consultative Reasoning.
- **Continuity:** downstream cause must match the previous stage effect exactly after normalization.
- **Uncertainty:** unresolved upstream stages block downstream promotion; hypothetical intermediate outcomes never become World Model facts.
- **Comparison:** requires at least two distinct valid paths under the same owner/session/baseline and preserves path/relation lineage and stage divergences.
- **Governance:** read-only/consultative; no truth, causality proof, probability calibration, Memory, World Model writes, Learning, Planning mutation, rules, Structural Transfer, execution, action or new authority.


## Long-horizon Investigation Continuity update

- **Owner boundary:** extensión pasiva del lifecycle de investigación existente; Planning permanece en `planning_foundation`.
- **Productive state:** `GovernedInvestigationEpisodeState` puede convertirse en un checkpoint durable pasivo y luego en un `GovernedInvestigationResumeCandidate`.
- **Temporal lineage:** snapshot previo y snapshot actual se conservan por separado; un cambio exige review explícito.
- **Fail-closed:** source mismatch, inquiry resuelta y budget histórico agotado no se reactivan silenciosamente.
- **Governance:** no autopersistencia, Memory/World Model writes, Planning mutation, background process, capability invocation, execution, Reasoning rerun o nueva autoridad.
- **Residual siguiente:** Resume Candidate → existing Planning/Authorization/Re-entry → Model Vn+1.


## Long-horizon Investigation Resume Admission update

- **Owner boundary:** extensión de continuidad de investigación; Planning permanece en `planning_foundation`.
- **Productive state:** checkpoint + resume candidate + exact `DiscriminatingEvidenceRequirement` pueden producir una admisión gobernada.
- **Semantic rebinding:** el requirement se recibe como objeto explícito; no se reconstruye ni inventa desde IDs.
- **Fail-closed:** checkpoint/thread/source/requirement/snapshot mismatch, inquiry no elegible o budget agotado no producen Planning eligibility.
- **Governance:** la admisión es read-only y no crea plans, authorization, execution, reasoning, Memory/World Model writes, background work, nuevos episodios o nueva autoridad.
- **Residual siguiente:** Resume Admission → Existing Evidence Acquisition Planning.

## CAP-11 Governed Horizon Generalization — constitutional RED

The certified two-acquisition cycle remains productive and unchanged. A RED contract now freezes the constitutional Episode/checkpoint generalization only: explicit governed budget `1..4` with historical default `2`, N-step `current_step`, generic budget-aware continuation/stopping, exact checkpoint step/budget continuity, and resume without budget growth. Step 3+ remains non-productive until a later governed reconciliation of the existing Planning/Authorization/Execution/Reasoning chain.

### CAP-11 — Governed Horizon Generalization: Episode/checkpoint GREEN

The Episode/budget/stopping authority remains `GovernedMultiStepInvestigationEpisodeBoundaryV1`. Its constitution now supports a finite governed budget `1..4` with historical default `2`, N-step `current_step`, generic budget-aware reentry/continuation, and exact passive checkpoint continuity. `GovernedLongHorizonInvestigationContinuityV1` carries and fingerprints the exact step/budget without changing either. The productive investigation chain remains certified only through the historical two-acquisition RR2 terminal closure; P3/A3/E3/RR3 remain residual and non-productive pending separate reconciliation.

### CAP-11 — Productive Continuation step N → Existing Planning re-entry: reconciled residual
The Episode/checkpoint constitution can now represent step N under the finite governed budget. The next productive residual does not require another Planning authority: `GovernedMultiStepInvestigationProductiveContinuationV1` and `GovernedMultiStepInvestigationPlanningReentryV1` already carry the required lineage and one-call Planning contract. Their only blocking specialization is historical eligibility fixed to step 2 / one remaining acquisition. The next RED must generalize those guards from Episode invariants while preserving the two-acquisition path exactly. The long-horizon P2 adapter stays step-2-specific; Authorization/Execution/Reasoning N-step remain residual.

### CAP-11 — Productive Continuation step N → Existing Planning re-entry: contractual RED
The RED contract now freezes the exact N-step Planning continuation residual. Existing Productive Continuation and Planning Re-entry remain the sole owners; no new planner is permitted. The future GREEN may generalize only their historical step-2 eligibility guards so valid Episode steps 2..4 can reach the existing Planning surface once. Historical step-2/budget-2 behavior remains a compatibility requirement. Authorization/Execution/Reasoning N-step are explicitly outside this block.

### CAP-11 — Productive Continuation step N → Existing Planning re-entry: GREEN
Los owners existentes `GovernedMultiStepInvestigationProductiveContinuationV1` y `GovernedMultiStepInvestigationPlanningReentryV1` quedan generalizados para steps gobernados dentro del budget constitucional, reutilizando exactamente la Planning existente. El path histórico step-2/budget-2 permanece compatible. El resultado PLANNABLE sólo declara elegibilidad para Authorization; A3/A4, Execution y Reasoning N-step siguen fuera de este bloque y no se introduce segunda autoridad.


### CAP-11 RED — Planning step N → existing Authorization re-entry

RED contractual: reuse the existing Authorization re-entry owner for governed step N; preserve P2/A2; STOP before Execution.


### CAP-11 GREEN — Planning step N → existing Authorization re-entry

Existing Authorization re-entry owner generalized structurally to governed step N; no second authority and no Execution invocation.

### CAP-11 — Authorization step N → existing Execution re-entry — reconciliación

Residual confirmado: generalizar `GovernedMultiStepInvestigationExecutionReentryV1` desde E2 terminal a adquisición autorizada step N, reutilizando el mismo Level2 read-only gateway y Episode Boundary. Sin segundo executor; STOP antes de Reasoning re-entry.


### CAP-11 RED — Authorization step N → existing Execution re-entry

RED contractual: reuse the existing Execution re-entry owner for governed step N; preserve A2/E2; STOP before Reasoning re-entry.


### CAP-11 GREEN — Authorization step N → existing Execution re-entry

Existing Execution re-entry owner generalized to governed step N. A2/E2 remains supported; STOP before Reasoning re-entry.


### CAP-11 — Execution step N → existing Reasoning re-entry — reconciliation

Existing Reasoning and Episode authorities are sufficient; residual is generalization of the current terminal RR2 integration owner. STOP before next requirement.


### CAP-11 — Execution step N → existing Reasoning re-entry — RED

Contract requires the existing Reasoning re-entry + Episode owner path to support intermediate RR3 and terminal RR4 while preserving RR2 and stopping before R(N+1).


### CAP-11 — Execution step N → existing Reasoning re-entry — GREEN

Existing Reasoning + Episode authorities now support intermediate and terminal N-step re-entry. STOP remains before the next requirement.

### CAP-11 — RR(N) → R(N+1) discriminante

Reconciliado. Residual: generalizar la admisión histórica RR1→R2 a step N sin nueva autoridad. STOP antes de Planning.

### CAP-17 — EPUB Library Reading Support — GREEN

- **Owner de lectura:** `DocumentReadingService` continúa como única autoridad para lectura de documentos locales; EPUB es un formato adicional, no una capacidad paralela.
- **Catálogo:** `GovernedLocalLibraryConfig` incluye `.epub` entre los sufijos permitidos por defecto.
- **Ruta:** selección explícita → `DocumentReadingService` → handoff/bound retriever existente → Unified Retrieval Runtime → `KnowledgeRetrievalArtifact` → STOP.
- **Seguridad:** lectura ZIP en memoria, OPF/spine, 512 miembros máximo, 8.000.000 bytes descomprimidos máximo, rechazo de traversal y sin extracción al filesystem.
- **Fuera de alcance:** DRM, OCR, embeddings, indexación global, Memory/Learning, background scanning y productive ROBY proposal source.

### CAP-17 — Cognitive Evidence Need → Local Library Proposal — GREEN

- **Reasoning authority:** existing `governed_reasoning` produces `DiscriminatingEvidenceRequirement`; CAP-17 does not create evidence needs.
- **Knowledge assessment authority:** `OfficialKnowledgeRuntimeGateway.assess_evidence_requirement(...)` converts the structured gap into one `KnowledgeSourceNeed` while preserving semantic query intent.
- **Source decision authority:** canonical `KnowledgeSourcePolicy`; Biblioteca dispatch occurs only for `LOCAL_SOURCE_PREFERRED`.
- **Instrumental bridge:** `GovernedCognitiveEvidenceToLocalLibraryBridgeV1`; preserves requirement/source/world-snapshot/source-decision lineage and never searches or reads the library directly.
- **Admission convergence:** `GovernedLocalLibraryConversationV1.handle_admitted_request(...)` is the neutral post-admission path shared by user and ROBY initiative.
- **Productive composition:** `GovernedLocalLibraryRuntimeWiring.cognitive_bridge` exists only when the authorized library is provisioned.
- **Guardrails:** no `KnowledgeRetrievalStep` schema change, no Memory/Learning, no background execution, no hardcoded personal root and no new planning/reasoning authority.

### CAP-17 — Productive cognitive library reachability
- `knowledge.local_library.read` puede ser alcanzado desde un `DiscriminatingEvidenceRequirement` productivo admitido mediante `GovernedProductiveReasoningLibraryBridgeContributorV1`.
- Autoridad del requisito: `governed_reasoning`; autoridad de fuente: `KnowledgeSourcePolicy`; autoridad de iniciativa: `GovernedIndependenceAuthorizationBoundaryV1`; ejecución documental: cadena CAP-17 existente.
- El contributor es composición instrumental del `CognitiveRuntimeOrchestrator` y no constituye una nueva autoridad.

### CAP-17/CAP-11 — Governed Local Evidence Episode Recording
- **Episode authority:** `GovernedMultiStepInvestigationEpisodeBoundaryV1` remains canonical.
- **Local lineage:** Unified Retrieval execution IDs are recorded in `local_execution_ids`; Level-2 plan/authorization/execution lineage is not synthesized.
- **Budget:** `consumed_acquisitions` counts both historical Level-2 and governed local-library acquisitions under the same episode hard cap.
- **Transition:** successful local re-entry → `AWAITING_REQUIREMENT` when budget remains, otherwise `CLOSED / BUDGET_EXHAUSTED`.
- **Productive path:** CAP-17 records only after its existing `GovernedLocalEvidenceReasoningReentryV1` result; no second Reasoning, retrieval, Memory or Learning authority is added.


### CAP-17/CAP-11 — Governed Evidence → Existing Hypothesis Reassessment → Requirement Continuation — GREEN

- **State:** **CERTIFIED / CLOSED** on baseline **13.928 PASS + Ruff limpio + 0 FAIL**.
- **Exact provenance:** `DiscriminatingEvidenceRequirement.source_report_id` links R(N) to the exact prior `GovernedHypothesisDeepeningReport`.
- **Reassessment owner:** existing `governed_reasoning`; `GovernedHypothesisDeepener.reassess_with_governed_evidence(...)` is source-agnostic and does not create a transport-specific reasoner.
- **Local evidence lineage:** productive CAP-17 preserves the completed `GovernedLocalEvidenceReasoningReentryResult`; no fake Level-2 lineage is synthesized.
- **Continuation:** revised hypothesis product is consumed by the existing `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1` and existing Episode continuation authority.
- **STOP:** no Planning N+1, Memory, Learning, background acquisition or new authority is opened by this closure.

---

## POST-G22 — DOCUMENTATION NORMALIZATION / FINAL CLOSURE

**Estado oficial:** INTEL-G22 CERTIFIED / CLOSED — **14.189 PASS · 0 FAIL · Ruff clean**.

La cadena gobernada de corrección G13→G22 queda cerrada para el alcance actual. G22 separa `CERTIFIED REQUEST` de `EXECUTION AUTHORIZATION`; sólo el par exacto request + autorización APPLY-NOW puede reingresar al G18/G17 existente.

Alias canónico: `INTEL_G21_WHAT_DID_YOU_LEARN_*` se conserva por trazabilidad pero corresponde a **INTEL-G2.1 — WHAT DID YOU LEARN**. El G21 canónico actual es **APPROVED REVISION PREPARATION CONTINUITY**.

`scripts/clean_project_caches.py` queda incorporado a la secuencia oficial antes de baseline/Ruff/pytest. Los tres snapshot guards históricos del `OfficialConversationGateway` fueron reanclados, tras auditoría, al SHA G22 `808104708cf035702cf1a181a75b630181a9879f79c68dec129f102460b10ef1`.

**NO G23 OPENED.** La próxima evolución debe derivarse de una carencia funcional demostrada por inventario/auditoría.

## Post-M400 integration residency reconciliation — External Intelligence / Governed Source Query

- Source-query execution authority: unchanged; existing governed source-query path / `OfficialConversationGateway`.
- External Intelligence admission authority: unchanged; `core.governed_external_intelligence.boundary.GovernedExternalIntelligenceBoundary`.
- Cross-capability adapter residency: `app.governed_external_information_source_integration.GovernedExternalInformationSourceIntegration`.
- The adapter is integration/orchestration only and owns no source, execution, memory, planning or cognitive authority.
- Historical M400.9 topology remains evidence, not current package residency authority.
- Status: **CLOSED / CERTIFIED**; owner baseline **12,534 PASS · 0 FAIL · Ruff clean**.

## Governed Reasoning / Learning source-neutral residency reconciliation

- Reasoning authority remains `core.governed_reasoning`; it owns the
  `GovernedRelationalAbstractionCandidate`, not Learning admission.
- Cross-capability abstraction→Learning adaptation resides at
  `app.governed_relational_abstraction_learning_bridge`.
- The integration reuses existing `LearningFoundation`,
  `GovernedLearningCandidateM369EvaluationV1`,
  `GovernedG6ExplicitHumanLearningApprovalV1`,
  `GovernedG7ApprovedLearningMemoryMaterializationV1` and the existing Memory
  writer/gateway path.
- No Curiosity-specific evaluation report, `PreferenceLearning`, new Learning
  authority, new Memory writer or productive runtime wiring is introduced.
- `core -> app` absolute imports after reconciliation: expected **0**.
- Status: **CLOSED / CERTIFIED**; owner baseline **12,535 PASS · 0 FAIL · Ruff clean**.

## Personal Organization / Calendar neutral Agenda evidence boundary reconciliation

- Calendar remains the external scheduled-event/provider authority.
- `CognitiveAgendaManager` remains the internal Cognitive Agenda authority.
- `PersonalOrganizationAuthority` remains the canonical Organization authority.
- Provider-specific `CalendarEvent` stops at
  `app.productive_organization_advisory_wiring._AgendaReadAdapter`.
- The adapter maps Calendar events to
  `core.agenda_evidence.AgendaEventEvidence` before Organization consumption.
- Organization core consumes only `agenda_id`, `title` and `source_reference`;
  it owns no Calendar provider metadata, attendees, availability or write contract.
- M391.5/M391.6 behavior and productive reachability remain unchanged.
- Direct `core -> infrastructure.calendar` imports for this seam: **0**.
- Status: **CLOSED / CERTIFIED**; owner baseline **12,536 PASS · 0 FAIL · Ruff clean**.

## Core root disconnected legacy utilities five-island retirement

- Retired disconnected legacy paths:
  `core/circuit_breaker.py`, `core/retry.py`, `core/event_bus.py`,
  `core/logging.py`, `core/runtime.py`.
- Productive import reachability before retirement: **0** for all five.
- No canonical capability authority, writer, store, registry or Composition Root
  moved or replaced.
- At this historical checkpoint `core/cache.py` remained outside this scope; it was later separately reconciled and retired under the M22 boundary.
- Current event authority/integration remains `core.cognitive_event_bus`.
- Current recovery/circuit-health surface remains `core.executive_recovery_health`.
- Current runtime composition authority remains `core.runtime_composition_root`.
- Historical manifests remain historical evidence and are not rewritten.
- Status: **CLOSED / CERTIFIED**; owner baseline **12,537 PASS · 0 FAIL · Ruff clean**.

## RP24.5 Unified Learning Base historical authority retirement

- Retired `core/unified_learning_base.py` and its direct RP24.5 behavioral
  certification.
- Removed historical `LearningDomain.RECORDS` / `LearningRole.RECORD` from the
  current M369 Learning Foundation inventory.
- Removed the descriptive
  `core.unified_learning_base:LearningRecord` implementation path from current
  M369 authority metadata.
- Archived the RP24.5 design document unchanged under
  `docs/history/legacy-learning/`.
- Historical SHA evidence remains unchanged.
- Current CAP-12 ownership remains **Learning authority + memory_gateway**.
- Durable governed learning writes remain exclusively under
  `OfficialMemoryGateway`.
- No replacement learning store, writer or persistence authority was created.
- Status: **CLOSED / CERTIFIED — owner baseline 12,530 PASS · 0 FAIL · Ruff clean**.

## M375 contextual conversation historical authority retirement

- Retired disconnected `core/contextual_conversation.py` /
  `ConversationContextAuthority`.
- Preserved `ConversationContext` as a current shared conversational contract.
- Current operational context continuity remains under
  `app.context_continuity_runtime:OfficialContextContinuityRuntimeGateway`.
- Current lower seams remain `core.conversational_context_continuity`, context
  curation and conversation-history sanitization.
- No new authority, context store, persistence path or runtime was created.
- Original M375 documentation is archived unchanged under
  `docs/history/legacy-conversation/`.
- Status: **CLOSED / CERTIFIED — owner baseline 12,523 PASS · 0 FAIL · Ruff clean**.


## M378 global explanation historical authority retirement

- Retired disconnected `core/intelligent_explanations.py` /
  `IntelligentExplanationAuthority`.
- Current explainability is source-owned: each canonical authority may explain
  only its own governed decision/state/result from explicit evidence and traces.
- Preserved current specialized surfaces in Governed Reasoning, Cognitive
  Planning, Controlled Autonomy and Trust without changing their ownership.
- No global replacement authority, explanation registry, store, writer,
  persistence path or runtime was created.
- Original M378 documentation is archived unchanged under
  `docs/history/legacy-explainability/`.
- Status: **CLOSED / CERTIFIED — owner baseline 12,520 PASS · 0 FAIL · Ruff clean**.

## M378.1 CCI-08 certification evidence reconciliation

- CCI-08 remains diagnostic and `PASS_BY_DESIGN`; it does not establish productive Adaptive Personality -> explainability wiring.
- Adaptive delivery remains bounded by `core/adaptive_personality.py` and its M377 boundary tests.
- Current explanation evidence is source-owned and is represented in CCI-08 by `core/governed_reasoning/explanations.py`, where `ExplainableAnswerRenderer` renders immutable `DecisionRecord` evidence.
- The retired global M378 explanation authority is not a current certification dependency and must not be restored.


## M376 historical unrealized conversation archive authority retirement

- Retired disconnected `core/long_term_conversation.py` / `LongTermConversationAuthority`; the historical foundation had zero productive reachability, runtime wiring and production persistence.
- No replacement archive authority is declared.
- Operational conversation journal = session/turn history, not Cognitive Memory.
- Living Conversation = longitudinal topic/thread continuity, not a replacement archive or Cognitive Memory authority.
- Durable Cognitive Memory remains under the existing memory authority / `OfficialMemoryGateway`; conversation summaries are not automatically admitted memory.
- Original M376 documentation is archived unchanged under `docs/history/legacy-conversation/`.
- Status: **CLOSED / CERTIFIED — owner baseline 12,513 PASS · 0 FAIL · Ruff clean**.

## Post-M376 documentary baseline reconciliation

- Current owner-certified baseline: **12,513 PASS · 0 FAIL · Ruff clean**.
- M376 historical unrealized conversation archive retirement: **CLOSED / CERTIFIED**.
- This reconciliation changes documentary current-state metadata only; capability residency and authority boundaries are unchanged.


## M367 historical inventory succession / current owners

**Reconciliation status:** **CLOSED / CERTIFIED — owner gate 12,440 PASS · 0 FAIL · Ruff clean**. This certifies the already-implemented retirement/current-owner reconciliation; it does not retire M367.1 or M367.6 and introduces no new authority.

- **RETIRED historical inventory/diagnostic surfaces:** M367.2 `UserProfileModel`, M367.3 `ProjectKnowledgeModel`, M367.4 `GoalsObjectivesModel`, M367.5 `ContextStateModel`, M367.7 `MentalModelStabilization`. These were read-only descriptive/closure surfaces, not current state owners.
- **KEEP / CURRENT:** M367.1 `app.internal_world_model_foundation:InternalWorldModelFoundation`, evolved by M391/M392 into the governed World Model façade.
- **KEEP / CURRENT:** M367.6 `app.priority_reasoning:PriorityReasoning` compatibility surface with current implementation in `domain.priority_reasoning`, productively reused by Intelligent Personal Organization.
- **Planning:** `app.planning_foundation:PlanningFoundation` remains the canonical planning-foundation authority and references current specialized sources directly.
- **Personal Organization goals:** `core.household_goals:HouseholdGoalManager` is the existing personal/household goal owner used by `PersonalOrganizationAuthority`; cognitive goals remain distinct under their existing cognitive-goal owner.
- **CCI-03 mental-model evidence:** current causal source is `core.adaptive_cognition.mental_models:MentalModel` projected by `core.mental_model_decision_evidence:GovernedMentalModelDecisionEvidenceProjector`, not M367.7.


## APP BRAIN repository layering reconciliation

BRAIN composition remains application-owned while persistence implementations remain
infrastructure-owned. The application composition consumes existing repository contracts
(`BrainRepository`, `HouseholdGoalRepository`, `HouseholdProjectRepository`); diagnostic
entry points provide `AtomicJsonBrainRepository`, `SQLiteHouseholdGoalRepository`, and
`SQLiteHouseholdProjectRepository`. No capability authority changes ownership.

Status: **CLOSED / CERTIFIED — owner baseline 12,355 PASS · 0 FAIL · Ruff clean**.

## Current productive reachability reconciliation — Governed Proposal → Executive Notification

Governed proposals now have a productive Desktop presentation seam without authority
succession. `OfficialConversationGateway` remains the governed proposal composition
owner; `GovernedProposalPresentationPolicy` remains the eligibility authority;
`GovernedProposalLifecycle` remains the lifecycle authority; and
`RuntimeExecutiveIntegration` / `ExecutiveNotificationBroker` remain the existing
notification spine. The new resident adapter only projects a presentation-eligible
proposal into that spine and records `OFFERED` after broker dispatch.

Status: **CLOSED / CERTIFIED — owner baseline 12,358 PASS · 0 FAIL · Ruff clean**. This does not grant autonomous execution.

## Current productive reachability reconciliation — Self-Improvement → Governed Proposal

A prepared M399.5 `DiagnosticProposal` may now enter the canonical governed proposal
model/inbox through a bounded adapter owned by no new authority. The diagnostic proposal
remains the technical self-diagnostics artifact; the governed proposal is only its human
presentation envelope. No diagnostic generation, code mutation, approval, execution,
background self-diagnosis, or second inbox is introduced.

Status: **CLOSED / CERTIFIED — explicit owner recertification 12,440 PASS · 0 FAIL · Ruff clean**. Historical 12,358/12,361 values remain provenance and are not rewritten.

## CAP-14 reachability reconciliation — explicit opportunity intake

CAP-14 now has one bounded application composition joining explicit technical
observations, threshold, explicit hypothesis and hash-bound project evidence through the
existing M399 proof/proposal chain into the canonical Governed Proposal inbox. This does
not create a second self-diagnostics authority and does not make Self Diagnostics a
background resident. Runtime opportunity discovery remains a separate future question.

## Reminder semantic reachability — life events

Reminder is the canonical authority for user requests phrased as `recordame` or `haceme
acordar`, regardless of topic. Life-event semantics do not create medical, travel, concert
or birthday reminder managers. Explicit dates are normalized into the existing Reminder
`due_at`; recurrence remains owned by the existing Reminder domain. Calendar creation
continues to require explicit calendar intent and its existing confirmation gate.

## Medical consultation preparation reachability

Reminder awareness may recognize a bounded medical-appointment cue for Carlos or
Cristina and offer the existing pre-consultation preparation capability. Reminder keeps
temporal authority; Health keeps medical-data authority; the adapter owns neither.
Ambiguity fails closed to the ordinary reminder presentation.

### Governed Local Music Collection — read-only catalogue foundation

**Authority / owner boundary:** `GovernedLocalMusicCatalogueV1` owns only bounded,
read-only catalogue discovery over one explicitly authorized local root.

**Official runtime capability:** `music.local_catalogue.read`.

**Provisioning:** `ROBY_LOCAL_MUSIC_ROOT`; absent or invalid configuration does not
register the capability.

**Current boundary:** metadata/provenance catalogue and bounded search only. No
selection authority, no playback authority, no `MusicMemory`, no Pinacoteca reuse.

### Governed Local Music Collection — selection foundation

`GovernedLocalMusicSelectionV1` is the bounded selection authority over the existing
read-only catalogue. It returns `SELECTED`, `AMBIGUOUS` or `NOT_FOUND`; all results keep
`playback_authorized=False`. The existing `music.local_catalogue.read` productive seam
can expose explicit human selection without crossing into playback execution.

### Governed Local Music Collection — playback authorization / execution foundation

**Authorization authority:** `GovernedLocalMusicPlaybackAuthorizationV1`.

**Execution adapter:** `LocalCommandMusicPlaybackExecutor`.

**Official runtime capability:** `music.local_playback.execute`, registered only when
both the governed music root and `ROBY_LOCAL_MUSIC_PLAYBACK_COMMAND` are configured.

**Current boundary:** explicit human request + unique governed selection → resolved
authorized source path → local player execution. Ambiguity, missing selection and
selection-only requests do not execute. Queue/control/autonomous playback remain out of
scope.


### Intellectual Evolution — Productive Investigation Reentry Routing (reconciled candidate)

- Starting certified baseline: **12,413 PASS · 0 FAIL · Ruff clean**.
- Protected `app/governed_reasoning_runtime.py` remains byte-identical at
  `bb5801db8fa7b3336106eb7dd323d6be03b8b06dc6d4cff3df3a7aa3202a804b`.
- New bounded application seam:
  `app/authorized_goal_productive_investigation_routing.py`.
- Productive reachability is exposed from `app/official_runtime_composition.py` using the
  existing `root.dependencies.governed_reasoning_runtime`.
- The route requires exactly two explicit structured hypotheses with exact authorized-goal
  lineage, reuses existing Scenario/Causal evaluation, Deepening and discrimination, and
  forwards exactly one discriminating requirement through the existing G4 admission.
- It does not call or replace the generic explanatory-model reentry.
- Zero or multiple discriminating requirements fail closed before CAP-11.
- No new reasoning, investigation, requirement, planning, authorization or execution
  authority is created.
- Owner certification: **12,420 PASS · 0 FAIL · Ruff clean**.
- Status: **CLOSED / CERTIFIED**.


### Intellectual Evolution — CAP-11 terminal closure → existing M369 learning candidate admission

- Starting certified baseline: **12,420 PASS · 0 FAIL · Ruff clean**.
- Residual type: **productive reachability only**.
- Existing authority reused unchanged:
  `GovernedInvestigationLearningCandidateAdmissionV1`.
- Official runtime composition now constructs and exposes that existing admission once.
- The admission still requires canonical terminal CAP-11 closure plus explicit learning
  semantics (`subject`, `proposed_value`, `confidence`).
- Output remains the existing M369 `LearningCandidate` with review required.
- No M369 evaluation, G6 approval, G7 materialization, Memory write or durable knowledge
  write is performed by this seam.
- Owner certification: **12,425 PASS · 0 FAIL · Ruff clean**.
- Status: **CLOSED / CERTIFIED**.


### Intellectual Evolution — M369 candidate → existing M369 evaluation reachability

- Starting certified baseline: **12,425 PASS · 0 FAIL · Ruff clean**.
- Residual type: **productive reachability only**.
- Existing authority reused unchanged: `GovernedLearningCandidateM369EvaluationV1`.
- Official runtime composition constructs and exposes the existing evaluator once.
- Existing Safe Learning Policies remain the evaluation authority.
- The seam stops at the read-only M369 evaluation result.
- No G6 approval, G7 materialization, Memory write or durable knowledge write occurs.
- Owner certification: **12,430 PASS · 0 FAIL · Ruff clean**.
- Status: **CLOSED / CERTIFIED**.


### Intellectual Evolution — M369 evaluation → existing G6 explicit human approval reachability

- Starting certified baseline: **12,430 PASS · 0 FAIL · Ruff clean**.
- Existing authority reused unchanged: `GovernedG6ExplicitHumanLearningApprovalV1`.
- Explicit human response, approver and exact G6 lineage remain mandatory.
- Official composition exposes G6 but never fabricates or infers approval.
- STOP before G7/materialization/durable writes.
- Owner certification: **12,435 PASS · 0 FAIL · Ruff clean**.
- Status: **CLOSED / CERTIFIED**.

### Intellectual Evolution — G6 approved learning → existing G7 governed materialization reachability

- Starting certified baseline: **12,435 PASS · 0 FAIL · Ruff clean**.
- Residual type: **productive reachability only**.
- Existing authority reused unchanged: `GovernedG7ApprovedLearningMemoryMaterializationV1`.
- Exact G6/M369 lineage and existing structural-eligibility governance remain mandatory.
- Official composition exposes G7 but does not call materialization automatically.
- STOP before the existing memory-write adapter, OfficialMemoryGateway and durable writes.
- Owner certification: **12,440 PASS · 0 FAIL · Ruff clean**.
- Status: **CLOSED / CERTIFIED**.

### CIH — Governed Reasoning → Living Companion minimal seam

- Starting certified baseline: **12,505 PASS · 0 FAIL · Ruff clean**.
- Residual type: **productive semantic reachability seam only**.
- Existing authority reused unchanged: canonical `governed_reasoning`.
- Existing core seam reused unchanged:
  `core.reasoning_runtime_integration.GovernedReasoningSource`.
- Existing productive adapter reused:
  `CanonicalProductiveReasoningSource`.
- Official Composition Root injects the same canonical reasoning source into
  `LivingCompanionRuntime`; no parallel reasoning authority is created.
- Explicit questions remain on the normal conversation path.
- Existing local Living Companion situation recognition remains first; governed reasoning
  is only a bounded fallback after a local miss.
- Capability selection/execution remains under the existing Official Runtime Capability
  Registry, including risk and confirmation gates.
- No permission, consent, persistence, Memory, Learning or executive-autonomy authority
  changed.
- Seam gap closed; a narrower semantic-abstention residual remains open and requires
  separate evidence before any further surgery.
- Owner certification: **12,506 PASS · 0 FAIL · Ruff clean**.
- Status: **CLOSED / CERTIFIED**.


### R-CI-SI-S5 — Self-Epistemic Relevance Horizon Closure

- Owner-certified baseline: **13,110 PASS · 0 FAIL · Ruff clean**.
- C1 determines explicit `NEED_TO_ASK` without asking now.
- C2 projects the need into existing Curiosity gap evidence with
  `relevance=UNKNOWN`.
- C3 determines `NO_COMPATIBLE_GOVERNED_TOPIC_EVIDENCE_ROUTE` for the current
  lineage.
- Existing CAP-10 Relevance/Curiosity authorities remain canonical and
  unchanged.
- Compatible governed topic evidence for this S5 lineage is
  **FUTURE / NOT CURRENTLY PRODUCTIVELY REACHABLE**.
- STOP before Relevance; no C4, topic inference, new classifier, new Relevance
  owner or new Curiosity owner is authorized.
- Status: **CLOSED / CERTIFIED — DOCUMENTARY**.


### CAP-17 / R-CAP17-O3-S16 — Explicit nested relative-path conversational reachability (bounded)

**Owner map unchanged:** `core/governed_local_library/catalogue.py` (canonical direct lookup), `core/governed_local_library/conversation_selection.py` (canonical selection), `core/governed_local_library/handoff.py` (selection fingerprint distinction/revalidation), `app/governed_local_library_conversation.py` (existing conversational caller), `app/governed_local_library_runtime_wiring.py` (existing Knowledge admission), existing Document Reading and Unified Retrieval. No persistence or new authority.

**Contract tests:** `tests/architecture/test_cap17_o3_explicit_relative_path_contract_red.py` (8), `tests/architecture/test_cap17_o3_s13_conversational_explicit_path_contract_red.py` (7), original CAP-17 catalogue (12), EPUB/selection/handoff regressions (49). Windows focal result 76 PASS and Ruff focal PASS. S15 one-run read-only real-library diagnosis PASS with no catalogue scan.

**Residual:** ordinary title search still uses bounded catalogue; no general discovery outside its limit. Conversational model interpretation latency is unmeasured. **State:** O3/S16 OWNER-CERTIFIED / CONTROLLED BASELINE PROMOTED WITH M377 EXCEPTION; Windows focal 76 PASS, G2 focal 16 PASS, integral 13,724 PASS / 47 M377 intentional RED / 0 unexpected failures. Not a global zero-failure GREEN. M377 HOLD remains; see S16-CLOSE quality gate record. Historical card certification figures remain historical and are not overwritten by focal counts.
