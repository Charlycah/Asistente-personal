# ROBY XI.2 — Official Desktop External Image Presentation Composition
## POST-GREEN Master Plan Reconciliation

## Owner-certified starting state

The Surgical GREEN is Owner-certified:

- 13,445 tests passed;
- 0 tests failed;
- Ruff clean;
- 10 contractual RED failures became 10 passes;
- same-turn visual companion composition is certified.

## Purpose

This reconciliation determines whether the certified composition is
productively consumed by the official desktop runtime.

It adds no RED test and no productive implementation.

## Certified foundation now present

The repository now contains and certifies:

- external image presentation projection;
- `DesktopExternalImagePresenter`;
- bounded external-image presentation wiring;
- `DesktopVisualTurnCompanion`;
- `compose_external_image_turn`;
- `present_desktop_visual_companion`;
- `dispatch_desktop_visual_render`.

These authorities and contracts must be reused.

## Productive consumer evidence

Repository-wide consumer inspection finds:

- `compose_external_image_turn` is used only by its defining module and
  its architecture contract;
- `present_desktop_visual_companion` is used only by its defining
  module and its architecture contract;
- `dispatch_desktop_visual_render` is used only by its defining module
  and its architecture contract;
- no productive desktop/runtime composition imports the new companion.

Therefore the composition foundation is certified but not yet bound to
the official desktop runtime.

## Current desktop path

`ROBYDesktopApp` constructs the existing
`DesktopConversationController`.

The submit worker calls `self.controller.submit(...)`.

`DesktopConversationController.submit` calls the existing adapter and
reduces the response to text-only `DesktopMessage` objects.

`finish_submit` renders those text messages through the existing
transcript.

The existing worker ends with `root.after(...)`, preserving the
canonical Tk-thread handoff.

This path currently has no visual-companion consumer.

## Governed-result evidence

`OfficialConversationGateway.execute_applied_conversational_intelligence`
already returns the existing applied result with both:

- `natural_answer_text`; and
- `conversational_result`.

The certified visual companion can consume that shape without a second
query.

The normal `RuntimeUIAdapter -> UIResponse -> DesktopMessage` path does
not preserve that governed result.

## Demonstrated residual

The remaining productive residual is:

`OFFICIAL_DESKTOP_VISUAL_COMPANION_RUNTIME_BINDING`

It is a composition-root/UI binding residual.

It is not:

- a new projection;
- a new presenter;
- a new source query;
- a new source authority;
- a new cognitive authority;
- a new worker or dispatcher.

## Canonical next composition

EXISTING SAME-TURN GOVERNED APPLIED RESULT
-> CERTIFIED DesktopVisualTurnCompanion
-> CERTIFIED DesktopExternalImagePresenter
-> EXISTING DESKTOP WORKER
-> EXISTING UI-THREAD HANDOFF
-> TK-OWNED VISUAL SURFACE
-> EXISTING TEXT TRANSCRIPT PRESERVED

The future binding must not reconstruct the governed result from
`UIResponse.text`.

## Tk surface boundary

The current transcript is text-only.

A later binding may add the smallest Tk-owned visual region associated
with the same completed turn.

It must preserve the existing transcript and textual fallback.

A detail/modal view remains optional UI behavior over the same admitted
artifact and may not trigger a new search.

## Next governed block

The next authorized block is:

`OFFICIAL DESKTOP VISUAL COMPANION RUNTIME BINDING — PRE-RED
RECONCILIATION`

It must determine the smallest existing composition point that can
expose the same applied result to both text delivery and visual
companion composition without duplicating the query.

It must also fix:

- exact worker-side preview-I/O ownership;
- exact UI-thread render handoff;
- minimal Tk visual surface;
- concrete bounded preview transport composition;
- text fallback and lifecycle behavior;
- exact tests and import surfaces for later CONTRACT RED.

## Separate later residuals

These remain outside this block:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

and:

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

`mostrame fotos` and `ultimas` must not be repaired inside runtime
binding.

## Duplicate-risk exclusions

Do not create:

- another image projection;
- another image presenter;
- another source-query executor;
- another NASA/Web authority;
- another Vision gateway or image repository;
- another desktop conversation controller;
- another worker, scheduler, dispatcher, or main loop;
- a generic browser/crawler authority;
- automatic persistence, Vision, Memory, Learning, diagnostics,
  Proposal, Planning, or Execution.

## Stop

`POST_GREEN_MASTER_PLAN_RECONCILIATION:
COMPLETE / PENDING OWNER CERTIFICATION`

`GREEN FOUNDATION: CERTIFIED / REUSE`

`DEMONSTRATED PRODUCTIVE RESIDUAL:
OFFICIAL_DESKTOP_VISUAL_COMPANION_RUNTIME_BINDING`

`NEW COGNITIVE AUTHORITY: NONE`

`NEW PRE_RED: NOT YET OWNER-AUTHORIZED`

STOP for Owner local certification.
