# ROBY XI.2 — Official Desktop External Image Presentation Composition
## PRE-RED Reconciliation

## Owner-certified starting state

The Post-Integration Master Plan Reconciliation is Owner-certified:

- 13,435 tests passed;
- 0 tests failed;
- Ruff clean;
- projection, presenter, and integration wiring are certified;
- the selected residual is desktop presentation composition.

## Purpose

This PRE-RED fixes the smallest composition boundary needed to connect the
already governed external-image result to the official desktop UI.

It adds no RED test and no productive implementation.

## Existing authorities to reuse

The repository already owns:

- governed conversational source selection and query execution;
- `GovernedConversationalQueryResult`, including immutable raw items;
- `project_external_image`;
- `project_governed_external_images`;
- `ExternalImageTurnPresentation`;
- `DesktopExternalImagePresenter`;
- `BoundedExternalImagePreviewFetcher`;
- `DesktopConversationController`;
- the desktop worker thread;
- `UIThreadDispatcher`;
- the Tk desktop application.

None may be duplicated.

## Where visual information currently disappears

`OfficialConversationGateway.execute_applied_conversational_intelligence`
returns `AppliedConversationalIntelligenceResult`.

That result preserves both:

- `natural_answer_text`; and
- `conversational_result`.

The latter is the governed result containing the admitted raw image metadata.

The normal desktop path does not preserve that companion information.
`LocalConversationUIAdapter` returns the text-only `UIResponse`, and
`DesktopConversationController.submit` finally creates text-only
`DesktopMessage` objects.

Therefore visual composition must occur before governed result identity is
discarded. It must not reconstruct visual semantics from `UIResponse.text`.

## Canonical composition boundary

The future composition must preserve this direction:

EXISTING OFFICIAL GOVERNED CONVERSATIONAL RESULT
-> EXISTING SAME-TURN IMAGE PROJECTION
-> EXISTING EXTERNAL-IMAGE TURN PRESENTATION
-> EXISTING DESKTOP EXTERNAL-IMAGE PRESENTER
-> EXISTING WORKER BOUNDARY
-> EXISTING UI DISPATCH BOUNDARY
-> TK-OWNED INLINE/GALLERY RENDERING

The text response remains independently valid and canonical.

## Result propagation rule

The visual payload must be a companion to the text result.

It must not:

- add image fields to `DesktopMessage` as semantic authority;
- make `UIResponse` own governed image meaning;
- parse URLs or image identity back out of text;
- execute a second governed source query;
- repeat source selection;
- change the admitted artifact identity.

A later CONTRACT RED may select the smallest mechanical companion transport
through existing runtime/desktop composition surfaces.

## Worker and UI-thread rule

`DesktopApplication.submit` already runs `DesktopConversationController.submit`
inside its existing background worker.

That worker is the canonical place for bounded preview I/O when visual
presentation is required.

Tk mutation must remain on the UI thread.

The existing `root.after(...)` completion boundary and
`UIThreadDispatcher.post(callback)` contract are the only authorized UI-thread
handoff mechanisms for this block.

No second thread manager, scheduler, worker pool, or presentation loop is
authorized.

## Tk rendering boundary

The current transcript is a text `ScrolledText` surface.

The PRE-RED does not authorize replacing the transcript.

A future minimal visual surface may be an additive Tk-owned inline/gallery
region associated with the same completed owner turn.

It must preserve:

- the existing text transcript;
- artifact order;
- artifact identity;
- title/source metadata where already admitted;
- textual fallback if preview transport, decode, or rendering fails.

A detail/modal view may only reuse the same admitted artifact. It may not
perform a new source query or semantic selection.

## Preview transport boundary

The certified `BoundedExternalImagePreviewFetcher` accepts an injected
transport. No generic canonical concrete preview transport is demonstrated in
the current composition path.

A later RED may require a smallest presentation-only transport adapter, but it
must remain:

- artifact-bound;
- HTTPS-only;
- timeout-bounded;
- byte-bounded;
- image-content-type bounded;
- redirect-safe under the same HTTPS policy;
- non-persistent;
- non-cognitive;
- non-discovery;
- non-browser.

Source-specific acquisition clients must not silently become a general browser
authority.

## Exact future CONTRACT RED scope

After Owner certification, a surgical CONTRACT RED may prove only:

1. the same successful governed turn can expose a visual companion before
   text-only projection discards its governed result;
2. existing `DesktopMessage` and `UIResponse` behavior remains compatible;
3. no second query or source selection occurs;
4. existing image projection and presenter are reused;
5. bounded preview I/O occurs outside the Tk main thread;
6. Tk rendering is dispatched through an existing UI-thread boundary;
7. inline/gallery rendering preserves artifact order and identity;
8. visual failure preserves the successful text transcript;
9. detail/modal reuses the same artifact and performs no requery;
10. no Vision, repository, Memory, Learning, diagnostics, Proposal, Planning,
    or Execution side effect occurs.

Exact productive module/class names are not authorized by this PRE-RED.

## Explicitly separate residuals

This block does not change:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

or:

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

`mostrame fotos` and `ultimas` remain later governed blocks.

## Stop

`OFFICIAL_DESKTOP_EXTERNAL_IMAGE_PRESENTATION_COMPOSITION_PRE_RED:
COMPLETE / PENDING OWNER CERTIFICATION`

`CANONICAL_MISSING_SEAM: SAME_TURN_VISUAL_COMPANION_TO_OFFICIAL_DESKTOP`

`TEXT_TRANSCRIPT: PRESERVE`

`EXISTING WORKER/UI_DISPATCH: REUSE`

`NEW_COGNITIVE_AUTHORITY: NONE`

`CONTRACT_RED_READINESS: CERTIFIED BY RECONCILIATION`

`PRODUCTIVE_GREEN: NOT AUTHORIZED`

STOP before CONTRACT RED.
