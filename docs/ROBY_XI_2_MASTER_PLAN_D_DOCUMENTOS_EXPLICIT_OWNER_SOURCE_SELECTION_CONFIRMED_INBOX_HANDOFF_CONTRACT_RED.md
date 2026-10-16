# ROBY XI.2 — Master Plan — D:\Documentos

## Explicit Owner Source Selection & Confirmed Inbox Handoff — CONTRACT RED

## Status

CONTRACT RED established. Product implementation remains intentionally absent.

Baseline authority is the immediately preceding PRE-RED reconciliation and the
Owner-certified global gate of 13,387 passing tests with Ruff clean.

## Proven residual

`EXPLICIT_OWNER_PERSONAL_DOCUMENT_SOURCE_SELECTION_AND_CONFIRMED_INBOX_HANDOFF`

The residual is not document discovery, document reading, Inbox persistence, or
Reasoning admission. Those authorities already exist.

The missing seam is the explicit Owner conversation route that can present
bounded candidates, accept an explicit selection, require a second explicit
confirmation before durable Inbox ingestion, and then stop.

## Existing authorities preserved

- `PersonalDocumentRootDiscoveryAdapter` owns governed source discovery and
  selected-source revalidation.
- `DocumentReadingService` owns document text extraction.
- `DocumentInboxManager` owns durable Inbox persistence.
- `DocumentRecord` remains the durable document entity.
- `PersonalDocumentReasoningAdmissionAdapterV1` remains the explicit downstream
  Reasoning admission authority.
- `OfficialRuntimeCapabilityRegistry` remains the conversation capability
  registration and interception authority.
- `runtime_root_factory` remains the canonical productive composition root.

No second source authority, Inbox, registry, gateway, Reasoning authority, or
persistence mechanism is authorized.

## Contracted capability

Conceptual capability name:

`personal_documents.ingest_selected`

Required descriptor semantics:

- permission scope: `WRITE`
- effect class: `STATE_CHANGING`
- interaction scope: `HUMAN`
- initiation policy: `HUMAN_APPROVAL`
- `requires_confirmation = True`

The descriptor must not be weakened to READ or READ_ONLY merely because the
first discovery turn is read-only. The capability contains a durable handoff to
the existing Inbox.

## Contracted state machine

The minimum permitted route is:

`explicit Owner intent`
`-> bounded existing discovery`
`-> metadata-only candidate presentation`
`-> explicit candidate selection`
`-> explicit ingestion confirmation`
`-> existing source.ingest_selected()`
`-> existing DocumentInboxManager`
`-> safe result presentation`
`-> STOP`

The following inequalities are contractual:

`DISCOVERY != INGESTION_AUTHORIZATION`

`CANDIDATE_SELECTION != DURABLE_INGESTION_AUTHORIZATION`

`INBOX_HANDOFF != REASONING_ADMISSION`

Neither discovery nor candidate selection may create a `DocumentRecord`.

## Explicit intent

The interception port must reject generic document/file language that does not
unambiguously refer to the governed personal-document source.

The RED admits an explicit phrase such as:

`consultá mis documentos personales: plan`

and rejects generic requests such as:

`buscá un documento`

`buscá archivos de ROBY`

This contract does not authorize broad semantic capture of every request that
mentions a PDF, file, document, or ROBY.

## Presentation and privacy

Discovery presentation is metadata-only.

It may expose safe relative paths and bounded non-sensitive metadata.

It must not expose:

- the absolute configured root;
- `personal-document:` internal source references;
- candidate IDs;
- document body content during discovery/disambiguation.

No hidden content search or second unbounded scan is authorized.

## Selection and confirmation

Selection state and confirmation state are ephemeral and session-scoped.

A selection may be made only from the candidates presented in the active
session, using a visible ordinal or exact presented relative path.

Selection must not ingest.

After selection, the port must ask for explicit confirmation of durable Inbox
handoff.

Confirmation is valid only for the selected candidate in the same session and
within the bounded TTL. The RED fixes the intended TTL at five minutes.

Cancellation clears pending state.

An expired confirmation cannot ingest.

A successful confirmation is one-shot: repeated `confirmo` after completion
must not perform another ingestion attempt from the same pending state.

## Existing ingestion authority

The future port must call the already existing
`PersonalDocumentRootDiscoveryAdapter.ingest_selected()`.

It must not duplicate source revalidation, file reading, MIME handling, or
Inbox persistence.

The source adapter continues to call the existing
`DocumentInboxManager.ingest_text()` and therefore remains the only selected
source-to-Inbox handoff implementation.

## Productive runtime reachability

Unlike the earlier D:\Roby consultation contract, this residual explicitly
includes productive composition-root reachability.

The future GREEN must wire the builder from `runtime_root_factory` into the
same `OfficialRuntimeCapabilityRegistry` already created there.

The builder must receive the same canonical `document_inbox` instance created
once by `build_document_inbox_from_environment()`.

No second `DocumentInboxManager` may be created by the new runtime module.

The document reader may be injected as the existing stateless extraction
service required by the source builder.

If `ROBY_PERSONAL_DOCUMENTS_ROOT` is absent or blank, no capability is
registered.

## STOP after ingestion

A successful handoff may present the resulting canonical `document_id` and
safe document metadata.

It must then STOP.

The contract does not authorize automatic:

- Reasoning admission;
- Knowledge admission;
- Memory admission;
- Learning admission;
- self-improvement;
- current-truth promotion;
- background scanning;
- watcher creation;
- source mutation.

Any later Reasoning use must continue through the existing explicit document-ID
admission authority.

## RED test

Added contract test:

`tests/architecture/`
`test_master_plan_d_documentos_explicit_owner_source_selection_`
`confirmed_inbox_handoff_contract_red.py`

The test contains 12 checks:

- 9 intended RED checks for the absent runtime module and productive wiring;
- 3 guardrails proving existing authorities remain intact.

The expected absent module is:

`app.personal_document_ingestion_runtime`

Expected public API:

- `PersonalDocumentIngestionInterceptionPort`
- `build_personal_document_ingestion_runtime_from_environment`
- `personal_document_ingestion_descriptor`

## Local RED result

Focused contract execution:

`9 failed, 3 passed`

All nine intended failures terminate at exactly:

`ModuleNotFoundError: No module named 'app.personal_document_ingestion_runtime'`

The three guardrails pass.

No productive module was added or modified in this RED.

## GREEN boundary

The smallest admissible GREEN is expected to require:

1. one subordinate conversation/runtime module implementing the contracted
   state machine and descriptor;
2. minimal imports and one builder invocation in `runtime_root_factory` so the
   capability is productively reachable through the existing registry.

The GREEN must not modify the canonical source, Inbox persistence, or Reasoning
admission semantics unless a concrete test proves an unavoidable integration
issue. Any such issue requires reconciliation before widening the surgery.

## Gate

`CONTRACT_RED: ESTABLISHED`

`INTENDED_RED: 9`

`GUARDRAILS_GREEN: 3`

`PRODUCT_CHANGE: NONE`

`CONTRACT_RED_AUTHORIZED: CONSUMED`

`SURGICAL_GREEN_AUTHORIZED: AFTER OWNER RED CERTIFICATION`

STOP before GREEN.
