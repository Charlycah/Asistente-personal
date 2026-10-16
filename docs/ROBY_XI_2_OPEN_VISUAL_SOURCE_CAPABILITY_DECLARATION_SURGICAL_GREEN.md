# ROBY XI.2 — Open Visual Source Capability Declaration — Surgical GREEN

## Scope
Implements only the Owner-certified capability-declaration contract.

## Productive delta
- `InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY`.
- Immutable `GovernedInformationSource.capabilities`, default `frozenset()`.
- Existing canonical selector requires that explicit capability for
  `OPEN_VISUAL_SUBJECT`.
- `GovernedSourceQueryContract.prepare()` repeats the same authorization check.
- `TOPIC_CONSTRAINED` topic validation remains unchanged.

## Preserved boundaries
All legacy/current sources, including NASA, inherit the empty capability set.
No productive general-image provider or adapter is added. No new registry,
selector, executor, gateway authority, presentation behavior, or freshness
ordering is introduced.

The repaired contract test is included with the canonical `name=` fixture.
