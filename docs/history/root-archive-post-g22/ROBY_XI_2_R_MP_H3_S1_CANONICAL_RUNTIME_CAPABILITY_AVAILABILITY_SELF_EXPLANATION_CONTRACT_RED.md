# ROBY XI.2 — R-MP-H3-S1 — CANONICAL RUNTIME CAPABILITY AVAILABILITY SELF-EXPLANATION — CONTRACT RED

## Status

**CONTRACT RED — STOP BEFORE GREEN**

## Purpose

Freeze the smallest governed contract that prevents conversational self-explanation
from equating a capability's declarative `enabled` flag with its effective runtime
availability.

The existing bounded SE2-S1-B inspection remains the conversational owner. This
contract does not create a new registry, readiness authority, graph, observability
layer, planner, manager, or execution path.

## Existing authorities preserved

- `OfficialRuntimeCapabilityRegistry` owns official capability registration and the
  bounded `interface_snapshot()` used by conversational inspection.
- `RuntimeHealthReadinessService` owns readiness interpretation; inspection MUST NOT
  reimplement readiness rules.
- `OfficialROBYRuntime` owns the canonical runtime snapshot and the optional canonical
  `RuntimeCapabilityGraph` provisioned by composition.
- `RuntimeCapabilityGraph` remains composition-owned. The registry MUST NOT construct
  or reconstruct it for inspection.
- `PlanningCapabilityEvidence` remains Planning-only evidence and MUST NOT be consumed
  by conversational inspection.

## Contractual distinction

`enabled` and runtime availability are different facts.

A capability MAY be registered with `enabled=True` while canonical runtime readiness
is `UNAVAILABLE`, `DEGRADED`, or `UNKNOWN`. Conversational self-explanation MUST NOT
translate `enabled=True` into a claim that the capability is currently available.

The existing declarative wording `habilitada` MAY remain, but when a canonical
availability fact is supplied the response MUST state that availability separately.

## Canonical read-only seam

GREEN MAY add only a bounded read-only availability projection into the existing
inspection path. The projection MUST originate from existing runtime/readiness
owners and MUST NOT execute a capability.

The seam MUST satisfy all of the following:

1. preserve `interface_snapshot()` as the official bounded interface projection;
2. preserve `RuntimeCapabilityView` declarative semantics;
3. consume no `planning_capability_evidence()`;
4. consume no risk or confirmation metadata;
5. perform no capability execution;
6. construct no `RuntimeCapabilityGraph` inside the registry or inspection path;
7. implement no readiness algorithm inside the registry;
8. treat absent/non-canonical availability as `UNKNOWN`, not `AVAILABLE`;
9. preserve the empty-registry fail-safe;
10. preserve existing SE2-S1-B name/description/enabled/tags behavior.

## RED behavioral proof

The RED suite must demonstrate the missing seam with an enabled capability whose
canonical read-only availability is `UNAVAILABLE`.

Expected post-GREEN semantics:

- the response still reports the capability as declaratively `habilitada`;
- it separately reports current availability as `no disponible`/`unavailable`;
- it does not describe that capability as currently available;
- if canonical availability cannot be established, it reports availability as
  unknown rather than manufacturing availability.

## Non-goals

This block does NOT authorize:

- risk/confirmation publication;
- Planning evidence consumption;
- dependency declaration changes;
- new productive dependency declarations;
- capability execution during introspection;
- a second capability registry;
- a second readiness service;
- a second runtime capability graph;
- generalized self-model redesign;
- Voice, multimodal, curiosity, initiative, or companion expansion.

## STOP boundary

**STOP BEFORE GREEN.**

GREEN is authorized only after OWNER certification that the RED failures are limited
to the missing canonical availability projection and that all pre-existing tests
remain green.
