# ROBY XI.2 — E1-B Creative Critical Disposition → Existing Proposal Reachability
## CONTRACT RED

Date: 2026-10-04  
Status: **CONTRACT RED / EXPECTED RED / STOP BEFORE GREEN**  
Product change: **NONE**

## 1. Certified entry gate

This contract starts from the immediately preceding certified reconciliation:

`ROBY_XI_2_MASTER_PLAN_E1_B_CREATIVE_CRITICAL_DISPOSITION_TO_EXISTING_PROPOSAL_REACHABILITY_PRE_RED_RECONCILIATION.md`

Entry baseline recorded there:

- pytest: **13,399 PASS / 0 FAIL**;
- Ruff: **clean**;
- exact residual revalidated as
  `EXPLICIT_HUMAN_PROMOTION_OF_CREATIVE_CRITICAL_DISPOSITION_TO_EXISTING_PROPOSAL`;
- CONTRACT RED: **AUTHORIZED**.

No historical E1-B status label overrides this current executable gate.

## 2. Exact missing seam

The contract targets only:

`exact GovernedCreativeCandidateCriticalDisposition(REVIEW_REQUIRED)`  
`→ explicit human promotion bound to exact disposition/session`  
`→ MISSING subordinate creative-disposition Proposal projection`  
`→ existing GovernedProposalModel.create(...)`  
`→ existing GovernedProposalInbox.enqueue(...)`  
`→ existing PENDING GovernedProposal`  
`→ STOP`.

This is a reachability/semantic-projection residual between existing authorities.
It is not a missing creative engine and not a missing Proposal system.

## 3. Existing authorities that remain canonical

The RED preserves without replacement:

- E1-A producer: `OfficialGovernedReasoningRuntimeGateway`;
- Proposal model: `domain.governed_proposal.GovernedProposalModel`;
- Proposal inbox: `domain.governed_proposal_inbox.GovernedProposalInbox`;
- Proposal lifecycle: `app.governed_proposal_lifecycle.GovernedProposalLifecycle`;
- E1-B-S1-A/B/C downstream human-review chain.

No second model, inbox, lifecycle, planner, manager, reasoning authority, or Proposal
brain is admissible.

## 4. Contract obligations

The RED requires the future bounded projection to prove that:

1. it consumes the exact canonical E1-A disposition type;
2. E1-A remains read-only and `creates_proposal=False`;
3. `REVIEW_REQUIRED` alone never creates a Proposal;
4. explicit human promotion is required;
5. the promotion is bound to exact disposition/session semantics;
6. canonical `GovernedProposalModel` owns Proposal construction;
7. canonical `GovernedProposalInbox` owns admission to `PENDING`;
8. proposal provenance preserves disposition id, synthesis fingerprint, hypothesis
   identity/fingerprint, disposition status, rationale, independent-evidence
   requirement, and `governed_reasoning` source authority;
9. replay of one promotion attempt cannot create a duplicate Proposal;
10. the seam does not accept/dismiss the Proposal;
11. it performs no Planning, Authorization, Execution, Memory, Knowledge, Learning,
    network action, subprocess action, or self-modification;
12. proactive `RelevanceEvaluator` / `should_share` policy is not promotion authority;
13. productive composition reuses the exact Proposal model/inbox instances already
    owned by `OfficialConversationGateway`.

## 5. RED artifact

`tests/architecture/test_e1_b_creative_critical_disposition_existing_proposal_reachability_contract_red.py`

Expected RED cause:

`app.governed_creative_disposition_proposal_projection` does not yet exist, and the
productive gateway therefore does not yet compose that subordinate projection.

No productive implementation is added in this phase.

## 6. Protected boundaries

This RED does **not** modify `app/governed_reasoning_runtime.py` and does not reopen
E1-B-S1-A/B/C. It does not authorize automatic proposal creation, automatic
acceptance, Planning, Authorization, Execution, Memory/Knowledge/Learning writes,
background activity, or a new cognitive/Proposal authority.

## 7. STOP

`CONTRACT_RED: ESTABLISHED`

`EXPECTED_FAILURE: MISSING BOUNDED CREATIVE-DISPOSITION → EXISTING-PROPOSAL PROJECTION`

`PRODUCTIVE_IMPLEMENTATION: NONE`

`GREEN: NOT AUTHORIZED IN THIS BLOCK`

STOP before GREEN.
