# ROBY XI.2 — E1-B-S1-A — Exact Governed Proposal Human-Review Disposition — Contractual RED

## Status

**CONTRACTUAL RED / NO PRODUCTIVE IMPLEMENTATION / STOP BEFORE GREEN**

Starting Owner-certified baseline: **12,900 PASS · 0 FAIL · Ruff clean**.

## Reconciliation correction captured by this RED

Current certified code already contains the canonical proposal disposition authority:

- `domain.governed_proposal.ProposalState` with `OFFERED → ACCEPTED` and `OFFERED → DISMISSED`;
- `domain.governed_proposal_inbox.GovernedProposalInbox` as the canonical local proposal state owner;
- `app.governed_proposal_lifecycle.GovernedProposalLifecycle` as the canonical stored proposal transition authority;
- existing gateway surfaces `accept_governed_proposal(...)` and `dismiss_governed_proposal(...)`;
- existing presentation policy and executive-notification reachability that move a presented proposal to `OFFERED` only after real broker dispatch.

Therefore the prior hypothesis that E1-B lacked a proposal-disposition owner is destroyed.

The exact missing seam is narrower:

`EXISTING OFFERED GOVERNED PROPOSAL`
→ `EXPLICIT HUMAN RESPONSE BOUND TO EXACT proposal_id`
→ **MISSING BOUNDED HUMAN-REVIEW SEMANTIC PROJECTION**
→ `EXISTING GovernedProposalLifecycle.accept(...) / dismiss(...)`
→ `ACCEPTED | DISMISSED`
→ `STOP`.

## Contract obligations

The RED requires one bounded projection that:

1. reuses `GovernedProposalLifecycle` as the sole disposition authority;
2. consumes an exact `proposal_id` and explicit human response;
3. accepts only an already-`OFFERED` proposal through existing lifecycle rules;
4. projects explicit acceptance to existing `ACCEPTED`;
5. projects explicit dismissal to existing `DISMISSED`;
6. fails closed on ambiguous human text without mutating proposal state;
7. preserves exact proposal identity;
8. creates no second inbox/model/lifecycle/approval authority;
9. performs no Planning, Authorization, Execution, Memory/Learning write, network action, subprocess action, or self-modification;
10. stops immediately after inert proposal disposition.

No `DEFER` state is invented: the current canonical proposal model does not define one.

## RED artifact

`tests/architecture/test_e1_b_s1_a_exact_governed_proposal_human_review_disposition_contract_red.py`

The expected RED is the absence of the bounded projection module:

`app.governed_proposal_human_review_projection`

No productive module is added by this RED.

## STOP

Do not implement GREEN until Owner certification of this RED.
