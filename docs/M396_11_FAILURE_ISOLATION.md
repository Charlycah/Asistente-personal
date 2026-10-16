# M396.11 — Failure Isolation Guardrails

## Invariant

**M396-I11 — Failure Isolation**

The failure, unavailability, revocation or disappearance of an extended residence or
presence endpoint must remain local to that context. It must not invalidate ROBY's
primary home, create a second authority, trigger implicit failover, or collapse the
residence model as a whole.

## Rules

1. An `EXTENDED` residence may be `UNAVAILABLE` while `PRIMARY_HOME` remains valid.
2. An `EXTENDED` residence may be `REVOKED` without revoking or replacing the home.
3. A missing or closed Web/presence endpoint does not invalidate the residence
   snapshot.
4. Failure of one extended residence does not change the identity of any other
   residence.
5. Failure does not promote another residence to `PRIMARY_HOME`.
6. Failure does not trigger leader election, home migration, replication or recovery.
7. Residence Domain contains no global shutdown, panic, failover or restart authority.
8. Runtime wiring remains unaware of Residence Domain at this stage.
9. Existing local ROBY behavior remains sufficient when no extended residence is usable.
10. I03-I10 remain binding.

## Architectural meaning

If the mini-PC is off, the cellular device loses connectivity, or a Web session closes,
ROBY's home does not disappear. Those windows become unavailable; the house remains.

**A broken window does not bring down the house.**
