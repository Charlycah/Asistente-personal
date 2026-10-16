# ROBY XI.2 — Canonical Owner-Turn Lifecycle Extension Seam
## SURGICAL GREEN — REPAIR V2

## Trigger

SURGICAL GREEN V1 was rejected by Owner certification:

- 117 failed;
- 13,373 passed;
- unexpected regressions present.

The failures collapsed into two primary implementation regressions and one
related historical structural contract.

## Repair 1 — preserve empty external-evidence behavior

V1 passed `external_evidence=()` into the ordinary runtime path.

Historical runtime stubs and the productive conversation boundary do not
accept that keyword unless an explicit per-turn evidence handoff exists.

V2 restores the certified rule:

- empty external evidence does not cross the runtime boundary;
- non-empty external evidence keeps the existing explicit handoff;
- explicit document/source/evidence/visual context remains unchanged;
- recognized applied requests still execute inside the canonical gateway
  lifecycle.

This also restores the M401.3 contract.

## Repair 2 — restore the canonical core structural anchor

V1 placed `_last_applied_owner_turn_result` before the existing canonical core
construction and displaced `CanonicalCognitiveCore` from line 52 to line 53.

V2 moves only that new state initialization after the canonical core
construction.

The certified structural anchor is restored:

`CanonicalCognitiveCore -> line 52`

No historical anchor test is weakened or migrated.

## Applied lifecycle behavior retained

The authorized Class-2 evolution remains intact:

- `OfficialConversationGateway` remains the lifecycle authority;
- recognized applied requests execute once;
- ordinary runtime conversation is bypassed only for a recognized applied
  request;
- the exact applied result remains exposed read-only;
- the exposure is cleared before every owner-turn attempt;
- common gateway observer, evidence, accounting and failure closure remain
  canonical;
- the additive composition remains compatibility delegation;
- `UnifiedBrain` is not modified.

## Owner-failure replay

The 77 test files containing all 117 failures from the V1 Owner log were
executed together after the repair:

`737 PASS / 0 FAIL`

Focused repair set:

`30 PASS / 0 FAIL`

M361 plus the lifecycle RED and desktop owner-turn compatibility contracts:

`28 PASS / 0 FAIL`

The complete suite cannot be collected in this execution environment because
the transferred project lacks local Owner-environment material, including:

- `app.personal_document_ingestion_runtime`;
- `.roby/config.json`.

Those collection limitations are not repaired or worked around here.

Ruff is also unavailable in this execution environment.

Owner-local Ruff and full pytest therefore remain mandatory certification
steps.

## Source quality

The modified gateway parses successfully.

`CanonicalCognitiveCore` is on line 52.

The modified gateway has zero lines longer than 88 characters.

No import-order change is introduced by Repair V2.

## Scope exclusions

Still outside this block:

- official desktop visual composition root productive binding;
- external-image natural-language reachability;
- external-image freshness ordering.

No new authority, worker, loop, source owner or autonomous behavior is added.

## Status

`SURGICAL_GREEN_V1: OWNER-REJECTED`

`SURGICAL_GREEN_REPAIR_V2: COMPLETE / PENDING OWNER CERTIFICATION`

`V1 OWNER RESULT: 117 FAIL / 13,373 PASS`

`V2 OWNER-FAILURE REPLAY: 737 PASS / 0 FAIL`

`CANONICAL CORE ANCHOR: LINE 52 RESTORED`

`EMPTY EXTERNAL EVIDENCE HANDOFF: REMOVED`

`M401.3 EXPLICIT HANDOFF: PRESERVED`

`UNIFIED BRAIN MODIFICATION: NONE`

`NEW AUTHORITY: NONE`

STOP for Owner local certification.
