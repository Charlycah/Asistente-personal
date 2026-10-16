# ROBY XI.2 — External Image Result → Official Conversation Visual Presentation
## CONTRACT RED

Date: 2026-10-05

## Certified starting state

Owner-certified PRE-RED baseline:

- Ruff: clean.
- pytest: 13,413 PASS / 0 FAIL.
- source acquisition: existing / reuse.
- cognitive authorities: existing / unchanged.
- missing seam: external image presentation projection + desktop rendering.

## RED purpose

This RED does not authorize implementation. It makes the already reconciled presentation
residual executable as a failing contract while preserving every existing authority.

The contract is provider-neutral. NASA is the demonstrated real source, but the missing
presentation seam must consume already governed image-result metadata rather than become
NASA-specific or create a second source-query path.

## Required contract

The future GREEN must provide one immutable external-image presentation projection that:

- derives only from an already governed/admitted raw result item;
- admits only `media_type=image` with an HTTPS preview URL;
- preserves source id, external id, title, description, publication metadata,
  verification, preview URL, and provenance;
- remains provider-neutral;
- performs no network access and owns no cognitive authority.

The desktop presenter must:

- consume the projected artifact, never a source query;
- render one image inline and multiple images as an ordered gallery;
- allow an optional detail/modal view over the exact same artifact;
- never requery a provider from inline/gallery/detail presentation;
- treat preview-byte retrieval as a subordinate mechanical dependency;
- bound preview retrieval by HTTPS, timeout, byte limit, and supported image type;
- degrade presentation failure to textual/source fallback without invalidating the
  successful governed information result.

## Explicit non-authorities

The seam is not a new Web, NASA, Vision, Reasoning, Memory, Learning, Proposal,
Planning, Execution, or multimodal cognition authority. M268 remains outside ownership
of this output-presentation seam.

No change to `GovernedConversationalQueryResult` or `DesktopMessage` is required by this
contract. The projection is derived from preserved governed raw metadata.

## RED file

`tests/architecture/`
`test_external_image_official_conversation_visual_presentation_contract_red.py`

The RED intentionally references the missing canonical surfaces:

- `app.external_image_presentation`
- `app.desktop_external_image_presenter`

A correct RED run must therefore fail only on the newly introduced contract until the
surgical GREEN supplies those surfaces. Existing tests must remain green.

## STOP boundary

CONTRACT_RED: DELIVERED / PENDING OWNER CERTIFICATION.
PRODUCTIVE_GREEN_AUTHORIZATION: NO.
STOP: BEFORE GREEN.
