# M396.14 — No Autonomous Promotion Guardrails

## Invariant

**M396-I14 — No Autonomous Promotion**

No extended residence may decide, infer, trigger or obtain promotion to `PRIMARY_HOME`
by itself. Availability, capability richness, uptime, interaction frequency, user
preference, latency or temporary home unavailability never constitute promotion
authority.

## Rules

1. `PRIMARY_HOME` remains an explicit constitutional role, never a computed ranking.
2. `EXTENDED` never becomes `PRIMARY_HOME` because it is `AVAILABLE`.
3. An unavailable primary home does not cause automatic promotion or failover.
4. Capability count, performance, uptime or interaction frequency cannot rank
   residences.
5. Active `InteractionLocality` cannot change residence roles.
6. A preference about a residence has no architectural promotion power.
7. Residence Domain defines no promote, elect, takeover, leader or
   primary-selection API.
8. Runtime wiring contains no residence promotion, election or failover path.
9. Any future home migration requires a separate explicit governed contract.
10. I03-I13 remain binding.

## Architectural meaning

ROBY may one day prefer the mini-PC for some tasks, enjoy the Web as a window, or use
the
cellular residence more often. None of those experiences may silently rewrite the
home.

**Preference may influence experience; it never grants promotion authority.**
