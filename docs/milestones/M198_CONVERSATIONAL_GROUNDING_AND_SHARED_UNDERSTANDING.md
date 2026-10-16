# M198 — Conversational Grounding and Shared Understanding

M198 adds an explicit, bounded model of shared understanding to ROBY's official
conversation runtime. It distinguishes ordinary alignment, explicit
confirmation, corrected scope, and unresolved clarification.

The capability consumes M197 repair guidance when available, preserves
clarification boundaries, and contributes only prompt guidance and traceable
references. It cannot execute tools, change providers, mutate memory, authorize
plans, or initiate actions.

## Acceptance

- deterministic grounding classification;
- explicit confirmation acknowledgement;
- corrected-scope projection;
- unresolved-clarification boundary preservation;
- official ordering immediately after M197;
- provider request preservation;
- advisory-only behavior and deterministic lineage.
