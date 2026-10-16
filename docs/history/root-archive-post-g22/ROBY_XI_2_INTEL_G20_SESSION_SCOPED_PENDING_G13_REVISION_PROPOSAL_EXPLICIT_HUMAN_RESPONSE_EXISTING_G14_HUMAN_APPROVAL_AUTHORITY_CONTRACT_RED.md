# ROBY XI.2 — INTEL-G20 — CONTRACT RED

## Scope

Prove the missing productive seam:

`session-scoped pending G13 revision proposal + explicit human response`
→ existing `M369ExplicitHumanLearningApprovalEvidenceFoundation.evaluate_revision(...)`
→ `ApprovedKnowledgeRevisionEvidence | None`
→ STOP.

## Required reuse

- Existing `OfficialConversationGateway`.
- Existing `ProductiveGovernedLearningWiring`.
- Existing G19 session-scoped pending G13 proposal.
- Existing G14 human approval authority (`self._approval`).
- Exact G13 proposal identity and exact human linkage.

## RED expectations

1. Existing productive wiring exposes a pending-revision approval seam.
2. That seam retrieves the exact session-scoped pending proposal and delegates to
   `self._approval.evaluate_revision(...)`.
3. Official conversation accepts an explicit revision approval response and routes
   it through the same productive wiring using the effective session.
4. The stage stops before G15, G16, G18/G17 and Memory mutation.
5. No duplicate wiring, approval authority, manager or Memory gateway.

## Frozen distinctions

- PENDING PROPOSAL != APPROVED PROPOSAL
- SAME SESSION != HUMAN APPROVAL
- HUMAN RESPONSE != EXACT LINKAGE
- EXACT LINKAGE != APPROVAL
- G14 APPROVED EVIDENCE != G15 APPLICATION
- APPROVED REVISION != APPLIED REVISION
- NO PENDING PROPOSAL != PERMISSION TO RECONSTRUCT ONE
- ANOTHER SESSION'S PROPOSAL != CURRENT SESSION'S PROPOSAL
