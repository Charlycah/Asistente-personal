# CCI-03 — Governed Mental Model Decision Evidence Projection

Status: implementation/certification ready; closure validation pending.

CCI-03 adds one bounded evidence projection from existing Mental Model assertions to
the existing canonical decision advisory path. It creates no authority, manager,
gateway, persistence, option generator, action executor, or psychological inference.

Eligible evidence is restricted to ACTIVE mental models and ACCEPTED assertions with
sufficient confidence, provenance, compatible owner and intersecting scope. Option
compatibility is explicit: the projector never invents a mapping from a person model
to a decision option.

Decision authority remains `unified_cognitive_coordination` through
`CanonicalDecisionFacade` and `GovernedDecisionAdvisor`. Mental-model evidence is
read-only and advisory-only.

Certification includes the positive A/B causal case and negative controls for
tentative/disputed assertions, owner isolation, incompatible scope, low confidence,
missing provenance and irrelevance.

Whole-System diagnostic state after CCI-03: 6 PASS, 2 PASS_BY_DESIGN, 2 PARTIAL,
0 FAIL. Remaining PARTIAL scenarios are CCI-04 and CCI-10.
