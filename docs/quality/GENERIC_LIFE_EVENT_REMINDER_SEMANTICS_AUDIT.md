# Generic Life-Event Reminder Semantics Audit

## Decision

The phrase family `recordame` / `haceme acordar` already belongs to the canonical
Reminder capability and is intentionally topic-agnostic. Medical appointments, concerts,
travel, birthdays and ordinary household commitments are therefore not separate reminder
authorities.

Calendar remains separate: it is used only when the user explicitly asks to schedule or
create a calendar event. Reminder remains the authority when the user asks to be reminded.

## Bounded surgery

The existing reminder natural-language adapter now understands explicit calendar dates in
`DD/MM[/YYYY]`, `DD-MM[-YYYY]`, and Spanish named-month forms such as `3 de noviembre`.
The date is projected into the existing `due_at` field; temporal words are not retained in
the reminder title. A date without a year rolls to the next occurrence when the current-year
date has already passed. An explicitly supplied past year fails closed.

Existing recurrence remains authoritative, including yearly reminders for birthdays. No
category store, medical reminder model, event manager, calendar writer, notification broker
or new persistence path was added.

## Canonical boundary

`haceme acordar <anything>` -> existing Reminder conversation adapter -> existing Reminder
use cases/store -> existing Reminder Awareness -> existing Executive Notification path.

`agendá <event>` remains the existing Calendar confirmation-gated path.
