# Post-M409.1 — Governed Evidence Acquisition Planning Foundation v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Convert a governed `DiscriminatingEvidenceRequirement` into a read-only, consultative
plan describing which already-registered capabilities explicitly declare that they can
provide the missing evidence.

## Existing authorities reused
- `governed_reasoning` owns the upstream discrimination requirement.
- `planning_foundation` owns evidence-acquisition planning.
- M62 `CapabilityRegistryManager` remains the sole capability catalogue.

No new registry, routing authority, executor, worker, scheduler or service locator is added.

## Minimal capability contract extension
`CapabilityDescriptor` gains optional `evidence_outputs: tuple[str, ...] = ()`.
Existing registrations therefore keep exactly their prior behaviour until they explicitly
declare an evidence output. `OfficialRuntimeCapabilityRegistry.register()` only passes the
optional declaration into the existing descriptor.

## Matching rule
A planner candidate exists only when an enabled descriptor explicitly declares an evidence
output equal to the required evidence after case/whitespace normalization. Names, tags,
semantic triggers, supported intents and module names do not establish compatibility.

## Planning outcomes
- `PLANNABLE`: every missing evidence description has exactly one explicit provider.
- `PARTIALLY_PLANNABLE`: at least one description has a provider and at least one does not.
- `AMBIGUOUS`: at least one evidence description has multiple explicit providers.
- `NO_CAPABILITY_AVAILABLE`: no enabled descriptor explicitly provides the required evidence.

## Hard boundaries
The plan is read-only and consultative. It does not select a candidate for execution, grant
permission, invoke capabilities, acquire evidence, ask Curiosity, access Android, use
networking, write memory, mutate the world model, execute actions or start background work.

`plan != approval != execution`.

## Validation included
Nine architecture/semantic tests cover explicit matching, no-match fail-closed behaviour,
ambiguity, partial planning, disabled capabilities, exact lineage, reuse of PlanningFoundation,
absence of operational bypass and propagation through the official runtime registry.
