# ROBY XI.2 — POINT 7 / P7-C2-S1 — CONTRACTUAL RED

## Status

**RED CONTRACTUAL OPENED / PENDING OWNER RED CERTIFICATION**  
**Entry baseline: P7-C1-S1 OWNER-CERTIFIED — 12,809 PASS / 0 FAIL / Ruff clean**  
**P7-R1: CLOSED / UNMODIFIED**  
**P7-C1-S1: CLOSED / UNMODIFIED**  
**C-C2-1 scientific/official generalization: FROZEN**  
**C-C2-2 local/business/restaurant generalization: FROZEN**  
**E1-B: FROZEN**

## 1. Contract target

The R1-R2 reconciliation collapsed the prior two C2 residuals into one bounded
productive-composition seam:

`EXPLICIT ADMITTED EXTERNAL KNOWLEDGE NEED`
→ `EXISTING GOVERNED EXTERNAL SOURCE / RETRIEVAL`
→ `EXISTING M400 VERIFICATION / ASSESSMENT`
→ `EXISTING M401 CognitiveExternalEvidenceAdmission`
→ **`P7-C2-S1 BOUNDED COMPOSITION`**
→ `EXISTING OfficialGovernedReasoningRuntimeGateway`
→ `EXISTING ORDINARY CONVERSATION`
→ `STOP`.

The RED does not authorize a new retrieval, evidence, reasoning, conversation,
Memory, Learning, Planning or Execution authority.

## 2. Missing contractual seam

Expected module:

`app.governed_external_evidence_reasoning_composition`

Expected type:

`GovernedExternalEvidenceReasoningComposition`

The module/type must be absent at RED and is the only expected cause of the focal
contract failures.

## 3. Mandatory reuse

A future GREEN must reuse, not replace:

- `GovernedExternalInformationSourceIntegration` / existing M400 boundary;
- `CognitiveExternalEvidenceAdmission` / existing M401 contract;
- `OfficialGovernedReasoningRuntimeGateway` / canonical Reasoning authority;
- existing ordinary conversation authority.

CAP-17 local evidence re-entry is a semantic precedent, not an authority to be
retyped as external evidence.

## 4. Explicit authorization boundary

The seam must require explicit external intent/admission.

It must not infer network authority from:

- uncertainty;
- ambient conversation;
- P7-R1 participation;
- P7-C1 social feedback;
- Reasoning evidence need alone.

No global change to `retrieval_enabled=False` is authorized by this RED.

## 5. Epistemic boundary

External evidence remains evidence, not truth.

M400/M401 provenance, assessment, limitations and lineage remain authoritative.
The seam must not fabricate evidence, certify truth, erase uncertainty or create a
parallel evidence model/store.

## 6. Prohibited authority expansion

The future GREEN must not introduce or invoke a new:

- Web/Scientific/External Reasoning brain;
- retrieval coordinator;
- external evidence store;
- network client;
- Memory/Learning writer;
- Planning/Execution authority;
- conversational publisher/delivery authority.

The seam is composition only.

## 7. RED obligations

The focal contract proves:

1. existing external integration, M401 admission and canonical Reasoning authorities
   are present before surgery;
2. the bounded composition seam is currently absent;
3. the future seam must reference existing M401 admission and canonical Reasoning;
4. explicit external intent must be represented at the seam;
5. no parallel retrieval/reasoning authority is introduced;
6. no global retrieval enablement or direct network execution is introduced;
7. no Memory/Learning/Planning/Execution/delivery authority is introduced.

## 8. Expected RED disposition

The focal file contains seven tests:

- one existing-authority proof must PASS;
- six contractual tests must FAIL only because
  `app.governed_external_evidence_reasoning_composition` does not exist.

Expected focal result:

**1 PASS + 6 EXPECTED FAIL.**

## 9. Owner certification gate

After local focal confirmation, Owner RED certification remains mandatory:

`python scripts/clean_project_caches.py`  
`python scripts/generate_quality_baseline.py`  
`ruff check .`  
`pytest -q`

No GREEN is authorized until the Owner supplies the complete RED gate and then
explicitly authorizes **GREEN quirúrgico P7-C2-S1**.

## 10. STOP

**P7-C2-S1 → RED CONTRACTUAL → PENDING OWNER RED CERTIFICATION → STOP BEFORE GREEN.**
