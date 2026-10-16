# ROBY XI.2 — R-CI-SI-S5-B2-C3-A3
## Governed Authorization Productive Consumption Correspondence — CONTRACT RED

Status: RED contractual. No production implementation is authorized by this document.

## 1. Certified entry state

A3 begins only from an actual `GovernedEpistemicAuthorizationResultBinding`
produced by C3-A2. A3 MUST NOT accept a detached authorization report as its
S5 entry surface and MUST NOT reconstruct A1, selection, eligibility, request,
or authorization.

The canonical authorization policy owner remains
`GovernedIndependenceAuthorizationBoundaryV1`. The canonical productive
consumption owner remains
`GovernedIndependenceAuthorizationProductiveConsumptionV1`.

## 2. Exact responsibility

A3 is a read-only, derivational correspondence bridge. Its only positive act is:

ACTUAL A2 RESULT BINDING
→ exact existing `authorization_report`
→ `GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(report)`
→ exact productive consumption binding
→ STOP.

A3 creates no authorization policy, no new decision, no new eligibility rule,
no planning lineage, no acquisition authority, and no execution authority.

## 3. R1 — actual A2 admission only

The bridge MUST require an actual
`GovernedEpistemicAuthorizationResultBinding`. It MUST preserve that A2 object
by identity and preserve its A1 correspondence, selection, and selected-path
eligibility anchors by identity.

## 4. R2 — exact existing owner and report

The bridge MUST pass A2's exact `authorization_report` object to the existing
`GovernedIndependenceAuthorizationProductiveConsumptionV1.consume` owner.
It MUST call that owner exactly once. It MUST NOT call Authorization again.

## 5. R3 — exact productive object preservation

The result MUST preserve the exact returned
`GovernedIndependenceAuthorizationProductiveConsumption` object by identity.
It MUST preserve its decision, independence level, authorization ID,
requirement ID, plan ID, capability name, source reference, world snapshot ID,
rationale codes, and productive source fingerprint without translation.

## 6. R4 — A2 ↔ productive-consumption correspondence

A3 MUST reject a productive result whose embedded `authorization_report` is
not the exact A2 report object, or whose authorization ID, decision,
independence level, requirement ID, plan ID, capability name, source reference,
world snapshot ID, or rationale codes do not correspond exactly to A2's report.
No repair or normalization is permitted.

A2's canonical authorization-report `source_fingerprint` remains preserved on
A2. The productive consumption's `source_fingerprint` is the existing owner's
derived productive fingerprint; A3 MUST preserve it as such and MUST NOT claim
that the two fingerprints are the same semantic field.

## 7. R5 — next-gate eligibility is owner-derived only

A3 MUST expose the existing productive consumption's
`eligible_for_next_governed_gate` value without recalculation. It MUST NOT
create `AUTHORIZED_FOR_EXECUTION`, `EXECUTABLE`, `ACQUIRE_NOW`, scores,
confidence thresholds, or any parallel authorization/eligibility taxonomy.
`MAY_INITIATE` remains distinct from execution authorization.

## 8. R6 — direct Authorization IDs remain owner-internal

A3 MUST preserve A2's S5 `requirement_identity` separately from Authorization
owner-internal `requirement_id` and `plan_id`. It MUST NOT reinterpret those
direct IDs as S5 lineage and MUST NOT synthesize Evidence Acquisition Planning.

## 9. R7 — owner failure or invalid output cannot be repaired

If the productive-consumption owner raises, A3 MUST propagate the failure. If
it returns an invalid type or an inconsistent product, A3 MUST return no
binding. A3 MUST NOT retry, fabricate, repair, normalize, or fall back to a
second authority.

## 10. R8 — non-executive STOP

A3 MUST remain read-only and derivational. It MUST NOT:

- query capability registry or official runtime;
- rerun A1 or A2;
- select/rank/reselect epistemic paths;
- plan or acquire evidence;
- invoke C or D;
- query the selected source;
- call an execution gateway;
- authorize or execute actions;
- translate MUST_ASK into a question;
- translate MUST_ABSTAIN into an epistemic conclusion;
- resolve REVIEW_REQUIRED;
- invoke Curiosity, Relevance, Initiative, or Conversation;
- persist results, create learning candidates, or modify Memory/world model;
- create a new cognitive authority or claim subjective experience.

The STOP is immediately after exact productive authorization consumption
correspondence. Any route from this direct S5 authorization lineage toward
acquisition/evidence or execution requires a separate post-A3 reconciliation.

## 11. RED expectation

The contractual tests R1–R8 MUST fail only because
`app.governed_epistemic_authorization_productive_consumption_binding` does not
yet exist. No GREEN implementation is part of this increment.
