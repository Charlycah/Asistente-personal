# ROBY XI.2 — EXTERNAL IMAGE RESULT → OFFICIAL CONVERSATION
# VISUAL PRESENTATION — PRE-RED RECONCILIATION

Date: 2026-10-05
Starting Owner-certified state: 13,413 PASS / 0 FAIL / Ruff clean.

## 1. Scope and governance

This block reconciles the already demonstrated external-image presentation residual.
It adds no productive Python and no RED tests. Existing authorities are reused; no
parallel source, browser, Vision, multimodal brain, Reasoning, Memory, Learning,
Proposal,
Planning, or Execution authority is authorized.

## 2. Existing chain confirmed

The repository already provides:

- `NasaGovernedSourceAdapter` for the official NASA Images API;
- governed source selection and `GovernedSourceQueryExecutor`;
- normalized NASA raw items containing `media_type` and `preview_url`;
- `GovernedConversationalQueryResult.items`, whose `raw` mapping preserves those fields;
- governed external provenance/evidence admission independently of presentation;
- the official desktop conversation surface in `app.desktop_ui`;
- existing stored-image/Vision authorities for user/local visual evidence;
- map-display contracts and `DesktopMapPresenter` as a precedent for separating governed
  content from mechanical presentation.

No current consumer projects NASA `preview_url` into an external-result image preview,
gallery, or detail view in the official conversation UI.

## 3. Authority decision

M268 `OfficialMultimodalConversationIntegrationGateway` is not the owner of this seam.
It governs declared input/device modalities and consent; it does not render external
information results.

The canonical cognitive/source authorities remain unchanged. The missing element is a
presentation projection plus a desktop presenter. These are mechanical boundaries only.

## 4. Canonical PRE-RED seam

```text
OWNER EXPLICIT VISUAL REQUEST
-> EXISTING GOVERNED CONVERSATIONAL SOURCE SELECTION
-> EXISTING GOVERNED SOURCE QUERY / NASA
-> EXISTING GovernedConversationalQueryResult
   -> immutable raw item: source_id/external_id/title/media_type/preview_url/metadata
-> BOUNDED EXTERNAL IMAGE PRESENTATION PROJECTION
-> OFFICIAL DESKTOP PRESENTATION SURFACE
   -> inline preview/card(s)
   -> optional UI-owned detail/modal/lightbox
```

No source re-query is permitted after the governed result solely for semantic discovery.
The detail view consumes the same presentation artifact as the inline preview.

## 5. Candidate presentation contract

CONTRACT RED should require an immutable, source-neutral presentation shape that carries
only the already admitted result information needed by UI, including at minimum:

- source identity and external item identity;
- title and optional description/date;
- declared `media_type=image`;
- preview URI and, when available, original/source URI metadata;
- provenance/trace reference sufficient to bind the projection to the governed result;
- presentation status/rationale without cognitive claims.

The contract must be generic across governed image-capable sources. NASA is the first
proven case, not a reason to create a NASA-specific presenter.

## 6. Preview-byte retrieval boundary

`preview_url` is metadata; it is not itself admitted image bytes. If inline rendering
requires retrieval, CONTRACT RED must constrain a presentation-only fetch seam:

- only for an image item already present in the governed result;
- HTTPS only;
- bounded timeout and maximum bytes;
- bounded/allowed image content types;
- no redirects to disallowed schemes/targets without revalidation;
- no arbitrary user-supplied URL fetch API;
- no recursive resource discovery;
- no persistence into the governed image repository unless a separate explicit existing
  storage contract authorizes it;
- no automatic Vision analysis, Memory, Learning, diagnostics, or Proposal generation.

A preview-fetch failure is a presentation degradation, not a failure of a successful
source query.

## 7. Official desktop ownership

`DesktopMessage(sender, text)` and the Tk `ScrolledText` transcript are currently
text-only.
CONTRACT RED must preserve ordinary text behavior while allowing the desktop surface to
receive visual presentation artifacts through a compatible extension/composition seam.

The presenter owns rendering only. It may render a bounded list of previews and may
open an in-process detail/modal/lightbox for a selected preview. That detail surface
must not perform search, cognition, source selection, or independent external
retrieval beyond the
same governed preview-fetch policy.

## 8. Required degradation/fallback

The future contract must preserve useful text when:

- the result has no preview URI;
- media type is not an image;
- preview retrieval times out/fails/exceeds limits;
- image decoding fails;
- desktop visual presentation is unavailable.

The conversation must still expose the governed textual answer and safe source
metadata available from the admitted result. Presentation is additive and
non-authoritative.

## 9. Duplicate-risk exclusions

Do not create:

- image-search agent or NASA manager;
- second governed source executor;
- external-image Reasoning/Vision brain;
- second image repository;
- generalized browser/fetch authority;
- M268 output authority;
- automatic gallery scanner;
- Memory/Learning writer;
- autonomous Proposal/Planning/Execution path.

## 10. Candidate CONTRACT RED scope

A surgical RED should prove only:

1. source-neutral projection from existing successful conversational image items;
2. provenance/identity preservation and rejection of non-image/invalid preview items;
3. bounded presentation-only preview retrieval policy;
4. text-only fallback on retrieval/render failure;
5. desktop presenter can render multiple previews without changing cognitive authority;
6. detail/modal uses the same admitted artifact and performs no new search;
7. existing `DesktopMessage` text behavior remains compatible;
8. no automatic Vision/storage/Memory/Learning/Proposal side effects;
9. no hardcoded NASA-only UI semantics.

Exact production module names are intentionally not authorized by PRE-RED; CONTRACT RED
must select the smallest surfaces after contrasting existing presentation/map patterns.

## 11. STOP

PRE_RED_RECONCILIATION: CLOSED / READY_FOR_OWNER_CERTIFICATION.
CANONICAL_MISSING_SEAM: EXTERNAL_IMAGE_PRESENTATION_PROJECTION_AND_DESKTOP_RENDERING.
SOURCE_ACQUISITION: EXISTING / REUSE.
COGNITIVE_AUTHORITIES: EXISTING / UNCHANGED.
M268: NOT_OWNER_OF_OUTPUT_PRESENTATION.
MODAL_LIGHTBOX: UI_ONLY / SAME_ADMITTED_ARTIFACT.
CONTRACT_RED_READINESS: CERTIFIED_BY_RECONCILIATION / PENDING_OWNER_BASELINE.
PRODUCTIVE_GREEN_AUTHORIZATION: NO.
STOP: BEFORE CONTRACT RED.
