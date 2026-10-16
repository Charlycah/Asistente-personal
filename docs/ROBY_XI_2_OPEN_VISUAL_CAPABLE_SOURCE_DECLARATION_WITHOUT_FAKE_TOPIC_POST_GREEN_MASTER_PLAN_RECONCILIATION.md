# ROBY XI.2 — Open Visual Capable Source Declaration Without Fake Topic
## Post-GREEN Master Plan Reconciliation

### Owner-certified GREEN input
Owner certification:
- cache cleanup: 143 directories;
- M361 quality baseline regenerated;
- Ruff: clean;
- full suite: 13,542 PASS / 0 FAIL.

### Reconciled productive state
`GovernedInformationSource` now permits an empty `topics` declaration only
when the same source explicitly declares
`InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY`.

The effective declaration predicate is:

`bool(topics) OR OPEN_VISUAL_SUBJECT_QUERY in capabilities`

This is declaration validity only. Empty topics do not grant topic eligibility.

### Defense in depth remains intact
`GovernedConversationalSourceSelector` still requires the explicit capability
for `OPEN_VISUAL_SUBJECT` and retains topic-subset eligibility for
`TOPIC_CONSTRAINED`.

`GovernedSourceQueryContract.prepare()` independently enforces the same
open-visual capability and retains topic-subset validation for
topic-constrained queries.

Therefore:
`EMPTY_TOPICS != TOPIC_WILDCARD`.

### Preserved boundaries
- `GovernedInformationItem` still requires non-empty topics.
- `GovernedInformationSources.accept()` remains unchanged.
- all default source declarations remain unchanged.
- NASA remains topic-bounded and has no open-visual capability.
- no Wikimedia Commons source or adapter exists in productive `app/`.
- no provider-specific integration has been implemented.
- no freshness ordering has been implemented.
- no presentation authority changed.
- no registry, selector, executor, router, gateway, or source authority was
  duplicated.

### Seam closure
`OPEN_VISUAL_CAPABLE_SOURCE_DECLARATION_WITHOUT_FAKE_TOPIC` has no internal
residual after the Owner-certified GREEN.

It must not be reopened merely to integrate a provider.

### Parent residual
The parent availability objective remains open only at the provider-specific
integration seam.

Current exact residual:
`GOVERNED_WIKIMEDIA_COMMONS_OPEN_VISUAL_PROVIDER_INTEGRATION`

Wikimedia Commons remains the preferred candidate selected by the prior
provider/integration reconciliation. This post-GREEN reconciliation does not
authorize its implementation.

### Next governed step
Before any provider Contract RED or productive adapter code, perform:

`GOVERNED WIKIMEDIA COMMONS OPEN VISUAL PROVIDER — PRE-RED RECONCILIATION`

That reconciliation must bind the selected provider to ROBY's existing:
- non-default `source_declaration` admission path;
- `GovernedSourceQueryExecutor`;
- open-visual capability contract;
- bounded network/runtime policy;
- existing raw external-image result/presentation contract;
- provenance/attribution requirements.

It must also determine whether any additional data-model seam is actually
required rather than assuming one.

### Authorization state
`POST_GREEN_MASTER_PLAN_RECONCILIATION: COMPLETE`
`SEAM_INTERNAL_RESIDUAL: NONE`
`DECLARATION_RULE: CERTIFIED`
`EMPTY_TOPICS_AS_TOPIC_WILDCARD: PREVENTED`
`GOVERNED_INFORMATION_ITEM: UNCHANGED`
`NASA_GENERALIZATION: NONE`
`WIKIMEDIA_PRODUCTIVE_IMPLEMENTATION: NONE`
`NEXT_RESIDUAL: GOVERNED_WIKIMEDIA_COMMONS_OPEN_VISUAL_PROVIDER_INTEGRATION`
`NEXT_STEP: PROVIDER_PRE_RED_RECONCILIATION`
`PROVIDER_CONTRACT_RED_AUTHORIZATION: NO`
`PROVIDER_PRODUCTIVE_GREEN_AUTHORIZATION: NO`
`FRESHNESS: EXCLUDED / LATER`
`NEW_AUTHORITY: NONE`


## Wikimedia Commons provider PRE-RED outcome
Provider integration decomposed without new authority.\nExact next seam: WIKIMEDIA_COMMONS_GOVERNED_ADAPTER_CONTRACT.\nNext step: provider adapter Contract Design Reconciliation.\nProvider Contract RED/GREEN remain unauthorized.\n