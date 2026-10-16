# M176 — Desktop Runtime Integration

## Objective
Connect ROBY's desktop application to the governed conversational and operational response boundaries.

## Scope
- Add immutable desktop runtime requests and results.
- Preserve exact M162 readiness lineage.
- Reuse M172 for greetings, preserving M163–M165 lineage.
- Delegate non-greeting requests through an injected operational pipeline returning M175 responses.
- Map completed/partial, withheld, and failed outcomes to the stable desktop `UIResponse` contract.
- Preserve provider and network execution flags as lineage only.
- Add append-only in-memory audit storage.
- Add an operational desktop bootstrap helper without replacing the historical bootstrap.

## Non-goals
- No provider construction or routing.
- No knowledge retrieval or network authorization.
- No response synthesis or rewriting.
- No Tkinter event-loop changes.
- No platform mutation.

## Acceptance
- Ruff passes.
- 30 focused tests pass.
- Complete repository suite passes without regressions.
