# ROBY XI.2 — R-CI-SI-S5-B2-C3-A1
## Governed Authorization Input Correspondence — Contract RED

Status: RED CONTRACTUAL — pending OWNER CERTIFICATION

## 1. Purpose

Freeze the narrow, read-only, derivational correspondence that can relate an ACTUAL
`GovernedEpistemicPathSelection` to an ACTUAL
`CanonicalRuntimeReadinessProjectionReport` and explicit caller context so a later
boundary can form legitimate input for the EXISTING governed authorization owner.

Canonical transformation:

`ACTUAL SELECTION + ACTUAL RUNTIME REPORT + EXPLICIT OWNER + EXPLICIT REASON`
`-> GOVERNED AUTHORIZATION INPUT CORRESPONDENCE -> STOP`

A1 does not invoke Authorization and does not decide authorization.

## 2. Architectural authority

The existing `GovernedIndependenceAuthorizationBoundaryV1` remains the canonical
owner of direct read-only capability-initiation authorization policy. A1 MUST NOT
create a second authorization policy, engine, manager, planner, ranker, selector,
registry, or execution authority.

Because the existing authorization owner lives in `app.*`, a future A1 core seam
MUST NOT import or invoke it. A1 only establishes and preserves legitimate input
correspondence for a later integration boundary.

## 3. Canonical anchors

A positive correspondence requires BOTH:

1. an ACTUAL `GovernedEpistemicPathSelection`; and
2. an ACTUAL `CanonicalRuntimeReadinessProjectionReport`.

Detached C/D strings, detached eligibility or runtime-observation objects, detached
source/snapshot strings, reconstructed reports, registry queries, runtime queries,
or synthetic lineage MUST NOT substitute for these actual anchors.

`owner` and `reason` are explicit caller/context metadata. They MUST be non-blank and
MUST NOT be inferred from capability identity, ROBY identity, creator identity,
epistemic-need identity, source type, or any upstream evidence.

## 4. Exact selected-path correspondence

The authorization capability identity MUST be exactly
`selection.selected_capability_name`.

The selected declared evidence output D MUST remain exactly
`selection.selected_declared_evidence_output` and MUST be preserved by the A1 result
even though the existing authorization request schema evaluates capability C rather
than C/D.

A1 MUST preserve the actual `selection.selected_path_eligibility` object. It MUST NOT
reselect, reconstruct, replace, or reinterpret C/D.

`AUTHORIZATION C = SELECTED C`, while selected D remains explicit preserved lineage.

## 5. Runtime-report membership and lineage

The selected eligibility's ACTUAL `runtime_observation` MUST be one of the ACTUAL
runtime report's `observations` BY OBJECT IDENTITY. Structural similarity alone MUST
NOT authorize correspondence.

The report MUST correspond exactly to the selection's epistemic-need lineage:

- `runtime_report.epistemic_need_identity == selection.epistemic_need_identity`;
- `runtime_report.self_gap_source_reference ==`
  `selection.epistemic_need_source_reference`;
- `runtime_report.self_gap_lineage_kind == selection.epistemic_need_lineage_kind`.

A1 MUST NOT search history for a matching report, query registry/runtime, or rebuild a
report from detached values.

## 6. Authorization source and world-snapshot correspondence

The authorization input `source_reference` MUST derive exactly from the ACTUAL
runtime report's `reasoning_source_reference`.

The authorization input `world_snapshot_id` MUST derive exactly from the SAME ACTUAL
runtime report's `world_snapshot_id`.

These values form operational reasoning/snapshot lineage and MUST NOT be synthesized,
substituted with the epistemic-need source reference, or supplied independently as
free detached strings.

The selection's `epistemic_need_source_reference` remains distinct and MUST also be
preserved. A1 MUST NOT collapse reasoning-source lineage into self-gap/epistemic-need
lineage.

## 7. Explicit caller context

`owner` MUST be supplied explicitly by the caller/context and MUST be non-blank.
A1 MUST NOT derive owner from selected C/D, registry descriptors, ROBY identity,
creator identity, or epistemic lineage.

`reason` MUST be supplied explicitly by the caller/context and MUST be non-blank.
It is request metadata, not authorization evidence, determinacy evidence, selection
evidence, or proof that initiation is permitted.

A1 MUST NOT generate a narrative reason and treat it as governed evidence.

## 8. Preservation and projection boundary

A positive A1 correspondence MUST preserve by identity or exact value, as applicable:

- the ACTUAL `GovernedEpistemicPathSelection`;
- the ACTUAL selected `GovernedSelectionEligibility`;
- the ACTUAL `CanonicalRuntimeReadinessProjectionReport`;
- the ACTUAL selected runtime observation;
- selected C and selected D;
- exact epistemic-need identity, source reference, and lineage kind;
- exact requirement identity retained by selection;
- exact `reasoning_source_reference` from the runtime report;
- exact `world_snapshot_id` from the same runtime report;
- explicit non-blank `owner`;
- explicit non-blank `reason`.

A1 MAY expose the five values required by the existing direct authorization request:
`owner`, selected C as `capability_name`, `reason`, reasoning `source_reference`, and
`world_snapshot_id`. Such projection is correspondence only; it MUST NOT instantiate
or invoke the `app.*` authorization owner in the A1 core seam.

## 9. Negative semantics

If either actual anchor is absent, the selected runtime observation is not present by
identity in the supplied report, the X lineage does not match exactly, or explicit
owner/reason is blank, there is no governed A1 correspondence.

A1 MUST NOT repair mismatches, search for substitutes, choose another runtime report,
choose another path, infer owner, invent reason, or synthesize source/snapshot values.

A1 MUST NOT create authorization states such as `AUTHORIZED`, `DENIED`,
`MAY_INITIATE`, `MUST_ASK`, `MUST_ABSTAIN`, or `REVIEW_REQUIRED`.

## 10. Downstream boundary

Input correspondence is not Authorization. A1 MUST NOT call
`GovernedIndependenceAuthorizationBoundaryV1`, inspect authorization policy, inspect
capability risk/effect/scope/permission for a decision, or emit an authorization
report.

A1 also MUST NOT plan acquisition, authorize acquisition/execution, invoke C/D,
query a selected source, acquire evidence, ask a human, create a question, invoke
curiosity/initiative/conversation, persist results, learn, modify memory, or execute
actions.

The mandatory STOP is immediately after governed authorization input correspondence.

## 11. Contract requirements

### R1 — Actual selection anchor is mandatory

A1 MUST consume an ACTUAL `GovernedEpistemicPathSelection`. Detached C/D, eligibility,
determinacy, preference-set, requirement, or synthetic selection state MUST NOT
substitute for the actual C2-B selection.

### R2 — Actual runtime report anchor and observation identity are mandatory

A1 MUST consume an ACTUAL `CanonicalRuntimeReadinessProjectionReport`. The actual
`selection.selected_path_eligibility.runtime_observation` MUST occur in the report's
`observations` by object identity. Structural equality, detached observation values,
historical lookup, registry/runtime re-query, or reconstructed reports MUST NOT
substitute for this identity correspondence.

### R3 — Exact X lineage correspondence

The runtime report's epistemic-need identity, self-gap source reference, and self-gap
lineage kind MUST exactly equal the selection's epistemic-need identity, source
reference, and lineage kind. Mismatch means no correspondence; A1 MUST NOT repair or
reinterpret lineage.

### R4 — Exact C/D preservation

Authorization capability C MUST be exactly the selected C. Selected D MUST remain
exactly preserved even though the existing authorization request is capability-based.
The actual selected eligibility and runtime observation MUST be preserved; A1 MUST NOT
reselect or reconstruct them.

### R5 — Reasoning source and world snapshot come from one actual report

Authorization `source_reference` MUST be exactly the actual runtime report's
`reasoning_source_reference`, and `world_snapshot_id` MUST be exactly that SAME
report's `world_snapshot_id`. A1 MUST NOT substitute the epistemic-need source,
accept detached replacements, synthesize either value, or collapse the two source
lineages.

### R6 — Owner and reason are explicit non-inferred context

`owner` and `reason` MUST be explicit, non-blank caller/context inputs. Owner MUST NOT
be inferred from C/D, ROBY, creator identity, registry, or epistemic lineage. Reason
MUST NOT be generated as evidence or interpreted as authorization proof.

### R7 — Correspondence is not Authorization

A1 MUST NOT invoke the existing authorization owner or create/interpret authorization
decisions. It MUST NOT emit `MAY_INITIATE`, `MUST_ASK`, `MUST_ABSTAIN`,
`REVIEW_REQUIRED`, execution authorization, acquisition authorization, or any other
authorization outcome.

### R8 — Read-only, derivational, inert boundary

The future A1 seam MUST be read-only and derivational, with no `app.*` dependency. It
MUST NOT mutate upstream state; query registry/runtime; reconstruct selection,
eligibility, observations, or reports; synthesize planning/source/snapshot lineage;
rank/reselect paths; inspect preferences/effects/evidence to decide correspondence;
plan/acquire evidence; invoke C/D; ask humans; create questions; assign relevance;
invoke curiosity/initiative/conversation; persist; learn; modify memory; execute
actions; create cognitive authority; or claim subjective experience/consciousness.

## 12. RED acceptance boundary

This RED CONTRACTUAL increment contains only:

1. this contract document; and
2. the mechanically regenerated M361 quality baseline if regeneration records the
   new governed contract.

It MUST NOT add A1 RED tests, an A1 product seam, an authorization bridge, or changes
to the existing authorization owner.

Owner certification is expected to preserve the current productive baseline:

- Ruff clean;
- 13,054 PASS / 0 FAIL.

The exact owner result remains evidence-dependent and MUST NOT be claimed before the
owner run is supplied.

## 13. Frozen distinctions

`SELECTION != AUTHORIZATION INPUT CORRESPONDENCE`

`AUTHORIZATION INPUT CORRESPONDENCE != AUTHORIZATION`

`SELECTED C/D MUST REMAIN C/D`

`AUTHORIZATION CAPABILITY C = SELECTED C`

`AUTHORIZATION OWNER DOES NOT GAIN D SEMANTICS`

`REASONING SOURCE != EPISTEMIC-NEED SOURCE`

`WORLD SNAPSHOT MUST BE PRESERVED, NOT SYNTHESIZED`

`OWNER MUST BE EXPLICIT, NOT INFERRED`

`REASON MUST BE EXPLICIT CONTEXT, NOT AUTHORIZATION EVIDENCE`

`MAY_INITIATE != EXECUTE`

`MUST_ASK != ASK NOW`

## 14. STOP

STOP after RED CONTRACTUAL.

Do not create RED tests, GREEN implementation, invoke Authorization, acquire evidence,
execute a selected capability, ask a human, or enter conversational behavior in this
increment.
