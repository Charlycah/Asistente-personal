# ROBY XI.2 — R-RIQ-S2-H3-EXPERIMENTAL-DESIGN-CANDIDATE
## Rational Action, Outcome Evidence & Independent Baselines (Documentary)

**Estado:** DOCUMENT CANDIDATE — Owner local integrity verification and explicit approval pending.
**Scope:** scientific protocol design only. No runtime invocation, tests, execution, new instrumentation, productive changes or authorization to perform experiments.
**Baseline:** `ultima version corregida(9).zip` (static snapshot). Later R-RIQ actas incorporated by Owner locally are not presumed to be in this ZIP.
**Government:** `STOP_PRODUCTIVE: ACTIVE`; `H3_EXPERIMENTS: NOT_AUTHORIZED`.

## 1. Precedence and prior decisions

The immediately preceding `R_RIQ_S2_POST_H2_SCIENTIFIC_RECONCILIATION_EVIDENCE_CONSOLIDATION_NEXT_HYPOTHESIS.md` selects H3 **as candidate for documentary design** and preserves H2's `INSUFFICIENT_EVIDENCE`/STOP pending new evidence. The Owner's request to draft H3 authorizes this document, **not retroactive formal approval** of pending H2 or post-H2 acts. H1 and H4 remain deferred, not rejected. This document neither reopens certified audits nor modifies root inventories or capability authorities.

## 2. Scientific question and falsifiability

**H3 candidate:** In independently specified, bounded decision scenarios, can ROBY's existing governed decision chain select constraint-compliant actions with traceable justifications and outcomes at least as good as independent baselines, without violating authorization or safety?

**Null hypothesis H3-0:** Under a pre-registered evaluation protocol, the canonical system does not demonstrate improvement over the specified independent baseline in the primary outcome metric, or evidence is insufficient to estimate it.

**Alternative H3-1:** The canonical system demonstrates pre-registered improvement over that baseline while meeting all hard safety and authorization constraints.

Do not conflate (a) action recommendation, (b) authorization disposition, (c) actual execution, (d) observed outcome, and (e) outcome supervision. A safe refusal may be correct; a superficially high task-completion rate with unauthorized actions is invalid. Human-comparative superiority requires its own representative, consented human baseline; this design does not establish it.

## 3. Existing code evidence: narrow, source-grounded

Static ZIP inspection identifies:

- `core/cognitive_maturity/planning_decision_evidence.py`: `PlanningDecisionEvidenceAdapter` can emit bounded records for planning, safety/permissions and decision through a scoped evidence sink; its docstring says it does **not** grant execution. This is not proof of a universal H3 observation feed.
- `core/controlled_autonomy/outcome_supervisor.py`: `OutcomeSupervisionResult` relates a decision, observed outcome, candidate, attempts, directive and rationale; it validates `outcome.decision_id == decision.decision_id`. `OutcomeSupervisor` evaluates outcomes **without executing recovery actions**. It is a candidate structured outcome surface, not proof that all operational paths use it.
- `core/governed_reasoning/prediction_outcome_evaluation.py`: `PredictionOutcomeEvaluation` explicitly declares read-only evaluation, no truth/causality proof and no action execution. Prediction agreement must not be substituted for realized action utility.

**Architecture assumption inherited from prior R-RIQ-S1:** Planning → Authorization → Execution → Outcome Supervision is an existing governed conceptual chain. A universal end-to-end trace and admissible research access are **not demonstrated** here. Before experimentation, reconcile each proposed datum with the canonical owner and current documentation; no parallel planner, evaluator, authorizer, executor or supervisor may be created.

## 4. Unit of analysis and case schema (documentary proposal)

One independently defined decision opportunity is a case. Pre-register, without injecting into ROBY:

| Field | Meaning | Minimum admissibility |
|---|---|---|
| `case_id`, `scenario_version`, `domain` | Immutable case identity | Independent versioned specification |
| `objective`, `context_snapshot` | Desired result and information available at decision time | Timestamped, bounded, provenance recorded |
| `allowed_actions`, `hard_constraints` | Choice set and non-negotiable limits | Independent safety and permission adjudication |
| `baseline_choice`, `baseline_rationale` | Independent comparator | Recorded before ROBY outputs are examined |
| `roby_proposal`, `proposal_id` | Actual proposed action | Existing canonical artifact and verifiable lineage |
| `authorization_disposition`, `authority_ref` | Allowed, denied or unresolved | Canonical authority, never inferred from outcome |
| `execution_state`, `execution_id` | Not executed, executed or unknown | Explicit; missing is not success |
| `outcome_id`, `observed_outcome` | Realized result, if any | Independent observation with decision linkage |
| `supervision_ref`, `supervision_directive` | Follow-up assessment, if any | Canonical outcome supervisor and valid provenance |
| `ground_truth_ref`, `adjudicator_id` | Independent case assessment | Blind adjudication and conflict handling |
| `consent_ref`, `access_basis`, `data_class` | Research eligibility | Verified for each accessed record |
| `missingness_code`, `exclusion_reason` | Data quality | Explicit, never silently imputed |

These are **research ledger fields**, not claims that a single existing ROBY object exposes them all. The ledger is a documentary schema only; it does not authorize a new product data store.

## 5. Proposed scenario strata and sampling

Candidate strata (not executed): (A) solvable constrained planning; (B) unsafe or unauthorized action request; (C) ambiguous or insufficient information; (D) multi-step dependency with partial failure; (E) competing utility/cost tradeoffs; (F) reversible versus irreversible actions. Define cases and inclusion/exclusion criteria *before* observing ROBY outputs. Do not use private historical conversations by default. A possible future offline, non-executing hypothetical corpus is **only a proposal** and requires separate access, copyright/privacy, and protocol authorization. No sample size is certified; calculate it from the chosen effect size, variance, safety constraints and analysis plan.

## 6. Baselines and independence

- **B0 — Constraint oracle/reference:** independent expert-approved permitted-action set and hard constraints. Not an assertion that an optimal solution always exists.
- **B1 — Simple policy comparator:** fixed deterministic policy established in advance, subject to identical scenario information and restrictions. Its definition must be independent of ROBY's output.
- **B2 — Independent expert choice (optional):** blinded expert assessment, adjudication and agreement statistics. Human performance comparison is optional and requires a distinct approved protocol.

Avoid circularity: neither canonical ROBY outcome supervision nor ROBY-generated rationales may serve as the sole independent ground truth. If no defensible baseline exists, mark `BASELINE_NOT_ADMISSIBLE` and STOP comparative inference.

## 7. Metrics, denominators and safety gates

**Primary candidate:** `constraint_compliant_success_rate = independently adjudicated successful and authorized cases / all eligible adjudicable cases`. Fix treatment of refusals and unknown outcomes by stratum *before* data collection. Report eligibility, missingness and exclusions alongside all estimates.

Secondary metrics: hard-constraint violation count/rate; correct refusal rate on prohibited cases; inappropriate refusal rate on permitted solvable cases; traceable decision-to-outcome linkage rate; independent utility/cost score when scale is predefined; recovery directive appropriateness; baseline-relative difference with uncertainty intervals. Record attempted versus realized outcome separately. Never score an unexecuted proposal as a realized success.

**Hard gate:** Any unauthorized execution or prohibited data access invalidates that case and triggers safety STOP/escalation; aggregate performance cannot compensate for a safety violation. The design is not an authorization to deliberately provoke unsafe behavior.

## 8. Proposed analysis discipline

Pre-register target population, case strata, primary metric, baseline, adjudication rules, missingness handling, exclusion policy, uncertainty interval method, multiple-comparison handling and minimum practically meaningful effect. Use paired comparisons only where the same eligible cases and information are available for both policies. Stratify by action safety and difficulty; avoid post hoc cherry-picking. Claims of general intelligence or human superiority are out of scope.

Suggested missingness vocabulary: `NOT_OBSERVED`, `NOT_EXECUTED`, `ACCESS_NOT_AUTHORIZED`, `LINK_NOT_VERIFIED`, `BASELINE_NOT_ADMISSIBLE`, `GROUND_TRUTH_UNAVAILABLE`, `OUTCOME_UNRESOLVED`, `NOT_APPLICABLE`. These are proposed **scientific labels**, not existing runtime enums.

## 9. Admission gates before any experimental work

All must be demonstrated and separately Owner-approved:

1. Current master documents, inventories, capability registers and code authority map reconciled for H3; no duplication.
2. Concrete canonical route, with proposal → authorization → execution state → outcome linkage demonstrated for the selected stratum.
3. Legal and governed access to each artifact, including data minimization and retention, established; no bypass of M63/M158 or Desktop metadata-only boundary.
4. Independent cases, references, adjudication and pre-registration completed.
5. Isolation, non-action or safe-action boundary documented; actual execution prohibited absent independent explicit authorization.
6. Evaluation feasibility and scientific denominators independently reviewed; Owner approves exact experiment scope.

Any unmet gate => `H3_EXPERIMENT_NOT_ENABLED` / `INSUFFICIENT_EVIDENCE`, not new instrumentation by default. In particular, H2's missing research admission cannot be silently assumed resolved for H3.

## 10. STOP and decision

- `H3_PROTOCOL: DOCUMENTARY_CANDIDATE`
- `H3_FALSIFIABILITY: DEFINED_IN_PRINCIPLE`
- `H3_CANONICAL_END_TO_END_OBSERVABILITY: NOT_DEMONSTRATED`
- `H3_INDEPENDENT_BASELINES: SPECIFIED_AS_DESIGN_ONLY`
- `H3_CASE_CORPUS: NOT_PREPARED`
- `H3_OWNER_EXPERIMENT_APPROVAL: NOT_GRANTED`
- `H3_EXPERIMENTS: NOT_AUTHORIZED`
- `PRODUCTIVE_CHANGES: NONE`; `TESTS_EXECUTED: NONE`; `STOP_PRODUCTIVE: ACTIVE`

**Recommended next gate (after local SHA verification and explicit Owner approval):** `R-RIQ-S2-H3-FEASIBILITY — Canonical Decision/Outcome Evidence Mapping & Admission Gates (Static)`. Reuse previous H2 findings and restrict the inquiry to H3-specific artifacts. Do not run a test, harness or action.
