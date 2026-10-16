# RF-E/3A.8 — Governed Temporary Rule Productive Intake — Implementation v1

## Status

CLOSED/PASS. Official validated baseline: 12.186 tests + Ruff clean.

## Purpose

Compose the already certified RF-E boundaries on the one canonical governed-reasoning
runtime without adding semantic authority.

The productive path is:

1. explicit bounded rule interpretation;
2. bounded semantic role/relation grounding;
3. governed grounding compilation to an abstract instantiation spec;
4. session-local, in-memory continuity of that compiled spec;
5. bounded case grounding on a later turn in the same session;
6. explicit case claim projection;
7. contextual rule instantiation;
8. temporary concrete rule admission into the existing canonical inference registry.

## Governance

The intake remains subordinate to `governed_reasoning`.

It does not persist compiled specs, create or modify Memory/Learning, use a provider,
use retrieval, create an entity repository, create a second inference registry, execute
actions, or grant authority.

Pending compiled specs are process-local, session-isolated, bounded to four entries per
session, and expire after thirty minutes. A supported case consumes its pending spec and
admits only a temporary, review-required rule through the existing 3A.6 boundary.

## Epistemic limits

Case evidence must satisfy the already certified bounded case-grounding contract.
Unknown or incomplete alternative evidence cannot produce a claim projection or rule
admission. Unsupported and ambiguous cases fail closed.

GAP A remains deferred: this increment does not broaden the explicit `si ... entonces`
grammar certified by contextual rule interpretation.

## Compatibility

Calls to governed reasoning without `scope_reference` preserve legacy behavior and do
not participate in productive temporary-rule intake.
