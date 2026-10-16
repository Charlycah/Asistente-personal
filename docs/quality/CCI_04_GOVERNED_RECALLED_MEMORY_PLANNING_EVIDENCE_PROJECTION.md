# CCI-04 — Governed Recalled Memory Planning Evidence Projection

Status: implementation/certification ready; closure validation pending.

CCI-04 adds one bounded evidence projection from memories already selected by the
official Memory recall path into the existing Planning runtime contribution. It
creates no authority, manager, gateway, store, goal generator or action executor.

Memory remains authoritative for recall. Planning does not query the memory store.
The projection carries memory identity, owner, scope, confidence, recall score and
provenance through request metadata consumed only as bounded planning evidence.

Planning remains advisory. Recalled evidence may add a planning consideration to an
already approved/active executive plan, but cannot create goals, execute actions or
write Memory. Owner mismatch and malformed evidence fail closed; absent or irrelevant
recall preserves baseline Planning behavior.

Certification includes a causal A/B case from governed learned memory through
official recall into a changed Planning contribution, plus negative controls for no
recall, owner isolation, malformed evidence, missing provenance and power boundaries.

Whole-System diagnostic state after CCI-04: 7 PASS, 2 PASS_BY_DESIGN, 1 PARTIAL,
0 FAIL. The remaining PARTIAL scenario is CCI-10.
