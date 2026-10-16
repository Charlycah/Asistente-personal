# Post-M409.1 — ROBY Conversational E2E Reality Check
## Read-Only Desktop Diagnostic Harness

Status: IMPLEMENTED — diagnostic instrumentation only.

The harness reuses the official Desktop composition and the existing
`DevelopmentConsoleObserver`/`DevelopmentConsoleRenderer`. It does not add a
CLI option, Desktop control, capability registration, routing authority,
planner, coordinator, memory writer, or provider.

The diagnostic path is intentionally external to `main.py` and to
`ROBYDesktopApp.run()`:

`build_unified_desktop_app()` → `DesktopConversationController.submit()` →
existing Desktop interceptors/adapters → `OfficialConversationGateway` when
reached → existing conversation runtime.

Each controlled prompt records whether the Desktop controller created a new
official runtime turn. A zero turn delta is reported as a pre-runtime Desktop
interception. When a runtime turn exists, the existing read-only observer
records context reconstruction/curation metadata, context sources, structured
messages, provider transport and (unless `--metadata-only` is used) the local
prompt/message content.

The three bounded probes are:

- A — context grounding (car ownership);
- B — contradiction / existing reasoning consumption;
- C — epistemic follow-up / routing.

Run locally from the repository root:

```text
python scripts/diagnostics/roby_conversational_e2e_harness.py
```

The script resolves and inserts the repository root into `sys.path` before
importing `app`/`core`, so direct execution does not depend on an external
`PYTHONPATH` setting. This direct-entry contract is covered by a subprocess
regression test.

Optional output path:

```text
python scripts/diagnostics/roby_conversational_e2e_harness.py --output trace.txt
```

Use `--metadata-only` when prompt/message content must not be written to the
local diagnostic file.

The observer is read-only, but the prompts deliberately traverse ROBY's normal
Desktop conversation path; therefore normal runtime/journal behavior is
preserved. This harness is diagnostic instrumentation, not a permanent user
feature and not a cognitive capability.
