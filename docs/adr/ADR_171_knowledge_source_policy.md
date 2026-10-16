# ADR-171 - Knowledge Source Policy

## Status

Accepted.

## Context

M166 evaluates provider health, M167 applies a local-first provider policy, and
M168 declares a concrete provider route. ROBY still needs an explicit boundary
that decides whether a request can be answered from internal knowledge, should
use local documents, requires external sources, or must be verified.

## Decision

Introduce M169 as a pure knowledge-source policy downstream from the exact M168
route. It consumes a typed knowledge need with internal confidence, freshness,
verification, local-document availability, sensitivity, and preferred-source
signals.

M169 publishes internal-sufficient, local-source-preferred,
external-source-required, verification-required, withheld, and not-applicable
outcomes. External source preferences can include official documentation, web,
news, or APIs.

M169 only declares source requirements. It cannot retrieve content, access the
network, call providers, or mutate the platform.

## Consequences

- Stable knowledge remains local when confidence is sufficient.
- Local documents can be preferred before public sources.
- Current or explicitly requested information is marked for external retrieval.
- Low-confidence claims can require verification rather than confident guessing.
- Actual source retrieval remains isolated for a later module.
