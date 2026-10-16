# ROBY XI.2 — Probe B1-S1 — Conversational Library Query Admission — CONTRACT RED

## Classification

- CONTRACT RED / TESTS ONLY
- Product change: NONE
- CAP-17 catalogue change: NONE
- New authority: NONE
- STOP before GREEN

## Productive evidence

Probe B supplied a real ordinary-turn request equivalent to:

`Roby, busca en la biblioteca el libro Robots e Imperio y decime cuando lo encontrás`

The productive response reported no match for the surviving query equivalent to:

`el libro Robots e Imperio y decime cuando lo encontrás`

This demonstrates a bounded reachability/admission residual before the governed
CAP-17 catalogue: conversational material survives into the catalogue query.

## Existing owner

The existing `GovernedLocalLibraryConversationInterceptionPort` owns admission
of user library requests and `_search_query()` already bounds/normalizes the
text before `GovernedLocalLibraryConversationV1` invokes the governed
catalogue. The contract therefore reuses that authority. It does not authorize
a new parser, manager, catalogue, capability, or reasoning authority.

## Contract

The RED requires the existing admission boundary to:

1. convert the observed conversational request into the bounded bibliographic
   query `Robots e Imperio`;
2. preserve the already-supported simple request
   `Buscá en la biblioteca Robots e Imperio` unchanged;
3. continue through the existing CAP-17 governed catalogue and reading path.

The RED intentionally does not prescribe a general natural-language parser or
an implementation strategy.

## STOP boundary

No productive code is changed in this increment. A failing targeted test is the
required result. GREEN is a separate surgical step only after local RED
certification.
