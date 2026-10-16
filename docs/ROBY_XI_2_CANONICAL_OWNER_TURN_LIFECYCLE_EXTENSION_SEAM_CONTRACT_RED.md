# ROBY XI.2 — Canonical Owner-Turn Lifecycle Extension Seam
## CONTRACT RED

## Certified input

Migration PRE-RED is Owner-certified:

- 13,479 PASS;
- 0 FAIL;
- Ruff clean.

This RED modifies no productive Python code.

## Contract purpose

The RED proves the remaining Class-2 lifecycle deepening before gateway
implementation.

It contracts one recognized applied owner turn inside the existing canonical
gateway lifecycle.

It does not authorize a second gateway, brain, observer, reflection authority,
worker, lifecycle finalizer or source authority.

## New RED contract

`tests/architecture/
test_canonical_owner_turn_lifecycle_extension_seam_contract_red.py`

contains 11 tests.

On the certified pre-migration implementation the expected focused result is:

`6 FAILED / 5 PASSED`

The six failures are causal and correspond to absent productive behavior.

### RED 1 — canonical applied branch

A recognized James Webb applied request submitted through the official gateway
must bypass ordinary runtime conversation and become one interceptor turn.

Current failure: gateway still uses ordinary runtime conversation.

### RED 2 — exact result exposure

The exact `AppliedConversationalIntelligenceResult` that produced the turn must
be exposed by identity without a second applied execution.

Current failure: `submit` performs no applied execution.

### RED 3 — exposure lifecycle

The bounded exact-result exposure must exist and be cleared by later
non-applied turns.

Current failure: the exposure does not exist.

### RED 4 — explicit-context precedence

Explicit document/source/evidence/visual context must keep the normal runtime
path and leave applied-result exposure empty.

Current failure: the exposure does not yet exist.

The normal-path part already passes structurally.

### RED 5 — failure closure

An applied execution failure must remain inside the existing gateway failure
envelope, must not fall back to runtime and must not increment submitted-turn
accounting.

Current failure: no applied branch exists, so the injected applied failure is
never reached.

### RED 6 — additive composition delegation

The previously certified additive owner-turn composition must stop executing
applied intelligence independently after canonical migration.

It must delegate one turn to the gateway and read the bounded exact result.

Current failure: it still calls the applied bridge and constructs the applied
turn independently.

## Already-GREEN invariants in the new contract

Five tests already pass and therefore remain preservation guards:

- common observer/cycle epilogue remains structurally compatible;
- `LocalConversationTurn` schema is unchanged;
- UnifiedBrain remains byte-identical;
- no parallel lifecycle authority is introduced;
- historical gateway hash migration remains explicit and non-mechanical.

These passing tests are not implementation credit for the missing branch.
They are regression boundaries around the RED.

## Historical hash migration

The gateway still has the certified predecessor SHA:

`0f8896575116a7ebaac908486d897e22c2f6adff59a05b3cc2997d028b5e0b11`

This RED does not mechanically replace that SHA in historical tests.

The future GREEN must perform the already-certified semantic migration of the
28 old gateway whole-file guards.

The predecessor SHA remains documentary evidence.

All unrelated hashes and semantic assertions remain protected.

## UnifiedBrain

`app/unified_brain.py` remains byte-identical at:

`05f4c65fbb8a1478f9117b9b1de8c450d15211a257aa4835b8123a6babbc1750`

No UnifiedBrain change is authorized by this RED.

## GREEN implementation boundary

After Owner certification of this RED, the surgical GREEN may:

- evolve `OfficialConversationGateway` under the certified Class-2 decision;
- add the bounded exact applied-result exposure;
- insert the applied branch inside the existing lifecycle envelope;
- reuse existing applied intelligence;
- create the applied `LocalConversationTurn` inside the gateway;
- migrate the 28 historical whole-file gateway guards semantically;
- convert the additive composition to one-call gateway delegation.

It must not:

- add another authority;
- modify UnifiedBrain;
- change `LocalConversationTurn`;
- add a second execution;
- add desktop wiring;
- add natural-language image reachability;
- add freshness ordering;
- mechanically replace the old SHA with a new SHA.

## Expected Owner RED certification

Run:

`python scripts/clean_project_caches.py`

`python scripts/generate_quality_baseline.py`

`ruff check .`

`pytest -q`

Expected full-suite result:

- exactly the six new causal RED failures;
- all pre-existing certified tests remain passing;
- Ruff clean.

The exact total PASS count must be taken from Owner execution rather than
invented in advance.

## Status

`CANONICAL_OWNER_TURN_LIFECYCLE_EXTENSION_SEAM_CONTRACT_RED:
COMPLETE / PENDING OWNER RED CERTIFICATION`

`FOCUSED RED: 6 FAIL / 5 PASS`

`PRODUCTIVE PYTHON CHANGES: 0`

`UNIFIED BRAIN: BYTE-PRESERVED`

`OLD GATEWAY SHA: HISTORICAL PREDECESSOR EVIDENCE`

`MECHANICAL HASH REPLACEMENT: FORBIDDEN`

`GREEN: NOT AUTHORIZED UNTIL OWNER RED CERTIFICATION`

`NEW AUTHORITY: NONE`

STOP for Owner RED certification.
