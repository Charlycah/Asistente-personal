# M396.6 — Primary Residence Preservation

## Invariant

**M396-I06 — Primary Residence Preservation**

ROBY XI.2 preserves exactly one canonical `PRIMARY_HOME`. The primary home is the
continuity anchor of local residence and is not created by explicit admission, cannot
be revoked inside a `ResidenceContextSnapshot`, and cannot be displaced merely because
an extended residence or presence endpoint is available.

The current laptop remains the constitutional home. M396.6 does not hard-code a machine
name or hardware identifier: the stable `ResidenceId` established for the primary home
is the logical identity that carries home continuity.

## Rules

1. Every residence snapshot contains exactly one `PRIMARY_HOME`.
2. A primary home cannot be `REVOKED`.
3. A primary home carries no `admission_id`; explicit admission is for `EXTENDED` residences.
4. Availability does not determine primacy. An unavailable home remains the home.
5. An available extended residence never auto-promotes to primary.
6. A Web or other `PresenceEndpoint` never becomes home by being the active interaction.
7. Changing active `InteractionLocality` does not change `primary_home`.
8. M396.6 introduces no promotion, election, failover, leader selection or home migration.
9. Any future intentional home migration requires a separate governed contract.
10. Authority Preservation (M396-I03), Explicit Admission (I04), and Stable Residence
    Identity (I05) remain intact.

## Architectural meaning

The laptop is ROBY's home; mini-PC, cellular and Web can extend where the same ROBY is
present. Being elsewhere, even for a long time, does not silently rewrite where home is.

**One home. One ROBY. Many windows.**
