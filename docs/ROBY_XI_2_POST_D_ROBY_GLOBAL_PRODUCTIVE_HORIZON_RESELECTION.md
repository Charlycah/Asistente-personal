# ROBY XI.2 — POST-D:\Roby GLOBAL PRODUCTIVE HORIZON RESELECTION

Date: 2026-10-05
Starting Owner-certified state: 13,413 PASS / 0 FAIL / Ruff clean.

## Governance result

This is a reconciliation/selection block only. It does not authorize productive code.
Closed Humanization and D:\Roby blocks remain closed. Previously certified authorities
must be reused.

## Concrete Owner product requirement evaluated

Examples:
- "Roby, mostrame las últimas fotos de Marte."
- "Roby, mostrame las últimas fotos del James Webb."
- "Roby, mostrame las últimas fotos del Curiosity."

Desired product behavior is visual presentation inside the official conversation UI,
with provenance and an optional original-source link; an image may be enlarged through
a UI-owned detail/modal/lightbox surface. The requirement is presentation, not a new
search, vision, reasoning, memory, or source authority.

## Existing authorities / evidence

Existing source acquisition is already demonstrated for the NASA case:
- `app.governed_information_sources` declares NASA as an official, first-party source.
- `app.nasa_governed_source.NasaGovernedSourceAdapter` uses the NASA Images API,
  constrains media type to image, bounds response size/timeout, and returns normalized
  records including `media_type` and `preview_url`.
- `OfficialConversationGateway.execute_governed_source_query(...)` remains the existing
  governed source-query execution path.
- Existing stored-image/Vision authorities remain separate and must not be duplicated.

Existing official desktop presentation is text-only for conversation results:
- `DesktopMessage` contains only `sender` and `text`.
- the transcript is a Tk `ScrolledText` and appends rendered strings.
- stored/user-attached image paths are for governed local visual analysis and do not
  constitute an external-result presentation renderer.

Repository-wide inspection found `preview_url` produced only by the NASA source adapter;
no current consumer projects it into an image card/gallery/modal in the official UI.

## Demonstrated residual

EXTERNAL_IMAGE_RESULT_PRESENTATION_SEAM: DEMONSTRATED.

Existing chain:
OWNER VISUAL REQUEST
-> EXISTING GOVERNED SOURCE QUERY / NASA ACQUISITION
-> NORMALIZED EXTERNAL ITEM (`media_type=image`, `preview_url`, provenance)
-> MISSING GOVERNED VISUAL RESULT PROJECTION/PRESENTATION
-> OFFICIAL CONVERSATION UI

This is not evidence for a new image-search agent, NASA manager, Vision authority,
Reasoning authority, browser authority, repository, Memory writer, or Learning path.
Presentation/transport must not become semantic or execution authority.

## Candidate next governed block

`EXTERNAL IMAGE RESULT → OFFICIAL CONVERSATION VISUAL PRESENTATION`
`— PRE-RED RECONCILIATION`

PRE-RED must determine, before any contract or code change:
1. the canonical result/projection shape that can carry image preview + source metadata;
2. the existing conversation/UI owner that should render it;
3. whether image bytes may be fetched by an existing transport or require a bounded
   presentation-only fetch seam;
4. URL/media safety, size/timeout, provenance and failure/fallback semantics;
5. whether modal/lightbox is purely UI behavior over the same admitted result;
6. exact tests/callers/import surfaces affected;
7. text/link fallback when visual rendering is unavailable.

## STOP

GLOBAL_RESELECTION: COMPLETE.
SELECTED_PRODUCTIVE_RESIDUAL: EXTERNAL_IMAGE_RESULT_PRESENTATION_SEAM.
NEW_COGNITIVE_AUTHORITY: NONE.
CONTRACT_RED_AUTHORIZATION: NO.
PRODUCTIVE_GREEN_AUTHORIZATION: NO.
NEXT: PRE-RED RECONCILIATION ONLY.
