# ADR 198 — Conversational Grounding and Shared Understanding

## Decision

ROBY will add a deterministic, advisory grounding capability immediately after
M197. It will translate current repair signals and explicit user alignment into
a bounded shared-understanding state: aligned, explicitly confirmed, corrected
scope, or clarification pending.

## Rationale

M197 determines when dialogue repair is needed, but the runtime still lacks an
explicit representation of whether both sides can safely proceed under the same
scope. M198 makes that boundary visible to downstream cognitive stages without
inventing missing details or repeating the conversation unnecessarily.

## Consequences

- M198 may consume the current M197 assessment but does not own or mutate it;
- unresolved clarification remains a hard conversational boundary against assumptions;
- the latest correction becomes the active shared scope;
- explicit confirmations are acknowledged briefly rather than redundantly restated;
- no provider, tool, memory, planning, or action authority is added;
- references hash bounded classifications and metadata, not raw user content;
- official contributor order is M196, M197, M198, then existing cognitive stages;
- M198 remains optional, deterministic, and failure-contained.
