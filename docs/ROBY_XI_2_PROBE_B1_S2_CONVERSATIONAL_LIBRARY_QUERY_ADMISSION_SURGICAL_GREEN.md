# ROBY XI.2 — Probe B1-S2 — Conversational Library Query Admission — SURGICAL GREEN

## Classification

SURGICAL GREEN. Product change is limited to the existing conversational admission owner
for governed local-library queries.

## Demonstrated residual

Probe B1-S1 locally certified that the productive request `Roby, busca en la biblioteca
el libro Robots e Imperio y decime cuando lo encontrás` reached the catalogue with
conversational tail material still inside the search query.

## Surgical change

`GovernedLocalLibraryConversationInterceptionPort._search_query()` now bounds the
demonstrated Spanish book-request form after the existing library prefix has been
removed. It returns only the book object between `el libro` and the trailing
confirmation request.

The rule is intentionally narrow. It does not create a general natural-language parser
and does not move interpretation into CAP-17. Existing quoted-query handling remains
prior and unchanged; existing simple library queries remain unchanged.

## Authority preservation

- CAP-17 remains the governed catalogue/read authority.
- The existing conversation interception port remains the admission owner.
- Desktop, Reasoning, capability registry, and configuration are unchanged.
- No new manager, planner, agent, loop, capability, or authority is introduced.

## Directed evidence

`tests/architecture/test_probe_b1_s1_conversational_library_query_admission_contract_red.py`: 2 passed.

The build environment used for packaging did not provide the `ruff` executable. Ruff and
the full suite therefore remain required in local certification; no claim of full local
certification is made here.

## STOP

STOP after the surgical GREEN package. Productive Probe B resumes only after local
certification.
