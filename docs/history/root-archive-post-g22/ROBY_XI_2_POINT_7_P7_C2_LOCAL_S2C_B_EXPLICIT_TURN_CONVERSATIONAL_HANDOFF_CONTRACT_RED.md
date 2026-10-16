# ROBY XI.2 — P7-C2-LOCAL-S2C-B — CONTRACTUAL RED

## Contract

Exact seam:

`explicit local/business request + bounded geography + explicit per-turn external-access authorization`
→ existing S1
→ existing S2B-A
→ existing S2B-B
→ existing `OfficialConversationGateway.submit(... external_evidence=(admission,))`
→ existing `LocalConversationTurn`
→ **STOP**.

This RED opens no new capability authority. The application owner remains
`OfficialROBYRuntime`; the conversation authority remains the existing gateway.

## Frozen boundaries

- provider availability at startup is not per-turn network authorization;
- local/business intent is explicit;
- geography is bounded context and is not persisted;
- S1 prepares but does not retrieve;
- S2B-A requires explicit external-access authorization and reaches M400;
- S2B-B performs existing verification/assessment and reaches M401;
- M401 admission is passed unchanged to the existing conversational consumer;
- the existing conversation submit is the only publication path;
- no second runtime, gateway, brain, agent, selector, executor, verifier,
  assessor, evidence authority, Memory, Learning, Planning, Execution,
  booking, reservation, navigation, or location-retention authority is added.

## Expected RED

The current certified runtime does not yet expose the bounded S2C-B productive
entry or compose the three certified stages. Tests for already-existing
boundaries may pass; failures must be limited to the missing application
composition.

## Gate

Owner certification:

`python scripts/clean_project_caches.py`

`python scripts/generate_quality_baseline.py`

`ruff check .`

`pytest -q`

**STOP BEFORE GREEN.**
