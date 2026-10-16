# ROBY XI.2 — Governed Memory Write Request Execution Authorization Inventory

Baseline: current owner-certified tree after
G7 Materialization Proposal → Existing Memory Write Adapter Invocation →
Governed Memory Write Request.

Owner gate:
- 12,449 PASS
- 0 FAIL
- Ruff clean

## Scope

This inventory examines only the boundary between an already-certified inert
`GovernedMemoryWriteRequest` and the existing productive Memory path.

No productive code surgery is authorized by this inventory.

## Existing path

The current productive route already exists:

`GovernedMemoryWriteRequest`
→ `ProductiveGovernedLearningWiring.execute_certified_write_request(...)`
→ `_persist_certified_write_request(...)`
→ `OfficialMemoryGateway.remember_governed_learning(...)`
→ durable governed Memory

`OfficialConversationGateway.submit(...)` already accepts the keyword-only
`governed_memory_write_request` seam and routes it directly into
`execute_certified_write_request(...)`.

## Existing authorization carried by the request

The write request preserves upstream learning approval lineage, including:
- approval identifier;
- approver;
- approval scope;
- human approval fingerprint;
- learning category;
- structural eligibility evidence;
- writer authority/component/method;
- idempotency identity.

The request itself remains inert:
- `read_only=True`
- `write_performed=False`
- `persists_results=False`
- `creates_memory=False`
- `executes_actions=False`
- `grants_authority=False`

This proves upstream approval and structural eligibility, but it is not a separate
apply-now execution authorization.

## Demonstrated execution-authorization gap

`ProductiveGovernedLearningWiring.execute_certified_write_request(...)` currently accepts
only the write request. It does not require a separate execution-authorization object.

`OfficialConversationGateway.submit(...)` likewise accepts
`governed_memory_write_request` without a paired learning-memory execution authorization.

Therefore an inert certified write request, once supplied to the existing seam, reaches
the official Memory writer without a distinct apply-now authorization gate.

This is the demonstrated residual.

## Existing reusable pattern

ROBY already contains the governed pattern required for durable knowledge revision:

`GovernedKnowledgeRevisionRequest`
+ `AuthorizedKnowledgeRevisionExecutionEvidence`
→ exact-lineage validation
→ `OfficialMemoryGateway.apply_governed_knowledge_revision(...)`

The existing revision authorization is:
- explicit;
- human-derived;
- exact-request-linked;
- read-only/inert evidence;
- fail-closed when absent;
- fail-closed on lineage mismatch;
- separate from the certified revision request;
- checked immediately before the official Memory mutation.

This is a valid architectural pattern to reuse conceptually.

## What must NOT be reused directly

`AuthorizedKnowledgeRevisionExecutionEvidence` is revision-specific. Its contract contains
revision-only lineage:
- revision request;
- application proposal;
- revision approval;
- revision proposal;
- target memory;
- expected target fingerprint;
- replacement idempotency key.

It is therefore not the correct type for first-time governed learning Memory writes.

Reusing that type directly would blur distinct capabilities and create false revision
semantics.

## Next demonstrated residual

**GOVERNED MEMORY WRITE REQUEST → EXPLICIT HUMAN EXECUTION AUTHORIZATION → EXISTING PRODUCTIVE MEMORY WIRING**

The missing capability is not a new writer, gateway, adapter, or productive route.
It is a bounded authorization contract for one exact already-certified
`GovernedMemoryWriteRequest`.

A valid future surgery should:
1. introduce or reuse the canonical human-authorization authority to evaluate one
   explicit apply-now response for one exact write request;
2. emit inert execution-authorization evidence bound to that request;
3. require the exact request + exact authorization pair at
   `execute_certified_write_request(...)`;
4. fail closed when authorization is absent, mismatched, stale, or non-exact;
5. preserve `OfficialMemoryGateway` as the sole writer;
6. avoid automatic persistence.

## Architectural STOP

No code change is authorized by this inventory.

STOP before:
- creation of a new authorization type;
- changing `execute_certified_write_request(...)`;
- changing `OfficialConversationGateway.submit(...)`;
- any durable Memory write behavior.

The next step requires explicit owner authorization for one minimal authorization-boundary
surgery.
