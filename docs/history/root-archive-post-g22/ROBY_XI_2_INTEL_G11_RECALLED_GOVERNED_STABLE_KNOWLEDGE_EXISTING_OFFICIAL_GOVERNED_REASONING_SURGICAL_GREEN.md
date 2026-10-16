# ROBY XI.2 — INTEL-G11 — SURGICAL GREEN

## Status
SURGICAL GREEN — pending final local certification.

## Certified RED baseline
14,123 PASS + 4 intentional FAIL; Ruff clean.

## Implemented seam
Reuses the already-selected governed memory projection carried by the LLMRequest.

- `ReasoningRuntimeContributor` decodes the existing read-only memory evidence.
- Only `category == "stable_knowledge"` is forwarded.
- `user_preference` is not promoted into governed reasoning.
- `CanonicalProductiveReasoningSource` exposes keyword-only
  `recalled_memory_evidence=()`.
- The same `OfficialGovernedReasoningRuntimeGateway` exposes and receives
  that seam.
- The recalled evidence participates in the productive episode input
  fingerprint, preserving exact turn/input lineage without treating recall as
  truth or authorization.

## Authorities preserved
No new memory reader, MemoryGateway, reasoning gateway, manager, writer,
authorization authority, external-evidence path, recall operation, automation,
or silent learning was introduced.

## Governing distinctions
RECALLED != TRUE
RECALLED != EVIDENCE SUFFICIENT
RECALLED != AUTHORIZATION
RECALLED MEMORY != EXTERNAL EVIDENCE
USER_PREFERENCE != STABLE_KNOWLEDGE

## Historical SHA reconciliation
Because G11 legitimately changes `app/governed_reasoning_runtime.py`, the three
historical whole-file reasoning SHA guards in Gate5C1, Gate5C21 and Gate5C31
were advanced from the certified pre-G11 SHA to the exact G11 source SHA.
No protected Analysis Mode / Observability / Episode Budget authority was
otherwise changed.

## Assistant-environment validation
- G11 contract: 5 PASS.
- G11 + Gate5C1 + Gate5C21 + Gate5C31: 34 PASS.
- Quality baseline regenerated.
- Full suite attempted but the execution environment interrupted the run
  before completion; no full-suite result is claimed here.
- Ruff is unavailable in this execution environment.

## Required local certification
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
