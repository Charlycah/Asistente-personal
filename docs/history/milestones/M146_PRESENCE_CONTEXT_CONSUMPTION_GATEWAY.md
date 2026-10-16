# M146 — Presence Context Consumption Gateway

M146 exposes governed M145 logical deliveries through a stable consumer-facing boundary.

## Responsibility

- select the latest eligible delivery;
- validate consumer, topic, and schema compatibility;
- expose immutable complete or partial access records;
- preserve exact M145 delivery lineage;
- represent incompatible access explicitly as empty.

## Explicit exclusions

M146 does not execute consumers, transform context, confirm consumption, invoke callbacks, perform transport, infer identity/activity/intent, decide responses, adapt behavior, call providers, automate actions, or mutate the platform.
