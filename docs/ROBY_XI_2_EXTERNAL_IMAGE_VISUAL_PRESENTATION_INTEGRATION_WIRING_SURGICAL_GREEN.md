# ROBY XI.2 — External Image Visual Presentation Integration Wiring Surgical GREEN

## Owner-certified starting state

The CONTRACT RED was Owner-certified with:

- Ruff clean.
- 13,425 existing tests passed.
- 10 expected RED failures.
- 0 unexpected regressions.
- every RED failure caused by the deliberate absence of
  `app.external_image_presentation_wiring`.

## Surgical implementation

This GREEN adds only:

`app.external_image_presentation_wiring`

The module is a mechanical integration seam. It does not own source
selection, source querying, cognition, image analysis, persistence, or UI
scheduling.

## Implemented contract

The seam provides:

- immutable `ExternalImageTurnPresentation`;
- immutable `ExternalImageTurnPresentationOutcome`;
- same-turn projection through the already certified
  `project_external_image`;
- `BoundedExternalImagePreviewFetcher` over an injected transport;
- HTTPS validation;
- positive timeout and byte-limit validation;
- payload byte-limit validation;
- supported image content-type validation;
- delegation to the existing external-image presenter contract;
- safe textual fallback when presentation fails;
- delegation to the existing `dispatcher.post(callback)` contract.

## Preserved authorities

No change was made to:

- governed conversational source selection;
- governed source-query execution;
- NASA acquisition;
- `OfficialConversationGateway`;
- `DesktopConversationController`;
- `DesktopMessage`;
- `UIResponse`;
- Vision;
- governed image storage;
- Memory;
- Learning;
- diagnostics;
- Proposal;
- Planning;
- Execution.

No thread, worker manager, scheduler, crawler, or browser authority was added.

## Scope boundary

This GREEN does not add concrete Tk widgets, gallery layout, modal/lightbox
widgets, or a concrete network client. Those remain composition concerns and
must be demonstrated before any further productive change.

Natural-language reachability for `mostrame fotos` remains separate.

Newest-first semantics for `ultimas` remains separate.

## Validation

The Owner-certified RED contract now passes:

`10 passed`

Additional nearby regressions and M361 are validated before packaging.

Ruff is not available in the assistant environment. Owner local certification
remains authoritative.

## Stop

`INTEGRATION_WIRING_SURGICAL_GREEN: DELIVERED / PENDING OWNER CERTIFICATION`

`RED_CONTRACT: GREEN`

`NEW_COGNITIVE_AUTHORITY: NONE`

`SOURCE_QUERY_AUTHORITY: UNCHANGED`

`TEXT_CONTRACTS: UNCHANGED`

`PRODUCTIVE_UI_WIDGET_EXTENSION: NOT AUTHORIZED`

STOP for Owner local certification.
