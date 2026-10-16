# ROBY XI.2 — Probe B1-S8B
## Library Validation Collaborator Compatibility — SURGICAL GREEN

Status: SURGICAL GREEN — local build certification completed.

## Baseline

B1-S8A demonstrated one interface/substitutability regression introduced by
B1-S8: the retriever unconditionally required `validate_selected_entry()` on
its library collaborator, while the pre-existing ROBY-initiated CAP-17 path
uses a transparent collaborator that delegates catalogue operations to the
canonical `GovernedLocalLibraryCatalogueV1` authority.

The three affected pre-existing contracts reached the unique-candidate path
but returned `failed` instead of `completed`.

## Surgical change

`GovernedLocalDocumentRetrieverV1._validate_selection()` now resolves the
canonical point-validation operation through either:

- the supplied library collaborator when it exposes `validate_selected_entry`;
  or
- its transparent `delegate` when that delegate is the existing
  `GovernedLocalLibraryCatalogueV1` authority.

If neither route exposes the canonical validation authority, retrieval fails
closed with `TypeError`.

The validation algorithm remains exclusively in
`GovernedLocalLibraryCatalogueV1.validate_selected_entry()`. The retriever does
not reproduce entry reconstruction, identity, stale-entry, provenance, root,
or symlink rules and does not fall back to `catalogue()`.

## Preserved architecture

- CAP-17 catalogue authority remains canonical.
- Same-request selected-entry validation remains point validation.
- No second full catalogue traversal is reintroduced.
- No cache, index, manager, planner, agent, loop, authority, or capability was
  added.
- Unified retrieval execution remains the existing execution path.
- ROBY-initiated authorization remains one-shot and unchanged.
- B2/B3/B4 remain in STOP.

## Local build evidence

- Three B1-S8A affected contracts: 3 passed.
- Three B1-S7 reuse/validation contracts: 3 passed.
- Directly related CAP-17/B1 set executed in the build environment: 57 passed.
- `py_compile` passed for the modified productive module.
- Modified productive module contains no lines longer than 88 characters.

Ruff is not installed in the build environment. The complete suite was also
started but did not finish within the available execution window; neither gate
is therefore claimed as locally certified here. User-side Ruff and complete
suite certification remain authoritative.

## STOP boundary

This increment authorizes no broader optimization and no Probe B2/B3/B4 work.
Any further Probe B1 action must start from the locally certified S8B package
and the existing governed documentation.
