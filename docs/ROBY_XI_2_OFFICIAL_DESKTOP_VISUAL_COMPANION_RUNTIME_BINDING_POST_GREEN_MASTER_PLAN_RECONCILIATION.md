# ROBY XI.2 — Official Desktop Visual Companion Runtime Binding
## POST-GREEN Master Plan Reconciliation

## Owner-certified starting state

The Surgical GREEN is Owner-certified:

- 13,455 tests passed;
- 0 tests failed;
- Ruff clean;
- the runtime binding contracts changed from 10 RED failures to 10 passes.

The certified binding is mechanical and introduces no new cognitive or source
authority.

## Reconciliation purpose

Determine whether the certified runtime binding is productively consumed by the
official desktop or whether a narrower integration residual remains.

No productive code or new RED contract is introduced here.

## Certified foundation

The repository now contains:

- certified external-image projection;
- certified desktop external-image presenter;
- certified external-image presentation wiring;
- certified same-turn desktop visual companion;
- certified desktop visual runtime binding.

The binding provides:

- `DesktopVisualRuntimeTurn`;
- `bind_applied_result_to_desktop`;
- `execute_desktop_visual_turn`;
- `present_desktop_runtime_visuals`;
- `dispatch_desktop_runtime_visual_render`.

These capabilities are foundation to reuse, not work to recreate.

## Productive-consumer audit

Repository inspection finds no productive import or call of:

`app.desktop_visual_companion_runtime_binding`

outside its own implementation.

Its functions are referenced only by their architecture contract tests.

Therefore the certified binding is not yet composed into the official desktop
runtime.

## Current official desktop path

`desktop_bootstrap.py` still constructs the official desktop with the existing
decorated `LocalConversationUIAdapter`.

The current productive owner-turn path remains:

`ROBYDesktopApp worker`
-> `DesktopConversationController.submit`
-> decorated UI adapter
-> `LocalConversationUIAdapter.submit_text`
-> `LocalConversationUIAdapter._submit`
-> `UnifiedBrain.process`
-> `UIResponse`
-> `DesktopMessage`
-> `root.after(...)`
-> text transcript

The visual runtime binding is not part of this path.

## Current information-loss boundary

`LocalConversationUIAdapter._submit` receives the existing brain turn and
reduces it to `UIResponse`.

`DesktopConversationController.submit` then reduces that response to
text-only `DesktopMessage`.

Both contracts are intentionally preserved.

The certified visual binding cannot recover governed image identity from these
text-only contracts, and it must not parse URLs from text.

## Applied-result evidence

`OfficialConversationGateway.execute_applied_conversational_intelligence`
produces an `AppliedConversationalIntelligenceResult` containing:

- governed source selection;
- governed conversational result;
- natural answer text.

However, it is not a productive caller in the current desktop turn path.

Calling it after the normal desktop submit would violate the certified rule:

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION`

Therefore a future integration must not append a second gateway execution to
the existing text path.

## Demonstrated productive residual

The remaining residual is:

`OFFICIAL_DESKTOP_VISUAL_RUNTIME_COMPOSITION`

This means composing the already-certified same-turn visual binding into the
existing official desktop runtime so that one admitted owner turn can deliver
both:

- its existing text response; and
- its same-turn governed visual companion.

This residual is narrower than another visual subsystem.

## Required future PRE-RED questions

A future PRE-RED must establish, from existing authorities:

1. the exact canonical same-turn execution surface that may expose the applied
   result without duplicating `UnifiedBrain.process`;
2. whether that surface belongs inside the existing brain/runtime path or at
   the existing adapter composition boundary;
3. how the existing decorated UI adapter behavior remains intact;
4. how the existing controller text contract remains intact;
5. how the existing desktop worker carries the visual outcome without a second
   worker or source query;
6. which existing UI-thread handoff is the smallest canonical render path;
7. the minimal additive Tk visual surface and its lifecycle;
8. the concrete bounded preview transport composition;
9. failure behavior preserving the successful text transcript;
10. exact tests proving one execution and no duplicated authority.

The PRE-RED must not assume a new adapter/controller class merely to transport
the companion.

## Explicitly preserved boundaries

Do not create:

- another `OfficialConversationGateway`;
- another `UnifiedBrain`;
- another desktop controller;
- another source-query executor;
- another image projection, companion, presenter, or runtime binding;
- another worker, scheduler, dispatcher, or main loop;
- a generic browser/crawler;
- automatic Vision, repository, Memory, Learning, diagnostics, Proposal,
  Planning, or Execution side effects.

`UIResponse` and `DesktopMessage` remain text contracts unless a later
reconciliation proves a governed need to change them.

## Separate later residuals

Still independent:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

and:

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

`mostrame fotos` and `ultimas` must not be repaired inside desktop visual
runtime composition.

## Reconciled status

`RUNTIME_BINDING_GREEN: CLOSED / OWNER-CERTIFIED`

`CERTIFIED_BINDING: FOUNDATION / REUSE`

`PRODUCTIVE_CONSUMER: ABSENT`

`DEMONSTRATED_PRODUCTIVE_RESIDUAL:
OFFICIAL_DESKTOP_VISUAL_RUNTIME_COMPOSITION`

`SECOND GOVERNED TURN EXECUTION: FORBIDDEN`

`NEW COGNITIVE/SOURCE AUTHORITY: NONE`

`NEXT PRE-RED: NOT YET OWNER-AUTHORIZED`

STOP for Owner local certification.
