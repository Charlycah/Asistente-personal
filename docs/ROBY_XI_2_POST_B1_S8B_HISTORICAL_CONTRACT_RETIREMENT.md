# ROBY XI.2 — POST-B1-S8B HISTORICAL CONTRACT RETIREMENT

**Classification:** SURGICAL GREEN / TESTS AND DOCUMENTATION ONLY  
**PRODUCT_CHANGE: NONE**  
**AUTHORIZED_GREEN: TESTS_AND_DOCUMENTATION_ONLY**  
**Authority change:** NONE

## Certified residual

CONFIG_GUARDS: 7  
DESKTOP_GUARDS: 2  
REGISTRY_GUARDS: 3  
TOTAL_STALE_GUARDS: 12

The twelve failures were historical active assertions, not productive regressions.

## Historical hash evidence

`PRESERVE_HISTORICAL_HASH_EVIDENCE`

The historical config and Desktop hashes remain recorded in their original contracts
and in the preceding reconciliation documents. Retirement removes only their obsolete
use as permanent byte-identity requirements against later governed repository state.

`RETIRE_ACTIVE_BYTE_IDENTITY_ASSERTION`

`NO_SILENT_REANCHOR`

`DO_NOT_REPLACE_OLD_HASH_WITH_CURRENT_HASH`

No historical expected hash is replaced by a current hash. No later state is
retroactively declared to be the old Gate5 or pre-S6-C baseline.

## Desktop

`DO_NOT_REVERT_PRODUCT`

`PRESERVE_CURRENT_DESKTOP_SEMANTICS`

`REFORMULATE_DESKTOP_GUARD`

The two stale whole-file Desktop hash checks are retired while their live semantic
assertions remain. S6-C productive state is not reverted.

## Capability registry

`DO_NOT_REORDER_REGISTRY`

`NO_NEW_ABSOLUTE_POSITION_GUARD`

`PRESERVE_REGISTRY_UNIQUENESS`

`PRESERVE_REQUIRED_CAPABILITY_MEMBERSHIP`

`PRESERVE_ONLY_REQUIRED_RELATIVE_PRECEDENCE`

The registry remains the single official runtime registry. Historical tuple equality
and absolute index expectations are replaced by membership and uniqueness invariants.
No new absolute first/last/index guard is introduced. Existing explicit operational
precedence tests remain untouched where they test actual interceptor behavior.

The canonical `knowledge.local_library.read` registration remains governed current
state and is not removed or reordered merely to reproduce a historical snapshot.

## Surgical boundary

Only the stale assertion inside each affected historical test is retired or
reformulated. Unrelated tests and semantic assertions in those files remain intact.

No productive module, configuration, capability authority, registry construction, or
Desktop behavior is modified.

B2: STOP  
B3: STOP  
B4: STOP
