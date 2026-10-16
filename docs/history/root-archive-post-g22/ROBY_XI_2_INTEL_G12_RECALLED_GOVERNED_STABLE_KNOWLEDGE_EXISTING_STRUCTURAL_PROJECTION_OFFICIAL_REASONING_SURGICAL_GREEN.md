# ROBY XI.2 — INTEL-G12 — SURGICAL GREEN

## Gate
RECALLED GOVERNED STABLE KNOWLEDGE → EXISTING GOVERNED STRUCTURAL PROJECTION
→ EXISTING OFFICIAL GOVERNED REASONING

## Certified RED baseline
14,128 PASS · 4 intentional FAIL · Ruff clean · 0 unrelated regressions.

## Surgical implementation
Production change is confined to `app/governed_reasoning_runtime.py`.

The same `OfficialGovernedReasoningRuntimeGateway` now:
1. accepts only already-selected `stable_knowledge` from the G11 seam;
2. adapts that bounded evidence in-memory for the existing
   `GovernedRecalledKnowledgeStructuralProjector` without performing recall;
3. projects the current target through the existing
   `GovernedTargetProblemStructuralProjector`;
4. requires an existing `GovernedStructuralKnowledgeTransferMatcher`
   `TRANSFER_CANDIDATE`;
5. only then reuses the existing productive temporary-rule intake/admission and
   explicit-case claim projection so the same governed reasoning authority can
   evaluate the transferred rule under review;
6. exposes successful same-turn lineage through
   `productive_recalled_knowledge_reference_ids(...)`.

Unsupported/unstructured recalled knowledge falls back to the pre-G12 reasoning
path and exposes no successful structural-reuse references.
`user_preference` is excluded at the gateway boundary as well as at G11.

## Governance preserved
- no second Memory recall;
- no new Memory reader/gateway;
- no new Reasoning gateway/authority;
- no ExternalEvidence path;
- no Memory or Learning write;
- no persistent rule;
- transferred rule remains temporary and review-required under the existing
  productive/canonical admission boundary;
- target claims remain proposed human hypotheses;
- no action or automation authority.

RECALLED != TRUE
RECALLED != EVIDENCE SUFFICIENT
RECALLED != AUTHORIZATION
RECALLED MEMORY != EXTERNAL EVIDENCE
USER_PREFERENCE != STABLE_KNOWLEDGE

## Historical SHA reconciliation
The three existing whole-file SHA guards for
`app/governed_reasoning_runtime.py` were reconciled to the final G12 file SHA:

8f5b2c711fab931073bafaebdc14cb3c55efbab4cc5bdf1f8d59ef5b4839343f

No protected Analysis Mode / Observability / Episode Budget behavior was changed.

## Validation in assistant environment
G12 + G11 + manual structural reuse + RC-1.4 transfer admission +
Gate5C1/C21/C31: 55 PASS.

`app/governed_reasoning_runtime.py` compiles successfully.
Quality baseline regenerated.

Ruff cannot be executed in this environment.
No full-suite certification is claimed.

## Required local certification
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
