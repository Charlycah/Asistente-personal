# ROBY XI.2 — POINT 7 / P7-C2-SCI-S1
# BOUNDED SCIENTIFIC EVIDENCE-SOURCE DISCRIMINATION — GREEN SURGICAL

## Status

**GREEN QUIRÚRGICO IMPLEMENTED / PENDING OWNER CERTIFICATION**

Certified entry state:

- RED contractual — OWNER-CERTIFIED;
- RED baseline — **12,817 PASS + 8 expected RED failures**;
- Ruff — clean in Owner RED gate;
- no unexpected RED failures.

## Surgical change

Exactly one productive module was added:

`app/governed_scientific_evidence_source_discrimination.py`

No existing productive module was modified.

The new seam is:

`GovernedScientificEvidenceSourceDiscrimination`.

It closes only the certified residual:

`EXPLICIT SCIENTIFIC / OFFICIAL KNOWLEDGE NEED`
→ `EXISTING DISCRIMINATING EVIDENCE REQUIREMENT`
→ `EXISTING REGISTERED GOVERNED SOURCE METADATA`
→ `BOUNDED SCIENTIFIC EVIDENCE-SOURCE DISCRIMINATION`
→ `EXISTING GOVERNED CONVERSATIONAL SOURCE SELECTOR`
→ **`STOP BEFORE RETRIEVAL`**.

## Existing authorities reused

The GREEN reuses:

- `DiscriminatingEvidenceRequirement` for the epistemic evidence need;
- `GovernedInformationSources` as the canonical registered-source registry;
- `GovernedInformationSource` and its existing classification metadata;
- `InformationEvidenceKind` for the already-defined evidence classification;
- `GovernedConversationalSourceSelector` for the existing governed selection
  authority.

It creates no source registry, retrieval coordinator, scientific brain, scientific
agent, Reasoning gateway or evidence store.

## Bounded discrimination behavior

The seam requires:

- explicit scientific intent;
- an existing `DiscriminatingEvidenceRequirement`;
- an existing governed source-selection request;
- an explicit set of already-registered source identifiers.

It projects the declared evidence need onto the existing bounded evidence kinds:

- `SCIENTIFIC_GUIDANCE` for supported scientific/guidance needs;
- `OFFICIAL_RECORD` / `OFFICIAL_ANNOUNCEMENT` for supported official-source needs.

Only declared `OFFICIAL` or `PUBLIC_INSTITUTION` governed sources whose existing
classification and declared topics satisfy the bounded request remain eligible.

The resulting candidate identifiers are passed to the existing
`GovernedConversationalSourceSelector`.

No retrieval is executed.

## Fail-closed behavior

The result status is one of:

- `SELECTED`;
- `NOT_AUTHORIZED`;
- `NOT_SUPPORTED`;
- `UNAVAILABLE`.

The seam fails closed when:

- explicit scientific intent is absent;
- the evidence need cannot be mapped to the existing bounded evidence-kind
  vocabulary;
- no already-registered governed source matches the need;
- the existing selector cannot select a source.

Unknown registered-source identifiers are ignored rather than promoted into a new
source authority.

## Epistemic boundaries preserved

The GREEN preserves:

`SOURCE RELEVANCE`
≠ `SOURCE AUTHORITY`
≠ `EVIDENCE QUALITY`
≠ `EVIDENCE SUFFICIENCY`
≠ `REASONED CONCLUSION`
≠ `DURABLE KNOWLEDGE`.

The seam does not:

- certify truth;
- certify evidence sufficiency;
- assess retrieved evidence;
- invoke M400/M401;
- invoke canonical Reasoning;
- write Memory or Learning;
- invoke Planning or Execution;
- publish conversational output.

## Authorization boundary

`SOURCE SELECTION ≠ NETWORK AUTHORIZATION`.

The implementation imports no external/unified retrieval runtime and performs no
HTTP/network operation.

The selected result contains the existing selector's prepared query only. The STOP
remains before any retrieval execution.

## Local verification

Focal RED contract suite after GREEN:

`9 passed`.

A direct functional probe demonstrated:

- supported scientific-guidance need → `SELECTED`;
- selected source → `argentina_healthy_eating`;
- existing selector prepared its governed query;
- selector snapshot remained `automatic_fetch_enabled=False`.

New module line-length inspection:

- maximum line length: **88**;
- lines over 88 characters: **0**.

Ruff is not installed in the assistant execution environment, therefore no local
Ruff certification is claimed.

## Frozen fronts

This GREEN does not reopen or modify:

- C2-LOCAL;
- Current Affairs;
- P7-C2-S1;
- P7-R1;
- P7-C1-S1;
- E1-B;
- Point 9.

## Owner certification gate

Run from the project root:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

Expected contractual transition:

- the 8 RED failures become GREEN;
- no unrelated regression appears;
- final expected test count from the certified RED baseline is **12,825 PASS**.

The actual Owner output remains authoritative.

## STOP

**GREEN QUIRÚRGICO → PENDING OWNER CERTIFICATION → STOP.**

No further Point 7 phase is authorized by this artifact.
