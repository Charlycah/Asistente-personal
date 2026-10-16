# ROBY XI.2 — CAP-17 — Productive Runtime Wiring — GREEN

## Purpose
Connect the already-certified governed local-library capability to ROBY's single
productive runtime composition root without adding a new cognitive authority.

## Productive wiring
- Environment root: `ROBY_LOCAL_LIBRARY_ROOT`.
- Missing root: `not_provisioned`.
- Invalid root: `invalid_configuration`.
- Valid root: `provisioned`.
- One shared `GovernedLocalLibraryCatalogueV1` instance.
- One `GovernedLocalLibraryConversationV1` composition path.
- One `GovernedIndependenceAuthorizationBoundaryV1` using the official runtime
  capability registry manager.
- One `GovernedRobyInitiatedLibraryAccessV1` adapter.
- One user-initiated interception port registered with the canonical descriptor
  `knowledge.local_library.read`.
- Retrieval continues through `OfficialUnifiedRetrievalExecutionRuntimeGateway`.

## Preserved boundaries
No EPUB support is introduced here. `Documentos` is not added as another root.
No Memory/Learning write occurs. No background scan, watcher, polling process,
alternate router, planner, retrieval runtime or `.roby/config.json` mutation is added.

## Contract
`tests/architecture/test_cap17_productive_runtime_wiring_red.py` contains the 20 RED
contracts promoted to GREEN by this increment.
