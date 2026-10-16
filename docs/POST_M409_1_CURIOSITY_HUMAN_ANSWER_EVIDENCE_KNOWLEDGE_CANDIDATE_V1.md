# Post-M409.1 — Curiosity Human Answer Evidence & Knowledge Candidate Foundation v1

## Status

IMPLEMENTED / CERTIFICATION PENDING USER GATES.

## Purpose

Represent an explicitly linked human answer to a certified curiosity question
and, when appropriate, produce a read-only knowledge candidate that remains
pending admission by existing authorities.

The foundation preserves the distinction between:

- what Carlos or Cristina explicitly said;
- what epistemic strength that answer currently has;
- what ROBY may later admit as knowledge.

## Outcomes

`KNOWLEDGE_CANDIDATE`, `PARTIAL_KNOWLEDGE_CANDIDATE`,
`UNCERTAIN_KNOWLEDGE_CANDIDATE`, `CORRECTION_CANDIDATE`,
`NOT_AN_ANSWER`, and `ABSTAIN`.

Exact linkage requires the curiosity report id, question id and explicit human
answer reference. Missing or mismatched linkage fails closed with `ABSTAIN`.

## Governance

This v1 does not persist, write memory, create a Learning-domain candidate,
modify knowledge, call `LearningAuthority`, call `OfficialKnowledgeRuntimeGateway`,
wire the conversation Gateway, use a provider, use network access, execute an
action or create a new authority.

A produced `CuriosityKnowledgeCandidate` is only evidence prepared for a later
admission gate. Even an explicit human answer remains pending admission.

M410, networking and Residential remain out of scope.
