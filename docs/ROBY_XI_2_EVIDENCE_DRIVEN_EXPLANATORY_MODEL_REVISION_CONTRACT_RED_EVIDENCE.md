# ROBY XI.2 — Evidence-driven Explanatory Model Revision
## Contract RED Evidence — feedback-loop closure

**Entry baseline:** 13,521 PASS + Ruff clean (user-certified).

## Objective

Freeze the missing productive contract after governed Level2 evidence re-entry,
without implementing GREEN and without creating a new reasoning authority.

Target loop:

`Explanatory Model V1`
→ `DiscriminatingEvidenceRequirement`
→ governed investigation/evidence acquisition
→ `GovernedLevel2ReasoningReentryResult`
→ same-hypothesis reassessment
→ revised discrimination
→ `Explanatory Model V2`
→ ordinary Reasoning consultative reachability.

## Existing boundary confirmed

`GovernedLevel2ReasoningReentryFoundationV1` already:
- converts acquired evidence into an `EvidenceReference`;
- preserves requirement / plan / authorization / execution / snapshot lineage;
- registers the observation in the canonical evidence registry;
- performs exactly one governed reasoning reevaluation;
- remains generic and does not own explanatory-model composition.

`GovernedExplanatoryModelComposer` already composes governed multi-hypothesis
reports into a bounded consultative model. The RED contract therefore requires
**composition between existing owners**, not a new Explanatory Model Revision
Engine.

## RED contract frozen

The future GREEN must provide an existing-owner composition boundary with these
externally testable surfaces:

1. `app.governed_explanatory_model_revision`
   - `GovernedExplanatoryModelRevision`
   - `GovernedEvidenceDrivenExplanatoryModelRevisionV1`

2. `OfficialGovernedReasoningRuntimeGateway`
   - `bind_productive_explanatory_model_revision(...)`
   - `productive_explanatory_model_revision(...)`
   - `productive_explanatory_model_revision_reference_ids(...)`

3. `CanonicalProductiveReasoningSource`
   - `explanatory_model_revision_context_lines(...)`

These names define a composition contract, not a new cognitive authority.

## Required semantic invariants for GREEN

A valid revision must be able to prove:
- V2 derives from the exact V1 model lineage;
- the exact acquired `evidence_id` is part of the revision lineage;
- the same original hypothesis set is reassessed rather than silently replaced;
- discrimination is recomputed from governed evidence;
- V2 has a materially changed governed assessment or explicitly abstains from
  claiming revision when evidence is non-discriminating;
- unresolved discrimination requirements may shrink, change, or remain;
- owner/session/world-snapshot lineage remains coherent;
- result remains read-only and consultative;
- no truth or causality is established;
- no Memory, Learning, World Model, Structural Transfer, rule registration,
  capability execution, action, or new authority is introduced.

## RED execution

External contract test:
`test_evidence_driven_explanatory_model_revision_contract_red.py`

Execution result on the certified codebase:

**4 FAILED + 1 PASSED**

Expected failures:
- missing governed revision composition boundary;
- missing runtime productive binding;
- missing same-turn revision accessor/reference surface;
- missing consultative Reasoning context surface.

Expected passing invariant:
- Level2 reasoning re-entry remains generic and does **not** become the
  explanatory-model authority.

This is a valid RED state: the already-certified architecture remains intact,
while the exact feedback-loop gap is now executable and explicit.

## GREEN admission rule

GREEN is complete only when this RED contract becomes fully green **without
weakening any existing tests**, while preserving the historical import graph and
all canonical authority boundaries.

Official promotion after GREEN remains gated by:

`ruff check .`

`pytest -q`

The current official baseline remains **13,521 PASS + Ruff clean** until the
future GREEN block is locally certified.
