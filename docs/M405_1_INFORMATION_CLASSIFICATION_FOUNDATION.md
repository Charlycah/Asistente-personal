# M405.1 — Information Classification Foundation

**Source baseline:** Post-M404 — 11,142 tests, Ruff clean, M361 synchronized.

## Objective

Introduce a neutral canonical sensitivity vocabulary and make M403 the first productive
consumer through an outbound-only classification admission overlay.

## Canonical taxonomy

`domain.information_classification.InformationClassification` defines exactly:

- `UNCLASSIFIED`
- `PUBLIC`
- `PERSONAL`
- `PRIVATE`
- `SENSITIVE`

The taxonomy is nominal, not ordinal. It does not grant access, authorize synchronization,
select routes, persist data or replace any domain policy.

## M403 first consumer

`SynchronizationClassificationPolicy` is a frozen sidecar policy subordinate to
`GovernedSynchronizationAdmission`.

- No policy supplied: existing M403 behavior remains unchanged.
- Policy supplied: classification becomes required; absent classification is treated as
  `UNCLASSIFIED` and fails closed.
- `PUBLIC` may pass the classification layer without extra sensitivity allowance.
- `PERSONAL`, `PRIVATE` and `SENSITIVE` require explicit inclusion in the flow policy.
- Existing domain prohibitions override classification allowance.
- `SyncShareabilityClass` remains authoritative for synchronization eligibility;
  classification can restrict it but never expand it.

## Compatibility boundary

M405.1 does **not** add classification to `GovernedSyncEnvelope`, does not change the M403
codec/content type and does not introduce receiver-side classification verification.
This milestone is an **outbound classification guard**, not end-to-end enforcement.

Legacy M403 domains remain unchanged until explicitly opted into classification-aware
admission.

## Explicitly out of scope

- global migration of legacy models;
- `InformationClassificationAuthority`, Privacy Manager or global classifier;
- global classification registry;
- `Classified[T]` wrapper;
- M404 producer integration;
- memory/conversation/calendar migration;
- Web Panel integration;
- envelope/codec/schema changes;
- receiver-side verification.

## Invariants

1. `UNCLASSIFIED` never means `PUBLIC`.
2. Classification never expands shareability.
3. `LOCAL_ONLY` remains local regardless of classification.
4. Classification does not replace authorization, provenance, retention or identity gates.
5. Domain-specific restrictions always remain stronger than generic classification policy.
6. No new executable authority is introduced.
