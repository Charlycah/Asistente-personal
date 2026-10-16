# ROBY XI.2 — P7-C2-LOCAL-S2B-B — CONTRACTUAL RED

## Status

**CONTRACTUAL RED / OWNER CERTIFICATION PENDING / NO PRODUCTIVE IMPLEMENTATION**

Entry baseline: P7-C2-LOCAL-S2B-A Owner-certified / CLOSED at
**12,863 PASS / 0 FAIL / Ruff clean**.

## Exact seam

**R-C2-LOCAL-S2B-B — EXISTING M400 INFORMATION-SOURCE ENVELOPE → EXISTING
VERIFICATION/ASSESSMENT → EXISTING M401 LINEAGE/ADMISSION → EXISTING
CONVERSATIONAL HANDOFF.**

The RED requires one bounded application composition and no new epistemic authority.

## Required contract

The future composition must:

1. accept an already-existing M400 `ExternalIntelligenceEnvelope`;
2. require an explicit timezone-aware `assessed_at` boundary;
3. reuse `GovernedExternalIntelligenceVerifier`;
4. reuse `GovernedExternalEvidenceAssessor`;
5. construct the existing `CognitiveExternalEvidenceLineage`;
6. construct the existing `CognitiveExternalEvidenceAdmission`;
7. derive cognitive admission status from the existing assessment semantics;
8. never promote REJECTED evidence into cognitively usable evidence;
9. preserve limitations and explicit rationale;
10. preserve that external evidence does not certify truth;
11. return/expose the existing admission object for the already-existing
    `external_evidence` conversational handoff;
12. STOP before conversational publication.

## Status derivation boundary

The RED requires the implementation to derive, not accept arbitrarily, M401 status.
The exact mapping must remain bounded by existing M400/M401 semantics:

- M400 `REJECTED` → M401 `REJECTED`;
- weaker/non-complete evidence must not be silently promoted to unrestricted
  `ADMITTED`;
- usable strong evidence may become `ADMITTED`;
- usable evidence with material limitations remains `LIMITED`.

This mapping is evidence admission, not truth certification.

## Existing downstream handoff

`OfficialConversationGateway.submit(... external_evidence=...)` already accepts
`CognitiveExternalEvidenceAdmission` objects. S2B-B must expose the admission for
that existing consumer; it must not call `submit()` itself.

This preserves:

**ADMISSION COMPOSITION ≠ CONVERSATION PUBLICATION.**

## Explicit non-authorizations

This RED does not authorize:

- provider execution;
- network authorization;
- Foursquare access;
- query preparation;
- new retrieval authority;
- new verifier/assessor;
- new evidence model;
- new cognitive runtime;
- Memory or Learning;
- Planning or Execution;
- persistence;
- booking/reservation;
- navigation/routing;
- automatic/background work;
- gateway surgery;
- reopening S1, RC1, S2B-A or P7-C2-S1;
- Point 9.

## Expected RED

Existing-authority and S2B-A STOP tests should pass.
Tests requiring `app.governed_external_cognitive_admission_composition` must fail
until GREEN.

**STOP FOR OWNER RED CERTIFICATION BEFORE GREEN.**
