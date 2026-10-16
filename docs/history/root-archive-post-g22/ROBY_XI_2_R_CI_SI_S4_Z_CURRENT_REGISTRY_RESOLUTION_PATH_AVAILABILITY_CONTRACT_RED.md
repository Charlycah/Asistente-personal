# ROBY XI.2 — R-CI-SI-S4-Z
## Current Registry Resolution-Path Availability — RED Contractual

Status: RED CONTRACTUAL — FROZEN FOR OWNER CERTIFICATION

## 1. Purpose

Freeze the minimum governed contract that observes the current CapabilityRegistry backing of every material self-epistemic resolution path produced by S4-W, without performing runtime-readiness evaluation, source selection, acquisition planning, authorization, questioning, relevance, curiosity, initiative, conversation, persistence, learning, or execution.

This block is a read-only derivational observation over existing authorities. It does not create a new availability authority.

## 2. Certified input boundary

The contract consumes:

- one `MaterialSelfEpistemicResolutionPathSet` produced by S4-W; and
- the canonical `CapabilityRegistryManager` whose current descriptors own registration, exact declared evidence outputs, and `enabled` state.

Each S4-W path remains identified by its admitted S4-T binding:

`(capability_name C, declared_evidence_output D)`.

S4-Z MUST preserve the complete S4-W material anchor and every original binding.

## 3. Scope of availability

S4-Z observes CURRENT REGISTRY AVAILABILITY only.

`REGISTRY_AVAILABLE(C/D)` means exactly:

1. `registry.get(C)` returns the current exact descriptor;
2. exact `D` is still a member of that descriptor's `evidence_outputs`; and
3. that descriptor has `enabled is True`.

It does NOT mean runtime-ready, dependency-ready, reachable, authenticated, permitted, authorized, selected, preferred, executable, acquired, sufficient, question-worthy, relevant, or curiosity-worthy.

## 4. Required per-path states

Every input binding MUST receive exactly one explicit registry-scoped observation:

- `NOT_REGISTERED`: exact C is absent from the current registry.
- `EVIDENCE_DECLARATION_MISMATCH`: C exists, but exact D is not currently declared in `C.evidence_outputs`.
- `DISABLED`: exact C/D still exists, but the current descriptor has `enabled is False`.
- `REGISTRY_AVAILABLE`: exact C/D exists and the current descriptor has `enabled is True`.

Precedence is exact and fail-closed:

`NOT_REGISTERED` → `EVIDENCE_DECLARATION_MISMATCH` → `DISABLED` → `REGISTRY_AVAILABLE`.

No missing or negative state may be repaired by inference or substitution.

## 5. Contract requirements

### R1 — Exact current registry availability

For a S4-W binding C/D whose current exact descriptor exists, still declares exact D, and is enabled, the result MUST preserve the binding and report `REGISTRY_AVAILABLE`.

### R2 — Missing capability is explicit and non-destructive

If `registry.get(C)` is `None`, the result MUST preserve the original binding and report `NOT_REGISTERED`.

It MUST NOT create, discover, substitute, or semantically search for another capability.

### R3 — Evidence declaration mismatch is exact and fail-closed

If C exists but exact D is absent from the current descriptor's `evidence_outputs`, the result MUST preserve the original binding and report `EVIDENCE_DECLARATION_MISMATCH`.

No fuzzy, normalized, substring, semantic, embedding, retrieval, or LLM matching is allowed.

### R4 — Disabled is not available and does not invalidate the binding

If exact C/D exists but the current descriptor has `enabled is False`, the result MUST preserve the original binding and report `DISABLED`.

The S4-T semantic resolution binding remains intact; S4-Z observes only current registry state.

### R5 — Zero / one / many paths remain observational and non-selective

Zero, one, or many S4-W resolution bindings are legitimate.

The result MUST preserve one availability observation per input binding and MUST NOT expose or derive `selected_path`, `preferred_path`, `best_path`, or equivalent selection semantics.

One `REGISTRY_AVAILABLE` path does NOT mean selected path.

### R6 — Complete auditability and deterministic representation

Unavailable paths MUST NOT be filtered out. The result MUST preserve all input bindings with their explicit observations.

Representation MUST be deterministic and MUST preserve S4-W ordering. S4-Z MUST NOT rank or reorder paths by availability, risk, permission, preference, or any other criterion.

### R7 — Material anchor and binding lineage preservation

The result MUST preserve without mutation the S4-W material anchor:

- `assessment_id`
- `requirement_id`
- `epistemic_need_identity`
- `reasoning_source_reference`
- `world_snapshot_id`
- `self_gap_source_reference`
- `self_gap_lineage_kind`

Each observation MUST retain its exact original `EpistemicResolutionBinding`, including its S4-T identity/source/lineage/provenance evidence.

### R8 — Registry-only, read-only, subordinate seam

The S4-Z observer MUST be `read_only=True` and `derivational=True`.

It MAY perform only exact current registry lookup and exact descriptor-field observation needed by this contract.

It MUST NOT:

- mutate the capability registry;
- register, enable, disable, or update capabilities;
- perform semantic capability search;
- discover substitute resolution paths;
- infer resolution semantics;
- consult or reconstruct runtime capability graphs;
- assess runtime/dependency readiness;
- inspect runtime lifecycle or residents;
- rank sources or capabilities;
- select sources or capabilities;
- plan or authorize acquisition;
- acquire evidence;
- create questions;
- assign question-worthiness;
- assign relevance;
- invoke curiosity;
- create goals;
- invoke initiative;
- invoke conversation;
- persist results;
- modify memory;
- create learning candidates;
- execute actions;
- grant authority;
- claim subjective experience or consciousness.

## 6. Existing-authority preservation

S4-Z MUST reuse `CapabilityRegistryManager.get()` and the current exact `CapabilityDescriptor` fields `evidence_outputs` and `enabled`.

It MUST NOT create a second capability registry, availability registry, evidence-acquisition planner, runtime graph, runtime-readiness authority, or source selector.

The existing Evidence Acquisition planner remains the owner of its own requirement-driven planning contract and MUST NOT be invoked by fabricating a synthetic `DiscriminatingEvidenceRequirement`.

## 7. Runtime-readiness boundary

S4-Z MUST NOT consume `OfficialROBYRuntime.capability_graph`, `RuntimeHealthReadinessService`, `RuntimeCapabilityAvailability`, or any equivalent runtime/dependency readiness result.

The following distinctions are contractual:

`REGISTRY_AVAILABLE != RUNTIME_READY`

`RUNTIME_READINESS_NOT_REPRESENTED != RUNTIME_UNAVAILABLE`

`READY != AUTHORIZED != SELECTED`

Runtime readiness remains a later governed block.

## 8. STOP boundary

The block ends after preserving the complete S4-W path set with one exact current-registry observation per path.

`MATERIAL PATH SET`
`→ CURRENT REGISTRY OBSERVATION`
`→ STOP`

No progression is authorized to:

`RUNTIME READINESS → SOURCE SELECTION → NEED-TO-ASK / QUESTION-WORTHINESS → RELEVANCE → CURIOSITY`.

## 9. RED-test target after owner certification

After this contractual document is owner-certified, RED tests should require a new minimal product seam only, expected conceptually under:

`core.cognitive_maturity.current_registry_resolution_path_availability`

The RED tests must fail exclusively because that product seam is absent, not because existing S4-W, S4-T, CapabilityRegistry, planner, runtime, or authorization behavior is changed.

No productive implementation is authorized by this RED contractual step.
