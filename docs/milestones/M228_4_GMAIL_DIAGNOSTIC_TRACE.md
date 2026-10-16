# M228.4 — Gmail Diagnostic Trace

## Objective

Extend M228.3 with a deterministic, secret-free stage trace for degraded Gmail startup
without changing the certified runtime contract.

## Delivered

- Immutable nine-stage Gmail diagnostic trace.
- Stable `OK`, `FAILED`, `NOT_EXECUTED`, and `DISABLED` states.
- Compact diagnostic preserved as the first output line.
- Structured trace serialization.
- No diagnostic preflight in startup wiring.
- No new Gmail capability, network call, or mailbox mutation.

## Operational example

```text
GMAIL> DEGRADED [token/credentials_unavailable]: No hay credenciales OAuth utilizables. Acción: Ejecutar la activación OAuth gobernada o corregir ROBY_GMAIL_TOKEN_PATH.
GMAIL TRACE> 1/9 Runtime: OK
GMAIL TRACE> 2/9 Configuration: OK
GMAIL TRACE> 3/9 google-auth: OK
GMAIL TRACE> 4/9 OAuth: OK
GMAIL TRACE> 5/9 Secure Credential Store: OK
GMAIL TRACE> 6/9 Token & Scopes: FAILED
GMAIL TRACE> 7/9 Gmail API Backend: NOT_EXECUTED
GMAIL TRACE> 8/9 Startup Announcement: NOT_EXECUTED
GMAIL TRACE> 9/9 Runtime Completion: NOT_EXECUTED
```
