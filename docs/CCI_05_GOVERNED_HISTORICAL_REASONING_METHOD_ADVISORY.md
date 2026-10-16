# CCI-05 — Governed Historical Reasoning Method Advisory

## Contract

CCI-05 adds one bounded consultative consumer under the existing
`governed_reasoning` authority. It consumes certified historical method
awareness and may recommend, but never select or execute, one of the explicitly
supplied candidate method fingerprints when compatible evidence supports it.

The advisory is scope-bound and provenance-preserving. It does not establish
causality, global effectiveness or method superiority. It creates no memory,
learning candidate, persistence, authority, action or background process.

## Fail-closed behavior

- incompatible or insufficient history -> `NO_APPLICABLE_HISTORY`;
- review-required evidence -> `REVIEW_REQUIRED`;
- no unique supported method -> `AMBIGUOUS`;
- a bounded unique observed preference -> `METHOD_PREFERENCE_OBSERVED`;
- a single sufficiently supported candidate -> `ONE_METHOD_SUPPORTED`.

Every recommendation has `application_authorized = False`,
`selects_method = False`, `modifies_reasoning = False`, and
`reruns_reasoning = False`.

## Certification

The architectural certification covers bounded preference, single-method
support, scope isolation, minimum evidence, review-required history,
ambiguity, provenance preservation, and absence of persistence/learning/
execution/authority power.

CCI-05 closes only the advisory bridge. Automatic method selection or rerun is
explicitly outside this contract and requires a new Audit → Contract /
Go-No-Go.
