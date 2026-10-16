# ROBY XI.2 — Historical Transport Contract Semantic Migration
## CONTRACT REPAIR

## Certified input

Owner-certified post-GREEN reconciliation:

- 13,502 passes;
- two expected historical transport contract failures;
- Ruff clean;
- M361 reproducible;
- no additional regression.

## Repair scope

Only two historical architecture contracts and documentation are changed.

No productive Python is modified.

The repair does not weaken the original behavioral obligations.

## Attachment transport contract

The historical attachment contract previously required the literal call:

`self.controller.submit(`

The productive owner-turn transport now reaches the certified visual companion
seam:

`self.controller.submit_with_visual_companion(`

The repaired contract still requires:

- explicit document IDs reach the existing turn transport;
- exactly one controller transport call is present;
- no implicit ZIP extraction;
- no new reasoning authority.

## Four-source convergence contract

The historical S6-B contract previously recognized only a controller method
whose AST attribute name was `submit`.

The repaired helper recognizes the productive
`submit_with_visual_companion` seam.

The contract continues to require all four channels together:

- explicit document IDs;
- explicit sources;
- explicit evidence references;
- integrated visual context.

It still proves exactly one controller call.

Its controller-level assertion now inspects
`DesktopConversationController.submit_with_visual_companion`.

That method must carry all four channels into exactly one existing adapter
visual-companion submission.

The contract therefore continues to prohibit source-specific deliberations or
parallel multisource cognitive authority.

## Productive protection

The Owner-supplied corrected `desktop_ui.py` is unchanged by this repair.

`runtime_ui_adapter.py`, `UnifiedBrain`, the canonical gateway and all other
productive Python remain unchanged.

M361 is unchanged from the Owner-certified reconciliation input.

## Local verification

The two repaired historical contracts plus the current visual root binding
contract execute:

`24 passed`

No line in either repaired test exceeds 88 characters.

## Status

`CONTRACT_REPAIR: COMPLETE / PENDING OWNER CERTIFICATION`

`PRODUCTIVE PYTHON DELTA: ZERO`

`HISTORICAL CONTRACTS MIGRATED: TWO`

`BEHAVIORAL OBLIGATIONS REMOVED: ZERO`

`EXACTLY-ONCE TRANSPORT: PRESERVED`

`FOUR-SOURCE CONVERGENCE: PRESERVED`

`NEW AUTHORITY: NONE`

STOP for Owner certification.
