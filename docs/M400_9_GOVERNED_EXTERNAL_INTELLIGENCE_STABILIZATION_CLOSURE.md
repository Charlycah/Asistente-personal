# M400.9 — Governed External Intelligence Stabilization & Closure

## Closure purpose

M400.9 performs the final integration and governance audit for
**M400 — Governed External Intelligence**. It adds no new provider, source,
router, executor, network path, cognitive authority or automatic acquisition
mechanism. Its purpose is to prove that M400.1 through M400.8 form one governed
external-intelligence boundary around capabilities that remain subordinate to
ROBY.

The certified pre-closure baseline is **M400.8 — 11,012 tests / Ruff clean /
M361 synchronized / 0 regressions**.

## Permanent closure invariants

- **M400-C00 — ROBY retains cognitive authority.** Providers, sources, adapters,
  verifiers, assessors and corroborators never become ROBY's brain or decision
  authority.
- **M400-C01 — One governed external boundary.**
  `GovernedExternalIntelligenceBoundary` remains the canonical admission
  boundary for external evidence.
- **M400-C02 — Providers and sources remain distinct.** `Inference Provider`
  and `Information Source` share provenance rules but are never collapsed into
  one semantic capability.
- **M400-C03 — Execution stays outside the M400 boundary package.** M400 does
  not call provider `generate()`, source `execute()`, `urlopen` or `requests`;
  it admits results already produced by existing governed authorities.
- **M400-C04 — Existing authorities remain owners.** Provider routing/execution,
  `OfficialConversationGateway`, and M397/M398 connectivity/transport keep
  their responsibilities.
- **M400-C05 — Local or remote is not authority.** Ollama may be local and
  Gemini/Mistral remote; location or transport does not grant cognitive power.
- **M400-C06 — Provenance precedes verification.** External evidence cannot be
  verified without explicit origin, scope, time and lineage.
- **M400-C07 — Verification is not truth certification.** `VERIFIED` means the
  available provenance satisfies contracts; `truth_certified` remains false.
- **M400-C08 — Execution trace is not truth certification.** Provider/source
  execution identifiers prove technical lineage only.
- **M400-C09 — Assessment is not truth certification.** `STRONG`, `MODERATE`
  and `WEAK` express policy-derived structural assessment, not factual truth.
- **M400-C10 — Confidence is not certainty.** Assessment confidence is visible,
  bounded and reproducible, and never becomes certainty.
- **M400-C11 — Corroboration is not truth certification.** `CORROBORATED` or
  `CONTRADICTED` summarize explicit stances; neither proves semantic truth.
- **M400-C12 — Majority is not truth.** More supporting actors cannot by itself
  certify a proposition.
- **M400-C13 — Actor diversity is not epistemic independence.** Different
  `actor_id` values can still share upstream sources or biases.
- **M400-C14 — No silent external acquisition.** M400 contains no polling,
  background fetching, automatic provider/source expansion or self-directed
  external query loop.
- **M400-C15 — Closure is hash-audited and quality-gated.** The complete
  `core/governed_external_intelligence` package is frozen in the M400.9 closure
  manifest; formal closure requires M361 regeneration, Ruff clean and the
  complete pytest suite.

## Closed governed chain

The closed path is:

**explicit external need → governed route/query → existing execution authority
→ M400 boundary → external evidence → provenance → verification → assessment
→ corroboration → ROBY interpretation and decision**

M400 ends before autonomous cognitive delegation. External systems contribute
capacity or evidence only.

## Scope closed by M400

M400 now provides:

- audited multiprovider/source authority mapping;
- one common external-evidence boundary;
- governed provider-result integration;
- governed information-source-result integration;
- provenance and verification;
- source execution trace;
- policy-visible evidence assessment;
- explicit evidence corroboration and contradiction handling.

Ollama remains preserved as a governed local provider. Gemini and Mistral remain
governed remote providers. NASA remains an `Information Source`, not an LLM
provider.

## Explicitly outside the closure

M400 does not give providers or sources cognitive authority, does not certify
semantic truth, does not autonomously choose new external goals, does not poll
or fetch in the background, does not create new providers/sources, and does not
replace provider routing, source execution, connectivity or transport
authorities.

Any future capability that lets ROBY decide when or why to expand external
research, synthesize new external goals, or act on external evidence must open
a new governed stage and preserve every M400 invariant.

## Formal closure statement

When M400.9 passes M361 regeneration, `ruff check .` and the complete
`pytest -q` suite, **M400 — Governed External Intelligence is CLOSED**. Future
external-intelligence evolution must open a new governed stage rather than
adding new product capability inside M400.
