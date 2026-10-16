# ROBY XI.2 — INTEL-G11 — SURGICAL GREEN CORRECTIVE

## Scope
Backward-compatible recalled-memory seam only.

## Local failure being corrected
The first G11 GREEN passed its focal contract but caused historical cognitive
runtime sources that do not expose `recalled_memory_evidence` to fail when
`ReasoningRuntimeContributor` always supplied the new keyword.

## Corrective
`ReasoningRuntimeContributor` now inspects the callable contract before
invocation.

- If the source explicitly accepts `recalled_memory_evidence`, or accepts
  `**kwargs`, the G11 evidence is supplied.
- If the source implements the historical four-keyword contract only, it is
  invoked exactly with `owner`, `session_id`, `text`, and `now`.
- No `TypeError` is caught or retried, so genuine source failures remain
  visible.
- Stable-knowledge filtering remains unchanged.
- No second memory recall is introduced.
- No new reader, gateway, manager, writer, authority, automation, or external
  evidence path is introduced.

## G11 invariants preserved
RECALLED != TRUE
RECALLED != EVIDENCE SUFFICIENT
RECALLED != AUTHORIZATION
RECALLED MEMORY != EXTERNAL EVIDENCE
USER_PREFERENCE != STABLE_KNOWLEDGE

## Validation in assistant environment
- G11 + the diagnostic families that produced the 15 local regressions:
  63 PASS.
- G11 + Gate5C1/C21/C31 + M361 + those diagnostic families:
  97 PASS.
- `docs/quality/M361_QUALITY_BASELINE.json` regenerated.
- Full suite was attempted but the execution environment timed out before
  completion; no full-suite result is claimed.
- Ruff is unavailable in this environment.

## Required local certification
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
