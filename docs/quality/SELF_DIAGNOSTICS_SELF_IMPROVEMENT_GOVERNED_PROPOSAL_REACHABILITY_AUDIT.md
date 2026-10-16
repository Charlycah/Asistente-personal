# Self-Diagnostics / Self-Improvement Proposal → Governed Proposal Reachability Audit

## Baseline

Owner-certified input: **12,358 PASS · 0 FAIL · Ruff clean**.

## Finding

M399.5 already owns the inert technical review artifact `DiagnosticProposal`. The
self-improvement producer already derives a bounded `DiagnosticProposalRequest` from a
reproduced proof and hash-bound project evidence. Separately, the canonical governed
proposal model/inbox now have a certified productive route to the existing Executive
Notification spine.

The residual was not another self-improvement engine or notifier. It was a bounded
presentation seam from an already-prepared `DiagnosticProposal` into the canonical
household governed-proposal inbox.

## Surgery

`SelfImprovementGovernedProposalReachability` accepts only `DRAFT` diagnostic proposals
and uses the already-constructed `GovernedProposalModel` and `GovernedProposalInbox`.
It creates a human-presentation envelope with category `self_improvement_review`, keeps
proposal/proof/hypothesis/review identities in metadata, addresses both co-owners, and
marks `human_review_required=true` and `autonomous_execution=false`.

It deliberately does **not** use personal-interest relevance as the admission criterion:
a technical self-improvement proposal requiring owner review is a governance obligation,
not an entertainment/news-interest candidate. It also does not bypass the canonical
proposal model or inbox.

## Boundaries preserved

- `GovernedSelfDiagnostics` remains the only self-diagnostics authority.
- `DiagnosticProposal` remains the technical review artifact.
- `GovernedProposalModel` remains the governed proposal creation authority.
- `GovernedProposalInbox` remains the canonical proposal inbox.
- Existing presentation/lifecycle policy remains unchanged.
- Existing Executive Notification reachability remains unchanged.
- No code mutation, patch apply, approval, autonomous execution, background diagnosis,
  new persistence path, new inbox, new broker, or new Composition Root is introduced.

## Status

**IMPLEMENTED / PENDING OWNER CERTIFICATION**.
