# M396.10 — Credential Isolation Guardrails

## Invariant

**M396-I10 — Credential Isolation**

Residence membership, presence, capability declaration and interaction locality never
carry, copy, expose or distribute ROBY credentials. Credentials remain private local
runtime material under the pre-existing credential subsystem and are not Residence
Domain state.

## Rules

1. Residence models contain no credential, secret, token, password or API-key fields.
2. `ResidenceCandidate` and `ResidenceAdmissionRecord` carry no authentication secret.
3. `ResidenceIdentityAnchor` proves logical provenance, never possession of a secret.
4. A `PresenceEndpoint` never carries credentials or session secrets.
5. Residence capabilities cannot contain credential material as structured authority.
6. Admission never copies the primary home's credential store to an extended residence.
7. Availability or active interaction never causes credential propagation.
8. Residence Domain never imports the credential/secrets subsystem.
9. The canonical local `.roby/credentials.json` remains outside Residence Domain.
10. M396.10 introduces no credential replication, pairing secret, token exchange, remote
    secret store, authentication protocol or transport.
11. Any future residence authentication must use a separate governed security contract
    and must not imply copying ROBY's private service credentials.
12. I03-I09 remain binding.

## Architectural meaning

A mini-PC, cellular residence or Web endpoint may become an authorized place where the
same ROBY is present. That fact does not make the laptop's private credentials part of
the residence description and does not authorize copying those secrets elsewhere.

**A window may identify itself without receiving the keys to the house.**
