# ROBY XI.2 — External Image Result Visual Presentation — Surgical GREEN

## Certified starting state

The Owner-certified CONTRACT RED established:

- existing baseline: 13,413 PASS;
- Ruff: clean;
- expected contract RED: 12 FAIL;
- unexpected regressions: zero.

The missing seam was limited to external-image presentation projection and
mechanical desktop presentation. Existing governed source acquisition,
OfficialConversationGateway, NASA source execution, Vision, Reasoning,
Memory, Learning, Planning, and Execution authorities remain unchanged.

## Surgical implementation

This GREEN adds only:

- `app/external_image_presentation.py`;
- `app/desktop_external_image_presenter.py`.

`ExternalImagePresentationArtifact` is an immutable, provider-neutral
projection of an already governed external item. Projection admits only
`media_type=image` items with an HTTPS preview and preserves source identity,
external identity, descriptive metadata, verification, and provenance.

The projection performs no network I/O and owns no cognitive authority.

`DesktopExternalImagePresenter` consumes only projected artifacts. Preview
transport and UI rendering are injected mechanical dependencies. Inline
preview transport is bounded by explicit timeout and byte limits and accepts
only supported image content types. Failure degrades to text fallback without
mutating the admitted artifact.

Gallery presentation preserves input order. Detail presentation reuses the
same admitted artifact and does not requery or refetch it.

## Explicit exclusions

This GREEN does not create or replace:

- a Web or external-source authority;
- a NASA manager or second governed-source executor;
- a Vision authority or image repository;
- a Reasoning, Memory, Learning, Proposal, Planning, or Execution authority;
- a browser authority;
- an autonomous/background fetch loop.

It also does not extend the certified contract by silently wiring new Tk
widgets or a concrete HTTP preview transport. Those remain separate governed
integration questions if productive UI wiring is demonstrated as the next
residual after Owner certification.

## Local assistant validation

Focused CONTRACT RED after GREEN:

- 12 PASS / 0 FAIL.

Nearby regression set covering desktop UI/runtime adapter, M344 governed
source query and NASA, M400 external-source integration, map presentation,
M361, and the new contract:

- 143 PASS / 0 FAIL.

Final M361 plus contract check after cache cleanup and baseline regeneration:

- 17 PASS / 0 FAIL.

The assistant environment does not provide Ruff. Owner local certification
remains authoritative for Ruff and the complete suite.

## Protected masters

`ROBY_XI_2_CURRENT_TRUTH.md` remains byte-identical:

`fd9d51f8b4dc9b214b9a68e3adb1cb6f8e65f4e67baec2fb57b1e5b15336bab9`

`ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md` remains byte-identical:

`973b41c614b401915d0429bb3206f742fbfc1057779fd8fc57786130b6eeb320`

## STOP

- SURGICAL_GREEN: DELIVERED / PENDING OWNER CERTIFICATION
- NEW_COGNITIVE_AUTHORITY: NONE
- SOURCE_ACQUISITION: EXISTING / REUSE
- PRESENTATION_PROJECTION: IMPLEMENTED
- DESKTOP_PRESENTER_FOUNDATION: IMPLEMENTED
- PRODUCTIVE_UI_WIRING_EXTENSION: NOT AUTHORIZED
- NEXT: OWNER LOCAL CERTIFICATION
