# ROBY XI.2 — Governed External Image Freshness Order Representation
## POST-GREEN MASTER PLAN RECONCILIATION

### Owner-certified input
Surgical GREEN:
- 13,594 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated / reproducible;
- canonical RED contract unchanged.

### Reconciliation result
The representation block is internally complete.

Canonical transport remains:
`GovernedConversationalSourceSelectionRequest`
-> existing `GovernedConversationalSourceSelector`
-> `GovernedSourceQuery`
-> existing `GovernedSourceQueryContract`
-> existing `GovernedSourceQueryExecutor`.

No parallel freshness authority was introduced.

### Productive representation audit
`GovernedSourceQueryOrder` exists only in the existing query/selection
representation path.

The selector projects `order=request.order` exactly once.

`query.order` has only two productive semantic uses:
1. capability admission in `GovernedSourceQueryContract`;
2. execution-identity completeness in `GovernedSourceQueryExecutor`.

The source capability appears in the already-certified declaration plus the
selector/query-contract gates and Wikimedia's already-certified declaration.

### Preserved boundaries
No productive occurrence of:
- `gsrsort`;
- `sorted(raw_items`;
- `sorted(response.raw_items`.

Therefore:
- executor is not ordering authority;
- presentation is not ordering authority;
- Wikimedia provider projection has not been implemented;
- no generic timestamp sort has been introduced.

Date bounds remain independent filters.

Natural-language freshness admission remains outside this block.

### Hash preservation
- `app/governed_source_query.py`:
  `d938b71a37238f02ce780fb5ce98e63c3acb70485e67dc273a03a65dc5ffcdad`
- `app/governed_conversational_source_selection.py`:
  `1cf16e2b14b058a139b4fe65d85f36de88622e9b9a31aeafdd93faeb75d1f4af`
- `app/governed_source_query_executor.py`:
  `e4da9b6f346be261c9a3c293eee839ff144fc586ad587a2c04618b52b80f803c`
- canonical RED contract:
  `b03b9840fc7d9fabd55e5f54b2704ed484790b6f65dd43601df5005a14807692`

No Python or test file changed during this POST-GREEN reconciliation.

### Local evidence
Focal + related architecture contracts:
`60 PASS / 0 FAIL`.

### Residual analysis
Internal residual for:
`GOVERNED_EXTERNAL_IMAGE_FRESHNESS_ORDER_REPRESENTATION`
is:
`NONE`.

Parent horizon remains:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`.

The next demonstrated independent dependency is:
`WIKIMEDIA_COMMONS_NEWEST_FIRST_SEARCH_PROJECTION`.

Reason:
- governed NEWEST_FIRST representation now exists;
- capability-gated source admission now exists;
- Wikimedia already explicitly declares the capability;
- the adapter still has no provider-supported newest-first projection;
- no `gsrsort` exists productively.

Natural-language admission remains later:
`EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`.

The provider-projection block must have its own PRE-RED reconciliation before
any contract or productive change.

### Formal closure
`POST_GREEN_MASTER_PLAN_RECONCILIATION: COMPLETE / PENDING OWNER CERTIFICATION`
`REPRESENTATION_INTERNAL_RESIDUAL: NONE`
`STOP_REPRESENTATION: CERTIFIED LOCALLY / OWNER CERTIFICATION PENDING`
`PARENT_RESIDUAL: EXTERNAL_IMAGE_FRESHNESS_ORDERING`
`NEXT_DEMONSTRATED_RESIDUAL: WIKIMEDIA_COMMONS_NEWEST_FIRST_SEARCH_PROJECTION`
`LATER_RESIDUAL: EXPLICIT_EXTERNAL_IMAGE_FRESHNESS_INTENT_ADMISSION`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`TEST_DELTA: ZERO`
`NEW_AUTHORITY: NONE`
`NEXT_AFTER_OWNER_CERTIFICATION: WIKIMEDIA COMMONS NEWEST-FIRST SEARCH PROJECTION — PRE-RED RECONCILIATION`
