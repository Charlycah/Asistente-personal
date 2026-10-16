# ROBY XI.2 — RP24.5 Unified Learning Base retirement

## Scope

Governed retirement of the historical RP24.5 SQLite learning authority and
reconciliation of the current M369 records-domain metadata.

## Physical retirement

- `core/unified_learning_base.py`
- `tests/test_rp245_unified_learning_base.py` (8 tests)

## M369 reconciliation

- removed `LearningDomain.RECORDS`;
- removed `LearningRole.RECORD`;
- removed the `core.unified_learning_base:LearningRecord` authority metadata;
- preserved all productive M369 candidate/evaluation/approval/materialization
  behavior.

## Historical preservation

The RP24.5 design document is archived unchanged at:

`docs/history/legacy-learning/RP_24_5_BASE_UNIFICADA_APRENDIZAJE.md`

`docs/history/manifests/SHA256SUMS.txt` remains unchanged.

## Current authority

Durable governed learning materialization remains under the existing
`memory_gateway` / `OfficialMemoryGateway` boundary. No new store or writer was
introduced.

## Test delta

Certified input baseline: **12,537 PASS**.

- 8 RP24.5 historical behavioral tests retired.
- 1 architectural guardrail added.

Collection after surgery: **12,530 tests collected**.

Local focused validation: **23 PASS** across M369 foundation, safe-learning,
stabilization and both retirement guardrails. M361 baseline reproducibility:
**5 PASS**.

Expected owner baseline: **12,530 PASS · 0 FAIL · Ruff clean**.

## Certification state

**IMPLEMENTED / PENDING OWNER CERTIFICATION**
