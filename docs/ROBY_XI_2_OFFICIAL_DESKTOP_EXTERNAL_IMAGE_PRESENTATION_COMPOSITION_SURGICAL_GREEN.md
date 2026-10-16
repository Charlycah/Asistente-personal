# ROBY XI.2 — Official Desktop External Image Presentation Composition
## Surgical GREEN

## Owner-certified starting state

The repaired CONTRACT RED is Owner-certified:

- 13,435 existing tests passed;
- 10 expected RED tests failed;
- 0 unexpected regressions;
- Ruff clean;
- M361 reconciled.

## Surgical implementation

This GREEN adds only:

`app.desktop_external_image_presentation_composition`

The module is a mechanical composition adapter over already certified
presentation authorities.

It introduces no source, cognitive, presentation, scheduling, or execution
authority.

## Reused authorities

The implementation reuses:

- `project_governed_external_images`;
- `ExternalImageTurnPresentation`;
- `present_external_image_turn_safely`;
- `dispatch_external_image_render`;
- the existing external-image presenter protocol;
- the existing UI dispatcher protocol.

## Same-turn companion

`compose_external_image_turn` reads only:

- `natural_answer_text`; and
- the same supplied `conversational_result.items[].raw` mappings.

It does not parse image identity from answer text and performs no source query.
The resulting `DesktopVisualTurnCompanion` is immutable and preserves artifact
order and identity.

The real governed raw item contract is mapping-based and is accepted without
requiring a mutable `dict`.

## Presentation and fallback

`present_desktop_visual_companion` converts the companion back to the existing
certified turn-presentation contract and delegates safe presentation to the
existing wiring.

Presentation failure therefore preserves canonical text fallback.

`dispatch_desktop_visual_render` delegates directly to the existing dispatch
contract. It creates no thread, worker, scheduler, or main loop.

## Preserved boundaries

This GREEN does not modify:

- `DesktopMessage`;
- `UIResponse`;
- `DesktopConversationController`;
- governed source selection/query;
- NASA/Web source authorities;
- Vision or image repository authorities;
- Memory, Learning, diagnostics, Proposal, Planning, or Execution.

It also does not implement natural-language `mostrame fotos` reachability or
`ultimas` newest-first semantics.

## Validation

The 10 composition RED contracts are GREEN.

Combined nearby validation covering composition, certified visual wiring,
visual presentation, desktop UI, and M361 is GREEN.

Owner local full-suite and Ruff certification remain authoritative.

## Stop

`OFFICIAL_DESKTOP_EXTERNAL_IMAGE_PRESENTATION_COMPOSITION_SURGICAL_GREEN:
DELIVERED / PENDING OWNER CERTIFICATION`

`CONTRACT_RED_TO_GREEN: 10 FAIL -> 10 PASS`

`NEW_COGNITIVE_OR_SOURCE_AUTHORITY: NONE`

`PRODUCTIVE_TK_WIDGET_EXTENSION: NOT AUTHORIZED BY THIS GREEN`

STOP for Owner local certification.
