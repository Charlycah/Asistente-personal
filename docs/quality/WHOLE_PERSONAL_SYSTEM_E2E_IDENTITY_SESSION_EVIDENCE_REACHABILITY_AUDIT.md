# ROBY XI.2 — Whole Personal System E2E Identity/Session Evidence Reachability Audit

Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**

Baseline audited: **12,355 PASS · 0 FAIL · Ruff clean**.

## Finding

WPS-01 correctly claims that personal Identity/Session reaches the official local
conversation and session-scoped context, but its historical `identity_session` evidence
only proved the existence of `PersonalIdentityRegistry.open_session()`. Productive runtime
reachability no longer depends on that method.

## Current productive chain

1. `app.household_always_on_bootstrap.bootstrap_household`
2. `app.personal_profile_factory.select_runtime_identity_from_environment`
3. `app.local_runtime_entrypoint.build_local_runtime_from_environment`
4. `app.local_conversation_factory.build_local_conversation_from_environment`
5. `core.end_to_end_local_conversation.runtime.EndToEndLocalConversation`

The runtime binds the selected `owner` and `session_id` into the governed conversation
request and derives session-scoped context from that request.

## Surgery

Only the static evidence requirements for WPS-01 and their architectural tests/frozen
report were reconciled. No productive runtime, Identity authority, store, persistence,
household provisioning behavior, Composition Root wiring, or private `.roby` state was
changed.

## Certification rule

This record must remain **PENDING / NOT CERTIFIED** until the owner executes the official
gate:

- `python scripts/clean_project_caches.py`
- `python scripts/generate_quality_baseline.py`
- `ruff check .`
- `pytest -q`
