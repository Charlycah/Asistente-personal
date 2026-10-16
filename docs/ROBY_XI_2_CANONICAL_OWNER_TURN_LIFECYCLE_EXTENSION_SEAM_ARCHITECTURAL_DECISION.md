# ROBY XI.2 — Canonical Owner-Turn Lifecycle Extension Seam
## Architectural Decision

## Owner-certified starting state

The preceding PRE-RED reconciliation is Owner-certified:

- 13,479 tests passed;
- 0 tests failed;
- Ruff clean;
- no injectable owner-turn lifecycle seam demonstrated;
- STOP before CONTRACT RED certified.

This decision changes no productive Python code and adds no RED tests.

## Decision question

The applied conversational capability already exists under the canonical
`OfficialConversationGateway`.

The remaining requirement is to admit one recognized applied owner-turn branch
inside the canonical lifecycle envelope so that the same turn receives,
exactly once:

- observer/evidence begin;
- governed branch execution;
- response evidence;
- post-turn reflection;
- submitted-turn accounting;
- observer completion;
- evidence sealing;
- subsequent UnifiedBrain cognitive analysis.

The question is whether this requires a new authority, an external lifecycle
wrapper, or a governed evolution of the existing owner.

## Documentary governance

The Master Capability Registry defines Class 2 as:

`Existing capability deepening`

and states that the preferred evolution path is to extend the canonical owner
and prove the residual with RED evidence.

Class 5 is reserved for authority/persistence migration and requires retirement
of the former owner plus zero parallel authority.

This case does not migrate authority.

`OfficialConversationGateway` remains the canonical owner before and after the
proposed evolution.

The Cognitive Inventory Master Guide also establishes:

- a failing existing test is presumed contractual until audited;
- never edit a test merely to make implementation pass;
- if a contract must intentionally change, document the architectural decision
  and migrate production plus tests together;
- historical contracts must not be erased.

Therefore a protected byte hash is not an eternal prohibition against any
future governed evolution. It is evidence of a certified architectural state
whose contract may only be migrated explicitly.

## Historical precedent

ROBY already distinguishes two cases.

### Rejected surgery

Earlier GREEN attempts that modified protected runtime surfaces without an
authorized migration were rejected.

The correct response was to restore those files byte-identically rather than
rewrite historical hashes.

That rule remains fully binding.

### Explicit contract evolution

CAP-11 records a different case: a formerly fixed step-two guard was
intentionally generalized to governed N-step semantics.

The same authority was preserved, historical step-two behavior remained an
exact compatibility guard, and one stale historical assertion was migrated
because the architectural contract itself had explicitly evolved.

This is the applicable governance pattern.

## Architectural classification

The required lifecycle seam is classified:

`CLASS 2 — EXISTING CAPABILITY DEEPENING`

It is not:

- Class 3 new instrumental capability;
- Class 4 new cognitive primitive;
- Class 5 authority migration.

Canonical authority remains:

`OfficialConversationGateway`

UnifiedBrain remains the existing integrated brain.

No new lifecycle authority is authorized.

## Chosen direction

The architectural decision is:

`AUTHORIZE A NARROW GOVERNED EVOLUTION OF THE CANONICAL GATEWAY LIFECYCLE`

The target semantic is not a public generic plugin framework.

The target is one bounded applied owner-turn branch admitted inside
`OfficialConversationGateway.submit` before the existing common finalization
section.

The branch must reuse the gateway's existing applied conversational
intelligence capability.

It must not create another applied executor or another source authority.

## Why gateway evolution is preferred

Existing internal interceptor branches establish the canonical pattern:

`INTERNAL BRANCH -> EXISTING COMMON FINALIZATION`

Placing the applied branch in the same lifecycle envelope preserves the
single-owner model and avoids:

- external private-state mutation;
- duplicated accounting;
- duplicated observers;
- duplicated reflection;
- second owner-turn execution;
- synthetic finalization APIs that mirror gateway internals.

A generic external finalizer would be a second lifecycle authority in
practice, even if named an adapter.

It is therefore rejected.

## UnifiedBrain decision

`app/unified_brain.py` is not authorized for productive modification in this
migration.

Its existing behavior is the desired behavior:

- call `submit_observed`;
- receive one canonical `LocalConversationTurn`;
- observe reflection exactly once through the callback;
- perform cognitive analysis after gateway lifecycle completion.

The gateway evolution must remain compatible with that behavior.

The certified UnifiedBrain hash remains a preservation guard.

## Applied-result exposure

The applied result must be retained from the exact execution that produced the
owner turn.

It must not be recomputed after `submit` returns.

The next PRE-RED must determine the smallest canonical exposure mechanism.

Preferred order:

1. reuse an existing per-turn result/evidence surface if one already exists;
2. otherwise add a bounded read-only last/completed-turn applied-result
   exposure owned by the gateway or its existing composition;
3. do not add a second execution;
4. do not parse visual identity from response text.

No exposure design is selected by this decision until the PRE-RED inventories
existing per-turn evidence/result surfaces.

## Explicit-context precedence

Existing explicit current-turn context keeps precedence.

When any explicit document/source/evidence/visual context is supplied, the new
applied branch must not reinterpret or replace that explicit selection.

The existing normal owner-turn path remains authoritative.

## Failure semantics

The new branch must live inside the existing gateway `try` lifecycle.

If applied execution fails, existing observer failure and evidence sealing must
run exactly once.

No external catch/finalizer may simulate this behavior.

## Contract migration policy

The current gateway SHA-256:

`0f8896575116a7ebaac908486d897e22c2f6adff59a05b3cc2997d028b5e0b11`

remains immutable historical evidence of the pre-migration certified gateway.

It must never be edited retroactively in historical documentation to pretend
the earlier file had different bytes.

However, architecture tests whose operative requirement is literally
"gateway must remain at the old hash" cannot remain the current contract after
an explicitly authorized Class-2 gateway evolution.

The next PRE-RED must classify every such assertion into:

### Historical compatibility evidence

Tests whose real semantic is preservation of an earlier capability must be
rewritten, where necessary, to assert that semantic behavior rather than the
obsolete whole-file hash.

### Still-current byte protection

Tests protecting unrelated files or authorities remain byte-identical and
unchanged.

### Historical provenance

The old gateway hash remains recorded in the migration documentation as the
certified predecessor state.

No test may simply receive a replacement hash as its only change.

A new whole-file hash must not become a substitute for semantic contracts.

## Required migration evidence

Before CONTRACT RED, the next reconciliation must produce a migration matrix
for every test containing the old gateway hash.

For each assertion it must state:

- original capability protected;
- whether the new applied branch can affect it;
- replacement semantic compatibility assertion, if migration is necessary;
- whether the test can remain unchanged;
- why the change is not weakening the contract.

It must also prove that `unified_brain.py` and other unrelated protected
surfaces remain byte-identical.

## Scope of the future RED

Only after that migration matrix is complete may CONTRACT RED be authorized.

The future RED may require:

- one recognized applied branch inside canonical gateway lifecycle;
- applied bridge exactly once;
- normal runtime conversation zero times for that recognized branch;
- explicit-context precedence;
- common lifecycle finalization exactly once;
- post-turn reflection exactly once;
- submitted-turn accounting exactly once;
- cognitive analysis exactly once;
- failure closure exactly once;
- exact applied-result identity exposure;
- no new authority.

The RED must also preserve representative historical behaviors protected by
the migrated hash assertions.

## Reuse of the additive GREEN composition

The existing
`applied_conversational_intelligence_owner_turn_composition.py`
remains certified evidence and reusable logic.

The next PRE-RED must determine whether its branch-selection logic can be
called by the canonical gateway without creating circular ownership or
whether the minimal semantics should be absorbed into the gateway while the
additive composition becomes a compatibility/delegation surface.

No duplicate branch-selection authority is authorized.

## Explicit non-decisions

This architectural decision does not authorize:

- CONTRACT RED yet;
- productive Python modification yet;
- desktop wiring;
- Tk changes;
- another worker;
- another gateway;
- another brain;
- another observer;
- another reflection authority;
- a generic lifecycle plugin system;
- private-state mutation by an external wrapper;
- automatic hash replacement;
- natural-language image reachability;
- freshness ordering.

## Next governed block

The next block is:

`CANONICAL OWNER-TURN LIFECYCLE EXTENSION SEAM — MIGRATION PRE-RED
RECONCILIATION`

It must complete:

1. old-hash test migration matrix;
2. existing per-turn applied-result exposure inventory;
3. exact gateway insertion point;
4. additive-composition reuse/absorption decision;
5. failure-path proof;
6. UnifiedBrain byte-preservation proof;
7. explicit-context precedence proof;
8. representative historical compatibility set.

Only then can it decide whether CONTRACT RED is sufficiently specified.

## Status

`CANONICAL_OWNER_TURN_LIFECYCLE_EXTENSION_SEAM_ARCHITECTURAL_DECISION:
COMPLETE / PENDING OWNER CERTIFICATION`

`CLASSIFICATION: CLASS 2 — EXISTING CAPABILITY DEEPENING`

`CANONICAL AUTHORITY: OfficialConversationGateway — PRESERVED`

`GATEWAY GOVERNED EVOLUTION: ARCHITECTURALLY APPROVED IN PRINCIPLE`

`OLD GATEWAY HASH: IMMUTABLE HISTORICAL PREDECESSOR EVIDENCE`

`AUTOMATIC HASH REPLACEMENT: FORBIDDEN`

`UNIFIED BRAIN MODIFICATION: NOT AUTHORIZED`

`CONTRACT RED: NOT YET AUTHORIZED`

`NEXT: MIGRATION PRE-RED RECONCILIATION`

`NEW AUTHORITY: NONE`

STOP for Owner local certification.
