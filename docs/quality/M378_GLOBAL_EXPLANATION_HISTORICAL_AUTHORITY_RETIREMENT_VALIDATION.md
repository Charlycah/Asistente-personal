# ROBY XI.2 — M378 global explanation historical authority retirement

## Scope

Governed retirement of the disconnected global M378
`IntelligentExplanationAuthority` foundation and reconciliation with current
source-owned explainability governance.

## Retired

- `core/intelligent_explanations.py`
- `tests/test_m378_intelligent_explanations.py` (8 tests)

## Preserved current architecture

- Governed Reasoning: `ExplainableAnswerRenderer`
- Cognitive Planning: `CognitiveDecisionExplainer`
- Controlled Autonomy: `DeterministicDecisionExplainer`
- Controlled Autonomy: `DeterministicAutonomyExplainer`
- Trust: `TrustExplainabilityManager`

These surfaces remain specialized under their existing source owners. No global
replacement explanation authority is introduced.

## Historical preservation

The original M378 document is archived unchanged at:

`docs/history/legacy-explainability/M378_INTELLIGENT_EXPLANATIONS.md`

Historical M378 changelog/decision entries remain historical; a current
supersession decision is appended rather than rewriting historical evidence.

## Expected test delta

Certified input baseline: **12,523 PASS**.

- 8 direct historical M378 tests retired.
- 1 architectural retirement/source-owned-governance guardrail added.

Expected owner baseline: **12,516 PASS · 0 FAIL · Ruff clean**.

## Certification state

**IMPLEMENTED / PENDING OWNER CERTIFICATION**
