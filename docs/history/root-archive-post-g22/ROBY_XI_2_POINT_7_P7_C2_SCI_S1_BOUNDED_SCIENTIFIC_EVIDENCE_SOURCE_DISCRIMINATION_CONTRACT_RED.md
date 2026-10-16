# ROBY XI.2 — POINT 7 / P7-C2-SCI-S1
# BOUNDED SCIENTIFIC EVIDENCE-SOURCE DISCRIMINATION — CONTRACT RED

## Status

**RED CONTRACTUAL OPENED / GREEN NOT AUTHORIZED**

Certified entry baseline: **12,816 PASS · 0 FAIL · Ruff clean**.

## Contractual residual

The preceding inventory and R1-C1 reconciliation reduce C2-SCI to one bounded
semantic seam:

`EXPLICIT SCIENTIFIC / OFFICIAL KNOWLEDGE NEED`
→ `EXISTING KNOWLEDGE-SOURCE ASSESSMENT`
→ `EXISTING DISCRIMINATING EVIDENCE REQUIREMENT`
→ **`GovernedScientificEvidenceSourceDiscrimination` — MISSING**
→ `EXISTING GOVERNED SOURCE SELECTOR`
→ **`STOP BEFORE RETRIEVAL`**.

The RED does not authorize a scientific brain, scientific agent, retrieval
executor, evidence store, Reasoning authority or scientific truth authority.

## Existing authorities that remain canonical

The contract preserves and reuses:

- `OfficialKnowledgeRuntimeGateway` for knowledge-source assessment;
- `DiscriminatingEvidenceRequirement` for the declared epistemic evidence need;
- `GovernedInformationSource` and existing registered source metadata;
- `GovernedConversationalSourceSelector` as the existing governed source-selection
  consumer;
- existing external/unified retrieval authorities after the STOP boundary;
- M400/M401 for external evidence governance/admission;
- P7-C2-S1 for admitted external evidence → canonical Reasoning;
- governed Reasoning for epistemic sufficiency and conclusions.

## Required semantics

A future GREEN seam must be bounded to semantic discrimination of an already
registered/governed source candidate for an explicit scientific/official evidence
need.

It must require:

1. explicit scientific/official intent;
2. an existing `DiscriminatingEvidenceRequirement`;
3. existing registered/governed source candidates only;
4. reuse of existing source classification/metadata rather than creation of a
   parallel source authority;
5. a deterministic bounded result compatible with the existing governed source
   selection architecture;
6. fail-closed behavior when the need is unsupported or no appropriate governed
   source is available.

## Epistemic non-claims

The seam must preserve:

`SOURCE RELEVANCE`
≠ `SOURCE AUTHORITY`
≠ `EVIDENCE QUALITY`
≠ `EVIDENCE SUFFICIENCY`
≠ `REASONED CONCLUSION`
≠ `DURABLE KNOWLEDGE`.

A source-discrimination decision therefore does not:

- certify truth;
- certify evidence sufficiency;
- perform M400/M401 assessment;
- invoke canonical Reasoning;
- create durable knowledge.

## Authorization boundary

The exact STOP is **before retrieval execution**.

A source-discrimination result may identify an appropriate already-governed source
or source class. It must not:

- invoke `OfficialExternalRetrievalRuntimeGateway`;
- invoke `OfficialUnifiedRetrievalExecutionRuntimeGateway`;
- enable global retrieval;
- perform HTTP/network access;
- start background or ambient investigation.

`SOURCE SELECTION ≠ NETWORK AUTHORIZATION`.

## Authority exclusions

The contract forbids:

- `ScientificBrain`;
- `ScientificAgent`;
- a scientific retrieval coordinator;
- a second source selector/manager authority;
- a scientific Reasoning gateway;
- a scientific evidence store;
- Memory writes;
- Learning writes;
- Planning;
- Execution;
- conversational publication/delivery authority.

## Frozen fronts

During this RED:

- C2-LOCAL remains FROZEN;
- Current Affairs remains CLOSED and unchanged;
- P7-C2-S1 remains CLOSED and unchanged;
- P7-R1 and P7-C1-S1 remain CLOSED;
- E1-B remains FROZEN;
- Point 9 remains separate.

## RED proof obligations

The RED test suite requires that the future seam:

1. exists under the bounded contract name;
2. requires explicit scientific intent and a real evidence requirement;
3. references existing evidence/source/selector contracts;
4. stops before retrieval/network execution;
5. does not claim truth or final sufficiency;
6. fails closed for unsupported source needs;
7. creates no parallel brain/selector/authority;
8. grants no Memory/Learning/Planning/Execution authority.

The existing-authority control test must remain GREEN in the RED state.

## Expected RED state

Until the bounded seam exists, the contract is expected to fail only because:

`app.governed_scientific_evidence_source_discrimination`

is absent.

No productive implementation is included in this RED increment.

## Owner certification gate

Run locally from the project root:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

The RED becomes Owner-certified only when the complete gate demonstrates that all
new failures are the expected contractual failures and there are no unrelated
regressions.

## STOP

**RED CONTRACTUAL → PENDING OWNER CERTIFICATION → STOP.**

GREEN is not authorized by this artifact.
