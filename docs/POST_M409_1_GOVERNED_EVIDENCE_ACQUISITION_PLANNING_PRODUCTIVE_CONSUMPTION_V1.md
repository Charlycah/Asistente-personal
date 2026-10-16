# Post-M409.1 — Governed Evidence Acquisition Planning Productive Consumption v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

Productively exposes the existing `EvidenceAcquisitionPlanningReport` while preserving
strictly consultative, non-executive semantics. Authority remains `planning_foundation`;
M62 remains the capability registry; matching remains explicit `evidence_outputs`.

Path: discrimination requirement → governed planner → planning report → read-only
productive exposure → `NOT_EXECUTED` → STOP.

`PLANNABLE`, `PARTIALLY_PLANNABLE`, `AMBIGUOUS`, and `NO_CAPABILITY_AVAILABLE` remain
visible without selecting a capability. No Curiosity, Conversation, Android, Memory
Gateway, networking, subprocess, capability invocation, or execution is introduced.

Eight architecture/semantic tests are included. Official certification remains
`ruff check .` plus complete `pytest -q` over the certified baseline.
