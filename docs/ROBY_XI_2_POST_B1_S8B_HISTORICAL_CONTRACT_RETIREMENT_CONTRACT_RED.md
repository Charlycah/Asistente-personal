# ROBY XI.2 — POST-B1-S8B HISTORICAL CONTRACT RETIREMENT — CONTRACT RED

**Classification:** CONTRACT RED / TEST-AND-DOCUMENTATION BOUNDARY  
**Product change:** NONE  
**Existing stale-guard rewrite in this RED:** NONE  
**B2/B3/B4:** STOP

## 1. Demonstrated residual

The certified post-B1-S8B Documentary Green leaves exactly twelve known historical
failures:

- seven Gate5 `.roby/config.json` full-byte guards;
- two Desktop full-byte guards superseded by later governed S6-C state;
- three capability-registry absolute ordering or positional guards superseded by the
  governed registration of `knowledge.local_library.read`.

These are not twelve productive regressions. They are twelve active assertions whose
historical assumptions no longer describe the current governed repository.

## 2. Retirement is not deletion

Retirement does not authorize deleting complete historical test files. Each file may
still protect valid functional or architectural invariants.

Retirement also does not authorize replacing an old expected hash with a current hash.
That would create a silent re-anchor instead of preserving historical evidence.

The future GREEN must preserve the old snapshot as history while removing only the
obsolete active requirement that current state remain byte-identical to that snapshot.

## 3. Configuration family

The seven Gate5 guards must retain documentary evidence of the certified historical
config baseline.

The active full-file byte-identity assertion may be retired only after the GREEN
explicitly preserves its historical role and leaves the unrelated Gate5 functional
contracts intact.

No current hash is promoted as a retroactive Gate5 baseline.

## 4. Desktop family

The two Desktop guards must preserve the semantic invariants that remain valid in their
respective contracts.

They must not force `app/desktop_ui.py` back to its pre-S6-C byte state. The future
GREEN may reformulate only the obsolete whole-file hash portion.

## 5. Capability-registry family

The three registry guards must stop treating historical absolute positions as permanent
architecture where later governed capability registration legitimately changes those
positions.

The future GREEN must preserve:

- one official runtime capability registry;
- capability uniqueness;
- required capability membership;
- relative precedence only where the contract demonstrates that precedence is
  architecturally required.

It must not repair the suite by merely incrementing old indices or by installing a new
absolute first-capability expectation.

## 6. Missing retirement register

The RED requires a canonical document:

`docs/ROBY_XI_2_POST_B1_S8B_HISTORICAL_CONTRACT_RETIREMENT.md`

That document must classify all twelve guards and explicitly govern the later surgical
rewrite of only their stale assertions.

The missing register is the intended RED seam. No productive seam is missing.

## 7. Authorized future GREEN boundary

The later GREEN may modify tests and documentation only where required to retire the
twelve stale assertions.

It may not modify `app/`, `core/`, `.roby/config.json`, capability registration, Desktop
productive behavior, or the architecture authorities that produced the current state.

B2, B3 and B4 remain stopped.

STOP before the test-and-documentation GREEN.
