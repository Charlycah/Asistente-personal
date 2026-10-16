# ROBY XI.2 — M402.2 Residential Node Minimal Lifecycle Integration

**Scope:** minimal read-only lifecycle integration over M402.1.

## Objective

Connect the M402.1 `ResidentialNodeBinding` to the existing
`ResidentComponentRegistry` without creating a new runtime, authority,
registry, capability catalog, synchronization layer or physical capability.

## Implementation

`app/residential_node_lifecycle.py` adds `ResidentialNodeLifecycleView`.

The view:

- resolves `binding.resident_component_id` through the existing registry;
- reads `ResidentRegistration.state` and `ResidentRegistration.health`;
- receives M396 residence facts and M397/M398 connection facts explicitly;
- delegates node-state derivation to the existing `ResidentialNodeEvaluator`;
- fails closed as `UNAVAILABLE` when the resident is not registered;
- never registers, starts, stops or mutates a resident.

## Preserved ownership

- M396: residence identity, admission and declared capabilities.
- M397: authentication, session and communication readiness.
- M398: governed physical transport.
- `ResidentComponentRegistry`: resident lifecycle state.
- M402: integration/observation only.

## Invariants

- RN-W01: resident component id resolves through the existing registry.
- RN-W02: unknown resident never creates implicit registration.
- RN-W03: lifecycle wiring is read-only.
- RN-W04: RUNNING alone never implies node READY.
- RN-W05: M402.1 evaluator remains the state derivation point.
- RN-W06: M402 owns neither connectivity nor transport.
- RN-W07: the generic resident registry receives no M396 semantics.
- RN-W08: primary-home operation remains independent of residential-node availability.
- RN-W09: node loss grants no authority and removes no central authority.
- RN-W10: no state synchronization is introduced.

## Explicitly out of scope

- `ResidentialNodeRuntime`;
- new lifecycle authority;
- new residential registry;
- remote execution;
- memory/knowledge/config synchronization;
- cameras, sensors or Residential Perception;
- hardware bootstrap;
- background polling.

## Validation target

Source baseline: validated M402.1 — 11,054 tests, Ruff clean, M361 synchronized.

M402.2 adds seven architecture tests. Expected full-suite total: **11,061 tests**.
