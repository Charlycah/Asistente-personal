# ROBY XI.2 — Official Desktop Visual Companion Runtime Binding
## PRE-RED Reconciliation

## Owner-certified starting state

The preceding POST-GREEN reconciliation is Owner-certified:

- 13,445 tests passed;
- 0 tests failed;
- Ruff clean;
- projection, presenter, wiring, and same-turn visual companion are certified;
- demonstrated residual:
  `OFFICIAL_DESKTOP_VISUAL_COMPANION_RUNTIME_BINDING`.

## Purpose

This PRE-RED fixes the smallest governed runtime/Tk binding seam.

It adds no contractual RED and no productive implementation.

## Existing composition root

`desktop_bootstrap.py` is the demonstrated official desktop composition root.

It already:

- builds the official runtime;
- obtains `official_runtime.conversation`;
- passes that same conversation runtime to `LocalConversationUIAdapter`;
- composes the adapter decorators;
- constructs `ROBYDesktopApp`.

Therefore no second `OfficialConversationGateway`, desktop controller, or runtime
composition is authorized.

## Current turn path

The current productive desktop path is:

OWNER TURN
-> existing desktop worker
-> `DesktopConversationController.submit`
-> existing decorated UI adapter
-> `LocalConversationUIAdapter._submit`
-> `UnifiedBrain.process`
-> `UIResponse`
-> text-only `DesktopMessage`
-> existing Tk completion handoff
-> transcript

`UIResponse` intentionally carries no governed external-image companion.

`DesktopMessage` intentionally remains text-only.

## Existing visual foundation

The certified visual path already contains:

- `project_governed_external_images`;
- `DesktopExternalImagePresenter`;
- bounded presentation wiring;
- `DesktopVisualTurnCompanion`;
- `compose_external_image_turn`;
- `present_desktop_visual_companion`;
- `dispatch_desktop_visual_render`.

These surfaces must be reused, not recreated.

## Critical single-execution rule

`OfficialConversationGateway.execute_applied_conversational_intelligence`
can produce an applied result containing both natural text and the governed
conversational result.

However, repository inspection finds no productive caller of that method.

The normal desktop turn already executes through `UnifiedBrain.process`.

A future binding must not solve visual presentation by executing:

1. the existing desktop text turn; and
2. a second applied conversational intelligence query.

That would duplicate turn execution and could duplicate source selection or
source access.

Therefore:

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION`

The visual companion must be projected from the exact same admitted result that
produces the text delivered for that turn.

## Canonical missing seam

The exact missing seam is:

`SAME_TURN_APPLIED_RESULT_EXPOSURE_TO_DESKTOP_COMPOSITION`

This is narrower than a new visual subsystem.

The future binding needs a mechanical same-turn result transport at the
existing runtime/adapter composition boundary.

It must preserve the existing `UIResponse` and `DesktopMessage` semantic
contracts.

## Authorized ownership direction

The demonstrated ownership direction is:

`desktop_bootstrap.py`
-> existing official conversation/runtime instance
-> existing local conversation adapter path
-> same-turn result companion transport
-> `ROBYDesktopApp`
-> existing desktop worker
-> certified visual companion/presenter
-> existing UI-thread handoff
-> Tk-owned visual surface

The exact production names remain intentionally unfixed until CONTRACT RED.

## Worker ownership

The existing `ROBYDesktopApp.submit` worker is the canonical background
execution boundary for the owner turn.

Bounded preview I/O, when required for the same completed turn, must remain
outside the Tk main thread.

No second worker pool, scheduler, presentation loop, or background scanner is
authorized.

## UI-thread handoff

Two existing mechanisms are demonstrated:

- the submit completion uses `root.after(...)`;
- `UIThreadDispatcher` queues callbacks and is drained by an existing Tk poll.

Future CONTRACT RED must choose the smallest existing handoff without creating
another dispatcher.

Tk widget mutation must occur only after that existing UI-thread handoff.

## Minimal Tk surface

The existing transcript remains canonical for text.

A future GREEN may add the smallest additive Tk-owned visual surface associated
with the same completed turn.

It must:

- preserve the transcript;
- preserve artifact order and identity;
- preserve source/title metadata already admitted;
- degrade to text when preview fetch/decode/render fails;
- avoid persistence and semantic reinterpretation.

Detail/modal behavior may reuse the exact same artifact only.

It may not perform another search or source selection.

## Concrete preview transport

`BoundedExternalImagePreviewFetcher` already defines the certified mechanical
fetch boundary, but no productive concrete generic preview transport is bound.

Future CONTRACT RED may require the smallest desktop presentation transport.

It must remain:

- bound to an already admitted artifact URL;
- HTTPS-only;
- timeout-bounded;
- byte-bounded;
- image-content-type bounded;
- redirect-safe under the same HTTPS policy;
- non-persistent;
- non-cognitive;
- non-discovery;
- non-browser.

Source-specific acquisition adapters must not become a generic browser.

## CONTRACT RED candidate scope

After Owner certification, CONTRACT RED should prove only:

1. one owner turn causes one governed turn execution;
2. the exact same-turn result can expose text plus visual companion mechanically;
3. `UIResponse` and `DesktopMessage` remain backward compatible;
4. no visual identity is parsed from response text;
5. the certified projection, companion, wiring, and presenter are reused;
6. no second source query or applied-intelligence execution is introduced;
7. preview I/O remains outside the Tk main thread;
8. Tk mutation uses the existing UI-thread handoff;
9. the additive visual surface preserves artifact order and identity;
10. visual failure preserves the successful text transcript;
11. detail/modal reuses the same artifact without requery;
12. no Vision, repository, Memory, Learning, diagnostics, Proposal, Planning,
    or Execution side effects are introduced.

Exact productive module/class names are not authorized by PRE-RED.

## Separate later residuals

Still outside this block:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

and:

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

`mostrame fotos` and `ultimas` must not be repaired here.

## Duplicate-risk exclusions

Do not create:

- another `OfficialConversationGateway`;
- another desktop conversation controller;
- another source-query executor;
- another image projection or presenter;
- another NASA/Web authority;
- another Vision gateway or image repository;
- another worker, scheduler, dispatcher, or main loop;
- a generic browser/crawler;
- automatic persistence, Vision, Memory, Learning, diagnostics, Proposal,
  Planning, or Execution.

## Stop

`OFFICIAL_DESKTOP_VISUAL_COMPANION_RUNTIME_BINDING_PRE_RED:
COMPLETE / PENDING OWNER CERTIFICATION`

`CANONICAL MISSING SEAM:
SAME_TURN_APPLIED_RESULT_EXPOSURE_TO_DESKTOP_COMPOSITION`

`ONE OWNER TURN -> ONE GOVERNED TURN EXECUTION`

`CONTRACT_RED: NOT YET OWNER-AUTHORIZED`

`PRODUCTIVE_GREEN: NOT AUTHORIZED`

STOP for Owner local certification.
