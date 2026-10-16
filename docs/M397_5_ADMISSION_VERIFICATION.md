# M397.5 — Admission Verification

## Purpose

M397.5 connects an authenticated peer identity to the canonical residence membership
defined by M396 without granting connectivity authority the power to admit or revoke.

## Core rule

> **Connectivity may verify admission; only the residence domain owns admission.**

## Boundary

`AdmissionVerificationRequest` combines:

- the finite connectivity session;
- an explicit `PeerAuthenticationResult`;
- the immutable canonical `ResidenceContextSnapshot`.

`AdmissionVerificationResult` returns one explicit disposition:

- `ADMITTED`;
- `NOT_ADMITTED`;
- `REVOKED`;
- `INDETERMINATE`.

No result mutates residence state.

## Authentication prerequisite

Admission verification is meaningful only after identity verification.

A `REJECTED` or `INDETERMINATE` authentication result cannot be upgraded into
membership. M397.5 therefore fails closed with `INDETERMINATE`.

A mismatched authentication/session pair also fails closed.

## Canonical verification

`CanonicalResidenceAdmissionVerifier` is a pure read-only verifier.

For an extended residence it requires:

- matching canonical `ResidenceId`;
- non-revoked administrative state;
- explicit `admission_id` provenance.

For the primary home, canonical bootstrap membership is preserved without inventing an
explicit admission record.

An authenticated identity absent from the canonical residence snapshot is
`NOT_ADMITTED`.

A canonical residence marked `REVOKED` is `REVOKED` even if identity authentication is
otherwise valid.

## Authority boundary

M397.5 cannot:

- create a `ResidenceAdmissionRecord`;
- add a residence to `ResidenceContextSnapshot`;
- change `ResidenceAdministrativeState`;
- restore a revoked residence;
- promote an extended residence;
- grant command or capability authority;
- open a network connection;
- distribute credentials.

The verifier reads M396 state; it does not own it.

## State separation

M397.5 preserves:

`AUTHENTICATED != ADMITTED != CONNECTED != READY`

A peer can be authenticated yet not admitted, or authenticated and revoked.

## Runtime and transport

No socket, server, client, network address, cryptographic implementation or runtime
wiring is introduced by M397.5.

## Exit criterion

M397.5 is complete when membership verification is read-only, fail-closed, based on
canonical M396 state, transport-neutral and regression-tested.

> **ROBY may recognize who is knocking and still answer: "I know who you are, but you
> are not an admitted residence."**
