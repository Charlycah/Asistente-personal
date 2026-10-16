# ROBY XI.2 — Official Desktop Visual Composition Root Productive Binding
## SURGICAL GREEN

## Certified input

Owner-certified repaired RED:

- 9 intentional failures;
- 13,495 passes;
- Ruff clean;
- protected runtime UI adapter preserved.

## Productive change

The GREEN deepens only existing certified composition surfaces.

### Exterior same-turn visual composition

`SameTurnVisualUIAdapterComposition` now wraps an existing desktop adapter.

For an ordinary turn it delegates once through the fully composed protected
desktop adapter.

For a turn with explicit document/source/evidence/visual context it delegates
once through the existing local conversation adapter that already owns that
context contract.

After the delegated turn completes, it reads the exact
`last_applied_owner_turn_result` from the shared canonical gateway.

It does not independently execute applied conversational intelligence.

### Official desktop root

The root now constructs the existing personality/service/proposal/source
composition first and wraps it with `SameTurnVisualUIAdapterComposition`.

The root also reuses `DesktopExternalImagePresenter`.

No new visual authority is introduced.

### Existing Tk worker

The existing worker now calls the already-certified
`submit_with_visual_companion` controller seam exactly once.

The controller preserves explicit current-turn context.

When the canonical gateway exposes an applied result, the worker reuses:

- `bind_applied_result_to_desktop`;
- `present_desktop_runtime_visuals`;
- `dispatch_desktop_runtime_visual_render`.

The existing `UIThreadDispatcher` remains the UI-thread handoff.

Presentation is downstream of the completed owner turn and never re-executes
that turn.

## Protected surfaces

`app/runtime_ui_adapter.py` remains byte-identical:

`2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1`

`app/unified_brain.py` remains byte-identical:

`05f4c65fbb8a1478f9117b9b1de8c450d15211a257aa4835b8123a6babbc1750`

No schema changes were made to `LocalConversationTurn`, `UIResponse` or
`DesktopMessage`.

## Local verification in the construction environment

The repaired RED contract is GREEN:

`14 passed`

The selected visual and historical protection regression set is GREEN:

`59 passed`

A direct composition probe confirmed:

- ordinary path: exactly one delegated submit;
- explicit-context path: exactly one delegated submit;
- exact gateway-owned applied-result identity preserved.

The full architecture collection cannot run in this construction container
because the distributed baseline lacks unrelated local resources, including
`app.personal_document_ingestion_runtime` and `.roby/config.json`.

Those unrelated absences were not modified or repaired.

Owner certification remains authoritative for the full suite and Ruff gate.

## Scope exclusions

Still separate:

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

## Status

`SURGICAL_GREEN: COMPLETE / PENDING OWNER CERTIFICATION`

`RED CONTRACT: 14/14 GREEN LOCALLY`

`FOCAL REGRESSION: 59 PASS`

`RUNTIME_UI_ADAPTER: BYTE-IDENTICAL`

`UNIFIED_BRAIN: BYTE-IDENTICAL`

`NEW AUTHORITY: NONE`

STOP for Owner certification.
