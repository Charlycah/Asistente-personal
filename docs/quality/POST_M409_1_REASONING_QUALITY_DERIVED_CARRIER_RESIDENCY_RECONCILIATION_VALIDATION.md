# Post-M409.1 Reasoning Quality Derived-Carrier Residency Reconciliation

Status: IMPLEMENTED / PENDING OWNER CERTIFICATION.

Scope:
- move the neutral derived reasoning-quality carrier from the application adapter into `core.governed_reasoning`;
- preserve the existing application productive-consumption adapter;
- preserve deterministic schema, identity, fingerprint and serialization semantics;
- add architecture guardrails for canonical residency and single-authority boundaries.

Explicitly out of scope:
- retirement of the Reasoning Quality app adapter;
- changes to the Reasoning Quality Foundation;
- new runtime wiring, persistence, Memory, Learning, execution or background behavior.

Owner gate:
```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
## Import-boundary correction

The canonical derived carrier remains in
`core.governed_reasoning.derived_reasoning_quality_assessment`, but is intentionally not
eagerly re-exported from `core.governed_reasoning.__init__`. This avoids the observed
`cognitive_maturity.epistemic -> governed_reasoning -> reasoning_quality -> hypothesis_deepening
-> cognitive_maturity.epistemic` circular import while preserving the canonical carrier
residency and the bounded app consumer.


## Corrected focused validation

After integrating the owner-supplied formatting/import corrections and the import-boundary
reconciliation, the focused suite covering the original failing import order, carrier
residency, app consumption, method provenance compatibility, and M361 reproducibility
completed with **32 PASS · 0 FAIL** in the assistant environment. Owner certification
remains mandatory for full closure.
