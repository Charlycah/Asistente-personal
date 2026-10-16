# ROBY XI.2 — Wikimedia Commons Newest-First Search Projection
## HISTORICAL CONTRACT SEMANTIC RECONCILIATION

### Trigger
Owner certification of SURGICAL GREEN:
- Ruff clean;
- M361 regenerated;
- 13,600 PASS / 2 FAIL.

Both failures were historical RED assertions that prohibited `gsrsort` before
provider projection was authorized.

### Diagnosis
No productive GREEN defect was demonstrated.

The two historical contracts mixed:
1. temporary phase-boundary prohibition: provider projection must not exist
   during earlier capability/representation blocks;
2. permanent architecture prohibitions: no parallel freshness authority, no
   executor/local sorting, no premature ACI freshness admission.

The later certified contract now explicitly authorizes provider-side:
`NEWEST_FIRST -> gsrsort=create_timestamp_desc`.

Therefore only the obsolete temporary assertions are migrated.

### Semantic migration 1
File:
`tests/architecture/test_external_image_freshness_order_source_capability_declaration_contract_red.py`

Removed only:
- `gsrsort` from the old forbidden-text tuple;
- the assertion that `gsrsort` must not occur in the Wikimedia adapter.

Preserved:
- no `freshness_order` wiring;
- no `newest_first=` parallel wiring;
- no parallel freshness manager/selector/executor authorities;
- all source-capability behavior.

### Semantic migration 2
File:
`tests/architecture/test_governed_external_image_freshness_order_representation_contract_red.py`

Removed only:
- the historical assertion that `gsrsort` must not occur in Wikimedia.

Preserved:
- no executor sorting of raw items;
- no executor sorting of response raw items;
- no ACI latest/newest/freshness admission in this block;
- no parallel freshness manager/selector/executor authority;
- all typed representation, projection, capability and identity contracts.

### Integrity
Product module remains unchanged from SURGICAL GREEN:
`app/wikimedia_commons_governed_source.py`
SHA-256:
`91039153e086979507cb71838de4439f154f35ee65e4756b895f2f35bf2a59ce`

Migrated test SHAs:
- source capability declaration:
  `129c1d8f2818c5844d20914c9b35aab8e58cbc6a3b494a8d43564285651a03f2`
- governed order representation:
  `9ac150a43e84bb1b6cb3e42b029ed406dc47943bd6dbef33fcb1e7a2936727de`

Both test files remain at maximum line length 88.

### Local focused evidence
Affected + provider contracts:
`47 PASS / 0 FAIL`.

### Governance
`HISTORICAL_PHASE_PROHIBITION != PERMANENT_ARCHITECTURAL_PROHIBITION`

`AUTHORIZED_LATER_PROVIDER_PROJECTION != PARALLEL_ORDERING_AUTHORITY`

No product hash was changed to legitimize an unintended modification.
No productive code was changed during this reconciliation.
No new authority was created.

### Formal state
`HISTORICAL_CONTRACT_SEMANTIC_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`PRODUCTIVE_GREEN_DEFECT: NONE DEMONSTRATED`
`HISTORICAL_CONTRACTS_MIGRATED: 2`
`PRODUCTIVE_CODE_DELTA_DURING_RECONCILIATION: ZERO`
`TEST_DELTA_DURING_RECONCILIATION: TWO HISTORICAL CONTRACTS ONLY`
`FOCUSED_CONTRACTS: 47 PASS / 0 FAIL`
`GREEN_PRODUCT_SHA: PRESERVED`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: RE-CERTIFY SURGICAL GREEN`
