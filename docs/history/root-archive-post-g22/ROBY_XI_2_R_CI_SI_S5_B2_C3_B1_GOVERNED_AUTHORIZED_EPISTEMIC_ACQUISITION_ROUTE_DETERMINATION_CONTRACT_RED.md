# ROBY XI.2 — R-CI-SI-S5-B2-C3-B1
## Governed Authorized Epistemic Acquisition Route Determination — CONTRACT RED

Status: RED contractual. No production implementation is authorized by this document.

## 1. Certified entry state

B1 begins only from an actual
`GovernedEpistemicAuthorizationProductiveConsumptionBinding` produced by
C3-A3. The certified A3 lineage is direct Authorization lineage and preserves
S5 `requirement_identity` separately from the Authorization owner's internal
`requirement_id` and `plan_id`.

The canonical Authorization and productive-consumption owners remain unchanged.
The existing Evidence Acquisition Planning and Level-2 read-only execution
owners remain unchanged.

## 2. Inventory result frozen by B1

The post-A3 inventory establishes all of the following:

- `OfficialRuntimeCapabilityRegistry` registers operational capability facts,
  interceptors, optional evidence readers, and dependency declarations, but it
  does not declare an authoritative S5 authorized epistemic acquisition route;
- `OfficialGovernedCapabilityRoutingRuntimeGateway` is a permission-first
  conversational/runtime routing surface, not an S5 epistemic-lineage owner;
- `GovernedLevel2ReadOnlyExecutionGatewayV1` requires an actual
  `GovernedEvidenceAcquisitionProductiveConsumption` whose `requirement_id` and
  `plan_id` correspond to Authorization;
- A3's direct Authorization IDs were not produced by the canonical Evidence
  Acquisition Planning owner and MUST NOT be rewritten as if they were;
- specialized integrations such as ROBY-initiated local-library access are
  precedents, not a generic capability-to-acquisition-route registry.

Therefore no compatible canonical acquisition/execution route is currently
proven for the direct S5 A3 lineage.

## 3. Exact responsibility

B1 is a read-only, derivational, fail-closed route-determination boundary. Its
only responsibility in the current architecture is:

ACTUAL A3 PRODUCTIVE AUTHORIZATION BINDING
→ preserve selected capability and exact Authorization lineage
→ evaluate only already-proven canonical lineage compatibility
→ `NO_COMPATIBLE_CANONICAL_ROUTE` when no such route is proven
→ STOP.

B1 does not create a route, route registry, planner, executor, capability
selection, permission decision, or acquisition authority.

## 4. R1 — actual A3 admission only

B1 MUST require an actual
`GovernedEpistemicAuthorizationProductiveConsumptionBinding`. It MUST preserve
that A3 object by identity and preserve its A2, A1 correspondence, Selection,
selected-path eligibility, productive Authorization consumption, and
Authorization report anchors by identity.

## 5. R2 — exact selected capability and Authorization lineage

B1 MUST preserve without translation the selected capability name, source
reference, world snapshot, Authorization decision, independence level,
authorization ID, Authorization owner's requirement ID and plan ID, and S5
`requirement_identity`.

The selected capability remains the capability already selected by C2-B. B1
MUST NOT rank, select, reselect, substitute, or semantically search for another
capability.

## 6. R3 — eligibility is necessary but not route proof

B1 MUST preserve A3's exact owner-derived
`eligible_for_next_governed_gate`. A false value MUST remain fail-closed and
MUST NOT produce a compatible route.

A true value is only eligibility to reach another governed gate. It MUST NOT be
interpreted as acquisition authorization, execution authorization, or proof
that a compatible route exists.

## 7. R4 — direct lineage is incompatible with the existing Level-2 route

B1 MUST preserve the fact that A3's Authorization owner-internal direct
`requirement_id` and `plan_id` are not S5 Planning lineage. In the absence of an
actual corresponding `GovernedEvidenceAcquisitionProductiveConsumption`, B1
MUST determine `NO_COMPATIBLE_CANONICAL_ROUTE` for the current direct S5
lineage.

B1 MUST NOT fabricate a `DiscriminatingEvidenceRequirement`, Planning product,
planning ID, requirement ID, or execution preflight input.

## 8. R5 — no invented route authority or registry inference

B1 MUST NOT infer an epistemic acquisition route from
`OfficialRuntimeCapabilityRegistry`, `evidence_reader`, interceptor type,
capability kind, tags, semantic triggers, dependency metadata, or the
permission-first governed capability routing runtime.

B1 MUST NOT introduce a capability-to-route table, plugin map, route priority,
fallback route, dynamic import, reflection-based discovery, or a second routing
authority.

## 9. R6 — specialized integrations are not generic routes

B1 MUST NOT infer that a specialized integration such as
`GovernedRobyInitiatedLibraryAccessV1` is the route for an S5 capability merely
because names, kinds, sources, or operational descriptors appear compatible.
It MUST NOT invoke CAP-17/local-library conversation or any other specialized
runtime from B1.

A future positive route requires an explicit canonical authority/declaration
that is not present in the certified A3 baseline.

## 10. R7 — deterministic fail-closed determination

For the certified direct S5 A3 lineage, repeated determination over the same A3
object MUST produce the same fail-closed status and rationale. The result MUST
state that no compatible canonical route is proven and MUST NOT synthesize an
alternative.

The result is an architectural determination only. It is not a new epistemic
conclusion about the world and does not alter the Authorization decision.

## 11. R8 — non-acquisitive, non-executive STOP

B1 MUST remain read-only and derivational. It MUST NOT:

- query or mutate the official capability registry/runtime;
- call the governed capability routing runtime;
- rerun A1, A2, A3, Authorization, or productive Authorization consumption;
- select/rank/reselect capabilities or epistemic paths;
- instantiate or call Evidence Acquisition Planning;
- construct a Planning product or Planning lineage;
- acquire evidence or query C, D, or the selected source;
- invoke a specialized capability integration;
- invoke the Level-2 execution gateway or official capability gateway;
- authorize or execute actions;
- ask a human or create a question;
- invoke Curiosity, Relevance, Initiative, or Conversation;
- persist results, learn, or modify Memory/world model;
- create a new cognitive, planning, routing, acquisition, or execution authority.

The STOP is immediately after route determination. Any future positive route
requires a separate reconciliation and explicit canonical authority/declaration
before acquisition or execution can be considered.

## 12. RED expectation

The contractual tests R1–R8 MUST fail only because
`app.governed_authorized_epistemic_acquisition_route_determination` does not yet
exist. No GREEN implementation is part of this increment.
