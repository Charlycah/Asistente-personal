# ROBY XI.2 — RR1 → R2 Requirement Admission — Contract RED

This RED freezes one missing long-horizon bridge:

`RR1 RECORDED_CONTINUATION + exact revised GovernedHypothesisDeepeningReport`
→ existing `GovernedMultiHypothesisProductiveConsumptionV1`
→ zero/one exact new `DiscriminatingEvidenceRequirement`
→ existing `GovernedMultiStepInvestigationProductiveContinuationV1`
→ `READY_FOR_PLANNING` or canonical `NO_NEW_REQUIREMENT` stop.

The bridge must prove that the RR1 acquired `evidence_id` is present in the revised
hypothesis assessment before discrimination. It must fail closed on source/snapshot
mismatch, non-RR1 state, missing reentry/evidence identity, or ambiguous (>1) requirements.

It must never manufacture or rewrite requirements, choose among multiple requirements,
invoke Planning/Authorization/Execution/Reasoning, create Curiosity questions, persist,
modify Memory/World Model, establish truth, retry, or start background work.
