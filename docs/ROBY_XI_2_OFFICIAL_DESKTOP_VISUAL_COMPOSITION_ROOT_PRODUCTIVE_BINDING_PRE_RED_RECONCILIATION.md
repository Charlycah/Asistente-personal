# ROBY XI.2 — Official Desktop Visual Composition Root Productive Binding
## PRE-RED RECONCILIATION

## Certified baseline

Input baseline:

`CANONICAL OWNER-TURN LIFECYCLE EXTENSION SEAM — POST-GREEN MASTER PLAN
RECONCILIATION`

Owner-certified state:

- Ruff clean;
- 13,490 passed;
- 0 failed;
- canonical applied owner-turn lifecycle closed;
- no lifecycle residual.

No previously certified block is reopened.

## Existing authorities and surfaces

The official desktop composition root remains:

`app/desktop_bootstrap.py`

It builds the existing conversational adapter chain and supplies that chain to
`ROBYDesktopApp`.

The official desktop UI remains:

`app/desktop_ui.py`

`ROBYDesktopApp` creates one `DesktopConversationController`.

The ordinary submit worker creates one existing `Thread` and performs one
existing `root.after` completion handoff.

No second worker, scheduler, dispatcher or main loop is required.

## Existing visual-capable controller seam

`DesktopConversationController` already owns:

`submit_with_visual_companion`

That method:

- asks its adapter for `submit_text_with_visual_companion`;
- falls back to the existing `submit` when the adapter lacks that capability;
- preserves the existing voice delivery;
- returns the ordinary desktop messages plus the same-turn applied result.

This controller seam is already implemented and must be reused.

The productive Tk worker currently calls only:

`self.controller.submit(...)`

Therefore the visual-capable controller seam is not productively reached.

## Existing same-turn composition

`SameTurnVisualRuntimeComposition` and
`SameTurnVisualUIAdapterComposition` already exist.

However, their original runtime contract predates the now-certified canonical
gateway lifecycle integration.

A new independent applied execution plus fallback execution must not be wired
into the desktop root because that would recreate the double-execution risk
already eliminated by the lifecycle block.

The canonical gateway now owns the one owner-turn execution and exposes the
exact successful applied result.

Therefore any productive desktop binding must adapt the existing canonical
turn path; it must not restore a second applied executor.

## Existing image presentation chain

The following already exist and must be reused:

- `compose_external_image_turn`;
- `bind_applied_result_to_desktop`;
- `present_desktop_runtime_visuals`;
- `dispatch_desktop_runtime_visual_render`;
- the existing external-image presenter/wiring contracts.

No new image source, projector or presentation authority is justified.

## Exact missing seam

The demonstrated residual is refined to two bounded composition obligations
inside the same block:

1. `CANONICAL_GATEWAY_RESULT_TO_VISUAL_UI_ADAPTER_BINDING`
2. `EXISTING_TK_WORKER_VISUAL_COMPANION_HANDOFF`

The first obligation must expose the already-completed canonical owner turn as
the existing UI response plus the gateway-owned exact applied result.

The second obligation must make the existing desktop worker use the existing
controller visual-companion path when available and dispatch presentation
through the existing UI-thread handoff.

These are composition/root-binding obligations, not new authorities.

## Explicit current-turn context

The existing ordinary controller submit path supports explicit document IDs,
sources, evidence references and integrated visual context.

The current `submit_with_visual_companion` signature does not carry those
arguments.

Contract RED must therefore preserve explicit current-turn context and prove
that visual binding cannot bypass or discard those inputs.

The future GREEN may deepen the existing visual-companion method signature
only as necessary to preserve that established behavior.

## Required Contract RED obligations

The next RED should prove at least:

- the official root composes the canonical gateway result with the existing
  visual UI companion contract;
- one desktop owner action causes one canonical gateway submit;
- no independent applied execution is introduced;
- the exact gateway-owned applied result identity reaches visual composition;
- a non-applied turn preserves the ordinary text path;
- explicit document/source/evidence/visual context preserves precedence;
- the existing Tk worker remains the only submit worker;
- the existing `root.after` remains the UI-thread completion boundary;
- image presentation reuses the certified presenter/wiring;
- visual presentation failure degrades to text without re-executing the turn;
- `UnifiedBrain`, `LocalConversationTurn` and `UIResponse` schemas remain
  unchanged;
- no natural-language image reachability or freshness ordering is added.

## Protected scope

The next RED must not authorize product changes.

The future GREEN must not create:

- a second owner-turn lifecycle;
- a second applied execution;
- a new cognitive/source authority;
- a second desktop worker;
- a second UI dispatcher;
- a new image presenter;
- autonomous execution.

## Separate residuals

Remain outside this block:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

## Status

`PRE_RED_RECONCILIATION: COMPLETE`

`EXACT RESIDUAL:
CANONICAL_GATEWAY_RESULT_TO_VISUAL_UI_ADAPTER_BINDING
+
EXISTING_TK_WORKER_VISUAL_COMPANION_HANDOFF`

`CANONICAL OWNER-TURN AUTHORITY: OfficialConversationGateway`

`DESKTOP COMPOSITION ROOT: desktop_bootstrap.py`

`DESKTOP WORKER OWNER: ROBYDesktopApp.run`

`PRODUCTIVE PYTHON DELTA: ZERO`

`NEW AUTHORITY: NONE`

STOP before Contract RED.
