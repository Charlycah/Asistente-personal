# ROBY XI.2 — Open Visual Source Capability Declaration
## Post-GREEN Master Plan Reconciliation

### Certification basis
Owner-certified Surgical GREEN: 13,531 PASS / 0 FAIL; M361 regenerated;
Ruff clean after the Owner import-order correction in the contract test.
The Ruff-clean contract test is integrated in this reconciled baseline.

### Closed seam
`OPEN_VISUAL_SOURCE_CAPABILITY_DECLARATION` is CLOSED / OWNER-CERTIFIED.

The existing governed source model now declares
`InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY`, with immutable
`capabilities` defaulting to the empty set. The existing canonical selector
requires that explicit capability for `OPEN_VISUAL_SUBJECT`, and
`GovernedSourceQueryContract.prepare()` independently enforces it.

`TOPIC_CONSTRAINED` behavior remains unchanged. Legacy sources, including
NASA, remain non-open-visual by default. NASA is not a general image source.

### Residual reconciliation
Internal residual for the capability-declaration seam: NONE.

The parent residual
`OPEN_VISUAL_SUBJECT_ELIGIBLE_GOVERNED_SOURCE_REACHABILITY` remains partially
open only at its second previously refined seam:

`OPEN_VISUAL_SUBJECT_CAPABLE_SOURCE_AVAILABILITY`

Capability metadata is authorization vocabulary; it is not evidence that a
productive general open-visual provider exists.

### Ordering and authorization
Next candidate: `OPEN_VISUAL_SUBJECT_CAPABLE_SOURCE_AVAILABILITY`.
Later: `EXTERNAL_IMAGE_FRESHNESS_ORDERING`.

Provider selection/addition, adapter changes, Contract RED, and productive
GREEN for the next seam remain unauthorized until a separate pre-change
reconciliation demonstrates the correct existing integration path.

No new registry, selector, executor, gateway authority, provider, adapter,
presentation path, or freshness behavior is introduced by this reconciliation.
