# ROBY XI.2 — E1-B-S1-B — Exact Presented Proposal Reference → Human-Review Transport Continuity — CONTRACT RED

Status: **CONTRACTUAL RED / NO PRODUCTIVE IMPLEMENTATION**

Certified starting baseline: **E1-B-S1-A Owner-certified — 12,901 PASS / 0 FAIL / Ruff clean**.

## Residual

The existing governed proposal notification path carries the exact `proposal_id` in
its executive event and moves that exact proposal to `OFFERED` after broker dispatch.
The desktop presentation boundary currently drains only rendered text. The existing
human conversational ingress later receives response text/session context, but not the
exact presented proposal reference required by the certified
`GovernedProposalHumanReviewProjection`.

The missing seam is therefore transport/reference continuity only:

`EXACT PRESENTED proposal_id`
→ bounded reference continuity
→ explicit human review
→ existing `GovernedProposalHumanReviewProjection`
→ existing `GovernedProposalLifecycle`
→ `ACCEPTED | DISMISSED`
→ **STOP**.

## Contract

The future GREEN must:

1. preserve only the exact identity of a proposal that was actually presented;
2. keep the proposal itself owned by the canonical inbox/lifecycle;
3. reuse the already-certified `GovernedProposalHumanReviewProjection`;
4. never infer identity from title, summary, newest/latest proposal, or "only OFFERED";
5. fail closed when no exact presented reference exists;
6. fail closed when more than one unresolved presented reference makes "esta propuesta" ambiguous;
7. consume only the exact transport reference after a successful terminal disposition;
8. leave ambiguous/failed review references and canonical proposal state unchanged;
9. create no second proposal inbox, lifecycle, semantic evaluator, or proposal authority;
10. grant no Planning, Authorization, Execution, Memory/Learning, network, subprocess,
    or self-modification authority;
11. STOP after the existing lifecycle returns the governed disposition.

This RED does **not** authorize changes to `OfficialConversationGateway`, Planning,
Authorization, Execution, or proposal creation semantics.
