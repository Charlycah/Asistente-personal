# PM2 / M163 — Conversation Entry Point

## Goal

Recognize how a user enters a conversation before any response is generated.

## Entry kinds

- greeting
- question
- request
- continuation
- comment
- attention
- farewell
- incomplete
- not applicable

## Core rules

- `Hola ROBY` is a greeting, never a command acknowledgement.
- `ROBY` alone is an attention call.
- Questions, requests, continuations and comments use distinct routes.
- M162 readiness lineage is preserved exactly.
- Blocked readiness withholds entry classification.
- M163 does not generate text or call any model.

## Safety boundary

The following remain false:

- response generation
- provider calls
- network access
- platform mutation
