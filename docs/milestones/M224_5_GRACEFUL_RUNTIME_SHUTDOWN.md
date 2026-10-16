# M224.5 — Graceful Runtime Shutdown

## Objective

Allow ROBY's local console to terminate cleanly without closing VS Code or leaving runtime resources active.

## Supported shutdown signals

- `exit`, `quit`, `salir`;
- `/exit`, `/quit`, `/salir`;
- EOF (`Ctrl+Z` then Enter on Windows, `Ctrl+D` on Unix);
- `Ctrl+C` while waiting for input or processing a turn.

## Guarantees

- shutdown commands never reach the conversation pipeline or provider;
- heartbeat supervision is stopped;
- long-lived lifecycle or bootstrap is stopped;
- runtime lease is released;
- existing error degradation behavior remains unchanged.
