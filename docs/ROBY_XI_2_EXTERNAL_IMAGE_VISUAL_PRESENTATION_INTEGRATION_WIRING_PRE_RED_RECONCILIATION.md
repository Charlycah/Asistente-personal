# ROBY XI.2 — External Image Visual Presentation Integration Wiring PRE-RED

## Certified starting state

Owner-certified baseline:

- 13,425 tests passed.
- 0 tests failed.
- Ruff clean.
- External image projection and desktop presenter foundation are GREEN.
- No new cognitive authority is authorized by this reconciliation.

## Scope

This PRE-RED reconciles only the productive wiring between an already governed
external image result and the official desktop presentation surface.

It does not reopen source acquisition, NASA authority, Vision, Reasoning,
Memory, Learning, Planning, Execution, or the certified presentation
foundation.

Natural-language reachability for phrases such as `mostrame fotos` and
newest-first semantics for `ultimas` remain separate residuals.

## Existing authorities and evidence

`OfficialConversationGateway.execute_governed_conversational_query()` already
returns `GovernedConversationalQueryResult` and preserves each admitted source
item as immutable raw information.

The certified `ExternalImagePresentationArtifact` is the provider-neutral
presentation projection. The certified `DesktopExternalImagePresenter` is the
mechanical presenter and accepts injected preview transport and renderers.

`DesktopMessage` remains the canonical text transcript value and must not be
expanded into an image authority.

`DesktopConversationController.submit()` currently returns text messages.
`RuntimeUIAdapter` currently returns `UIResponse`. Neither contract should be
silently repurposed as a visual semantic authority.

The official desktop already performs conversational work on a worker thread
and returns UI work to Tk through `root.after(...)`. `UIThreadDispatcher`
already exists for safe worker-to-UI dispatch. A second scheduler is forbidden.

## Demonstrated residual

The exact residual is:

`VISUAL_PRESENTATION_INTEGRATION_WIRING`

Canonical composition:

OWNER REQUEST
-> EXISTING GOVERNED CONVERSATIONAL SOURCE SELECTION
-> EXISTING GOVERNED SOURCE QUERY
-> EXISTING GovernedConversationalQueryResult
-> EXISTING external-image presentation projection
-> EXISTING DesktopExternalImagePresenter
-> OFFICIAL DESKTOP VISUAL SURFACE

The missing seam is the non-semantic propagation and composition of the
already governed result into the official desktop visual surface.

## Result propagation boundary

The wiring must be additive. It must not replace or mutate `DesktopMessage`
text semantics and must preserve the textual answer/fallback.

A visual presentation payload may only be derived from the exact governed
query result produced for the same owner turn. It may not perform another
source query, source selection, discovery pass, or semantic reinterpretation.

The smallest contract should prefer an explicit presentation companion or
turn-presentation projection rather than widening `DesktopMessage` into a
multimodal authority.

Any propagation through the UI adapter must preserve compatibility for
existing `UIResponse` callers. No existing text-only caller may be required to
understand visual presentation data.

## Preview transport ownership

`preview_url` remains metadata until explicitly retrieved for presentation.

PRE-RED authorizes a future CONTRACT RED to require a mechanical,
presentation-only preview transport with all of these constraints:

- input is only an admitted `ExternalImagePresentationArtifact`;
- HTTPS only;
- bounded timeout;
- bounded response bytes;
- supported image content types only;
- redirects must remain within the same HTTPS safety policy;
- no arbitrary public URL-fetch API;
- no search, discovery, crawling, recursive retrieval, or browser authority;
- no persistence into the governed image repository;
- no automatic Vision analysis;
- no Memory, Learning, diagnostics, Proposal, Planning, or Execution effects.

The transport is infrastructure for presentation, not an information-source
authority.

## Threading boundary

Network preview retrieval must not execute on the Tk main thread.

The existing desktop conversational worker is the canonical background
execution context for this wiring. A second worker manager, scheduler, or
presentation loop is not authorized.

Tk object creation and mutation must occur only on the UI thread. Existing
`root.after(...)` / `UIThreadDispatcher` mechanisms must be reused to cross
from worker completion to UI rendering.

A preview failure must degrade to the already available text result and must
not fail the successful governed source query.

## Desktop rendering boundary

Inline preview, gallery, and detail/lightbox are UI surfaces over the same
admitted presentation artifact.

Detail/lightbox must not:

- requery the source;
- perform a new semantic selection;
- create a new artifact identity;
- invoke Vision or Reasoning;
- persist the image automatically.

The text transcript remains available regardless of visual-rendering success.

## Duplicate-risk exclusions

Do not create:

- another source-query executor;
- another NASA or Web authority;
- another Vision gateway or repository;
- an image-search agent;
- a browser authority;
- a second desktop conversation controller;
- a second UI-thread dispatcher or scheduler;
- a visual Reasoning/Memory/Learning path;
- an automatic image persistence path.

## Candidate CONTRACT RED

A future surgical CONTRACT RED may prove only:

1. a successful governed image result can be projected for the same turn;
2. text-only `DesktopMessage` and `UIResponse` compatibility is preserved;
3. no second query or source selection occurs during presentation wiring;
4. preview retrieval is artifact-bound, HTTPS-only, timeout-bounded and
   byte-bounded;
5. unsupported content type, transport failure, decode failure, or renderer
   failure preserves text fallback;
6. preview retrieval runs outside the Tk main thread;
7. Tk rendering is dispatched onto the existing UI thread mechanism;
8. gallery order and artifact identity are preserved;
9. detail/lightbox reuses the same admitted artifact without requery;
10. no Vision, repository, Memory, Learning, diagnostics, Proposal, Planning,
    or Execution side effect is introduced.

Exact production module names are not authorized by PRE-RED. CONTRACT RED must
select the smallest existing integration surfaces after another code contrast.

## Separate later residuals

This block does not prove that natural-language forms such as `mostrame fotos`
reach the governed external-image query path.

This block also does not prove that `ultimas` produces newest-first ordering.

Those are query reachability and freshness/order semantics respectively and
must not be repaired inside presentation wiring.

## PRE-RED stop

`INTEGRATION_WIRING_PRE_RED_RECONCILIATION: COMPLETE`

`CANONICAL_MISSING_SEAM: VISUAL_PRESENTATION_INTEGRATION_WIRING`

`PRESENTATION_FOUNDATION: EXISTING / REUSE`

`TEXT_TRANSCRIPT: PRESERVE`

`PREVIEW_TRANSPORT: MECHANICAL / PRESENTATION_ONLY / BOUNDED`

`TK_THREADING: EXISTING WORKER + EXISTING UI DISPATCH / REUSE`

`NEW_COGNITIVE_AUTHORITY: NONE`

`CONTRACT_RED_READINESS: CERTIFIED`

`PRODUCTIVE_GREEN_AUTHORIZATION: NO`

STOP before CONTRACT RED.
