# ROBY XI.2 — Long-Horizon Investigation Authorization → Execution GREEN

## Productive cut

`Existing Governed Authorization → Existing Governed Execution Gateway` is implemented as a narrow adapter owned by no new authority. The adapter delegates only to `GovernedLevel2ReadOnlyExecutionGatewayV1`, which remains the canonical one-shot Level 2 read-only execution gateway.

## Preconditions

The gateway is reachable only when the existing authorization result is `AUTHORIZED`, the canonical decision is `MAY_INITIATE`, the canonical independence level is `LEVEL_2_READ_ONLY`, `eligible_for_existing_execution` is true, and the exact existing authorization and planning products preserve authorization/requirement/plan/source/snapshot lineage.

## Governed limits

The adapter performs at most one gateway call. It does not re-authorize, replan, retry, persist results, establish truth, record evidence into an episode, invoke reasoning, modify memory or world model, or start background work. A Level 1 `MAY_INITIATE` remains ineligible for this Level 2 gateway.

## Output

The adapter preserves the exact canonical `GovernedAcquiredEvidenceEnvelope` returned by the existing gateway and derives bridge status from the gateway status. Ineligible input invokes no gateway. Unexpected gateway failure or lineage mismatch fails closed as `REVIEW_REQUIRED`.

## Next residual

`Existing Acquired Evidence Envelope → Governed Episode Evidence Admission / Reasoning Reentry`
