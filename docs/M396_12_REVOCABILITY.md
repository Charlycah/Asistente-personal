# M396.12 — Revocability

## Invariant

**M396-I12 — Revocability**

Every extended residence can be explicitly removed from the authorized residence set
without altering ROBY's identity, changing the primary home, or erasing the historical
fact that the residence was previously admitted.

## Rules

1. Revocation applies to `EXTENDED` residences, never to `PRIMARY_HOME`.
2. Revocation is explicit and auditable, not inferred from unavailability.
3. `UNAVAILABLE` is not equivalent to `REVOKED`.
4. A revocation record preserves `ResidenceId` and admission provenance.
5. Revocation does not delete historical admission identity.
6. Revocation does not promote another residence.
7. Revocation does not alter ROBY identity, memory, personality or cognitive authority.
8. Revocation does not execute remote shutdown, wipe, disconnect or credential deletion.
9. Re-admission, if ever permitted, requires a future explicit governed contract.
10. I03-I11 remain binding.

## Architectural meaning

ROBY can close a window permanently without pretending that the window never existed.
The house remains the same, and the history of that authorized extension remains
auditable.

**A revoked window stops belonging to the house; it does not rewrite the house.**
