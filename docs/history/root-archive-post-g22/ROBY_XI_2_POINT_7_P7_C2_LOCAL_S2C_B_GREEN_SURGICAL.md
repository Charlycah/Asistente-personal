# ROBY XI.2 — P7-C2-LOCAL-S2C-B — GREEN QUIRÚRGICO

## Scope

Closes only the Owner-certified S2C-B contractual seam:

`explicit local/business turn + bounded geography + explicit per-turn external access authorization`
→ existing S1
→ existing S2B-A
→ existing S2B-B
→ existing `OfficialConversationGateway.submit(... external_evidence=(admission,))`
→ existing `LocalConversationTurn`
→ **STOP**.

## Surgical change

Only the existing application owner `OfficialROBYRuntime` receives the bounded
`submit_governed_local_business_turn(...)` composition surface. It reuses the
already-certified S1, S2B-A and S2B-B compositions and publishes exactly once
through the existing conversation gateway.

The Owner-supplied corrected contractual test is integrated with its ordered
import block unchanged.

## Preserved boundaries

- provider startup availability does not authorize a turn;
- external access authorization remains an explicit per-turn input;
- bounded geography is carried to S1 and is not persisted;
- S1 still stops before retrieval;
- S2B-A remains the execution/M400 composition;
- S2B-B remains the M401 admission composition;
- the M401 admission is handed unchanged to `external_evidence`;
- no second conversation gateway or publication path is introduced;
- no Memory, Learning, Planning, Execution, booking, reservation, navigation,
  or location-retention authority is introduced;
- no provider request occurs during runtime startup because of S2C-B.

## Local validation

- contractual S2C-B test: **16 PASS / 0 FAIL**;
- M361 reproducibility + S2C-B focal set: **21 PASS / 0 FAIL**;
- `py_compile`: PASS;
- maximum productive Python line length: **88**;
- Ruff is unavailable in the assistant execution environment, therefore no
  Owner certification is claimed.

## Owner gate

Run:

`python scripts/clean_project_caches.py`

`python scripts/generate_quality_baseline.py`

`ruff check .`

`pytest -q`

Expected transition from the certified RED baseline:

`12,888 PASS / 9 expected RED FAIL / Ruff clean`
→ approximately `12,897 PASS / 0 FAIL / Ruff clean`.

**STOP PENDING OWNER CERTIFICATION.**
