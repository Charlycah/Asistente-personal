# M398.10 — Governed Physical Transport Integration & Closure

## Closure purpose

M398.10 performs the final cross-stage integration audit for **M398 — Governed
Physical Transport**. It adds no new carrier, protocol, runtime authority or remote
capability. Its purpose is to prove that M398.1 through M398.9 form one governed
physical-transport capability subordinate to M397.

## Certified pre-closure baseline

M398.9 was externally validated with:

- `ruff check .` — clean.
- M361 regenerated.
- `pytest -q` — **10,799 passed, 0 failures**.

M398.10 starts only from that certified baseline.

## Permanent closure invariants

- **M398-C00 — One physical transport domain.** All M398 transport implementation
  remains under `core/physical_transport`.
- **M398-C01 — M397 remains logical authority.** Identity, authentication, admission,
  session lifecycle, health/readiness and logical failure/revocation remain owned by
  `core/connectivity_domain`.
- **M398-C02 — Carrier never becomes identity.** TCP address and
  `TransportPeerReference` remain adapter-local facts.
- **M398-C03 — Framing is bounded and fail-closed.** M398.4 remains the only wire
  representation authority for the auditable envelope.
- **M398-C04 — Physical lifecycle is separate.** Listener, dialer, EOF, close and
  redial do not create, revive or terminate M397 sessions.
- **M398-C05 — Recovery is bounded.** M398.7 contains no infinite/background retry
  engine and recovery never restores logical trust.
- **M398-C06 — End-to-end channel is composition only.** M398.8 joins existing
  contracts without creating another manager or authority.
- **M398-C07 — Security is mandatory but not authentication.** M398.9 guardrails
  reject replay, temporal abuse and context mismatch without replacing M397
  authentication/admission.
- **M398-C08 — No action authorization.** No M398 frame, carrier, binding, recovery,
  channel or security result authorizes operational execution.
- **M398-C09 — No distributed cognition.** M398 contains no remote tool execution,
  memory replication, cognitive routing or second ROBY brain.
- **M398-C10 — No hidden runtime activation.** M398 closes as a governed reusable
  capability; application/root runtime activation remains a later explicit decision.
- **M398-C11 — Closure is hash-audited.** The M398 physical domain and M397 logical
  domain are frozen in `M398_10_PHYSICAL_TRANSPORT_CLOSURE.json`.
- **M398-C12 — Documentation and quality remain synchronized.** Closure requires
  M361 regeneration, Ruff clean and the complete pytest suite.
- **M398-C13 — Future evolution must use the boundary.** New physical carriers or
  higher-level distributed capabilities must build through the closed M397/M398
  contracts rather than bypass them.

## Integrated architecture

The final governed path is:

`M397 logical governance`
→ `M398.2 runtime facts`
→ `M398.3 governed binding`
→ `M398.4 framing`
→ `M398.5 local TCP carrier`
→ `M398.6 listener/dialer lifecycle`
→ `M398.7 bounded recovery`
→ `M398.8 end-to-end residence channel`
→ `M398.9 security guardrails`

This chain does not transfer action authority to transport.

## Scope closed by M398

M398 now provides a concrete, testable physical communication path between ROBY
residences, including framing, local TCP, connection lifecycle, bounded recovery,
end-to-end envelope transport and transport-level anti-abuse checks.

## Explicitly outside the closure

M398 does not activate distributed cognition, remote capability execution, memory
replication, autonomous residence selection, public Internet exposure, cloud relay,
device discovery, encryption/PKI, or application runtime wiring. Those require later
governed stages.

## Formal closure statement

When M398.10 passes Ruff and the complete test suite, **M398 — Governed Physical
Transport is CLOSED**. No M398.11 should be created for new capability work. Future
work must open a new stage.
