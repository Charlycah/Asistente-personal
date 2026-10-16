# ROBY XI.2 — R-CI-SI-S5-B2-C3-A2
## Governed Authorization Invocation / Result Binding — Contract RED

Status: RED CONTRACTUAL — pending OWNER CERTIFICATION

## 1. Purpose

Freeze the narrow app-layer bridge that may consume an ACTUAL
`GovernedAuthorizationInputCorrespondence`, form the EXISTING direct read-only
capability-initiation request, invoke the EXISTING canonical Independence
Authorization owner exactly once, and bind its ACTUAL authorization report back to
the exact selected epistemic path C/D without creating a second authorization
policy.

Canonical transformation:

`ACTUAL A1 CORRESPONDENCE`
`-> EXACT EXISTING DIRECT INITIATION REQUEST`
`-> EXISTING AUTHORIZATION OWNER, ONCE`
`-> ACTUAL AUTHORIZATION REPORT`
`-> GOVERNED EPISTEMIC AUTHORIZATION RESULT BINDING -> STOP`

A2 invokes Authorization. A2 does not replace, reinterpret, extend, or duplicate
Authorization policy, and it does not execute the selected capability.

## 2. Architectural authority and layer

`GovernedIndependenceAuthorizationBoundaryV1` remains the sole existing owner of the
direct read-only capability-initiation decisions `MAY_INITIATE`, `MUST_ASK`,
`MUST_ABSTAIN`, and `REVIEW_REQUIRED`.

A2 MUST live in `app.*` because it consumes the core A1 correspondence and invokes
the existing app-layer authorization owner. `core.cognitive_maturity.*` MUST NOT
import `app.*` for A2.

A2 MUST NOT create an `EpistemicAuthorizationEngine`, authorization manager,
authorization planner, policy mirror, registry, selector, executor, or any parallel
authority.

## 3. Mandatory A1 anchor

A positive A2 result requires an ACTUAL
`GovernedAuthorizationInputCorrespondence` admitted by A1. Detached C/D strings,
detached Selection, detached runtime-report values, a free-form request, or
reconstructed lineage MUST NOT substitute for the actual A1 anchor.

A2 MUST preserve the ACTUAL A1 correspondence, its ACTUAL selection, its ACTUAL
selected eligibility, selected C/D, epistemic-need lineage, reasoning source, and
world snapshot. It MUST NOT rerun A1 admission, reselect, reconstruct eligibility,
search history, or re-query runtime.

## 4. Exact existing request projection

A2 MUST form the EXISTING `GovernedReadOnlyCapabilityInitiationRequest` mechanically
from A1 with exact field correspondence:

- `request.owner == correspondence.owner`;
- `request.capability_name == correspondence.capability_name`;
- `request.reason == correspondence.reason`;
- `request.source_reference == correspondence.source_reference`;
- `request.world_snapshot_id == correspondence.world_snapshot_id`.

A2 MUST NOT infer, rewrite, normalize, enrich, replace, or synthesize any of those
values. It MUST NOT add D to the existing request schema or claim that the existing
authorization owner independently evaluates D.

## 5. Exact existing authorization invocation

A2 MUST invoke the supplied EXISTING
`GovernedIndependenceAuthorizationBoundaryV1.evaluate_capability_initiation(request)`
exactly once for a positive invocation attempt.

A2 MUST NOT use the historical evidence-acquisition `evaluate(...)` route because
that route requires planning/productive-consumption lineage not present in A1. A2
MUST NOT fabricate an `EvidenceAcquisitionPlanningReport`, planning candidate,
productive-consumption object, P2 lineage, or any other synthetic planning state.

A2 MUST NOT inspect registry descriptors, initiation policy, effect class,
interaction scope, risk, permission scope, or confirmation requirements in order to
make or alter the decision. Those semantics remain exclusively inside the existing
authorization owner.

## 6. Canonical decision ownership

Every positive A2 binding MUST preserve the ACTUAL
`GovernedIndependenceAuthorizationReport` returned by the existing owner.

The A2 result MUST expose the report's exact `GovernedInitiationDecision` without
translation or a second decision taxonomy. `MAY_INITIATE`, `MUST_ASK`,
`MUST_ABSTAIN`, and `REVIEW_REQUIRED` mean exactly what the existing owner reports.

A2 MUST NOT manufacture an authorization decision when the owner raises an
exception, returns no canonical report, or produces a report that fails exact
binding validation. Such cases produce no admitted positive A2 binding; the bridge
MUST NOT convert them into synthetic `REVIEW_REQUIRED`, `MUST_ABSTAIN`, or any other
decision.

## 7. Exact result correspondence

A positive A2 binding requires exact correspondence between the ACTUAL report and
A1:

- `report.capability_name == correspondence.capability_name`;
- `report.source_reference == correspondence.source_reference`;
- `report.world_snapshot_id == correspondence.world_snapshot_id`.

The ACTUAL report object MUST be preserved. A2 MUST NOT reconstruct an equivalent
report or repair a mismatch.

The original selected D MUST remain exactly
`correspondence.selected_declared_evidence_output`. Authorization evaluates C. A2
MUST preserve D as selected-path lineage and MUST NOT claim that D was independently
authorized by the existing capability-based owner.

## 8. Direct-result internal identifiers

The existing direct authorization owner may produce internal identifiers such as
`discrimination-requirement-direct-*` and `evidence-acquisition-plan-direct-*`.
Those identifiers are canonical output of the existing owner for its direct route.

A2 MUST preserve them exactly as report fields. It MUST NOT generate them itself,
rewrite them, or equate them with the S5 `requirement_identity`, C1/C2 lineage, or a
new epistemic evidence-acquisition plan.

## 9. Preservation boundary

A positive A2 binding MUST preserve by identity or exact value, as applicable:

- the ACTUAL A1 correspondence;
- the ACTUAL `GovernedEpistemicPathSelection` reachable through A1;
- the ACTUAL selected `GovernedSelectionEligibility`;
- selected capability C;
- selected declared evidence output D;
- exact epistemic-need identity, source reference, and lineage kind;
- exact S5 requirement identity preserved by A1;
- exact reasoning `source_reference` and `world_snapshot_id` preserved by A1;
- exact explicit owner and reason preserved by A1;
- the exact EXISTING direct initiation request used for invocation;
- the ACTUAL authorization report returned by the owner;
- the report's exact authorization ID, decision, independence level, internal
  requirement ID, internal plan ID, rationale codes, and source fingerprint.

A2 MUST NOT collapse the S5 requirement identity into the authorization report's
internal direct requirement/plan identifiers.

## 10. Non-executive STOP

Authorization invocation/result binding is not acquisition or execution.

`MAY_INITIATE` means only the exact canonical authorization decision returned by the
existing owner. A2 MUST NOT turn it into execution authorization, capability
invocation, evidence acquisition, source query, or an execution-eligible product.

`MUST_ASK` MUST NOT ask a human or create a question.

`MUST_ABSTAIN` MUST NOT create a new epistemic conclusion.

`REVIEW_REQUIRED` MUST NOT resolve a conflict or create a review workflow.

A2 MUST NOT invoke Productive Authorization Consumption, Planning, an execution
gateway, `OfficialCapabilityGateway`, C/D, a source, Curiosity, Relevance, Personal
Initiative, Conversation, persistence, Learning, Memory, or world-model mutation.

The mandatory STOP is immediately after exact authorization-result binding.

## 11. Contract requirements

### R1 — Actual A1 correspondence is mandatory

A2 MUST consume an ACTUAL `GovernedAuthorizationInputCorrespondence`. Detached
Selection/C/D/request/source/snapshot/context values MUST NOT substitute for A1, and
A2 MUST preserve the actual A1, Selection, and selected eligibility objects.

### R2 — Existing direct request is an exact mechanical projection

A2 MUST construct the EXISTING `GovernedReadOnlyCapabilityInitiationRequest` with
owner, C, reason, reasoning source, and world snapshot exactly equal to the five A1
fields. A2 MUST NOT infer, normalize, enrich, synthesize, or substitute any request
field, and it MUST NOT add D semantics to the request.

### R3 — Existing authorization owner is invoked exactly once through the direct route

A2 MUST invoke the supplied EXISTING
`GovernedIndependenceAuthorizationBoundaryV1.evaluate_capability_initiation(...)`
exactly once for a positive invocation attempt. It MUST NOT call the planning-based
`evaluate(...)` route, synthesize planning/productive-consumption lineage, or inspect
registry/policy/risk/effect/scope/permission to decide authorization itself.

### R4 — Exact canonical authorization report and decision are preserved

A2 MUST preserve the ACTUAL `GovernedIndependenceAuthorizationReport` returned by
the existing owner and its exact `GovernedInitiationDecision`. It MUST NOT translate,
score, rank, reinterpret, override, or synthesize the decision or create a second
authorization-state taxonomy.

### R5 — Exact report-to-A1 binding is mandatory

A positive binding requires exact report correspondence for C, `source_reference`,
and `world_snapshot_id`. Mismatch means no admitted positive binding; A2 MUST NOT
repair, replace, re-query, retry, or reconstruct the report. Selected D remains the
exact A1 D and MUST NOT be represented as independently authorized by the owner.

### R6 — Direct owner identifiers remain owner-internal lineage

A2 MUST preserve the report's authorization ID, independence level, direct internal
requirement ID, direct internal plan ID, rationale codes, and source fingerprint
exactly. It MUST NOT manufacture those values or equate direct requirement/plan IDs
with S5 requirement identity or synthetic epistemic Planning lineage.

### R7 — Owner failure or invalid output cannot create a bridge decision

If the existing owner raises, returns no canonical report, or yields a report that
fails exact A1 binding, A2 MUST NOT fabricate `REVIEW_REQUIRED`, `MUST_ABSTAIN`,
`MUST_ASK`, `MAY_INITIATE`, or any replacement authorization report. No positive A2
binding is admitted. A2 MUST NOT retry or fall back to another owner/path.

### R8 — App-layer, read-only, non-executive result binding

The future A2 seam MUST live in `app.*`, consume core A1, and reuse the existing
authorization owner without adding authority. It MUST be read-only/non-executive and
MUST NOT reselect/rank paths; re-query registry/runtime; synthesize planning;
invoke Productive Authorization Consumption; authorize or perform acquisition or
execution; invoke C/D or a source; ask humans; create questions; assign relevance;
invoke Curiosity/Initiative/Conversation; persist; learn; modify Memory/world model;
start background work; or claim subjective experience/consciousness.

## 12. RED acceptance boundary

This RED CONTRACTUAL increment contains only:

1. this contract document; and
2. the mechanically regenerated M361 quality baseline if regeneration records the
   new governed contract.

It MUST NOT add A2 RED tests, an A2 product bridge, modify A1, modify the existing
authorization owner, invoke Authorization, or add acquisition/execution behavior.

Owner certification is expected to preserve the current productive baseline:

- Ruff clean;
- 13,062 PASS / 0 FAIL.

The exact owner result remains evidence-dependent and MUST NOT be claimed before the
owner run is supplied.

## 13. Frozen distinctions

`A1 CORRESPONDENCE != AUTHORIZATION`

`A2 BRIDGE != AUTHORIZATION POLICY`

`AUTHORIZATION INVOCATION != EXECUTION`

`AUTHORIZATION REPORT != EXECUTION AUTHORIZATION`

`REQUEST C = SELECTED C`

`SELECTED D REMAINS PRESERVED OUTSIDE OWNER D SEMANTICS`

`REPORT C = REQUEST C = SELECTED C`

`REPORT SOURCE = A1 REASONING SOURCE`

`REPORT SNAPSHOT = A1 WORLD SNAPSHOT`

`S5 REQUIREMENT IDENTITY != DIRECT OWNER REQUIREMENT/PLAN IDS`

`OWNER FAILURE != SYNTHETIC REVIEW_REQUIRED`

`MAY_INITIATE != EXECUTE`

`MUST_ASK != ASK NOW`

`MUST_ABSTAIN != NEW EPISTEMIC CONCLUSION`

`REVIEW_REQUIRED != CONFLICT RESOLUTION`

`AUTHORIZATION OF C != CLAIM THAT D WAS INDEPENDENTLY AUTHORIZED`

## 14. STOP

STOP after RED CONTRACTUAL.

Do not create A2 RED tests, implement the A2 app bridge, modify the existing
Authorization owner, acquire evidence, execute a selected capability, ask a human,
or enter conversational behavior in this increment.
